# -*- coding: utf-8 -*-
"""
Tests d'intégration de l'API locale FastAPI SAFINUM.
Vérifie les 4 endpoints : /health, /languages, /translate/batch, /feedback.
"""

import sys
import os
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.api import app

client = TestClient(app)


class TestSafinumAPI(unittest.TestCase):

    def test_health_endpoint(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["offline_catalog_loaded"])
        self.assertGreaterEqual(data["active_languages_count"], 2)

    def test_languages_endpoint(self):
        response = client.get("/languages")
        self.assertEqual(response.status_code, 200)
        langs = response.json()
        codes = [l["code"] for l in langs]
        self.assertIn("dua", codes)
        self.assertIn("bas", codes)
        # Vérification stricte : aucune entrée ne passe en human_validated sans locuteur natif
        dua_info = next(l for l in langs if l["code"] == "dua")
        self.assertEqual(dua_info["human_validated_entries"], 0, "Aucune traduction IA ne doit être human_validated")
        self.assertEqual(dua_info["status"], "machine_suggested")

    def test_batch_translation_endpoint(self):
        payload = {
            "source_lang": "fr",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "items": [
                {
                    "id": "item_1",
                    "text": "Solde disponible",
                    "screen_context": "dashboard"
                },
                {
                    "id": "item_2",
                    "text": "Frais de 1,5 % (min. 100 FCFA, max. 2 500 FCFA)",
                    "screen_context": "transfer_fees"
                },
                {
                    "id": "item_3",
                    "text": "Ce bénéficiaire n'a jamais été utilisé sur ce compte. Vérifiez le numéro avant de continuer.",
                    "screen_context": "beneficiary",
                    "is_critical_security": True
                }
            ]
        }
        response = client.post("/translate/batch", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_items"], 3)
        self.assertEqual(data["verified_integrity_rate"], 1.0)

        # Vérification item 2 : chiffres intacts et format bilingue FR [Proposition]
        item2 = data["items"][1]
        self.assertIn("1,5 %", item2["target_text"])
        self.assertIn("100 FCFA", item2["target_text"])
        self.assertIn("2 500 FCFA", item2["target_text"])
        self.assertTrue(item2["integrity_verified"])
        self.assertTrue(item2["bilingual_required"])
        # Format strict : texte français d'origine suivi de la proposition entre crochets
        self.assertTrue(item2["target_text"].startswith("Frais de 1,5 % (min. 100 FCFA, max. 2 500 FCFA) ["),
                        f"Format inattendu: {item2['target_text']}")

        # Vérification item 3 : sécurité critique bilingue
        item3 = data["items"][2]
        self.assertTrue(item3["bilingual_required"])
        self.assertTrue(item3["target_text"].startswith("Ce bénéficiaire n'a jamais été utilisé sur ce compte."),
                        f"Format inattendu: {item3['target_text']}")
        self.assertIn("[", item3["target_text"])
        self.assertIn("]", item3["target_text"])

    def test_feedback_endpoint(self):
        payload = {
            "source_text": "Solde disponible",
            "target_lang": "dua",
            "suggested_translation": "Moni mi titi",
            "screen_context": "dashboard",
            "validator_code": "TEST_VAL_01",
            "comment": "Test validation"
        }
        response = client.post("/feedback", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["status"], "recorded")
        self.assertTrue(data["feedback_id"].startswith("fbk_"))


    def test_fulfulde_engine_optional_fallback(self):
        """Vérifie que la langue ful est filtrée par défaut et accessible uniquement en mode expérimental."""
        # 1. Vérification dans /languages par défaut (ful absent)
        resp_lang = client.get("/languages")
        self.assertEqual(resp_lang.status_code, 200)
        codes = [l["code"] for l in resp_lang.json()]
        self.assertNotIn("ful", codes)

        # 1.bis Vérification avec include_experimental=true (ful présent)
        resp_lang_exp = client.get("/languages?include_experimental=true")
        self.assertEqual(resp_lang_exp.status_code, 200)
        codes_exp = [l["code"] for l in resp_lang_exp.json()]
        self.assertIn("ful", codes_exp)

        # 2. Requête vers Fulfulde SANS mode expérimental : repli source obligatoire immédiat
        payload_default = {
            "source_lang": "fr",
            "target_lang": "ful",
            "allow_machine_translation": True,
            "allow_experimental": False,
            "items": [
                {"id": "ful_1", "text": "Votre solde disponible est de 125 000 FCFA."},
                {"id": "ful_2", "text": "Confirmer le transfert"}
            ]
        }
        resp_default = client.post("/translate/batch", json=payload_default)
        self.assertEqual(resp_default.status_code, 200)
        data_default = resp_default.json()
        self.assertEqual(data_default["items"][0]["status"], "fallback_source")
        self.assertEqual(data_default["items"][1]["status"], "fallback_source")
        self.assertEqual(data_default["items"][1]["target_text"], "Confirmer le transfert")

        # 3. Requête vers Fulfulde AVEC mode expérimental : moteur activé
        payload_exp = dict(payload_default)
        payload_exp["allow_experimental"] = True
        resp_exp = client.post("/translate/batch", json=payload_exp)
        self.assertEqual(resp_exp.status_code, 200)
        data_exp = resp_exp.json()
        self.assertEqual(len(data_exp["items"]), 2)
        
        # item1 (avec montant sensible) : repli source sécurisé
        item1 = data_exp["items"][0]
        self.assertEqual(item1["source_text"], "Votre solde disponible est de 125 000 FCFA.")
        self.assertIn("125 000 FCFA", item1["target_text"])
        self.assertEqual(item1["status"], "fallback_source")

        # item2 : traduit par le modèle CTranslate2 si disponible, sinon repli source garanti
        item2 = data_exp["items"][1]
        self.assertEqual(item2["source_text"], "Confirmer le transfert")
        from backend.api import FULFULDE_ENGINE
        if FULFULDE_ENGINE.is_available():
            self.assertEqual(item2["status"], "machine_suggested")
            self.assertNotEqual(item2["target_text"], "Confirmer le transfert")
        else:
            self.assertEqual(item2["status"], "fallback_source")
            self.assertEqual(item2["target_text"], "Confirmer le transfert")


if __name__ == "__main__":
    unittest.main()

