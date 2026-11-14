# -*- coding: utf-8 -*-
"""
Tests unitaires pour le moteur de masquage et de vérification d'intégrité financière.
SAFINUM Innovate Challenge 2026.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.masking import mask_sensitive_data, restore_sensitive_data


class TestMaskingEngine(unittest.TestCase):

    def test_amount_and_currency_masking(self):
        text = "Solde disponible : 250 000 FCFA"
        masked, tokens = mask_sensitive_data(text)
        self.assertNotIn("250 000 FCFA", masked)
        self.assertEqual(len(tokens), 1)

        # Restauration normale
        translated_masked = masked.replace("Solde disponible", "Moni mi titi")
        restored, ok = restore_sensitive_data(translated_masked, tokens, text)
        self.assertTrue(ok)
        self.assertEqual(restored, "Moni mi titi : 250 000 FCFA")

    def test_complex_fee_sentence(self):
        text = "Frais de 1,5 % (min. 100 FCFA, max. 2 500 FCFA)"
        masked, tokens = mask_sensitive_data(text)
        self.assertNotIn("1,5 %", masked)
        self.assertNotIn("100 FCFA", masked)
        self.assertNotIn("2 500 FCFA", masked)
        self.assertEqual(len(tokens), 3)

        # Restauration simulée en Duala
        translated_dummy = masked.replace("Frais de", "Mutoa ma")
        restored, ok = restore_sensitive_data(translated_dummy, tokens, text)
        self.assertTrue(ok)
        self.assertEqual(restored, "Mutoa ma 1,5 % (min. 100 FCFA, max. 2 500 FCFA)")

    def test_account_and_phone(self):
        text = "Compte CM 001 2345 6789 01 lié au +237 6 99 12 34 56"
        masked, tokens = mask_sensitive_data(text)
        self.assertNotIn("CM 001 2345 6789 01", masked)
        self.assertNotIn("+237 6 99 12 34 56", masked)
        self.assertEqual(len(tokens), 2)

        restored, ok = restore_sensitive_data(masked, tokens, text)
        self.assertTrue(ok)
        self.assertEqual(restored, text)

    def test_reference_and_name(self):
        text = "Transfert SAF-2026-X7Y8Z9 envoyé à Jean-Paul Mbarga"
        masked, tokens = mask_sensitive_data(text)
        self.assertNotIn("SAF-2026-X7Y8Z9", masked)
        self.assertNotIn("Jean-Paul Mbarga", masked)
        self.assertEqual(len(tokens), 2)

        restored, ok = restore_sensitive_data(masked, tokens, text)
        self.assertTrue(ok)
        self.assertEqual(restored, text)

    def test_integrity_failure_fallback_to_source(self):
        """Si un jeton est supprimé par le moteur de traduction, repli immédiat au texte source."""
        text = "Solde restant : 225 000 FCFA"
        masked, tokens = mask_sensitive_data(text)

        # Simulation d'une altération : un jeton a disparu ou a été tronqué
        corrupted_translation = "Moni mi matiké : [jeton_perdu]"
        restored, ok = restore_sensitive_data(corrupted_translation, tokens, text)
        self.assertFalse(ok)
        # RÈGLE ABSOLUE : retour au texte source original
        self.assertEqual(restored, text)


if __name__ == "__main__":
    unittest.main()
