# -*- coding: utf-8 -*-
"""
backend/tests/test_annotate_security_alerts.py — Tests unitaires pour ANNOTATE_SECURITY_ALERTS.

Vérifie :
1. Factorisation de SECURITY_ALERT_KEYWORDS et de la fonction is_security_alert_text.
2. Réglage par défaut ANNOTATE_SECURITY_ALERTS = False.
3. Quand ANNOTATE_SECURITY_ALERTS est False (défaut) :
   - Un avertissement de sécurité ou alerte inédit reste en français sans annotation.
   - Aucun crochet '[' ou ']' n'est inséré autour d'un montant ou terme.
   - Le statut est 'fallback_source' et novel_annotated=False.
   - Le badge est « avertissement affiché en français : traduction non validée ».
   - L'intégrité financière est 100% vérifiée.
4. Quand ANNOTATE_SECURITY_ALERTS est True :
   - Les termes du glossaire sont annotés.
   - Le badge est « contenu inédit : termes annotés, phrase non traduite ».
5. Les contenus inédits non sécuritaires continuent d'être annotés normalement.
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.api import app, ANNOTATE_SECURITY_ALERTS
from backend.protect import SECURITY_ALERT_KEYWORDS, is_security_alert_text


class TestSecurityAlertKeywordsFactorization(unittest.TestCase):
    """Vérification de la factorisation des mots-clés de sécurité."""

    def test_keywords_not_empty(self):
        self.assertGreater(len(SECURITY_ALERT_KEYWORDS), 10)

    def test_expected_keywords_present(self):
        for kw in ["alerte", "sécurité", "securite", "attention", "fraude", "suspect", "danger", "warning", "alert"]:
            self.assertIn(kw, SECURITY_ALERT_KEYWORDS)

    def test_is_security_alert_text_positives(self):
        positives = [
            "Alerte de sécurité : tentative de débit suspect de 75 000 FCFA sur votre compte.",
            "Attention : activité suspecte détectée sur votre profil.",
            "Avertissement : votre carte a été bloquée pour cause de fraude.",
            "Security alert: unauthorized transaction attempt.",
            "Danger : ne communiquez jamais votre code confidentiel.",
        ]
        for p in positives:
            self.assertTrue(is_security_alert_text(p), f"Échec de détection positive pour: {p!r}")

    def test_is_security_alert_text_negatives(self):
        negatives = [
            "Votre solde disponible est de 25 000 FCFA.",
            "Confirmation de virement permanent.",
            "Un nouveau document est disponible dans votre espace client.",
            "Frais de transfert applicables.",
            "",
            None,
        ]
        for n in negatives:
            self.assertFalse(is_security_alert_text(n), f"Faux positif inattendu pour: {n!r}")


class TestAnnotateSecurityAlertsDefaultSetting(unittest.TestCase):
    """Vérification du réglage par défaut."""

    def test_default_is_false(self):
        # Par défaut dans le code, ANNOTATE_SECURITY_ALERTS doit être False
        self.assertFalse(ANNOTATE_SECURITY_ALERTS)


class TestTranslateBatchSecurityAlerts(unittest.TestCase):
    """Vérification du comportement de /translate/batch selon ANNOTATE_SECURITY_ALERTS."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_security_alert_default_false_remains_in_french(self):
        """Quand ANNOTATE_SECURITY_ALERTS=false (défaut), l'alerte reste en français sans annotation."""
        alert_text = "Alerte de sécurité : tentative de débit suspect de 75 000 FCFA sur votre compte."
        resp = self.client.post("/translate/batch", json={
            "source_lang": "fr",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "items": [{"id": "sec_1", "text": alert_text}]
        })
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]

        # Reste en français pur, sans aucun crochet
        self.assertEqual(item["target_text"], alert_text)
        self.assertNotIn("[", item["target_text"])
        self.assertNotIn("]", item["target_text"])

        # Statut et badges
        self.assertEqual(item["status"], "fallback_source")
        self.assertFalse(item.get("novel_annotated"))
        self.assertEqual(item.get("badge"), "avertissement affiché en français : traduction non validée")

        # Intégrité financière
        self.assertTrue(item["integrity_verified"])
        self.assertIn("75 000 FCFA", item["target_text"])

    def test_security_alert_explicit_false_in_payload(self):
        """annotate_security_alerts: false explicite dans la requête."""
        alert_text = "Attention alerte fraude : virement suspect de 100 000 FCFA."
        resp = self.client.post("/translate/batch", json={
            "source_lang": "fr",
            "target_lang": "bas",
            "allow_machine_translation": True,
            "annotate_security_alerts": False,
            "items": [{"id": "sec_2", "text": alert_text}]
        })
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]

        self.assertEqual(item["target_text"], alert_text)
        self.assertNotIn("[", item["target_text"])
        self.assertEqual(item["status"], "fallback_source")
        self.assertEqual(item.get("badge"), "avertissement affiché en français : traduction non validée")

    def test_security_alert_true_in_payload_annotates_glossary(self):
        """annotate_security_alerts: true explicite dans la requête -> glossaire annoté."""
        alert_text = "Alerte de sécurité : tentative de débit suspect de 75 000 FCFA sur votre compte."
        resp = self.client.post("/translate/batch", json={
            "source_lang": "fr",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "annotate_security_alerts": True,
            "items": [{"id": "sec_3", "text": alert_text}]
        })
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]

        # Montant préservé sans crochet
        self.assertIn("75 000 FCFA", item["target_text"])
        self.assertNotIn("[75 000 FCFA]", item["target_text"])

        # Statut machine_suggested et badge générique
        self.assertEqual(item["status"], "machine_suggested")
        self.assertTrue(item.get("novel_annotated"))
        self.assertEqual(item.get("badge"), "contenu inédit : termes annotés, phrase non traduite")

    def test_non_security_novel_content_annotated_normally(self):
        """Un contenu inédit non sécuritaire est annoté normalement quel que soit le réglage."""
        novel_text = "Votre solde actuel est suffisant pour ce transfert."
        resp = self.client.post("/translate/batch", json={
            "source_lang": "fr",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "annotate_security_alerts": False,
            "items": [{"id": "non_sec", "text": novel_text}]
        })
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]

        self.assertEqual(item["status"], "machine_suggested")
        self.assertTrue(item.get("novel_annotated"))
        self.assertEqual(item.get("badge"), "contenu inédit : termes annotés, phrase non traduite")


if __name__ == "__main__":
    unittest.main(verbosity=2)
