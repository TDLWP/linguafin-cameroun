import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import csv
from backend.engine import CTranslate2FulfuldeEngine
from backend.protect import mask_sensitive_data, restore_sensitive_data, verify_integrity

TEST_STRINGS = [
    # Navigation & Écrans clés
    "Solde",
    "Frais",
    "Bénéficiaire",
    "Récapitulatif",
    "Confirmation",
    "Erreur",
    "Avertissement de sécurité",
    # Intégrité financière (montants, devises, pourcentages)
    "Votre solde disponible est de 125 000 FCFA.",
    "Les frais s'élèvent à 1.5% du montant transféré.",
    "Montant à envoyer : 25 000 FCFA",
    # Données sensibles (téléphone, référence, date)
    "Numéro de téléphone du destinataire : +237 670 00 00 00",
    "Référence de transaction : TX-98472-XAF",
    "Date de l'opération : 14/11/2026",
    # Actions & Boutons
    "Confirmer le transfert",
    "Annuler",
    # Messages système & Avertissements
    "Ne partagez jamais votre code secret avec qui que ce soit.",
    "Solde insuffisant pour effectuer cette transaction.",
    "Transfert effectué avec succès.",
    "Historique des transactions",
    "Veuillez vérifier les informations avant de valider."
]

def main():
    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "models", "francais-fufulde"))
    print(f"Chargement du moteur CTranslate2 depuis : {model_dir}")
    engine = CTranslate2FulfuldeEngine(model_dir=model_dir)

    print(f"Moteur disponible : {engine.is_available()}")
    if not engine.is_available():
        print(f"MODE REPLI ACTIF : Le modèle CTranslate2 n'est pas présent ({engine._load_error}). Activation du repli source garanti sans planter.")

    results = []
    print("\n" + "=" * 125)
    print(f"{'#':<3} | {'SOURCE':<30} | {'SORTIE BRUTE MOTEUR':<45} | {'DIFFÉRENT'} | {'INTÉGRITÉ'}")
    print("=" * 125)

    diff_count = 0

    for i, src in enumerate(TEST_STRINGS, 1):
        # 1. Sortie brute directe du moteur sans masque
        raw_direct = engine.translate(src, "fr", "ful").strip()
        is_diff = "oui" if (raw_direct != src.strip() and bool(raw_direct)) else "non"
        if is_diff == "oui":
            diff_count += 1

        # 2. Pipeline avec masquage des données sensibles
        masked, token_map, order = mask_sensitive_data(src)
        raw_masked_tr = engine.translate(masked, "fr", "ful")
        restored, is_valid = restore_sensitive_data(raw_masked_tr, token_map, src)
        
        # 3. Contrôle d'intégrité
        if is_valid and verify_integrity(src, restored, token_map):
            status_integ = "PASS (Inviolé)"
        elif restored == src:
            status_integ = "PASS (Repli source sécurisé)"
        else:
            status_integ = "FAIL (Altéré)"
        
        results.append({
            "id": i,
            "source": src,
            "sortie_brute": raw_direct,
            "different_de_la_source": is_diff,
            "masked": masked,
            "raw_masked_translation": raw_masked_tr,
            "restored": restored,
            "integrity": status_integ
        })

        src_disp = (src[:27] + "...") if len(src) > 30 else src
        raw_disp = (raw_direct[:42] + "...") if len(raw_direct) > 45 else raw_direct
        print(f"{i:<3} | {src_disp:<30} | {raw_disp:<45} | {is_diff:<9} | {status_integ}")

    print("=" * 125)
    print(f"Total sorties non vides et différentes de la source : {diff_count} / {len(TEST_STRINGS)} ({diff_count / len(TEST_STRINGS) * 100:.1f}%)")
    
    # Export CSV pour traçabilité
    out_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "catalogue", "evaluation_fulfulde_20.csv"))
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "source", "sortie_brute", "different_de_la_source", "masked", "raw_masked_translation", "restored", "integrity"
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nRapport complet généré dans : {out_csv}")

if __name__ == "__main__":
    main()
