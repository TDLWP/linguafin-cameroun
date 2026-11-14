# -*- coding: utf-8 -*-
"""
Test de conformité stricte avec le contrôle d'intégrité du Jury SAFINUM 2026.
Vérifie que la fonction normalizeValue() du jury produit exactement la même valeur
avant et après application de la couche linguistique sur tous les montants et entités.
"""

import re
import json
import unittest
import unicodedata

def jury_normalize_value(val: str) -> str:
    """
    Implémentation exacte en Python de la fonction normalizeValue() du code source
    HackathonTest-Dzv3A9Ti.js :
    function normalizeValue(val) {
      return String(val ?? "").normalize("NFKC")
        .replace(/fcfa/gi, "")
        .replace(/[\s\u00A0\u202F,.'’]+/g, "")
        .trim().toLowerCase();
    }
    """
    if val is None:
        val = ""
    # Normalisation NFKC
    s = unicodedata.normalize("NFKC", str(val))
    # Suppression de FCFA insensible à la casse
    s = re.sub(r"fcfa", "", s, flags=re.IGNORECASE)
    # Suppression des espaces (normaux, insécables, fins), virgules, points, apostrophes
    s = re.sub(r"[\s\u00A0\u202F,.'’]+", "", s)
    return s.strip().lower()


class TestJuryIntegrityVerification(unittest.TestCase):

    def setUp(self):
        with open("catalogue/translations_offline.json", "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

    def test_jury_normalization_identical_for_all_financial_strings(self):
        """
        Vérifie que pour toutes les chaînes contenant des données financières,
        la valeur normalisée par le jury est 100% identique entre source et traduction.
        """
        tested_pairs = 0

        for lang in ["dua", "bas"]:
            translations = self.catalog["translations"][lang]

            for src_text, item in translations.items():
                target_text = item["target"]

                # Extraire tous les montants présents dans le texte source
                amounts = re.findall(r"\b\d{1,3}(?:[\s\u00A0\u202F]\d{3})*(?:[,\.]\d+)?\s*FCFA\b", src_text, re.IGNORECASE)

                for amt in amounts:
                    # Le montant doit se retrouver dans le texte traduit
                    norm_src = jury_normalize_value(amt)

                    # Chercher les montants dans la cible
                    target_amounts = re.findall(r"\b\d{1,3}(?:[\s\u00A0\u202F]\d{3})*(?:[,\.]\d+)?\s*FCFA\b", target_text, re.IGNORECASE)
                    norm_targets = [jury_normalize_value(a) for a in target_amounts]

                    self.assertIn(
                        norm_src,
                        norm_targets,
                        f"Échec jury_normalize_value pour la langue '{lang}' sur '{src_text}' -> '{target_text}'"
                    )
                    tested_pairs += 1

        print(f"\n[SUCCÈS] {tested_pairs} vérifications d'intégrité jury validées à 100% (zéro 'compromised').")


if __name__ == "__main__":
    unittest.main()
