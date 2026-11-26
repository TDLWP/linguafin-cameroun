# -*- coding: utf-8 -*-
"""
tests/test_integrite_figee.py — Tests unitaires d'intégrité financière (91 cas figés).
Conforme aux règles de l'oracle de tests_integrite/run.js :
- Préservation caractère par caractère des valeurs sensibles
- Préservation intégrale des chiffres Unicode (\\p{Nd})
- Protection absolue des secrets (OTP / PIN) : jamais envoyés, jamais modifiés
- Préservation des valeurs pures
"""

import os
import sys
import json
import shutil
import unittest
import unicodedata
import subprocess
from typing import Dict, List, Any

# Encodage standardisé UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.protect import (
    mask_sensitive_data,
    restore_sensitive_data,
    verify_integrity,
    is_secret_text,
    TOKEN_REGEX,
)
from scripts.test_integrite_figee import (
    judge,
    run_path_a_protect_pipeline,
    run_path_b_api_batch,
    run_path_c_offline_node,
)
from fastapi.testclient import TestClient
from backend.api import app


class TestIntegriteFigee(unittest.TestCase):
    """Suite de tests unitaires rejouant cases.json (91 cas figés)."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.cases_file = os.path.join(PROJECT_ROOT, "tests_integrite", "cases.json")
        with open(cls.cases_file, "r", encoding="utf-8") as f:
            cls.cases_data = json.load(f)
        cls.cases = cls.cases_data.get("cases", [])

    def test_secrets_detection(self):
        """Vérifie la détection exacte des secrets (OTP, PIN, mots de passe) sans faux positif."""
        # Secrets positifs
        self.assertTrue(is_secret_text("Votre code OTP est 482913. Ne le communiquez à personne."))
        self.assertTrue(is_secret_text("Code PIN : 1234"))
        self.assertTrue(is_secret_text("Your one-time password is 482913"))
        self.assertTrue(is_secret_text("Votre code de validation est 992811"))
        self.assertTrue(is_secret_text("Temporary password: Pass1234"))

        # Non-secrets (recommandations ou messages d'avertissement sans code secret)
        self.assertFalse(is_secret_text("Ne partagez jamais votre code PIN."))
        self.assertFalse(is_secret_text("Votre mot de passe doit contenir 8 caractères."))
        self.assertFalse(is_secret_text("Total à débiter : 25 000 FCFA"))

    def test_secrets_never_sent_nor_modified_in_api(self):
        """Vérifie que l'API sanctuarise les secrets (OTP/PIN) : texte source restitué intact."""
        secret_texts = [
            "Votre code OTP est 482913. Ne le communiquez à personne.",
            "Code PIN : 1234",
            "Your one-time password is 482913"
        ]
        payload = {
            "source_lang": "fr",
            "target_lang": "dua",
            "items": [{"id": f"sec_{i}", "text": txt} for i, txt in enumerate(secret_texts)]
        }
        resp = self.client.post("/translate/batch", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        for i, item in enumerate(data.get("items", [])):
            self.assertEqual(item["target_text"], secret_texts[i], f"Le secret {secret_texts[i]} a été altéré !")
            self.assertEqual(item["status"], "fallback_source")
            self.assertTrue(item["integrity_verified"])

    def test_chemin_a_protect_pipeline_91_cases(self):
        """Chemin (a) : Pipeline protect.py (masquage/pseudo-traduction/restauration) sur les 91 cas."""
        outs = run_path_a_protect_pipeline(self.cases)
        self.assertEqual(len(outs), len(self.cases))

        echecs = []
        for i, c in enumerate(self.cases):
            res = judge(c, outs[i])
            if res["s"] == "ECHEC":
                echecs.append((c["id"], c["group"], res["why"], outs[i]))

        if echecs:
            msg = "\n".join([f"{cid} [{grp}] {why} (out: {repr(out)[:80]})" for cid, grp, why, out in echecs])
            self.fail(f"Échecs détectés sur Chemin (a) :\n{msg}")

    def test_chemin_b_api_batch_91_cases(self):
        """Chemin (b) : POST /translate/batch (FastAPI) sur les 91 cas (FR et EN)."""
        outs = run_path_b_api_batch(self.cases)
        self.assertEqual(len(outs), len(self.cases))

        echecs = []
        for i, c in enumerate(self.cases):
            res = judge(c, outs[i])
            if res["s"] == "ECHEC":
                echecs.append((c["id"], c["group"], res["why"], outs[i]))

        if echecs:
            msg = "\n".join([f"{cid} [{grp}] {why} (out: {repr(out)[:80]})" for cid, grp, why, out in echecs])
            self.fail(f"Échecs détectés sur Chemin (b) :\n{msg}")

    def test_chemin_c_status(self):
        """Chemin (c) : Vérifie le statut d'exécution hors ligne (jsdom)."""
        outs = run_path_c_offline_node(self.cases)
        if outs is not None:
            self.assertEqual(len(outs), len(self.cases))
            for i, c in enumerate(self.cases):
                res = judge(c, outs[i])
                self.assertNotEqual(res["s"], "ECHEC", f"Échec sur {c['id']}: {res['why']}")
        else:
            # jsdom non installé : statut attendu et documenté
            self.assertIsNone(outs)


if __name__ == "__main__":
    unittest.main()
