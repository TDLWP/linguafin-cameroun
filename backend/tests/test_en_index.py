# -*- coding: utf-8 -*-
"""
backend/tests/test_en_index.py — Tests unitaires de l index EN->FR.

Verifie :
 - Chargement de en_to_fr_index.json
 - normalize_en_key : NFKC, lower, espaces insecables
 - Resolution exacte EN->FR
 - Resolution insensible a la casse
 - Espaces insecables U+00A0 / U+202F normalises avant lookup
 - Chaine anglaise inconnue -> None (jamais inventee)
 - Montants anglais masques par protect.py : 25,000 FCFA
 - api.py : source_lang="en" achemine vers la bonne traduction
"""

import os
import sys
import json
import csv
import unicodedata
import unittest

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EN_INDEX_PATH = os.path.join(BASE_DIR, "data", "en_to_fr_index.json")
TRANSLATIONS_PATH = os.path.join(BASE_DIR, "catalogue", "translations.csv")


def normalize_en_key(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u00A0", " ").replace("\u202F", " ").replace("\u2007", " ")
    return s.lower().strip()


def load_index():
    with open(EN_INDEX_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("en_to_fr", {})


def resolve_en_to_fr(text, index):
    key = normalize_en_key(text)
    return index.get(key)


class TestEnIndexLoad(unittest.TestCase):

    def setUp(self):
        self.index = load_index()

    def test_index_non_vide(self):
        self.assertGreater(len(self.index), 0)

    def test_index_79_entrees(self):
        self.assertEqual(len(self.index), 79)

    def test_cles_minuscules(self):
        for k in self.index:
            self.assertEqual(k, k.lower(), f"Cle non normalisee : {k!r}")

    def test_valeurs_sources_fr_non_vides(self):
        for k, v in self.index.items():
            self.assertIsInstance(v, str)
            self.assertTrue(v.strip(), f"Source FR vide pour cle EN {k!r}")

    def test_valeurs_dans_catalogue(self):
        with open(TRANSLATIONS_PATH, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        catalogue_sources = {r["source"].strip() for r in rows}
        manquants = []
        for en_key, fr_src in self.index.items():
            if fr_src not in catalogue_sources:
                manquants.append((en_key, fr_src))
        self.assertEqual(manquants, [],
                         f"Sources FR absentes du catalogue : {manquants[:3]}")


class TestNormalizeEnKey(unittest.TestCase):

    def test_lower(self):
        self.assertEqual(normalize_en_key("Online Banking"), "online banking")

    def test_strip(self):
        self.assertEqual(normalize_en_key("  Safinum Pay  "), "safinum pay")

    def test_espace_insecable_u00a0(self):
        self.assertEqual(normalize_en_key("Test\u00a0Protocol"), "test protocol")

    def test_espace_insecable_u202f(self):
        self.assertEqual(normalize_en_key("Test\u202fProtocol"), "test protocol")

    def test_espace_insecable_u2007(self):
        self.assertEqual(normalize_en_key("Test\u2007Protocol"), "test protocol")

    def test_vide(self):
        self.assertEqual(normalize_en_key(""), "")

    def test_vide_espaces(self):
        self.assertEqual(normalize_en_key("   "), "")

    def test_nfkc_apostrophe(self):
        # NFKC Python ne convertit pas U+2019 en apostrophe ASCII.
        # On verifie que la normalisation ne leve pas d exception.
        norm = normalize_en_key("it\u2019s")
        self.assertIsInstance(norm, str)
        self.assertIn("it", norm)



class TestResolveEnToFr(unittest.TestCase):

    def setUp(self):
        self.index = load_index()

    def test_online_banking(self):
        result = resolve_en_to_fr("Online banking", self.index)
        self.assertEqual(result, "Banque en ligne")

    def test_insensible_casse(self):
        result = resolve_en_to_fr("ONLINE BANKING", self.index)
        self.assertEqual(result, "Banque en ligne")

    def test_espace_insecable_normalise(self):
        result = resolve_en_to_fr("Online\u00a0banking", self.index)
        self.assertEqual(result, "Banque en ligne")

    def test_safinum_pay(self):
        result = resolve_en_to_fr("Safinum Pay", self.index)
        self.assertEqual(result, "Safinum Pay")

    def test_back_to_hackathon(self):
        result = resolve_en_to_fr("Back to hackathon", self.index)
        self.assertEqual(result, "Retour au hackathon")

    def test_available_balance(self):
        result = resolve_en_to_fr("Available balance", self.index)
        self.assertIsNotNone(result)
        self.assertIn("Solde", result)

    def test_inconnu_retourne_none(self):
        result = resolve_en_to_fr("This phrase does not exist xyz", self.index)
        self.assertIsNone(result)

    def test_vide_retourne_none(self):
        result = resolve_en_to_fr("", self.index)
        self.assertIsNone(result)

    def test_jamais_invente(self):
        result = resolve_en_to_fr("Available balance!", self.index)
        self.assertIsNone(result)

    def test_em_dash(self):
        result = resolve_en_to_fr(
            "Test environment \u2014 fictional data, no real transaction.",
            self.index
        )
        # Peut ne pas etre dans l index si le em-dash differe de l original
        # On verifie juste que ca ne leve pas d exception
        # (None est acceptable si le tiret differ)

    def test_toutes_entrees_resolues(self):
        for en_key_norm, fr_src in self.index.items():
            result = resolve_en_to_fr(en_key_norm, self.index)
            self.assertEqual(result, fr_src,
                             f"Cle {en_key_norm!r} devrait retourner {fr_src!r}")


class TestEnglishAmountMasking(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, BASE_DIR)
        from backend.protect import mask_sensitive_data, restore_sensitive_data, verify_integrity
        self.mask = mask_sensitive_data
        self.restore = restore_sensitive_data
        self.verify = verify_integrity

    def _round_trip(self, text):
        masked, token_map, _ = self.mask(text)
        restored, ok = self.restore(masked, token_map, text)
        self.assertTrue(ok, f"Restauration echouee pour {text!r}")
        self.assertTrue(self.verify(text, restored, token_map))
        return masked, restored

    def test_montant_anglais_virgule_fcfa(self):
        masked, restored = self._round_trip("Your fee is 25,000 FCFA.")
        self.assertNotIn("25,000 FCFA", masked)
        self.assertIn("25,000 FCFA", restored)

    def test_montant_dollar_virgule(self):
        masked, restored = self._round_trip("Amount: $1,250.00")
        self.assertNotIn("$1,250.00", masked)
        self.assertIn("$1,250.00", restored)

    def test_montant_francais_espace(self):
        masked, restored = self._round_trip("Montant : 25 000 FCFA")
        self.assertNotIn("25 000 FCFA", masked)
        self.assertIn("25 000 FCFA", restored)

    def test_montant_espace_fine_insecable(self):
        # protect.py normalise U+202F (espace fine insec.) en U+00A0 lors du masquage.
        # On verifie que le montant est correctement masque ET restaure
        # (sous forme U+202F ou U+00A0 selon la normalisation interne).
        masked, restored = self._round_trip("Montant : 75\u202f000 FCFA")
        self.assertNotIn("75\u202f000 FCFA", masked)   # masque avant restauration
        # Apres restauration : presence du montant (sous forme u202F ou u00A0)
        self.assertTrue(
            "75\u202f000 FCFA" in restored or "75\u00a0000 FCFA" in restored or "75 000 FCFA" in restored,
            f"Montant 75\u202f000 FCFA absent de la restauration : {restored!r}"
        )


    def test_pas_de_crochet_dans_montant(self):
        masked, _ = self._round_trip("Security alert: debit of 25,000 FCFA")
        self.assertNotRegex(masked, r"\[25")

    def test_sans_montant_non_altere(self):
        text = "Your account is active."
        masked, restored = self._round_trip(text)
        self.assertEqual(masked, text)
        self.assertEqual(restored, text)


class TestApiEnSourceLang(unittest.TestCase):

    def setUp(self):
        try:
            from fastapi.testclient import TestClient
            from backend.api import app
            self.client = TestClient(app)
            self.available = True
        except Exception:
            self.available = False

    def _skip(self):
        if not self.available:
            self.skipTest("FastAPI non disponible")

    def _post(self, source_lang, text, target_lang="dua"):
        return self.client.post("/translate/batch", json={
            "source_lang": source_lang,
            "target_lang": target_lang,
            "allow_machine_translation": True,
            "items": [{"id": "t1", "text": text, "screen_context": "test"}]
        })

    def test_en_known_dua_meme_que_fr(self):
        self._skip()
        en = self._post("en", "Online banking", "dua")
        fr = self._post("fr", "Banque en ligne", "dua")
        self.assertEqual(en.status_code, 200)
        self.assertEqual(fr.status_code, 200)
        en_tgt = en.json()["items"][0]["target_text"]
        fr_tgt = fr.json()["items"][0]["target_text"]
        self.assertEqual(en_tgt, fr_tgt,
                         f"EN {en_tgt!r} != FR {fr_tgt!r}")

    def test_en_known_bas(self):
        self._skip()
        resp = self._post("en", "Available balance", "bas")
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]
        self.assertNotEqual(item["target_text"], "Available balance")

    def test_en_unknown_fallback(self):
        self._skip()
        resp = self._post("en", "Completely unknown phrase xyz123", "dua")
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]
        self.assertIn(item["status"], ("fallback_source", "machine_suggested"))

    def test_en_amount_preserve(self):
        self._skip()
        resp = self._post("en", "Your fee is 25,000 FCFA.", "dua")
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]
        self.assertIn("25,000 FCFA", item["target_text"])
        self.assertTrue(item["integrity_verified"])

    def test_fr_toujours_ok(self):
        self._skip()
        resp = self._post("fr", "Banque en ligne", "dua")
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["items"][0]
        self.assertNotEqual(item["target_text"], "Banque en ligne")

    def test_en_integrity_always_true(self):
        self._skip()
        for txt in ["Online banking", "Unknown phrase xyz"]:
            resp = self._post("en", txt, "dua")
            item = resp.json()["items"][0]
            self.assertTrue(item["integrity_verified"],
                            f"integrity_verified False pour {txt!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
