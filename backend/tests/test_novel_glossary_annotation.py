# -*- coding: utf-8 -*-
"""
backend/tests/test_novel_glossary_annotation.py — Tests d'annotation du glossaire pour contenus inédits.

Objectifs :
- Vérifier que pour tout texte absent de la mémoire de traduction :
    1. Le texte source est conservé tel quel (aucune traduction globale générée).
    2. Les termes financiers du glossaire sont annotés entre crochets : « terme [équivalent glossaire] ».
    3. Les montants, références, téléphones, dates et bénéficiaires restent intacts SANS AUCUN crochet.
    4. Le statut renvoyé est 'machine_suggested' avec badge 'contenu inédit : termes annotés, phrase non traduite'.
    5. Prise en charge stricte de \\u202F (espace fine insécable) et \\u00A0 (espace insécable standard).
    6. Repli source ('fallback_source') si aucun terme financier n'est présent dans le texte.
"""

import unittest
from fastapi.testclient import TestClient
from backend.api import app, MEMOIRE
from backend.protect import (
    mask_sensitive_data,
    restore_sensitive_data,
    verify_integrity,
    annotate_glossary_in_masked_text
)


class TestNovelGlossaryAnnotation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # =========================================================================
    # 1. Montants inchangés & absence absolue de crochets autour des montants
    # =========================================================================

    def test_amount_unchanged_and_no_brackets_around_amount_dua(self):
        """Vérifie qu'un montant dans un contenu inédit reste 100% inchangé et sans aucun crochet."""
        novel_text = "Veuillez vérifier votre solde avant d'envoyer 25 000 FCFA à Jean-Paul Mbarga."
        payload = {
            "source_lang": "fr",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "items": [{"id": "item_1", "text": novel_text}]
        }
        resp = self.client.post("/translate/batch", json=payload)
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]

        # 1. Montant présent et inchangé
        self.assertIn("25 000 FCFA", item["target_text"])

        # 2. Aucun crochet autour du montant
        self.assertNotIn("[25 000 FCFA]", item["target_text"])
        self.assertNotIn("25 000 FCFA [", item["target_text"])
        self.assertNotIn("[25000", item["target_text"])

        # 3. Bénéficiaire intact et sans crochet
        self.assertIn("Jean-Paul Mbarga", item["target_text"])
        self.assertNotIn("[Jean-Paul Mbarga]", item["target_text"])

        # 4. Intégrité validée
        self.assertTrue(item["integrity_verified"])

    def test_multiple_amounts_and_fees_no_brackets(self):
        """Vérifie plusieurs montants et frais dans une même phrase inédite."""
        novel_text = "Frais de 500 FCFA appliqués sur votre virement de 50 000 FCFA. Solde restant : 199 500 FCFA."
        payload = {
            "source_lang": "fr",
            "target_lang": "bas",
            "allow_machine_translation": True,
            "items": [{"id": "item_multi", "text": novel_text}]
        }
        resp = self.client.post("/translate/batch", json=payload)
        self.assertEqual(resp.status_code, 200)
        tgt = resp.json()["items"][0]["target_text"]

        # Tous les montants préservés sans crochets
        for amt in ["500 FCFA", "50 000 FCFA", "199 500 FCFA"]:
            self.assertIn(amt, tgt)
            self.assertNotIn(f"[{amt}]", tgt)
            self.assertNotIn(f"[{amt}", tgt)

    # =========================================================================
    # 2. Statut machine_suggested et badge de contenu inédit
    # =========================================================================

    def test_status_machine_suggested_with_novel_badge(self):
        """Vérifie que le statut est 'machine_suggested' et que le badge inédit est présent."""
        novel_text = "Alerte de sécurité : veuillez contrôler votre solde disponible."
        payload = {
            "source_lang": "fr",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "items": [{"id": "item_badge", "text": novel_text}]
        }
        resp = self.client.post("/translate/batch", json=payload)
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]

        # Statut machine_suggested obligatoire
        self.assertEqual(item["status"], "machine_suggested")
        # Attribut novel_annotated activé
        self.assertTrue(item.get("novel_annotated"))
        # Badge visible conforme
        self.assertEqual(item.get("badge"), "contenu inédit : termes annotés, phrase non traduite")

    def test_glossary_terms_annotated_in_brackets(self):
        """Vérifie que les termes du glossaire sont annotés sous la forme 'terme [équivalent]'."""
        # En Duala : solde -> Moni mi titi
        novel_text = "Votre solde actuel est suffisant pour ce transfert."
        payload = {
            "source_lang": "fr",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "items": [{"id": "item_anno", "text": novel_text}]
        }
        resp = self.client.post("/translate/batch", json=payload)
        tgt = resp.json()["items"][0]["target_text"]

        # Annotation du terme solde
        self.assertTrue("solde [Moni mi titi]" in tgt or "Solde [Moni mi titi]" in tgt)
        # Structure de la phrase conservée en français
        self.assertTrue(tgt.startswith("Votre") or "actuel est suffisant" in tgt)

    # =========================================================================
    # 3. Comportement avec \u202F (espace fine insécable) et \u00A0 (espace insécable)
    # =========================================================================

    def test_narrow_non_breaking_space_u202F_behavior(self):
        """Vérifie le comportement avec l'espace fine insécable (\\u202F de Intl.NumberFormat)."""
        # Montant avec \u202F
        amt_u202f = "25\u202F000 FCFA"
        novel_text = f"Nouveau solde calculé : {amt_u202f} après déduction des frais."

        payload = {
            "source_lang": "fr",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "items": [{"id": "item_u202f", "text": novel_text}]
        }
        resp = self.client.post("/translate/batch", json=payload)
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]

        # Intégrité 100% vérifiée
        self.assertTrue(item["integrity_verified"])
        # Aucun faux crochet autour du montant
        tgt = item["target_text"]
        self.assertNotIn(f"[{amt_u202f}]", tgt)
        self.assertNotIn("[25 000 FCFA]", tgt)
        # La valeur numérique 25 000 doit être préservée (soit en \u202F soit en \u00A0)
        has_25k = ("25\u202F000 FCFA" in tgt) or ("25\u00A0000 FCFA" in tgt)
        self.assertTrue(has_25k, f"Le montant 25 000 FCFA n'a pas été retrouvé intact dans : {tgt}")

    def test_non_breaking_space_u00A0_behavior(self):
        """Vérifie le comportement avec l'espace insécable standard (\\u00A0)."""
        amt_u00a0 = "250\u00A0000 FCFA"
        novel_text = f"Confirmation de réception : {amt_u00a0} crédités sur votre compte."

        payload = {
            "source_lang": "fr",
            "target_lang": "bas",
            "allow_machine_translation": True,
            "items": [{"id": "item_u00a0", "text": novel_text}]
        }
        resp = self.client.post("/translate/batch", json=payload)
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]

        self.assertTrue(item["integrity_verified"])
        tgt = item["target_text"]
        self.assertNotIn(f"[{amt_u00a0}]", tgt)
        self.assertNotIn("[250 000 FCFA]", tgt)
        has_250k = ("250\u00A0000 FCFA" in tgt) or ("250\u202F000 FCFA" in tgt)
        self.assertTrue(has_250k, f"Le montant 250 000 FCFA n'a pas été retrouvé intact dans : {tgt}")

    # =========================================================================
    # 4. Phrase inédite sans aucun terme financier du glossaire (Repli source)
    # =========================================================================

    def test_novel_text_without_financial_terms_fallback_source(self):
        """Vérifie qu'un texte inédit sans aucun terme financier reste en texte source pur (fallback_source)."""
        novel_text = "Bienvenue dans l'interface d'aide et de support technique."
        payload = {
            "source_lang": "fr",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "items": [{"id": "item_no_fin", "text": novel_text}]
        }
        resp = self.client.post("/translate/batch", json=payload)
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]

        # Texte strictement identique à la source
        self.assertEqual(item["target_text"], novel_text)
        # Statut fallback_source
        self.assertEqual(item["status"], "fallback_source")
        # Pas de badge d'annotation
        self.assertFalse(item.get("novel_annotated"))
        self.assertIsNone(item.get("badge"))

    # =========================================================================
    # 5. Test unitaire direct de la fonction annotate_glossary_in_masked_text
    # =========================================================================

    def test_direct_annotate_glossary_function(self):
        """Vérifie directement la fonction helper annotate_glossary_in_masked_text."""
        masked = "Consultez votre solde et calculez vos frais pour __SAFE_AMOUNT_0__."
        glossary = {
            "solde": {"dua": "Moni mi titi", "bas": "Kôbô i moni"},
            "frais": {"dua": "Mutoa", "bas": "Ntomb"}
        }

        annotated_dua, has_anno_dua, terms_dua = annotate_glossary_in_masked_text(masked, glossary, "dua")
        self.assertTrue(has_anno_dua)
        self.assertIn("solde [Moni mi titi]", annotated_dua)
        self.assertIn("frais [Mutoa]", annotated_dua)
        self.assertIn("__SAFE_AMOUNT_0__", annotated_dua)

        annotated_bas, has_anno_bas, terms_bas = annotate_glossary_in_masked_text(masked, glossary, "bas")
        self.assertTrue(has_anno_bas)
        self.assertIn("solde [Kôbô i moni]", annotated_bas)
        self.assertIn("frais [Ntomb]", annotated_bas)
        self.assertIn("__SAFE_AMOUNT_0__", annotated_bas)


if __name__ == "__main__":
    unittest.main()
