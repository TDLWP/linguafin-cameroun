# -*- coding: utf-8 -*-
"""
backend/tests/test_security_audit_v2.py — Tests automatisés de l'audit de sécurité v2.
Vérifie :
1. Limitation de débit (Rate Limiting anti-DoS HTTP 429 + Retry-After)
2. Validation des tailles de payloads sur /feedback et /translate/batch (HTTP 422 / 413 / 400)
3. Gestionnaire global d'exceptions (HTTP 500 sans fuite de données techniques)
4. Restrictions CORS (protection contre les origines non autorisées)
5. Anonymisation absolue des journaux (aucun texte utilisateur ni montant consigné)
"""

import io
import os
import sys
import time
import logging
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.api import app, reset_rate_limit, RATE_LIMIT_PER_MINUTE

client = TestClient(app)


class TestSecurityAuditV2(unittest.TestCase):

    def setUp(self):
        reset_rate_limit()

    def tearDown(self):
        reset_rate_limit()

    def test_rate_limiting_enforcement(self):
        """Vérifie que le dépassement du quota de requêtes par minute renvoie un code HTTP 429."""
        with patch("backend.api.RATE_LIMIT_PER_MINUTE", 5):
            # Consommer le quota autorisé
            for i in range(5):
                resp = client.get("/health")
                self.assertEqual(resp.status_code, 200, f"La requête {i+1} aurait dû réussir")

            # La requête suivante doit être bloquée avec HTTP 429
            blocked_resp = client.get("/health")
            self.assertEqual(blocked_resp.status_code, 429)
            self.assertEqual(blocked_resp.headers.get("retry-after"), "60")
            data = blocked_resp.json()
            self.assertIn("detail", data)
            self.assertIn("Limite de débit", data["detail"])

            # Après réinitialisation, l'accès est restauré
            reset_rate_limit()
            restored_resp = client.get("/health")
            self.assertEqual(restored_resp.status_code, 200)

    def test_rate_limiting_options_preflight_exempt(self):
        """Vérifie que les requêtes CORS pré-vol (OPTIONS) sont exemptées du compteur de rate limit."""
        with patch("backend.api.RATE_LIMIT_PER_MINUTE", 3):
            # Simuler un quota atteint
            for _ in range(3):
                client.get("/health")

            # Requête OPTIONS de preflight CORS (ne doit pas être bloquée en 429)
            options_resp = client.options("/translate/batch", headers={
                "Origin": "https://safinum.cm",
                "Access-Control-Request-Method": "POST"
            })
            self.assertNotEqual(options_resp.status_code, 429)

    def test_feedback_payload_size_validation(self):
        """Vérifie le rejet des payloads géants sur /feedback (protection anti-DoS disque/mémoire)."""
        # 1. source_text trop long (> 2000 caractères)
        oversized_payload = {
            "source_text": "A" * 2001,
            "target_lang": "dua",
            "suggested_translation": "Valide",
            "screen_context": "dashboard"
        }
        resp = client.post("/feedback", json=oversized_payload)
        self.assertEqual(resp.status_code, 422, "Un texte source > 2000 car. doit être rejeté en 422")

        # 2. suggested_translation trop long (> 2000 caractères)
        oversized_translation = {
            "source_text": "Solde",
            "target_lang": "dua",
            "suggested_translation": "B" * 2001,
            "screen_context": "dashboard"
        }
        resp2 = client.post("/feedback", json=oversized_translation)
        self.assertEqual(resp2.status_code, 422, "Une traduction > 2000 car. doit être rejetée en 422")

        # 3. Payload valide respectant les contraintes
        valid_payload = {
            "source_text": "Solde disponible",
            "target_lang": "dua",
            "suggested_translation": "Moni ma titi",
            "screen_context": "dashboard",
            "comment": "Traduction standard certifiée"
        }
        resp3 = client.post("/feedback", json=valid_payload)
        self.assertEqual(resp3.status_code, 201)

    def test_unhandled_exception_sanitization_no_leak(self):
        """Vérifie qu'une exception inattendue ne divulgue aucun détail technique (stack trace, chemins)."""
        safe_client = TestClient(app, raise_server_exceptions=False)
        with patch("backend.api.MEMOIRE.translations", new_callable=dict):
            # Forcer une exception inattendue lors de l'appel
            with patch("backend.api.is_security_alert_text", side_effect=RuntimeError("Secret database path: C:\\Secrets\\db.sqlite")):
                payload = {
                    "source_lang": "fr",
                    "target_lang": "dua",
                    "items": [{"id": "item1", "text": "Test exception"}]
                }
                resp = safe_client.post("/translate/batch", json=payload)
                self.assertEqual(resp.status_code, 500)
                data = resp.json()
                # Le corps doit être générique
                self.assertEqual(data.get("detail"), "Une erreur interne s'est produite. Aucun détail technique n'est divulgué.")
                # Aucune fuite d'informations sensibles
                self.assertNotIn("Secrets", str(resp.content))
                self.assertNotIn("RuntimeError", str(resp.content))
                self.assertNotIn("Traceback", str(resp.content))

    def test_cors_restriction(self):
        """Vérifie que les origines non autorisées ne reçoivent pas les headers CORS permissifs."""
        # Origine autorisée
        resp_allowed = client.get("/health", headers={"Origin": "https://safinum.cm"})
        self.assertEqual(resp_allowed.headers.get("access-control-allow-origin"), "https://safinum.cm")

        # Origine non autorisée
        resp_disallowed = client.get("/health", headers={"Origin": "https://malicious-site.example.com"})
        self.assertIsNone(resp_disallowed.headers.get("access-control-allow-origin"))

    def test_logger_strict_privacy_no_user_data(self):
        """Vérifie qu'aucun texte utilisateur ni montant n'est écrit dans les logs du serveur."""
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        target_logger = logging.getLogger("safinum_api")
        target_logger.addHandler(handler)

        sensitive_phrase = "Virement secret de 999999 FCFA pour M. Paul Atangana"
        payload = {
            "source_lang": "fr",
            "target_lang": "dua",
            "items": [{"id": "sec_item", "text": sensitive_phrase}]
        }

        try:
            resp = client.post("/translate/batch", json=payload)
            self.assertEqual(resp.status_code, 200)

            logged_output = log_stream.getvalue()
            # Vérifications d'absence absolue
            self.assertNotIn(sensitive_phrase, logged_output)
            self.assertNotIn("999999", logged_output)
            self.assertNotIn("Paul Atangana", logged_output)
            # Vérifier que les logs contiennent uniquement des métriques agrégées
            self.assertIn("1 items", logged_output)
        finally:
            target_logger.removeHandler(handler)


if __name__ == "__main__":
    unittest.main(verbosity=2)
