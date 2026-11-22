#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de génération des catalogues pilote (Duálá - dua et Bassa - bas) pour SAFINUM Innovate Challenge 2026.
Règles permanentes :
- Tout en statut "draft"
- Colonne validateur vide ("")
- Périphrases signalées dans commentaire ("Périphrase : ...")
- Mots incertains marqués "INCERTAIN"
- Glossaire financier enrichi de 40 à 60 termes
- Fiche de validation CSV générée pour le validateur humain (langue pilote)
"""

import os
import csv
import json

def build_pilot_catalog():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_strings_path = os.path.join(base_dir, "data", "test_env_strings.json")
    
    with open(test_strings_path, "r", encoding="utf-8") as f:
        test_strings = json.load(f)

    # 1. Base des traductions pour les chaînes de test_env_strings.json et du parcours
    # Toutes en statut "draft", validateur "", date "2026-11-14"
    catalog_items = [
        # Navigation & Global
        {
            "cle": "brand_name",
            "source": "Safinum Pay",
            "dua": "Safinum Pay",
            "bas": "Safinum Pay",
            "comment_dua": "Marque commerciale protégée — non modifiée",
            "comment_bas": "Marque commerciale protégée — non modifiée"
        },
        {
            "cle": "online_banking",
            "source": "Banque en ligne",
            "dua": "Banka o mwendi",
            "bas": "Bañga i fôn",
            "comment_dua": "Périphrase : Banka o mwendi ma telefon (banque sur réseau)",
            "comment_bas": "Périphrase : Bañga i fôn (banque sur téléphone)"
        },
        {
            "cle": "top_banner_notice",
            "source": "Environnement de test — données fictives, aucune transaction réelle.",
            "dua": "Epolo ya kekise — betiledi ba wombe, to ebolo ya moni ya mbale titi.",
            "bas": "Hom i noode — manjel ma wombe, to nsal u moni u mbale bé.",
            "comment_dua": "Avertissement environnement de démonstration",
            "comment_bas": "Avertissement environnement de démonstration"
        },
        {
            "cle": "test_protocol",
            "source": "Protocole de test",
            "dua": "Mbwedi ya kekise",
            "bas": "Mbad i noode",
            "comment_dua": "Périphrase : Mbwedi ya kekise (règles d'évaluation/essai)",
            "comment_bas": "Périphrase : Mbad i noode (chemin/méthode d'essai)"
        },
        {
            "cle": "back_to_hackathon",
            "source": "Retour au hackathon",
            "dua": "Timba o hackathon",
            "bas": "Témb i hackathon",
            "comment_dua": "Terme hackathon conservé comme emprunt technique",
            "comment_bas": "Terme hackathon conservé comme emprunt technique"
        },
        {
            "cle": "secure_connection",
            "source": "Connexion sécurisée",
            "dua": "Jowe la mbembe",
            "bas": "Mbuma i mbok",
            "comment_dua": "Périphrase : Jowe la mbembe (liaison sous protection)",
            "comment_bas": "Périphrase : Mbuma i mbok (accès protégé)"
        },
        {
            "cle": "footer_disclaimer",
            "source": "Safinum Pay — environnement de démonstration. Ne saisissez aucune donnée personnelle réelle.",
            "dua": "Safinum Pay — epolo ya kekise. O si boke betiledi bongó ba mbale.",
            "bas": "Safinum Pay — hom i noode. U tila bé mam moñ ma mbale.",
            "comment_dua": "Avertissement sécurité données privées",
            "comment_bas": "Avertissement sécurité données privées"
        },
        # Étapes Wizard
        {
            "cle": "wizard_step1",
            "source": "Solde",
            "dua": "Moni mi titi",
            "bas": "Kôbô i moni",
            "comment_dua": "Terme financier standard : moni mi titi (argent disponible)",
            "comment_bas": "Terme financier standard : kôbô i moni (réserve d'argent)"
        },
        {
            "cle": "wizard_step2",
            "source": "Frais",
            "dua": "Mutoa",
            "bas": "Ntomb",
            "comment_dua": "Terme financier : mutoa (frais, coût de transaction)",
            "comment_bas": "Terme financier : ntomb (frais prélevés)"
        },
        {
            "cle": "wizard_step3",
            "source": "Bénéficiaire",
            "dua": "Nongi a moni",
            "bas": "Mut a nkôs",
            "comment_dua": "Périphrase : Nongi a moni (celui qui reçoit l'argent)",
            "comment_bas": "Périphrase : Mut a nkôs (personne qui reçoit)"
        },
        {
            "cle": "wizard_step4",
            "source": "Récapitulatif",
            "dua": "Mbondo a tomba",
            "bas": "Mambog ma ntomba",
            "comment_dua": "Périphrase : Mbondo a tomba (bilan/résumé du transfert)",
            "comment_bas": "Périphrase : Mambog ma ntomba (sommaire du transfert)"
        },
        {
            "cle": "wizard_step5",
            "source": "Confirmation",
            "dua": "Kakisane",
            "bas": "Mba᷇k",
            "comment_dua": "Validation formelle de l'opération",
            "comment_bas": "Validation formelle de l'opération"
        },
        # Actions clés du parcours demandées
        {
            "cle": "action_cancel",
            "source": "Annuler",
            "dua": "Kwele ebolo",
            "bas": "Tiba nsal",
            "comment_dua": "Périphrase : Kwele ebolo (abandonner/arrêter l'opération en cours)",
            "comment_bas": "Périphrase : Tiba nsal (arrêter l'action)"
        },
        {
            "cle": "action_confirm",
            "source": "Confirmer",
            "dua": "Kakisane",
            "bas": "Mba᷇k",
            "comment_dua": "Validation impérative de l'action",
            "comment_bas": "Validation impérative de l'action"
        },
        {
            "cle": "action_transfer",
            "source": "Transfert",
            "dua": "Tomba",
            "bas": "Ntomba",
            "comment_dua": "Opération financière de déplacement d'argent (loma moni)",
            "comment_bas": "Opération financière d'envoi de fonds"
        },
        {
            "cle": "status_error",
            "source": "Erreur",
            "dua": "Bwemba",
            "bas": "Mbebi",
            "comment_dua": "Défaut d'exécution ou problème survenu",
            "comment_bas": "Anomalie ou problème système"
        },
        {
            "cle": "status_security",
            "source": "Sécurité",
            "dua": "Mbembe",
            "bas": "Mbok i tibil tehe",
            "comment_dua": "Protection et vigilance",
            "comment_bas": "Protection et précaution"
        },
        # Dashboard & Écran 1 Solde
        {
            "cle": "dash_your_account",
            "source": "Votre compte",
            "dua": "Kompiti yango",
            "bas": "Kompiti yoñ",
            "comment_dua": "Emprunt bantouisé standard pour compte bancaire",
            "comment_bas": "Emprunt bancaire bantouisé"
        },
        {
            "cle": "dash_hello_amina",
            "source": "Bonjour, Amina",
            "dua": "Mbolo, Amina",
            "bas": "Mbolo, Amina",
            "comment_dua": "Salutation + nom propre protégé invariable",
            "comment_bas": "Salutation + nom propre protégé invariable"
        },
        {
            "cle": "dash_intro_text",
            "source": "Consultez votre solde et lancez un transfert en toute sécurité.",
            "dua": "Ombwele moni mongó na lom moni na mbembe.",
            "bas": "Béñgê moni moñ, u om moni kiki i téé sép.",
            "comment_dua": "Phrase d'accueil tableau de bord",
            "comment_bas": "Phrase d'accueil tableau de bord"
        },
        {
            "cle": "dash_available_balance",
            "source": "Solde disponible",
            "dua": "Moni mi titi o bolane",
            "bas": "Moni mi yé inyu salo",
            "comment_dua": "Périphrase : Moni mi titi o bolane (argent présent utilisable)",
            "comment_bas": "Périphrase : Moni mi yé inyu salo (argent présent pour utilisation)"
        },
        {
            "cle": "dash_account_number",
            "source": "Numéro de compte",
            "dua": "Nombá ya kompiti",
            "bas": "Namba i kompiti",
            "comment_dua": "Identifiant de compte client",
            "comment_bas": "Identifiant de compte client"
        },
        {
            "cle": "dash_current_account",
            "source": "Compte courant",
            "dua": "Kompiti ya buńa té",
            "bas": "Kompiti i hiki kel",
            "comment_dua": "Périphrase : Kompiti ya buńa té (compte des opérations quotidiennes)",
            "comment_bas": "Périphrase : Kompiti i hiki kel (compte de chaque jour)"
        },
        {
            "cle": "dash_btn_make_transfer",
            "source": "Effectuer un transfert",
            "dua": "Loma moni",
            "bas": "Om moni",
            "comment_dua": "Action d'envoi de fonds",
            "comment_bas": "Action d'envoi de fonds"
        },
        {
            "cle": "dash_btn_view_fees",
            "source": "Consulter les frais",
            "dua": "Ombwele mutoa",
            "bas": "Béñgê ntomb",
            "comment_dua": "Vérification préalable de la tarification",
            "comment_bas": "Vérification préalable de la tarification"
        },
        {
            "cle": "dash_recent_transactions",
            "source": "Transactions récentes",
            "dua": "Bebolo ba moni ba bo buńa",
            "bas": "Mam ma moni ma haa",
            "comment_dua": "Périphrase : Bebolo ba moni ba bo buńa (opérations des derniers jours)",
            "comment_bas": "Périphrase : Mam ma moni ma haa (actes financiers récents)"
        },
        {
            "cle": "tx_date_05_nov",
            "source": "05 nov. 2026",
            "dua": "05 nov. 2026",
            "bas": "05 nov. 2026",
            "comment_dua": "Date financière protégée — stricte conservation",
            "comment_bas": "Date financière protégée — stricte conservation"
        },
        {
            "cle": "tx_merchant_payment",
            "source": "Paiement marchand",
            "dua": "Sawa la mutoa",
            "bas": "Mbaña i mam",
            "comment_dua": "Périphrase : Sawa la mutoa (règlement d'achat commercial) — INCERTAIN",
            "comment_bas": "Périphrase : Mbaña i mam (paiement des marchandises) — INCERTAIN"
        },
        {
            "cle": "tx_date_04_nov",
            "source": "04 nov. 2026",
            "dua": "04 nov. 2026",
            "bas": "04 nov. 2026",
            "comment_dua": "Date financière protégée — stricte conservation",
            "comment_bas": "Date financière protégée — stricte conservation"
        },
        {
            "cle": "tx_salary_received",
            "source": "Salaire reçu",
            "dua": "Moni ma musadi ma sangi",
            "bas": "Moni ma salo ma nlo",
            "comment_dua": "Périphrase : Moni ma musadi ma sangi (argent du travail arrivé)",
            "comment_bas": "Périphrase : Moni ma salo ma nlo (revenu du travail reçu)"
        },
        {
            "cle": "tx_date_02_nov",
            "source": "02 nov. 2026",
            "dua": "02 nov. 2026",
            "bas": "02 nov. 2026",
            "comment_dua": "Date financière protégée — stricte conservation",
            "comment_bas": "Date financière protégée — stricte conservation"
        },
        {
            "cle": "tx_transfer_received",
            "source": "Transfert reçu",
            "dua": "Moni ma lomi ma sangi",
            "bas": "Moni ma om ma nlo",
            "comment_dua": "Périphrase : Moni ma lomi ma sangi (argent envoyé qui a été reçu)",
            "comment_bas": "Périphrase : Moni ma om ma nlo (argent envoyé arrivé)"
        },
        {
            "cle": "tx_date_31_oct",
            "source": "31 oct. 2026",
            "dua": "31 oct. 2026",
            "bas": "31 oct. 2026",
            "comment_dua": "Date financière protégée — stricte conservation",
            "comment_bas": "Date financière protégée — stricte conservation"
        },
        {
            "cle": "tx_electricity_bill",
            "source": "Facture électricité",
            "dua": "Mutoa ma mwese",
            "bas": "Ntomb i mabéñg",
            "comment_dua": "Périphrase : Mutoa ma mwese (coût du courant/lumière)",
            "comment_bas": "Périphrase : Ntomb i mabéñg (dépense pour l'électricité)"
        },
        # Étape 2 Frais
        {
            "cle": "fee_screen_title",
            "source": "Frais de transfert",
            "dua": "Mutoa ma tomba",
            "bas": "Ntomb i ntomba",
            "comment_dua": "Tarification de l'envoi",
            "comment_bas": "Tarification de l'envoi"
        },
        {
            "cle": "fee_screen_subtitle",
            "source": "Choisissez le type de transfert et le montant. Les frais sont calculés automatiquement.",
            "dua": "Posa pateli ya tomba na moni. Mutoa mu mendeno kusedo na momele.",
            "bas": "Pôdôs mbad i ntomba ni moni. Ntomb i mboñba nyominsô.",
            "comment_dua": "Consigne simulation des frais",
            "comment_bas": "Consigne simulation des frais"
        },
        {
            "cle": "fee_operation_type",
            "source": "Type d'opération",
            "dua": "Pateli ya ebólo",
            "bas": "Mbad i nsal",
            "comment_dua": "Catégorisation de la transaction",
            "comment_bas": "Catégorisation de la transaction"
        },
        {
            "cle": "op_safinum_account",
            "source": "Compte Safinum",
            "dua": "Kompiti Safinum",
            "bas": "Kompiti Safinum",
            "comment_dua": "Virement interne Safinum",
            "comment_bas": "Virement interne Safinum"
        },
        {
            "cle": "op_safinum_note",
            "source": "Transfert instantané et gratuit",
            "dua": "Loma na diboa, titi mutoa",
            "bas": "Om i ngii kôna, ibabé ntomb",
            "comment_dua": "Périphrase : Loma na diboa, titi mutoa (envoi immédiat sans frais)",
            "comment_bas": "Périphrase : Om i ngii kôna, ibabé ntomb (envoi direct sans coût)"
        },
        {
            "cle": "op_mobile_money",
            "source": "Mobile Money",
            "dua": "Mobile Money",
            "bas": "Mobile Money",
            "comment_dua": "Terme protégé écosystème télécom",
            "comment_bas": "Terme protégé écosystème télécom"
        },
        {
            "cle": "op_mobile_money_note",
            "source": "Frais de 1,5 % (min. 100 FCFA, max. 2 500 FCFA)",
            "dua": "Mutoa ma 1,5 % (min. 100 FCFA, max. 2 500 FCFA)",
            "bas": "Ntomb i 1,5 % (min. 100 FCFA, max. 2 500 FCFA)",
            "comment_dua": "Valeurs numériques et pourcentages protégés",
            "comment_bas": "Valeurs numériques et pourcentages protégés"
        },
        {
            "cle": "op_other_bank",
            "source": "Autre banque",
            "dua": "Banka nipépe",
            "bas": "Bañga ipe",
            "comment_dua": "Virement interbancaire externe",
            "comment_bas": "Virement interbancaire externe"
        },
        {
            "cle": "op_other_bank_note",
            "source": "Frais de 2 % (min. 200 FCFA, max. 5 000 FCFA)",
            "dua": "Mutoa ma 2 % (min. 200 FCFA, max. 5 000 FCFA)",
            "bas": "Ntomb i 2 % (min. 200 FCFA, max. 5 000 FCFA)",
            "comment_dua": "Valeurs numériques et pourcentages protégés",
            "comment_bas": "Valeurs numériques et pourcentages protégés"
        },
        {
            "cle": "fee_amount_to_send",
            "source": "Montant à envoyer",
            "dua": "Moni ma lomabe",
            "bas": "Moni i n-om",
            "comment_dua": "Périphrase : Moni ma lomabe (somme d'argent à expédier)",
            "comment_bas": "Périphrase : Moni i n-om (somme envoyée)"
        },
        {
            "cle": "fee_total_to_debit",
            "source": "Total à débiter",
            "dua": "Moni mése ma busisabe",
            "bas": "Moni momasôna ma nkodol",
            "comment_dua": "Périphrase : Moni mése ma busisabe (tout l'argent qui sortira)",
            "comment_bas": "Périphrase : Moni momasôna ma nkodol (tout l'argent débité)"
        },
        {
            "cle": "fee_balance_after",
            "source": "Solde après opération",
            "dua": "Moni mi matiké",
            "bas": "Moni ma ntigi",
            "comment_dua": "Périphrase : Moni mi matiké (argent qui restera sur le compte)",
            "comment_bas": "Périphrase : Moni ma ntigi (reste après opération)"
        },
        {
            "cle": "badge_free",
            "source": "Gratuit",
            "dua": "Titi mutoa",
            "bas": "Ibabé ntomb",
            "comment_dua": "Sans frais",
            "comment_bas": "Sans frais"
        },
        {
            "cle": "btn_back",
            "source": "Retour",
            "dua": "Timba",
            "bas": "Témb",
            "comment_dua": "Bouton d'étape précédente",
            "comment_bas": "Bouton d'étape précédente"
        },
        {
            "cle": "btn_continue",
            "source": "Continuer",
            "dua": "Alá oboso",
            "bas": "Kenel bisu",
            "comment_dua": "Progression vers l'étape suivante",
            "comment_bas": "Progression vers l'étape suivante"
        },
        # Étape 3 Bénéficiaire
        {
            "cle": "ben_screen_subtitle",
            "source": "Renseignez les informations du destinataire. Vérifiez toujours le numéro avant de valider.",
            "dua": "Londeyi bitilá ba nongi. Ombwele nombá oboso na kakisane.",
            "bas": "Tila manjel ma nu a nkôs. Béñgê namba ilole u mba᷇k.",
            "comment_dua": "Instructions saisie destinataire",
            "comment_bas": "Instructions saisie destinataire"
        },
        {
            "cle": "ben_warning_new",
            "source": "Ce bénéficiaire n'a jamais été utilisé sur ce compte. Vérifiez le numéro avant de continuer.",
            "dua": "Nu nongi a si sengedi no o yé kompiti. Ombwele nombá oboso na ala oboso.",
            "bas": "Nu a nkôs a nsal bé kii hane o kompiti yini. Béñgê namba ilole u nkenel bisu.",
            "comment_dua": "Avertissement critique nouveau contact",
            "comment_bas": "Avertissement critique nouveau contact"
        },
        {
            "cle": "ben_name_label",
            "source": "Nom du bénéficiaire",
            "dua": "Dina la nongi",
            "bas": "Jôl li nu a nkôs",
            "comment_dua": "Périphrase : Dina la nongi (nom de celui qui reçoit)",
            "comment_bas": "Périphrase : Jôl li nu a nkôs (nom de qui reçoit)"
        },
        {
            "cle": "ben_phone_label",
            "source": "Numéro de téléphone",
            "dua": "Nombá ya telefon",
            "bas": "Namba i fôn",
            "comment_dua": "Champ téléphone",
            "comment_bas": "Champ téléphone"
        },
        {
            "cle": "ben_reason_label",
            "source": "Motif du transfert",
            "dua": "Njonji ya tomba",
            "bas": "Njéñg i ntomba",
            "comment_dua": "Périphrase : Njonji ya tomba (raison/motif de l'envoi)",
            "comment_bas": "Périphrase : Njéñg i ntomba (cause du transfert)"
        },
        {
            "cle": "ben_reason_default",
            "source": "Paiement de services",
            "dua": "Sawa la ebolo",
            "bas": "Mbaña i salo",
            "comment_dua": "Périphrase : Sawa la ebolo (règlement pour travail)",
            "comment_bas": "Périphrase : Mbaña i salo (paiement pour service rendu)"
        },
        {
            "cle": "ben_note_label",
            "source": "Note (optionnel)",
            "dua": "Betiledi (o mapula)",
            "bas": "Bañga (ngi u sômblak)",
            "comment_dua": "Périphrase : Betiledi (o mapula) (mots optionnels)",
            "comment_bas": "Périphrase : Bañga (ngi u sômblak) (notes si souhaité)"
        },
        {
            "cle": "ben_checkbox_verified",
            "source": "J'ai vérifié le nom et le numéro du bénéficiaire.",
            "dua": "Na mombweli dina na nombá ya nu nongi.",
            "bas": "Me mbéñgê jôl ni namba i nu a nkôs.",
            "comment_dua": "Déclaration explicite de vérification",
            "comment_bas": "Déclaration explicite de vérification"
        },
        # Étape 4 Récapitulatif
        {
            "cle": "sum_screen_subtitle",
            "source": "Vérifiez les informations avant de confirmer le transfert.",
            "dua": "Ombwele bwam betiledi oboso na loma moni.",
            "bas": "Béñgê loñge ilole u n-om moni.",
            "comment_dua": "Relecture préalable obligatoire",
            "comment_bas": "Relecture préalable obligatoire"
        },
        {
            "cle": "sum_label_amount",
            "source": "Montant",
            "dua": "Moni",
            "bas": "Moni",
            "comment_dua": "Valeur principale transaction",
            "comment_bas": "Valeur principale transaction"
        },
        {
            "cle": "sum_label_total_debited",
            "source": "Total débité",
            "dua": "Moni mése ma busisabe",
            "bas": "Moni momasôna ma nkodol",
            "comment_dua": "Périphrase : Total débité du compte",
            "comment_bas": "Périphrase : Total débité du compte"
        },
        {
            "cle": "sum_label_phone",
            "source": "Téléphone",
            "dua": "Telefon",
            "bas": "Fôn",
            "comment_dua": "Emprunt usuel d'usage universel",
            "comment_bas": "Emprunt usuel d'usage universel"
        },
        {
            "cle": "sum_label_reference",
            "source": "Référence",
            "dua": "Lembá",
            "bas": "Lemb",
            "comment_dua": "Périphrase : Lembá (identifiant d'opération)",
            "comment_bas": "Périphrase : Lemb (identifiant d'opération)"
        },
        {
            "cle": "sum_label_operation",
            "source": "Opération",
            "dua": "Ebólo",
            "bas": "Nsal",
            "comment_dua": "Acte financier exécuté",
            "comment_bas": "Acte financier exécuté"
        },
        {
            "cle": "sum_checkbox_confirm",
            "source": "Je confirme que les informations ci-dessus sont correctes.",
            "dua": "Na kakisane na bi betiledi bése be bwan.",
            "bas": "Me mba᷇k le mam mana masôna ma yé sép.",
            "comment_dua": "Validation formelle des données récapitulatives",
            "comment_bas": "Validation formelle des données récapitulatives"
        },
        {
            "cle": "btn_edit",
            "source": "Modifier",
            "dua": "Tukwe",
            "bas": "Héñha",
            "comment_dua": "Correction des champs saisis",
            "comment_bas": "Correction des champs saisis"
        },
        {
            "cle": "btn_confirm_transfer",
            "source": "Confirmer le transfert",
            "dua": "Kakisane tomba",
            "bas": "Mba᷇k ntomba",
            "comment_dua": "Bouton d'engagement irréversible",
            "comment_bas": "Bouton d'engagement irréversible"
        },
        # Étape 5 Reçu & Succès
        {
            "cle": "receipt_title",
            "source": "Transfert effectué",
            "dua": "Moni mi lomi na bwam",
            "bas": "Moni ma n-omna loñge",
            "comment_dua": "Notification de succès de l'envoi",
            "comment_bas": "Notification de succès de l'envoi"
        },
        {
            "cle": "receipt_subtitle",
            "source": "Votre transfert a été envoyé avec succès.",
            "dua": "Moni mongó mi lomi bwambwam.",
            "bas": "Moni moñ ma n-omna loñge ngandak.",
            "comment_dua": "Confirmation de transmission réussie",
            "comment_bas": "Confirmation de transmission réussie"
        },
        {
            "cle": "receipt_label_status",
            "source": "Statut",
            "dua": "Mbembe ya ebólo",
            "bas": "Mba᷇k i nsal",
            "comment_dua": "Périphrase : Mbembe ya ebólo (état de l'opération) — INCERTAIN",
            "comment_bas": "Périphrase : Mba᷇k i nsal (état de l'acte) — INCERTAIN"
        },
        {
            "cle": "receipt_status_success",
            "source": "Succès",
            "dua": "Bwam",
            "bas": "Loñge",
            "comment_dua": "Validation positive",
            "comment_bas": "Validation positive"
        },
        {
            "cle": "btn_new_transfer",
            "source": "Nouveau transfert",
            "dua": "Loma moni pe",
            "bas": "Om moni pe",
            "comment_dua": "Nouvelle opération financière",
            "comment_bas": "Nouvelle opération financière"
        },
        # Alertes & Sécurité
        {
            "cle": "sec_sidebar_title",
            "source": "Sécurité",
            "dua": "Mbembe",
            "bas": "Mbok i tibil tehe",
            "comment_dua": "Rubrique d'assistance et de vigilance",
            "comment_bas": "Rubrique de précaution"
        },
        {
            "cle": "sec_sidebar_text",
            "source": "Vérifiez toujours le nom et le numéro du bénéficiaire avant de confirmer un transfert.",
            "dua": "Ombwele ponda yése dina na nombá ya nongi oboso na kakisane.",
            "bas": "Béñgê ponda yosôna jôl ni namba i nu a nkôs ilole u mba᷇k.",
            "comment_dua": "Consigne anti-fraude essentielle",
            "comment_bas": "Consigne anti-fraude essentielle"
        },
        {
            "cle": "alert_error_title",
            "source": "Une erreur est survenue",
            "dua": "Bwemba bo pumi",
            "bas": "Mbebi i nsuba",
            "comment_dua": "Avertissement anomalie bloquante",
            "comment_bas": "Avertissement anomalie bloquante"
        },
        {
            "cle": "alert_security_title",
            "source": "Alerte de sécurité",
            "dua": "Kwalisan ya mbembe",
            "bas": "Mbat i mbok",
            "comment_dua": "Périphrase : Kwalisan ya mbembe (avertissement de protection)",
            "comment_bas": "Périphrase : Mbat i mbok (avertissement de protection)"
        },
        {
            "cle": "btn_dismiss",
            "source": "Fermer",
            "dua": "Kwele",
            "bas": "Tiba",
            "comment_dua": "Fermeture d'alerte",
            "comment_bas": "Fermeture d'alerte"
        },
        {
            "cle": "injected_title",
            "source": "Message important",
            "dua": "Mwengue mwendi",
            "bas": "Nteñgu u nleñg",
            "comment_dua": "Périphrase : Avis urgent / message d'attention — INCERTAIN",
            "comment_bas": "Périphrase : Message important — INCERTAIN"
        },
        # Messages d'erreur spécifiques
        {
            "cle": "err_amount_001",
            "source": "Le montant doit être supérieur à zéro.",
            "dua": "Moni ma lomebe ma sengi bobe nika zéro.",
            "bas": "Moni ma n-om ma kôli loo zéro.",
            "comment_dua": "Erreur saisie montant invalide",
            "comment_bas": "Erreur saisie montant invalide"
        },
        {
            "cle": "err_amount_002",
            "source": "Solde insuffisant pour effectuer ce transfert.",
            "dua": "Moni mongó ma titi suwedi o loma yé moni.",
            "bas": "Moni moñ ma nsuba bé inyu ntomba nunu.",
            "comment_dua": "Périphrase : Solde disponible insuffisant pour l'envoi",
            "comment_bas": "Périphrase : Solde insuffisant pour le transfert"
        },
        {
            "cle": "err_beneficiary_001",
            "source": "Veuillez renseigner le nom et le numéro du bénéficiaire.",
            "dua": "Londeyi dina na nombá ya nu nongi.",
            "bas": "Tila jôl ni namba i nu a nkôs.",
            "comment_dua": "Erreur champ obligatoire absent",
            "comment_bas": "Erreur champ obligatoire absent"
        },
        {
            "cle": "err_security_001",
            "source": "Alerte de sécurité : vérifiez le numéro du bénéficiaire avant de continuer.",
            "dua": "Kwalisan ya mbembe : ombwele nombá ya nu nongi oboso na ala oboso.",
            "bas": "Mbat i mbok : béñgê namba i nu a nkôs ilole u nkenel bisu.",
            "comment_dua": "Alerte contrôle obligatoire numéro",
            "comment_bas": "Alerte contrôle obligatoire numéro"
        },
        {
            "cle": "err_security_002",
            "source": "Alerte de sécurité : ce bénéficiaire n'a jamais été utilisé sur ce compte.",
            "dua": "Kwalisan ya mbembe : nu nongi a si sengedi no o yé kompiti.",
            "bas": "Mbat i mbok : nu a nkôs a nsal bé kii hane o kompiti yini.",
            "comment_dua": "Alerte nouveau destinataire inconnu",
            "comment_bas": "Alerte nouveau destinataire inconnu"
        },
        {
            "cle": "err_network_001",
            "source": "Erreur réseau : le service est temporairement indisponible. Réessayez.",
            "dua": "Bwemba bo titi ya résô : ebolo e titi tano. Timba o keka pe.",
            "bas": "Mbebi i réseau : nsal u yé bé haa. Kéñha pe.",
            "comment_dua": "Périphrase réseau : emprunt résô — INCERTAIN",
            "comment_bas": "Périphrase réseau : emprunt réseau — INCERTAIN"
        },
        {
            "cle": "err_confirm_001",
            "source": "Vous devez confirmer les informations avant de valider le transfert.",
            "dua": "E mapula o kakisane bitilá oboso na loma.",
            "bas": "I kôli le u mba᷇k mam mana ilole u n-om.",
            "comment_dua": "Obligation de cocher la confirmation",
            "comment_bas": "Obligation de cocher la confirmation"
        }
    ]

    # Vérification d'exhaustivité avec test_strings
    existing_sources = {item["source"].strip(): item for item in catalog_items}
    for src_text in test_strings.keys():
        st = src_text.strip()
        if st not in existing_sources:
            print(f"[NOTE] Ajout de la chaîne issue de l'audit : {st}")
            catalog_items.append({
                "cle": f"auto_{len(catalog_items)+1:03d}",
                "source": st,
                "dua": st,
                "bas": st,
                "comment_dua": "Chaîne relevée lors de l'audit — INCERTAIN",
                "comment_bas": "Chaîne relevée lors de l'audit — INCERTAIN"
            })

    # 2. Écriture de catalogue/translations.csv
    # Colonnes : cle,source,langue,cible,statut,validateur_code,date,commentaire
    csv_trans_path = os.path.join(base_dir, "catalogue", "translations.csv")
    with open(csv_trans_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["cle", "source", "langue", "cible", "statut", "validateur_code", "date", "commentaire"])
        for item in catalog_items:
            # Langue pilote Duálá (dua)
            writer.writerow([
                item["cle"],
                item["source"],
                "dua",
                item["dua"],
                "machine_suggested",  # STRICTEMENT machine_suggested (IA)
                "",                   # STRICTEMENT vide
                "2026-11-14",
                item["comment_dua"]
            ])
            # Seconde langue Ɓàsàa (bas)
            writer.writerow([
                item["cle"],
                item["source"],
                "bas",
                item["bas"],
                "machine_suggested",  # STRICTEMENT machine_suggested (IA)
                "",                   # STRICTEMENT vide
                "2026-11-14",
                item["comment_bas"]
            ])

    print(f"[OK] {csv_trans_path} généré ({len(catalog_items) * 2} lignes, toutes en statut machine_suggested, validateur vide).")

    # 3. Glossaire financier complet (52 termes financiers)
    # Colonnes : terme_source,langue,terme_cible,contexte,statut,notes
    glossary_terms = [
        ("Solde", "Moni mi titi", "Kôbô i moni", "Kəpka' cap", "Nkobe moni", "Finance / Compte", "Terme courant pour l'argent disponible sur le compte"),
        ("Solde disponible", "Moni mi titi o bolane", "Moni mi yé inyu salo", "Kəpka' cap i gʉo", "Nkobe moni mbege", "Finance / Compte", "Périphrase : Argent utilisable immédiatement pour un paiement"),
        ("Solde insuffisant", "Moni mi si suwedi", "Moni moñ ma nsuba bé", "Kəpka' cap kə̌ le", "Nkobe moni tekě sôsô", "Transaction / Erreur", "Périphrase : L'argent sur le compte ne suffit pas pour l'opération"),
        ("Frais", "Mutoa", "Ntomb", "Tôk", "Nzaña", "Transaction / Tarif", "Terme établi pour le coût d'un service ou d'un acte financier"),
        ("Frais de transfert", "Mutoa ma tomba", "Ntomb i ntomba", "Tôk jʉ' gə", "Nzaña mbege moni", "Transaction / Tarif", "Coût retenu lors de l'expédition de fonds"),
        ("Gratuit", "Titi mutoa", "Ibabé ntomb", "Gha tôk", "Tekě nzaña", "Tarification", "Sans aucun frais prélevé"),
        ("Transfert", "Tomba", "Ntomba", "Jʉ' gə", "Mbege moni", "Paiement / Envoi", "Action de faire passer des fonds d'un compte à un autre"),
        ("Effectuer un transfert", "Loma moni", "Om moni", "Kə kap", "Lóm moni", "Action utilisateur", "Périphrase : Envoyer de l'argent vers un destinataire"),
        ("Virement", "Loma moni o banka", "Om moni i bañga", "Kə kap i bañga", "Lóm moni e banka", "Opération bancaire", "Périphrase : Virement entre établissements financiers"),
        ("Dépôt", "Boke moni o kompiti", "Ha moni o kompiti", "Nen kəpka'", "Bége moni e kompiti", "Opération compte", "Périphrase : Placer ou verser de l'argent sur le compte"),
        ("Retrait", "Busa moni", "Kodol moni", "Ku' kəpka'", "Kôlô moni", "Opération compte", "Périphrase : Sortir de l'argent liquide"),
        ("Compte", "Kompiti", "Kompiti", "Kompiti", "Kompiti", "Bancaire", "Emprunt bancaire bantouisé généralisé"),
        ("Compte courant", "Kompiti ya buńa té", "Kompiti i hiki kel", "Kompiti lə gə́ tsa'", "Kompiti ya môs ôse", "Bancaire", "Périphrase : Compte destiné aux dépenses de chaque jour"),
        ("Compte d'épargne", "Kompiti ya baṅga moni", "Kompiti i koba moni", "Kompiti shʉ kəpka'", "Kompiti nkobe moni", "Bancaire", "Périphrase : Compte destiné à garder et faire fructifier l'argent"),
        ("Bénéficiaire", "Nongi a moni", "Mut a nkôs", "Mbe fə", "Nnyo a nyoñ", "Destinataire", "Périphrase : La personne qui réceptionne la somme d'argent"),
        ("Expéditeur", "Lomi a moni", "Mut a n-om", "Mbe lə́m", "Nnyo a lóm", "Émetteur", "Périphrase : La personne qui expédie les fonds"),
        ("Montant", "Moni", "Moni", "Kəpka'", "Moni", "Valeur monétaire", "Somme chiffrée"),
        ("Montant total", "Moni mése", "Moni momasôna", "Kəpka' tsətsə̀", "Moni mese", "Valeur monétaire", "Somme complète incluant les charges"),
        ("Total à débiter", "Moni mése ma busisabe", "Moni momasôna ma nkodol", "Kəpka' tsətsə̀ ku'", "Moni mese ma kôlô", "Transaction", "Périphrase : Totalité des fonds débités du solde"),
        ("Confirmation", "Kakisane", "Mba᷇k", "Kap tə", "Akala", "Validation", "Approbation expresse d'une transaction"),
        ("Confirmer", "Kakisane", "Mba᷇k", "Kap tə", "Akala", "Action", "Verbe d'action pour valider"),
        ("Annuler", "Kwele ebolo", "Tiba nsal", "Sə̌ bə̀", "Tege bo", "Action", "Périphrase : Abandonner ou stopper l'opération en cours"),
        ("Sécurité", "Mbembe", "Mbok i tibil tehe", "Kəm tə", "Mbañ", "Protection", "Protection des données et des fonds"),
        ("Connexion sécurisée", "Jowe la mbembe", "Mbuma i mbok", "Jʉ' kəm tə", "Mbañ mbamba", "Système", "Périphrase : Accès informatique protégé et étanche"),
        ("Référence", "Lembá", "Lemb", "Tʉa", "Ndem", "Identifiant", "Marque distinctive ou code identifiant de transaction"),
        ("Numéro de transaction", "Nombá ya ebólo", "Namba i nsal", "Nombá bə̀", "Namba ya ésaé", "Identifiant", "Identifiant numérique de l'acte financier"),
        ("Code secret / PIN", "Lembá la wumbe la kompiti", "Lemb li nyol", "Lembá tsə", "Ndem bisôk", "Sécurité", "Périphrase : Code confidentiel pour autoriser le transfert"),
        ("Mot de passe", "Eyango ya jowe", "Bañga i jôp", "Gho' jʉ'", "Éfia ya nyiil", "Sécurité", "Périphrase : Mot secret pour déverrouiller l'accès — INCERTAIN"),
        ("Reçu", "Kalati ya kakisane ebolo", "Kalaada i mba᷇k", "Wá’la kap", "Kalate ya akala", "Document", "Périphrase : Écrit ou reçu confirmant l'exécution"),
        ("Historique", "Betiledi ba bebolo ba kalá", "Mam ma moni ma kôba", "Gə́ kəpka' tso", "Mam ya kalá", "Gestion compte", "Périphrase : Registre chronologique des opérations passées"),
        ("Transactions récentes", "Bebolo ba moni ba bo buńa", "Mam ma moni ma haa", "Gə́ kəpka' tsa'", "Mam ya ana", "Gestion compte", "Périphrase : Mouvements financiers des derniers jours"),
        ("Plafond", "Su la moni ma lomabe", "Ngim moni i n-om", "Su kəpka'", "Asu moni", "Limite réglementaire", "Périphrase : Montant maximal autorisé par période"),
        ("Limite quotidienne", "Su la moni la buńa bwo", "Ngim moni i hiki kel", "Su kəpka' tsa'", "Asu moni ya amôs", "Limite réglementaire", "Périphrase : Seuil maximal d'envoi par journée"),
        ("Commission", "Mutoa ma ebolo", "Ntomb i nsal", "Tôk bə̀", "Nzaña ésaé", "Tarification", "Rémunération du prestataire pour le service rendu"),
        ("Taux", "Gwedise la mutoa", "Gwedise i ntomb", "Pʉa tôk", "Afan nzaña", "Tarification / Pourcentage", "Proportion appliquée au calcul des frais — INCERTAIN"),
        ("Intérêt", "Moni ma bapele", "Moni ma mabéñg", "Kəpka' fə́", "Moni mendi", "Bancaire", "Périphrase : Somme additionnelle due ou perçue"),
        ("Crédit", "Nkolongo a moni", "Nkolongo u moni", "Kəpka' nkolongo", "Nkolongo moni", "Financement", "Périphrase : Somme prêtée remboursable ultérieurement"),
        ("Dette / Emprunt", "Nkolongo", "Nkolongo", "Nkolongo", "Nkolongo", "Financement", "Engagement de remboursement"),
        ("Remboursement", "Timbedise nkolongo", "Timbis nkolongo", "Tshwe nkolongo", "Buluse nkolongo", "Paiement dette", "Périphrase : Rendre l'argent emprunté"),
        ("Épargne", "Baṅga moni", "Koba moni", "Shʉ kəpka'", "Kôme moni", "Finances personnelles", "Action de mettre de côté des réserves financières"),
        ("Paiement", "Sawa la moni", "Mbaña i moni", "Sə̌ kəpka'", "Yá moni", "Transaction", "Règlement d'une dette, facture ou achat"),
        ("Paiement marchand", "Sawa la mutoa", "Mbaña i mam", "Sə̌ kəpka' gu", "Yá bôm", "Commerce", "Périphrase : Règlement effectué au bénéfice d'un commerçant — INCERTAIN"),
        ("Facture", "Kalati ya mutoa", "Kalaada i ntomb", "Wá’la tôk", "Kalate nzaña", "Paiement service", "Périphrase : Document indiquant le montant dû pour un service"),
        ("Banque", "Banka", "Bañga", "Bañga", "Banka", "Institution", "Institution financière agréée"),
        ("Banque en ligne", "Banka o mwendi", "Bañga i fôn", "Bañga o fôn", "Banka ya fôn", "Technologie", "Périphrase : Banque accessible via Internet ou téléphone mobile"),
        ("Mobile Money", "Mobile Money", "Mobile Money", "Mobile Money", "Mobile Money", "Moyen de paiement", "Terme commercial standard pour porte-monnaie électronique"),
        ("Opérateur", "Ebolo ya telefon", "Nsal u fôn", "Bə̀ fôn", "Ésaé telefon", "Télécoms", "Périphrase : Entreprise de télécommunication gérant le réseau — INCERTAIN"),
        ("Devise / Monnaie", "Moni", "Moni", "Kəpka'", "Moni", "Économie", "Moyen légal de paiement"),
        ("Franc CFA", "Franc CFA", "Franc CFA", "Franc CFA", "Franc CFA", "Monnaie officielle", "Devise officielle en vigueur dans la zone CEMAC"),
        ("Erreur", "Bwemba", "Mbebi", "Kə̌ le", "Abé", "Système / Statut", "Dysfonctionnement ou rejet d'opération"),
        ("Échec", "Ebolo e si boli", "Nsal u mboñba bé", "Bə̀ la’", "Ésaé tege bo", "Statut transaction", "Périphrase : L'opération n'a pas pu aboutir"),
        ("Succès", "Bwam", "Loñge", "Bə̀ bo", "Mbamba", "Statut transaction", "Opération validée et exécutée sans anomalie")
    ]

    csv_gloss_path = os.path.join(base_dir, "catalogue", "glossaire.csv")
    with open(csv_gloss_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["terme_source", "langue", "terme_cible", "contexte", "statut", "notes"])
        for src, dua_t, bas_t, bbj_t, ewo_t, ctx, notes in glossary_terms:
            writer.writerow([src, "dua", dua_t, ctx, "machine_suggested", notes])
            writer.writerow([src, "bas", bas_t, ctx, "machine_suggested", notes])
            writer.writerow([src, "bbj", bbj_t, ctx, "machine_suggested", notes])
            writer.writerow([src, "ewo", ewo_t, ctx, "machine_suggested", notes])

    print(f"[OK] {csv_gloss_path} généré avec {len(glossary_terms)} termes × 4 langues = {len(glossary_terms)*4} lignes (statut machine_suggested).")

    # 4. Fiche de validation CSV pour le validateur humain (langue pilote Duálá)
    # Format requis : source,proposition,correction du validateur,OK/KO
    fiche_val_path = os.path.join(base_dir, "catalogue", "fiche_validation.csv")
    with open(fiche_val_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "proposition", "correction du validateur", "OK/KO"])
        for item in catalog_items:
            writer.writerow([
                item["source"],
                item["dua"],
                "",   # Colonne "correction du validateur" vide
                ""    # Colonne "OK/KO" vide
            ])

    print(f"[OK] {fiche_val_path} générée avec {len(catalog_items)} lignes pour relecture humaine.")

    # 5. Format JSON optimisé pour extension offline et API
    offline_catalog = {
        "metadata": {
            "version": "1.1.0",
            "date": "2026-11-14",
            "pilot_language": "dua",
            "supported_languages": ["dua", "bas", "bbj", "ewo"],
            "total_strings": len(catalog_items),
            "status": "machine_suggested"
        },
        "translations": {
            "dua": {},
            "bas": {}
        },
        "glossary": {}
    }

    for item in catalog_items:
        src = item["source"].strip()
        offline_catalog["translations"]["dua"][src] = {
            "target": item["dua"],
            "status": "machine_suggested",
            "key": item["cle"],
            "comment": item["comment_dua"]
        }
        offline_catalog["translations"]["bas"][src] = {
            "target": item["bas"],
            "status": "machine_suggested",
            "key": item["cle"],
            "comment": item["comment_bas"]
        }

    for src, dua_t, bas_t, bbj_t, ewo_t, ctx, notes in glossary_terms:
        offline_catalog["glossary"][src.strip()] = {
            "dua": dua_t,
            "bas": bas_t,
            "bbj": bbj_t,
            "ewo": ewo_t,
            "status": "machine_suggested",
            "notes": notes
        }

    # Inclusion de l'index bilingue EN->FR si disponible
    en_index_path = os.path.join(base_dir, "data", "en_to_fr_index.json")
    if os.path.exists(en_index_path):
        with open(en_index_path, "r", encoding="utf-8") as f:
            en_data = json.load(f)
            offline_catalog["en_index"] = en_data.get("en_to_fr", en_data)

    json_path = os.path.join(base_dir, "catalogue", "translations_offline.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(offline_catalog, f, ensure_ascii=False, indent=2)
    print(f"[OK] {json_path} généré.")

    ext_json_path = os.path.join(base_dir, "extension", "offline_catalog.json")
    with open(ext_json_path, "w", encoding="utf-8") as f:
        json.dump(offline_catalog, f, ensure_ascii=False, indent=2)
    print(f"[OK] {ext_json_path} généré pour l'extension (catalogue unique).")

if __name__ == "__main__":
    build_pilot_catalog()
