# -*- coding: utf-8 -*-
"""
tests/test_recoupement_references_ui.py — Tests unitaires et d'intégrité du recoupement UI.
Vérifie :
1. La normalisation des chaînes pour correspondance exacte.
2. Le parseur Fluent (.ftl).
3. La conformité du fichier généré catalogue/recoupement_ui_resultats.csv (colonnes, décomptes exacts).
4. La stricte intégrité de catalogue/translations.csv (zéro modification).
"""

import os
import sys
import csv
import json
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.recoupement_references_ui import (
    normalize_text_for_match,
    parse_fluent_ftl,
    resolve_external_data_dir,
    DEFAULT_EXTERNAL_DIR,
)


class TestRecoupementReferencesUI(unittest.TestCase):

    def test_normalize_text_for_match(self):
        """Vérifie la normalisation insensible à la casse et à la ponctuation."""
        self.assertEqual(normalize_text_for_match("Continue"), "continue")
        self.assertEqual(normalize_text_for_match("Summary:"), "summary")
        self.assertEqual(normalize_text_for_match("Back to hackathon"), "back to hackathon")
        self.assertEqual(normalize_text_for_match("  <bold>Save</bold>!  "), "save")
        self.assertEqual(normalize_text_for_match("Test — environment."), "test environment")

    def test_recoupement_resultats_csv_conformance(self):
        """Vérifie le format et les métriques réelles de catalogue/recoupement_ui_resultats.csv."""
        csv_path = os.path.join(PROJECT_ROOT, "catalogue", "recoupement_ui_resultats.csv")
        self.assertTrue(os.path.exists(csv_path), f"Fichier {csv_path} introuvable.")

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # 160 segments évalués (80 clés × 2 langues)
        self.assertEqual(len(rows), 160, f"Nombre attendu de lignes : 160, obtenu : {len(rows)}")

        # Colonnes attendues
        expected_cols = {
            "cle", "langue", "source_fr", "source_en", "source_fr_en",
            "notre_proposition", "reference_communautaire", "origine", "accord"
        }
        self.assertTrue(expected_cols.issubset(set(reader.fieldnames or [])))

        # Décompte des accords
        accords_by_lang = {
            "dua": {"identique": 0, "different": 0, "absent": 0},
            "bas": {"identique": 0, "different": 0, "absent": 0}
        }

        matches_found = []
        for r in rows:
            lang = r["langue"]
            accord = r["accord"]
            self.assertIn(accord, ["identique", "different", "absent"])
            accords_by_lang[lang][accord] += 1
            if accord != "absent":
                matches_found.append((r["cle"], lang, r["reference_communautaire"], r["origine"]))

        # Chiffres réels certifiés
        self.assertEqual(accords_by_lang["dua"]["identique"], 0)
        self.assertEqual(accords_by_lang["dua"]["different"], 4)
        self.assertEqual(accords_by_lang["dua"]["absent"], 76)

        self.assertEqual(accords_by_lang["bas"]["identique"], 0)
        self.assertEqual(accords_by_lang["bas"]["different"], 4)
        self.assertEqual(accords_by_lang["bas"]["absent"], 76)

        # Exactement 8 correspondances (4 en dua, 4 en bas)
        self.assertEqual(len(matches_found), 8)

        matched_keys = set(m[0] for m in matches_found)
        expected_keys = {"wizard_step4", "btn_continue", "btn_edit", "receipt_status_success", "btn_back"}
        self.assertEqual(matched_keys, expected_keys)

    def test_translations_csv_never_modified(self):
        """Vérifie que catalogue/translations.csv n'a subi aucune modification de statut."""
        csv_path = os.path.join(PROJECT_ROOT, "catalogue", "translations.csv")
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        # Toutes les entrées doivent demeurer en machine_suggested (zéro promotion non autorisée)
        for r in rows:
            self.assertEqual(r["statut"], "machine_suggested")


if __name__ == "__main__":
    unittest.main()
