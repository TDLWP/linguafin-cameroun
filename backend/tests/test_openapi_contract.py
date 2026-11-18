# -*- coding: utf-8 -*-
"""
backend/tests/test_openapi_contract.py — Validation du contrat OpenAPI (openapi.yaml vs FastAPI).
Vérifie la stricte conformité entre la spécification openapi.yaml et l'implémentation effective
de backend/api.py (app.openapi()) :
- Chemins d'API et méthodes HTTP
- Paramètres de requête (ex: include_experimental sur /languages)
- Modèles et propriétés de requête (allow_experimental, annotate_security_alerts, source_lang)
- Schémas de réponse (status, novel_annotated, bilingual_required, badge, etc.)
"""

import os
import sys
import unittest
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.api import app

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OPENAPI_YAML_PATH = os.path.join(REPO_DIR, "openapi.yaml")


class TestOpenAPIContract(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.generated = app.openapi()
        cls.assertTrue(os.path.exists(OPENAPI_YAML_PATH), f"Fichier {OPENAPI_YAML_PATH} introuvable")
        with open(OPENAPI_YAML_PATH, "r", encoding="utf-8") as f:
            cls.existing = yaml.safe_load(f)

    def test_paths_and_methods_match(self):
        """Vérifie que tous les chemins et méthodes exposés par FastAPI existent dans openapi.yaml."""
        gen_paths = self.generated.get("paths", {})
        exist_paths = self.existing.get("paths", {})

        # Vérification des chemins
        for path in gen_paths:
            self.assertIn(path, exist_paths, f"Chemin manquant dans openapi.yaml: {path}")
            for method in gen_paths[path]:
                if method == "parameters":
                    continue
                self.assertIn(
                    method,
                    exist_paths[path],
                    f"Méthode {method.upper()} manquante pour le chemin {path} dans openapi.yaml"
                )

    def test_languages_query_parameter_include_experimental(self):
        """Vérifie que le paramètre include_experimental sur /languages est documenté dans openapi.yaml."""
        exist_languages = self.existing["paths"]["/languages"]["get"]
        params = exist_languages.get("parameters", [])
        param_names = [p.get("name") for p in params]
        self.assertIn(
            "include_experimental",
            param_names,
            "Le paramètre 'include_experimental' doit être présent sur GET /languages dans openapi.yaml"
        )

    def test_batch_translation_request_properties(self):
        """Vérifie que toutes les propriétés de BatchTranslationRequest correspondent."""
        gen_props = self.generated["components"]["schemas"]["BatchTranslationRequest"]["properties"]
        exist_props = self.existing["components"]["schemas"]["BatchTranslationRequest"]["properties"]

        for prop_name in ["source_lang", "target_lang", "allow_machine_translation", "allow_experimental", "annotate_security_alerts", "items"]:
            self.assertIn(
                prop_name,
                gen_props,
                f"Propriété {prop_name} absente du modèle FastAPI BatchTranslationRequest"
            )
            self.assertIn(
                prop_name,
                exist_props,
                f"Propriété {prop_name} absente de openapi.yaml dans BatchTranslationRequest"
            )

    def test_translation_item_response_properties(self):
        """Vérifie les champs novel_annotated, badge, bilingual_required et status sur TranslationItemResponse."""
        gen_props = self.generated["components"]["schemas"]["TranslationItemResponse"]["properties"]
        exist_props = self.existing["components"]["schemas"]["TranslationItemResponse"]["properties"]

        for prop_name in [
            "id", "source_text", "target_text", "status", "integrity_verified",
            "masked_tokens_count", "bilingual_required", "novel_annotated", "badge"
        ]:
            self.assertIn(
                prop_name,
                gen_props,
                f"Propriété {prop_name} absente du modèle FastAPI TranslationItemResponse"
            )
            self.assertIn(
                prop_name,
                exist_props,
                f"Propriété {prop_name} absente de openapi.yaml dans TranslationItemResponse"
            )

    def test_schema_coverage_and_no_missing_fields(self):
        """Vérifie qu'aucun champ clé des modèles Pydantic principaux n'est omis dans openapi.yaml."""
        models_to_check = [
            "HealthResponse",
            "LanguageInfo",
            "TranslationItemRequest",
            "BatchTranslationRequest",
            "TranslationItemResponse",
            "BatchTranslationResponse",
            "FeedbackRequest",
            "FeedbackResponse",
        ]

        gen_schemas = self.generated["components"]["schemas"]
        exist_schemas = self.existing["components"]["schemas"]

        for model_name in models_to_check:
            self.assertIn(model_name, gen_schemas, f"Modèle {model_name} manquant dans app.openapi()")
            self.assertIn(model_name, exist_schemas, f"Modèle {model_name} manquant dans openapi.yaml")

            gen_props = set(gen_schemas[model_name].get("properties", {}).keys())
            exist_props = set(exist_schemas[model_name].get("properties", {}).keys())

            missing_in_yaml = gen_props - exist_props
            self.assertEqual(
                missing_in_yaml,
                set(),
                f"Champs présents dans FastAPI mais manquants dans openapi.yaml pour {model_name}: {missing_in_yaml}"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
