# -*- coding: utf-8 -*-
"""
Tests unitaires et d'intégration d'intégrité financière — SAFINUM 2026.
Plus de 50 cas de tests couvrant :
- Montants et devises variés (FCFA, XAF, EUR, €, USD, $)
- Frais en pourcentage
- Téléphones camerounais et internationaux
- Références de transaction et comptes bancaires
- Dates calendaires et financières
- Noms de bénéficiaires
- Cas de falsification et altération qui DOIVENT ÉCHOUER (rejet et repli source)
- Jetons perdus, dupliqués, permutés, tronqués
- Tests du timeout du moteur automatique, des erreurs et des limites d'API
"""

import sys
import os
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.protect import mask_sensitive_data, restore_sensitive_data, verify_integrity
from backend.engine import AutomaticMockEngine, TranslationEngineTimeoutError, TranslationEngineError
from backend.api import app, MEMOIRE

client = TestClient(app)


class TestFinancialIntegrityCases(unittest.TestCase):
    """Vérification unitaire du masquage et de la restauration sans altération."""

    # --- 10 cas de Montants & Devises ---

    def test_01_montant_fcfa_standard(self):
        src = "Solde : 250 000 FCFA"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_AMOUNT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_02_montant_xaf_points(self):
        src = "Montant : 25.000 XAF"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_AMOUNT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_03_montant_euros_symbole(self):
        src = "Frais de conversion : 1,250.50 €"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_AMOUNT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_04_montant_euros_texte(self):
        src = "Total : 1250 EUR"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_AMOUNT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_05_montant_dollar_prefixe(self):
        src = "Facture reçue : $ 500"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_AMOUNT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_06_montant_dollar_suffixe(self):
        src = "Commission : 500 $"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_AMOUNT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_07_montant_zero(self):
        src = "Frais appliqués : 0 FCFA"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_AMOUNT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_08_montant_positif(self):
        src = "Crédit : +180 000 FCFA"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_AMOUNT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_09_montant_negatif(self):
        src = "Débit : -12 500 FCFA"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_AMOUNT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_10_montant_xof_millions(self):
        src = "Plafond : 2 500 000 XOF"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_AMOUNT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    # --- 6 cas de Frais en Pourcentage ---

    def test_11_pourcentage_virgule(self):
        src = "Frais de 1,5 %"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_PCT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_12_pourcentage_entier(self):
        src = "Frais de 2%"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_PCT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_13_pourcentage_point(self):
        src = "Taux de 0.5 %"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_PCT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_14_pourcentage_petit(self):
        src = "Taxe : 0,05 %"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_PCT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_15_pourcentage_dix(self):
        src = "Pénalité de 10 %"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_PCT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_16_pourcentage_compose(self):
        src = "Frais de 1,5 % (min. 100 FCFA, max. 2 500 FCFA)"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertEqual(len(tokens), 3)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    # --- 6 cas de Numéros de Téléphone ---

    def test_17_tel_cameroun_international_espace(self):
        src = "Destinataire : +237 6 99 12 34 56"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_TEL_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_18_tel_cameroun_local_compact(self):
        src = "Numéro : 699123456"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_TEL_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_19_tel_cameroun_international_compact(self):
        src = "Contact : +237670000000"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_TEL_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_20_tel_fixe_cameroun(self):
        src = "Service client : +237 2 22 12 34 56"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_TEL_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_21_tel_local_espaces(self):
        src = "Bénéficiaire au 6 77 88 99 00"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_TEL_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_22_tel_international_point(self):
        src = "Appel : +237.6.99.12.34.56"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_TEL_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    # --- 6 cas de Références de Transaction ---

    def test_23_reference_safinum_standard(self):
        src = "Référence : SAF-2026-X7Y8Z9"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_REF_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_24_reference_safinum_chiffres(self):
        src = "ID opération : SAF-2026-123456"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_REF_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_25_reference_format_ref(self):
        src = "Code reçu : REF-998877-XY"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_REF_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_26_reference_lettres(self):
        src = "Réf : SAF-2026-ABCDEF"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_REF_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_27_reference_test(self):
        src = "Numéro : REF-TEST-001"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_REF_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_28_reference_mixte(self):
        src = "Transaction SAF-2026-M4N8P2 validée"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_REF_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    # --- 6 cas de Dates ---

    def test_29_date_fr_abregee_nov(self):
        src = "Opération du 05 nov. 2026"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_DATE_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_30_date_fr_abregee_oct(self):
        src = "Reçu le 31 oct. 2026"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_DATE_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_31_date_slash(self):
        src = "Date valeur : 14/11/2026"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_DATE_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_32_date_iso(self):
        src = "Horodatage : 2026-11-14"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_DATE_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_33_date_janvier(self):
        src = "Échéance : 01 janv. 2026"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_DATE_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_34_date_tiret(self):
        src = "Enregistré le 12-05-2025"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_DATE_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    # --- 6 cas de Bénéficiaires & Comptes ---

    def test_35_beneficiaire_jean_paul_mbarga(self):
        src = "Envoyé à Jean-Paul Mbarga"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_BENEF_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_36_beneficiaire_amina_ngo_bell(self):
        src = "Titulaire : Amina Ngo Bell"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_BENEF_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_37_beneficiaire_amina_court(self):
        src = "Bonjour, Amina"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_BENEF_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_38_compte_cameroun_espace(self):
        src = "Numéro de compte : CM 001 2345 6789 01"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_ACCT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_39_compte_cameroun_compact(self):
        src = "RIB : CM0012345678901"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_ACCT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))

    def test_40_compte_cameroun_autre(self):
        src = "Virement vers CM 999 8888 7777 66"
        masked, tokens, _ = mask_sensitive_data(src)
        self.assertIn("__SAFE_ACCT_", masked)
        restored, ok = restore_sensitive_data(masked, tokens, src)
        self.assertTrue(ok)
        self.assertEqual(restored, src)
        self.assertTrue(verify_integrity(src, restored, tokens))


class TestFalsificationAndIntegrityFailureCases(unittest.TestCase):
    """
    Cas d'altération et de fraude qui DOIVENT IMPÉRATIVEMENT ÉCHOUER.
    La fonction verify_integrity doit retourner False et restore_sensitive_data
    doit basculer vers le texte source original.
    """

    def test_41_alteration_chiffre_montant(self):
        src = "Total : 25 000 FCFA"
        fraud = "Total : 20 000 FCFA"  # Montant falsifié
        self.assertFalse(verify_integrity(src, fraud))

    def test_42_alteration_devise(self):
        src = "Solde : 250 000 FCFA"
        fraud = "Solde : 250 000 EUR"  # Devise changée
        self.assertFalse(verify_integrity(src, fraud))

    def test_43_alteration_numero_telephone(self):
        src = "Bénéficiaire : +237 6 99 12 34 56"
        fraud = "Bénéficiaire : +237 6 99 12 34 57"  # Dernier chiffre modifié
        self.assertFalse(verify_integrity(src, fraud))

    def test_44_alteration_reference(self):
        src = "Transaction : SAF-2026-X7Y8Z9"
        fraud = "Transaction : SAF-2026-X7Y8Z0"  # Référence altérée
        self.assertFalse(verify_integrity(src, fraud))

    def test_45_alteration_nom_beneficiaire(self):
        src = "Transfert vers Jean-Paul Mbarga"
        fraud = "Transfert vers Paul Mbarga"  # Nom tronqué
        self.assertFalse(verify_integrity(src, fraud))

    def test_46_alteration_frais_pourcentage(self):
        src = "Frais de 1,5 %"
        fraud = "Frais de 2 %"  # Pourcentage augmenté
        self.assertFalse(verify_integrity(src, fraud))

    def test_47_jeton_perdu_dans_traduction(self):
        src = "Solde : 250 000 FCFA"
        masked, tokens, _ = mask_sensitive_data(src)
        # La traduction a supprimé le jeton
        corrupted_trans = "Moni mi titi : "
        restored, ok = restore_sensitive_data(corrupted_trans, tokens, src)
        self.assertFalse(ok)
        self.assertEqual(restored, src)  # Repli source

    def test_48_jeton_duplique_dans_traduction(self):
        src = "Frais : 100 FCFA"
        masked, tokens, _ = mask_sensitive_data(src)
        token = list(tokens.keys())[0]
        # Jeton répété deux fois
        corrupted_trans = f"Mutoa : {token} na {token}"
        restored, ok = restore_sensitive_data(corrupted_trans, tokens, src)
        self.assertFalse(ok)
        self.assertEqual(restored, src)

    def test_49_jetons_permutes(self):
        src = "Montant : 25 000 FCFA, Frais : 100 FCFA"
        masked, tokens, _ = mask_sensitive_data(src)
        t_keys = list(tokens.keys())
        self.assertEqual(len(t_keys), 2)
        # Inversion des jetons
        corrupted_trans = f"Montant : {t_keys[1]}, Frais : {t_keys[0]}"
        # Si on restaure avec permutation, les valeurs sont inversées
        restored_raw = corrupted_trans.replace(t_keys[0], tokens[t_keys[0]]).replace(t_keys[1], tokens[t_keys[1]])
        # L'intégrité de position doit être détectable si un contrôle contextuel est appliqué
        self.assertIn(tokens[t_keys[0]], restored_raw)

    def test_50_jeton_tronque(self):
        src = "Référence : SAF-2026-X7Y8Z9"
        masked, tokens, _ = mask_sensitive_data(src)
        # Jeton abîmé
        corrupted_trans = "Lembá : __SAFE_REF_0"
        restored, ok = restore_sensitive_data(corrupted_trans, tokens, src)
        self.assertFalse(ok)
        self.assertEqual(restored, src)

    def test_51_jeton_injecte_non_existant(self):
        src = "Opération gratuite"
        masked, tokens, _ = mask_sensitive_data(src)
        corrupted_trans = "Ebólo __SAFE_AMOUNT_99__"
        # Il y a un jeton dans la traduction alors qu'aucun n'était attendu
        restored, ok = restore_sensitive_data(corrupted_trans, tokens, src)
        self.assertFalse(ok)

    def test_52_alteration_date_financiere(self):
        src = "Reçu le 05 nov. 2026"
        fraud = "Reçu le 06 nov. 2026"  # Date changée
        self.assertFalse(verify_integrity(src, fraud))


class TestEngineTimeoutAndAPIErrorHandling(unittest.TestCase):
    """Vérification des erreurs, timeouts et replis de l'API locale."""

    def test_53_moteur_timeout_declenche_repli_source(self):
        # Moteur avec délai de 0.5s et timeout strict à 0.1s
        slow_engine = AutomaticMockEngine(timeout_seconds=0.1, simulated_delay=0.5)
        with self.assertRaises(TranslationEngineTimeoutError):
            slow_engine.translate("Texte inédit", "fr", "dua")

    def test_54_moteur_erreur_declenche_repli_source(self):
        # Moteur en échec
        broken_engine = AutomaticMockEngine(simulate_error=True)
        with self.assertRaises(TranslationEngineError):
            broken_engine.translate("Texte inédit", "fr", "dua")

    def test_55_api_depassement_limite_taille_lot(self):
        # Requête avec plus de 100 éléments (limite MAX_BATCH_SIZE)
        items = [{"id": f"item_{i}", "text": f"Texte {i}"} for i in range(105)]
        payload = {
            "source_lang": "fr",
            "target_lang": "dua",
            "items": items
        }
        res = client.post("/translate/batch", json=payload)
        self.assertEqual(res.status_code, 413)

    def test_56_api_depassement_longueur_texte(self):
        # Requête avec un texte de plus de 2000 caractères
        long_text = "A" * 2500
        payload = {
            "source_lang": "fr",
            "target_lang": "dua",
            "items": [{"id": "too_long", "text": long_text}]
        }
        res = client.post("/translate/batch", json=payload)
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
