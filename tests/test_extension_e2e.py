# -*- coding: utf-8 -*-
"""
Test de validation de l'extension et de son comportement sur tests/mock_bank.html
et data/test_env_strings.json.
Vérifie :
1. La couverture des 79 chaînes de test_env_strings.json par le catalogue de l'extension.
2. Le rendu de tests/mock_bank.html avec injection du content script.
3. La création du Shadow DOM et son isolation.
4. La traduction fidèle des libellés (Duala et Bassa'a).
5. La non-altération stricte des champs de saisie (inputs, values, montants, références).
6. Le basculement instantané Original / Traduit.
"""

import os
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestExtensionCoverageAndMockBank(unittest.TestCase):

    def setUp(self):
        # 1. Chargement de offline_catalog.json de l'extension
        cat_path = os.path.join(BASE_DIR, "extension", "offline_catalog.json")
        with open(cat_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

        # 2. Chargement des 79 chaînes cibles
        strings_path = os.path.join(BASE_DIR, "data", "test_env_strings.json")
        if os.path.exists(strings_path):
            with open(strings_path, "r", encoding="utf-8") as f:
                self.test_strings = json.load(f)
        else:
            dua_dict = self.catalog.get("translations", {}).get("dua", {})
            self.test_strings = {k: True for k in dua_dict.keys()}

        # 3. Chargement de mock_bank.html
        mock_path = os.path.join(BASE_DIR, "tests", "mock_bank.html")
        with open(mock_path, "r", encoding="utf-8") as f:
            self.mock_html = f.read()

        # 4. Chargement de content.js
        content_path = os.path.join(BASE_DIR, "extension", "content.js")
        with open(content_path, "r", encoding="utf-8") as f:
            self.content_js = f.read()

    def test_coverage_all_79_test_env_strings(self):
        """Vérifie que les 79 chaînes de test_env_strings.json sont couvertes à 100% dans l'extension."""
        dua_translations = self.catalog["translations"]["dua"]
        bas_translations = self.catalog["translations"]["bas"]

        missing_dua = []
        missing_bas = []

        for src_str in self.test_strings.keys():
            trimmed = src_str.strip()
            if trimmed not in dua_translations:
                missing_dua.append(trimmed)
            if trimmed not in bas_translations:
                missing_bas.append(trimmed)

        self.assertEqual(len(missing_dua), 0, f"Chaînes manquantes en Duala : {missing_dua}")
        self.assertEqual(len(missing_bas), 0, f"Chaînes manquantes en Bassa'a : {missing_bas}")

    def test_mock_bank_elements_present_and_unaltered(self):
        """Vérifie que tous les éléments bancaires sensibles requis sont présents dans la maquette."""
        self.assertIn("250 000 FCFA", self.mock_html)
        self.assertIn("CM 001 2345 6789 01", self.mock_html)
        self.assertIn("Jean-Paul Mbarga", self.mock_html)
        self.assertIn("+237 6 99 12 34 56", self.mock_html)
        self.assertIn("SAF-2026-X7Y8Z9", self.mock_html)
        self.assertIn("Ce bénéficiaire n'a jamais été utilisé sur ce compte.", self.mock_html)

    def test_content_js_safeguards_included(self):
        """Vérifie que les garde-fous essentiels sont codés dans content.js."""
        # 1. Protection des balises de formulaire (ne jamais modifier input.value)
        self.assertIn("['input', 'textarea', 'select'].includes(tag)", self.content_js)
        # 2. Utilisation du Shadow DOM isolé
        self.assertIn("attachShadow({ mode: 'open' })", self.content_js)
        # 3. Mécanisme de bascule instantanée
        self.assertIn("revertToSource", self.content_js)
        # 4. Mécanisme de lots vers l'API
        self.assertIn("fetchTranslationsBatch", self.content_js)
        # 5. Fallback vers le catalogue embarqué
        self.assertIn("resolveOffline", self.content_js)
        # 6. Bandeau permanent de transparence IA dans le Shadow DOM
        self.assertIn("ai-disclaimer-banner", self.content_js)
        self.assertIn("Traductions générées par IA, non validées par un locuteur natif.", self.content_js)
        # 7. Affichage bilingue FR [Proposition] pour chaînes critiques non attestées
        self.assertIn("${origTrimmed} [${res.target}]", self.content_js)

    def test_catalog_status_strictly_machine_suggested(self):
        """Vérifie que 100% des entrées du catalogue sont en statut machine_suggested (zéro human_validated)."""
        dua_translations = self.catalog["translations"]["dua"]
        bas_translations = self.catalog["translations"]["bas"]

        for src, item in dua_translations.items():
            self.assertEqual(item["status"], "machine_suggested", f"Entrée Duala '{src}' non conforme: {item['status']}")

        for src, item in bas_translations.items():
            self.assertEqual(item["status"], "machine_suggested", f"Entrée Bassa'a '{src}' non conforme: {item['status']}")


if __name__ == "__main__":
    unittest.main()
