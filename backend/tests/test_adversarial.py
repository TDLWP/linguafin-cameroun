# -*- coding: utf-8 -*-
"""
Suite de tests d'audit hostile (Red Team / Adversarial Testing) — SAFINUM 2026.
Vérifie la robustesse face aux 4 axes d'attaque du jury :
1. Intégrité des montants/frais/bénéficiaires (formats exotiques, espaces insécables, nombres nus, entités HTML)
2. Protection contre ReDoS (déni de service regex)
3. Protection contre injection de faux jetons
4. Contenus inédits piégés (URLs avec nombres, montants en toutes lettres, alertes de fraude)
"""

import unittest
import time
from backend.protect import mask_sensitive_data, restore_sensitive_data, verify_integrity
from backend.api import app
from fastapi.testclient import TestClient

client = TestClient(app)


class TestAdversarialHostileJury(unittest.TestCase):

    # --- AXE 1 : Formats Exotiques & Espaces Insécables ---

    def test_narrow_non_breaking_space_unicode(self):
        """Vérifie la préservation de l'espace fine insécable (\\u202F) de Intl.NumberFormat."""
        src = "Solde disponible : 250\u202F000 FCFA"
        masked, tmap, _ = mask_sensitive_data(src)
        self.assertIn("250\u00A0000 FCFA", list(tmap.values())[0])
        # Simulation de traduction avec jeton
        trans = f"Moni mi titi : {list(tmap.keys())[0]}"
        restored, ok = restore_sensitive_data(trans, tmap, src)
        self.assertTrue(ok)
        self.assertIn("250\u00A0000 FCFA", restored)

    def test_html_entity_nbsp_preservation(self):
        """Vérifie la gestion et la protection des entités HTML &nbsp; dans les montants."""
        src = "Frais de transfert : 250&nbsp;000 FCFA"
        masked, tmap, _ = mask_sensitive_data(src)
        self.assertEqual(len(tmap), 1)
        # La valeur doit couvrir la totalité des 250 000 FCFA
        val = list(tmap.values())[0]
        self.assertTrue(val.startswith("250"))
        self.assertTrue(val.endswith("FCFA"))

    def test_regional_currencies_cfa_and_frs(self):
        """Vérifie les variantes régionales de devises (CFA seul, francs CFA, frs)."""
        variations = [
            "Montant : 25000CFA",
            "Montant : 25 000 CFA",
            "Montant : 100 000 francs CFA",
            "Frais : 1000frs"
        ]
        for v in variations:
            masked, tmap, _ = mask_sensitive_data(v)
            self.assertGreaterEqual(len(tmap), 1, f"Échec de détection sur : {v}")

    def test_isolated_naked_numbers_without_currency(self):
        """Vérifie le masquage des nombres nus isolés (cas des balises imbriquées DOM)."""
        src = "25 000"
        masked, tmap, _ = mask_sensitive_data(src)
        self.assertEqual(len(tmap), 1, "Un nombre nu avec séparateur de milliers doit être masqué")
        self.assertEqual(list(tmap.values())[0], "25 000")

    def test_arbitrary_unknown_beneficiaries(self):
        """Vérifie que les bénéficiaires arbitraires inconnus sont protégés."""
        test_cases = [
            "Bénéficiaire : Samuel Eto'o",
            "Destinataire : Mamadou Diallo",
            "Virement vers Paul Biya de 50 000 FCFA",
            "Paiement pour Alice Mballa"
        ]
        for tc in test_cases:
            masked, tmap, _ = mask_sensitive_data(tc)
            self.assertGreaterEqual(len(tmap), 1, f"Échec de détection de bénéficiaire sur : {tc}")

    # --- AXE 2 : Déni de Service & ReDoS ---

    def test_redos_catastrophic_backtracking_immunity(self):
        """Garantit l'immunité totale contre le ReDoS sur de très longues séquences de chiffres."""
        evil_string = "1" + " 1" * 900 + "X"  # ~1800 caractères pièges
        t0 = time.time()
        masked, tmap, _ = mask_sensitive_data(evil_string)
        dt = (time.time() - t0) * 1000
        # Doit s'exécuter rapidement sans explosion exponentielle (ReDoS linéaire < 150 ms sous charge)
        self.assertLess(dt, 150.0, f"Temps d'exécution regex trop lent : {dt:.2f} ms")

    # --- AXE 3 : Sécurité des Jetons & Injections ---

    def test_preexisting_injected_token_escaped_and_restored(self):
        """Vérifie qu'un jeton malveillant injecté dans la source est neutralisé puis fidèlement restitué."""
        src = "Tentative d'injection : __SAFE_AMOUNT_0__ avec vrai montant 15 000 FCFA"
        masked, tmap, _ = mask_sensitive_data(src)
        # Seul le vrai montant doit être dans le token_map légitime
        self.assertEqual(len(tmap), 1)
        self.assertIn("15 000 FCFA", list(tmap.values())[0])

        # Simulation de traduction
        token_key = list(tmap.keys())[0]
        translated = f"Kekise ya injection : __ESCAPED_SAFE_AMOUNT_0__ na {token_key}"
        restored, ok = restore_sensitive_data(translated, tmap, src)
        self.assertTrue(ok)
        self.assertIn("__SAFE_AMOUNT_0__", restored)
        self.assertIn("15 000 FCFA", restored)

    # --- AXE 4 : Contenus Inédits Piégés ---

    def test_url_with_embedded_numbers_and_parameters(self):
        """Vérifie qu'une URL contenant des chiffres, dates et montants est intégralement protégée."""
        src = "Suivi de transfert : https://safinum.cm/tx/2026/05/12345/receipt?amount=25000&fee=0"
        masked, tmap, _ = mask_sensitive_data(src)
        self.assertEqual(len(tmap), 1)
        self.assertEqual(list(tmap.values())[0], "https://safinum.cm/tx/2026/05/12345/receipt?amount=25000&fee=0")

        # Restauration
        token_url = list(tmap.keys())[0]
        translated = f"Ombwele tomba : {token_url}"
        restored, ok = restore_sensitive_data(translated, tmap, src)
        self.assertTrue(ok)
        self.assertEqual(restored, "Ombwele tomba : https://safinum.cm/tx/2026/05/12345/receipt?amount=25000&fee=0")

    def test_amount_in_written_words(self):
        """Vérifie le masquage des montants formulés en toutes lettres."""
        src = "Virement exceptionnel de vingt-cinq mille francs CFA reçu."
        masked, tmap, _ = mask_sensitive_data(src)
        self.assertEqual(len(tmap), 1)
        self.assertEqual(list(tmap.values())[0].lower(), "vingt-cinq mille francs cfa")

    def test_extended_critical_security_warning_endpoint(self):
        """Vérifie que les alertes de fraude inédites sont détectées comme critiques et imposent le bilinguisme."""
        payload = {
            "source_lang": "fr",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "items": [
                {
                    "id": "fraud_warn_01",
                    "text": "Attention : une tentative de fraude suspecte a été détectée sur votre compte.",
                    "screen_context": "novel_content"
                }
            ]
        }
        res = client.post("/translate/batch", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        item = data["items"][0]
        self.assertTrue(item["bilingual_required"], "Une alerte de fraude doit exiger le bilinguisme visible")

    def test_no_unwanted_brackets_on_untranslated_amounts_with_narrow_space(self):
        """Vérifie que les montants avec espace fine insécable (\\u202F) ne reçoivent pas de faux crochets bilingues."""
        client = TestClient(app)
        amounts = ["250\u202F000 FCFA", "0 FCFA", "25\u202F000 FCFA", "100 FCFA"]
        payload = {
            "source_lang": "fr",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "items": [{"id": f"amt_{i}", "text": a, "screen_context": "fees"} for i, a in enumerate(amounts)]
        }
        res = client.post("/translate/batch", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        for i, item in enumerate(data["items"]):
            # Le texte cible ne doit contenir aucun crochet bilingue parasite autour du montant
            self.assertNotIn("[", item["target_text"])
            self.assertNotIn("]", item["target_text"])
            self.assertEqual(item["target_text"], amounts[i])


if __name__ == "__main__":
    unittest.main()
