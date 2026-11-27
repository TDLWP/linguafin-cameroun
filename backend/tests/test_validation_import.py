# -*- coding: utf-8 -*-
"""
backend/tests/test_validation_import.py -- Tests d'integrite de l'importateur de validation.

Verifie formellement la regle stricte :
  Une ligne NE DEVIENT JAMAIS 'human_validated' sans :
    1. Code validateur explicite
    2. Date de validation explicite
    3. Avis 'OK' explicite
    4. Absence de correction proposee

Et teste :
  - Les en-tetes reels des fiches catalogue/kit_validation/fiche_validation_duala.csv et _bassaa.csv
  - Absence de --validateur ou --date => aucune promotion
  - Mauvaise langue => aucune modification
  - Cle inconnue => signalée en erreur, jamais creee
  - Ligne avec correction => statut draft (jamais human_validated)
"""

import os
import sys
import csv
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.importer_validation import (
    process_validation_import,
    load_input_csv,
    normalize_col_name,
)

REAL_DUALA_CSV = os.path.join(
    REPO_ROOT, "catalogue", "kit_validation", "fiche_validation_duala.csv"
)
REAL_BASSAA_CSV = os.path.join(
    REPO_ROOT, "catalogue", "kit_validation", "fiche_validation_bassaa.csv"
)


class TestNormalizeColName(unittest.TestCase):
    """Teste la normalisation des en-tetes reels des fiches kit_validation."""

    def test_numero(self):
        self.assertEqual(normalize_col_name("N\u00b0"), "num")

    def test_cle_contexte(self):
        self.assertEqual(normalize_col_name("Cl\u00e9 / Contexte"), "cle")

    def test_texte_source_francais(self):
        self.assertEqual(normalize_col_name("Texte Source (Fran\u00e7ais)"), "source")

    def test_proposition_duala(self):
        self.assertEqual(normalize_col_name("Proposition Traduction (Du\u00e1l\u00e1)"), "proposition")

    def test_proposition_bassaa(self):
        # Colonne avec le caractere implosif B (U+0181)
        self.assertEqual(normalize_col_name("Proposition Traduction (\u0181\u00e0s\u00e0a)"), "proposition")

    def test_correction_validateur(self):
        self.assertEqual(normalize_col_name("Correction du validateur"), "correction")

    def test_validation_ok_ko(self):
        self.assertEqual(normalize_col_name("Validation (OK / KO)"), "avis")

    def test_commentaire_linguistique(self):
        self.assertEqual(normalize_col_name("Commentaire linguistique"), "commentaire")

    def test_priorite_de_relecture(self):
        self.assertEqual(normalize_col_name("Priorité de relecture"), "priorite de relecture")


class TestValidationImportBase(unittest.TestCase):
    """Classe de base avec catalogue temporaire."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.catalog_path = os.path.join(self.temp_dir.name, "translations.csv")
        self.headers = [
            "cle", "source", "langue", "cible", "statut",
            "validateur_code", "date", "commentaire"
        ]
        self.initial_rows = [
            {
                "cle": "solde_actuel",
                "source": "Solde actuel",
                "langue": "dua",
                "cible": "Musawadi ma titi",
                "statut": "machine_suggested",
                "validateur_code": "",
                "date": "",
                "commentaire": "traduction auto"
            },
            {
                "cle": "frais_trans",
                "source": "Frais de transfert",
                "langue": "dua",
                "cible": "Musawedi ma transfert",
                "statut": "machine_suggested",
                "validateur_code": "",
                "date": "",
                "commentaire": ""
            },
            {
                "cle": "code_secret",
                "source": "Ne partagez jamais votre code secret.",
                "langue": "bas",
                "cible": "U ti ban to pes kod yon i ndii.",
                "statut": "machine_suggested",
                "validateur_code": "",
                "date": "",
                "commentaire": ""
            },
            {
                "cle": "beneficiaire",
                "source": "Beneficiaire",
                "langue": "bas",
                "cible": "Nu a nkoshna",
                "statut": "machine_suggested",
                "validateur_code": "",
                "date": "",
                "commentaire": ""
            },
            {
                "cle": "wizard_step1",
                "source": "Solde",
                "langue": "dua",
                "cible": "Moni mi titi",
                "statut": "machine_suggested",
                "validateur_code": "",
                "date": "",
                "commentaire": ""
            },
            {
                "cle": "wizard_step1",
                "source": "Solde",
                "langue": "bas",
                "cible": "Kobo i moni",
                "statut": "machine_suggested",
                "validateur_code": "",
                "date": "",
                "commentaire": ""
            },
        ]
        self._write_catalog(self.initial_rows)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_catalog(self, rows):
        with open(self.catalog_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(rows)

    def _read_catalog(self):
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))


class TestStrictHumanValidatedRule(TestValidationImportBase):
    """Tests des regles strictes de promotion."""

    def test_ok_sans_validateur_reste_machine_suggested(self):
        """Avis OK mais SANS code validateur => jamais human_validated."""
        rows = [{
            "cle": "solde_actuel", "avis": "OK",
            "validateur_code": "", "correction": ""
        }]
        stats, _ = process_validation_import(
            rows, catalog_path=self.catalog_path, dry_run=False,
            target_lang="dua", val_code="", val_date="2026-11-15",
        )
        self.assertEqual(len(stats["promoted_human_validated"]), 0,
                         "Sans code validateur => pas de promotion")
        self.assertEqual(len(stats["retained_machine_suggested"]), 1)
        self.assertIn("code validateur absent", stats["retained_machine_suggested"][0]["reason"])
        cat = self._read_catalog()
        entry = next(r for r in cat if r["cle"] == "solde_actuel" and r["langue"] == "dua")
        self.assertEqual(entry["statut"], "machine_suggested")

    def test_ok_sans_date_reste_machine_suggested(self):
        """Avis OK + validateur mais SANS date => jamais human_validated."""
        rows = [{
            "cle": "solde_actuel", "avis": "OK",
            "validateur_code": "VAL_DUA_01", "correction": ""
        }]
        stats, _ = process_validation_import(
            rows, catalog_path=self.catalog_path, dry_run=False,
            target_lang="dua", val_code="VAL_DUA_01", val_date="",
        )
        self.assertEqual(len(stats["promoted_human_validated"]), 0)
        self.assertIn("date de validation absente", stats["retained_machine_suggested"][0]["reason"])

    def test_validateur_espaces_seuls_reste_machine_suggested(self):
        """Un validateur compose d'espaces seuls ne bypass pas la regle."""
        rows = [{
            "cle": "solde_actuel", "avis": "OK",
            "validateur_code": "   \t  ", "correction": ""
        }]
        stats, _ = process_validation_import(
            rows, catalog_path=self.catalog_path, dry_run=False,
            target_lang="dua", val_code="   \t  ", val_date="2026-11-15",
        )
        self.assertEqual(len(stats["promoted_human_validated"]), 0)

    def test_conditions_completes_promotion_human_validated(self):
        """Validateur + date + avis OK + pas de correction => human_validated."""
        rows = [{"cle": "solde_actuel", "avis": "OK", "correction": ""}]
        stats, _ = process_validation_import(
            rows, catalog_path=self.catalog_path, dry_run=False,
            target_lang="dua", val_code="VAL_DUA_LOC01", val_date="2026-11-15",
        )
        self.assertEqual(len(stats["promoted_human_validated"]), 1)
        cat = self._read_catalog()
        entry = next(r for r in cat if r["cle"] == "solde_actuel" and r["langue"] == "dua")
        self.assertEqual(entry["statut"], "human_validated")
        self.assertEqual(entry["validateur_code"], "VAL_DUA_LOC01")

    def test_doute_passe_en_rejected(self):
        """DOUTE => rejected par securite."""
        rows = [{"cle": "code_secret", "avis": "DOUTE", "correction": ""}]
        stats, _ = process_validation_import(
            rows, catalog_path=self.catalog_path, dry_run=False,
            target_lang="bas", val_code="VAL_BAS_01", val_date="2026-11-15",
        )
        self.assertEqual(len(stats["marked_rejected"]), 1)
        cat = self._read_catalog()
        entry = next(r for r in cat if r["cle"] == "code_secret" and r["langue"] == "bas")
        self.assertEqual(entry["statut"], "rejected")

    def test_correction_donne_draft_jamais_human_validated(self):
        """Une correction proposee => draft (JAMAIS human_validated, meme avec avis OK)."""
        new_target = "Musawedi ma bopanza"
        rows = [{"cle": "frais_trans", "avis": "OK", "correction": new_target}]
        stats, _ = process_validation_import(
            rows, catalog_path=self.catalog_path, dry_run=False,
            target_lang="dua", val_code="VAL_DUA_02", val_date="2026-11-15",
        )
        self.assertEqual(len(stats["marked_revision_draft"]), 1)
        self.assertEqual(len(stats["promoted_human_validated"]), 0,
                         "Correction presente => jamais human_validated")
        cat = self._read_catalog()
        entry = next(r for r in cat if r["cle"] == "frais_trans" and r["langue"] == "dua")
        self.assertEqual(entry["statut"], "draft")
        self.assertEqual(entry["cible"], new_target)

    def test_dry_run_ne_modifie_pas_le_disque(self):
        """dry_run=True => aucune modification sur disque."""
        rows = [{"cle": "beneficiaire", "avis": "OK", "correction": ""}]
        stats, _ = process_validation_import(
            rows, catalog_path=self.catalog_path, dry_run=True,
            target_lang="bas", val_code="VAL_BAS_01", val_date="2026-11-15",
        )
        self.assertEqual(len(stats["promoted_human_validated"]), 1)
        cat = self._read_catalog()
        entry = next(r for r in cat if r["cle"] == "beneficiaire" and r["langue"] == "bas")
        self.assertEqual(entry["statut"], "machine_suggested",
                         "Le fichier disque ne doit pas changer en dry-run")


class TestLangueHandling(TestValidationImportBase):
    """Tests de gestion de la langue."""

    def test_mauvaise_langue_zero_modification(self):
        """
        Fournir la langue 'bas' pour une entree qui n'existe qu'en 'dua'
        => erreur de correspondance, aucune modification du catalogue.
        """
        rows = [{"cle": "solde_actuel", "avis": "OK", "correction": ""}]
        stats, _ = process_validation_import(
            rows, catalog_path=self.catalog_path, dry_run=False,
            target_lang="bas", val_code="VAL_BAS_01", val_date="2026-11-15",
        )
        # solde_actuel n'existe qu'en dua => erreur attendue
        self.assertEqual(len(stats["errors"]), 1)
        self.assertEqual(len(stats["promoted_human_validated"]), 0)
        self.assertEqual(len(stats["marked_revision_draft"]), 0)
        # Le catalogue ne doit pas etre touche
        cat = self._read_catalog()
        entry_dua = next(r for r in cat if r["cle"] == "solde_actuel" and r["langue"] == "dua")
        self.assertEqual(entry_dua["statut"], "machine_suggested")

    def test_code_langue_inconnu_erreur(self):
        """Langue non reconnue => erreur signalee."""
        rows = [{"cle": "wizard_step1", "avis": "OK", "correction": ""}]
        stats, _ = process_validation_import(
            rows, catalog_path=self.catalog_path, dry_run=False,
            target_lang="xyz", val_code="VAL", val_date="2026-11-15",
        )
        self.assertEqual(len(stats["errors"]), 1)
        self.assertIn("non reconnu", stats["errors"][0]["reason"].lower())


class TestKeyNotFound(TestValidationImportBase):
    """Tests de gestion des cles introuvables."""

    def test_cle_inconnue_signalee_jamais_creee(self):
        """Cle absente du catalogue => erreur, aucune creation."""
        rows = [{"cle": "cle_qui_nexiste_pas", "avis": "OK", "correction": ""}]
        stats, _ = process_validation_import(
            rows, catalog_path=self.catalog_path, dry_run=False,
            target_lang="dua", val_code="VAL", val_date="2026-11-15",
        )
        self.assertEqual(len(stats["errors"]), 1)
        self.assertIn("cle_qui_nexiste_pas", stats["errors"][0]["reason"])
        # Le catalogue ne doit pas avoir de nouvelle ligne
        cat = self._read_catalog()
        cles = [r["cle"] for r in cat]
        self.assertNotIn("cle_qui_nexiste_pas", cles)

    def test_cle_vide_signalee_en_erreur(self):
        """Cle vide => erreur signalee."""
        rows = [{"cle": "", "avis": "OK", "correction": ""}]
        stats, _ = process_validation_import(
            rows, catalog_path=self.catalog_path, dry_run=False,
            target_lang="dua", val_code="VAL", val_date="2026-11-15",
        )
        self.assertEqual(len(stats["errors"]), 1)


class TestRealCSVHeaders(unittest.TestCase):
    """Tests avec les en-tetes reels des fiches kit_validation (si disponibles)."""

    @unittest.skipUnless(os.path.exists(REAL_DUALA_CSV), "Fiche duala absente")
    def test_load_real_duala_csv(self):
        """Les colonnes des vraies fiches doivent etre correctement normalisees."""
        rows = load_input_csv(REAL_DUALA_CSV)
        self.assertGreater(len(rows), 0, "La fiche duala doit avoir des lignes")
        first = rows[0]
        # Les colonnes normalisees attendues
        self.assertIn("cle", first, "Colonne 'cle' absente apres normalisation")
        self.assertIn("source", first, "Colonne 'source' absente apres normalisation")
        self.assertIn("proposition", first, "Colonne 'proposition' absente apres normalisation")
        self.assertIn("priorite de relecture", first, "Colonne 'priorite de relecture' absente apres normalisation")
        self.assertIn("avis", first, "Colonne 'avis' absente apres normalisation")

    @unittest.skipUnless(os.path.exists(REAL_BASSAA_CSV), "Fiche bassa'a absente")
    def test_load_real_bassaa_csv(self):
        """Les colonnes de la fiche bassa'a doivent etre normalisees (y compris Basaa)."""
        rows = load_input_csv(REAL_BASSAA_CSV)
        self.assertGreater(len(rows), 0)
        first = rows[0]
        self.assertIn("cle", first)
        self.assertIn("proposition", first)
        self.assertIn("priorite de relecture", first)

    @unittest.skipUnless(os.path.exists(REAL_DUALA_CSV), "Fiche duala absente")
    def test_duala_csv_sans_validateur_zero_promotion(self):
        """
        Importer la vraie fiche duala sans --validateur ni --date
        => zero promotions human_validated.
        """
        from scripts.importer_validation import DEFAULT_CATALOG_CSV
        if not os.path.exists(DEFAULT_CATALOG_CSV):
            self.skipTest("translations.csv absent")
        rows = load_input_csv(REAL_DUALA_CSV)
        stats, _ = process_validation_import(
            rows, catalog_path=DEFAULT_CATALOG_CSV, dry_run=True,
            target_lang="dua", val_code="", val_date="",
        )
        self.assertEqual(len(stats["promoted_human_validated"]), 0,
                         "Sans validateur ni date => zero promotion human_validated")

    @unittest.skipUnless(os.path.exists(REAL_BASSAA_CSV), "Fiche bassa'a absente")
    def test_bassaa_csv_sans_date_zero_promotion(self):
        """Importer la vraie fiche bassa'a sans date => zero promotions."""
        from scripts.importer_validation import DEFAULT_CATALOG_CSV
        if not os.path.exists(DEFAULT_CATALOG_CSV):
            self.skipTest("translations.csv absent")
        rows = load_input_csv(REAL_BASSAA_CSV)
        stats, _ = process_validation_import(
            rows, catalog_path=DEFAULT_CATALOG_CSV, dry_run=True,
            target_lang="bas", val_code="VAL_BAS_TEST", val_date="",
        )
        self.assertEqual(len(stats["promoted_human_validated"]), 0)

    @unittest.skipUnless(os.path.exists(REAL_DUALA_CSV), "Fiche duala absente")
    def test_import_with_priority_column_preserves_catalogue(self):
        """
        Vérifie que la présence de la colonne 'Priorité de relecture' dans les fiches
        n'altère en aucun cas le catalogue et est parfaitement lue par scripts/importer_validation.py.
        """
        from scripts.importer_validation import DEFAULT_CATALOG_CSV
        if not os.path.exists(DEFAULT_CATALOG_CSV):
            self.skipTest("translations.csv absent")

        # 1. Vérifier la lecture et le nombre exact de 84 entrées
        rows_dua = load_input_csv(REAL_DUALA_CSV)
        self.assertEqual(len(rows_dua), 84, "La fiche duala doit contenir exactement 84 lignes")
        rows_bas = load_input_csv(REAL_BASSAA_CSV)
        self.assertEqual(len(rows_bas), 84, "La fiche bassa'a doit contenir exactement 84 lignes")

        # 2. Vérifier que les priorités sont attribuées correctement
        priorites_dua = {r["priorite de relecture"] for r in rows_dua}
        self.assertTrue(priorites_dua.issubset({"haute", "normale", "référence concordante"}))
        self.assertIn("haute", priorites_dua)
        self.assertIn("normale", priorites_dua)

        # 3. Dry-run sur le catalogue réel : aucune modification ni promotion
        stats, changes = process_validation_import(
            rows_dua, catalog_path=DEFAULT_CATALOG_CSV, dry_run=True,
            target_lang="dua", val_code="", val_date="",
        )
        self.assertEqual(len(stats["promoted_human_validated"]), 0)
        self.assertEqual(len(stats["errors"]), 0, f"Erreurs inattendues lors de l'import : {stats['errors']}")



if __name__ == "__main__":
    unittest.main()
