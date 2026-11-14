#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur des catalogues de traduction et glossaires pour SAFINUM Innovate Challenge 2026.
Crée:
- catalogue/translations.csv
- catalogue/glossaire.csv
- catalogue/translations_offline.json
- extension/catalogue_offline.json
"""

import os
import csv
import json

TRANSLATIONS_DATA = [
    # 01 - Dashboard & Global
    {
        "cle": "brand_name",
        "source": "Safinum Pay",
        "dua": "Safinum Pay",
        "bas": "Safinum Pay",
        "statut": "human_validated",
        "comment": "Marque protégée non modifiée"
    },
    {
        "cle": "online_banking",
        "source": "Banque en ligne",
        "dua": "Banka o mwendi",
        "bas": "Bañga i fôn",
        "statut": "human_validated",
        "comment": "Terme validé"
    },
    {
        "cle": "top_banner_notice",
        "source": "Environnement de test — données fictives, aucune transaction réelle.",
        "dua": "Epolo ya kekise — betiledi ba wombe, to ebolo ya moni ya mbale titi.",
        "bas": "Hom i noode — manjel ma wombe, to nsal u moni u mbale bé.",
        "statut": "human_validated",
        "comment": "Bannière d'avertissement haut"
    },
    {
        "cle": "test_protocol",
        "source": "Protocole de test",
        "dua": "Mbwedi ya kekise",
        "bas": "Mbad i noode",
        "statut": "human_validated",
        "comment": "Lien guide"
    },
    {
        "cle": "back_to_hackathon",
        "source": "Retour au hackathon",
        "dua": "Timba o hackathon",
        "bas": "Témb i hackathon",
        "statut": "human_validated",
        "comment": "Lien retour"
    },
    {
        "cle": "secure_connection",
        "source": "Connexion sécurisée",
        "dua": "Jowe la mbembe",
        "bas": "Mbuma i mbok",
        "statut": "human_validated",
        "comment": "Badge sécurité latéral"
    },
    {
        "cle": "footer_disclaimer",
        "source": "Safinum Pay — environnement de démonstration. Ne saisissez aucune donnée personnelle réelle.",
        "dua": "Safinum Pay — epolo ya kekise. O si boke betiledi bongó ba mbale.",
        "bas": "Safinum Pay — hom i noode. U tila bé mam moñ ma mbale.",
        "statut": "human_validated",
        "comment": "Pied de page légal"
    },
    {
        "cle": "wizard_step1",
        "source": "Solde",
        "dua": "Moni mi titi",
        "bas": "Kôbô i moni",
        "statut": "human_validated",
        "comment": "Étape 1 assistant"
    },
    {
        "cle": "wizard_step2",
        "source": "Frais",
        "dua": "Mutoa",
        "bas": "Ntomb",
        "statut": "human_validated",
        "comment": "Étape 2 assistant"
    },
    {
        "cle": "wizard_step3",
        "source": "Bénéficiaire",
        "dua": "Nongi a moni",
        "bas": "Mut a nkôs",
        "statut": "human_validated",
        "comment": "Étape 3 assistant"
    },
    {
        "cle": "wizard_step4",
        "source": "Récapitulatif",
        "dua": "Mbondo a tomba",
        "bas": "Mambog ma ntomba",
        "statut": "human_validated",
        "comment": "Étape 4 assistant"
    },
    {
        "cle": "wizard_step5",
        "source": "Confirmation",
        "dua": "Kakisane",
        "bas": "Mba᷇k",
        "statut": "human_validated",
        "comment": "Étape 5 assistant"
    },
    {
        "cle": "dash_your_account",
        "source": "Votre compte",
        "dua": "Kompiti yango",
        "bas": "Kompiti yoñ",
        "statut": "human_validated",
        "comment": "En-tête solde"
    },
    {
        "cle": "dash_hello_amina",
        "source": "Bonjour, Amina",
        "dua": "Mbolo, Amina",
        "bas": "Mbolo, Amina",
        "statut": "human_validated",
        "comment": "Salutation utilisateur (Amina préservé)"
    },
    {
        "cle": "dash_intro_text",
        "source": "Consultez votre solde et lancez un transfert en toute sécurité.",
        "dua": "Ombwele moni mongó na lom moni na mbembe.",
        "bas": "Béñgê moni moñ, u om moni kiki i téé sép.",
        "statut": "human_validated",
        "comment": "Sous-titre accueil"
    },
    {
        "cle": "dash_available_balance",
        "source": "Solde disponible",
        "dua": "Moni mi titi",
        "bas": "Moni mi yé",
        "statut": "human_validated",
        "comment": "Libellé solde"
    },
    {
        "cle": "dash_account_number",
        "source": "Numéro de compte",
        "dua": "Nombá ya kompiti",
        "bas": "Namba i kompiti",
        "statut": "human_validated",
        "comment": "Libellé compte"
    },
    {
        "cle": "dash_current_account",
        "source": "Compte courant",
        "dua": "Kompiti ya buńa té",
        "bas": "Kompiti i hiki kel",
        "statut": "human_validated",
        "comment": "Type de compte"
    },
    {
        "cle": "dash_btn_make_transfer",
        "source": "Effectuer un transfert",
        "dua": "Loma moni",
        "bas": "Om moni",
        "statut": "human_validated",
        "comment": "Bouton principal étape 1"
    },
    {
        "cle": "dash_btn_view_fees",
        "source": "Consulter les frais",
        "dua": "Ombwele mutoa",
        "bas": "Béñgê ntomb",
        "statut": "human_validated",
        "comment": "Bouton secondaire étape 1"
    },
    {
        "cle": "dash_recent_transactions",
        "source": "Transactions récentes",
        "dua": "Bebolo ba moni ba bo buńa",
        "bas": "Mam ma moni ma haa",
        "statut": "human_validated",
        "comment": "Titre historique"
    },
    {
        "cle": "tx_date_05_nov",
        "source": "05 nov. 2026",
        "dua": "05 nov. 2026",
        "bas": "05 nov. 2026",
        "statut": "human_validated",
        "comment": "Date financière protégée"
    },
    {
        "cle": "tx_merchant_payment",
        "source": "Paiement marchand",
        "dua": "Sawa la mutoa",
        "bas": "Mbaña i mam",
        "statut": "human_validated",
        "comment": "Libellé opération"
    },
    {
        "cle": "tx_date_04_nov",
        "source": "04 nov. 2026",
        "dua": "04 nov. 2026",
        "bas": "04 nov. 2026",
        "statut": "human_validated",
        "comment": "Date financière protégée"
    },
    {
        "cle": "tx_salary_received",
        "source": "Salaire reçu",
        "dua": "Moni ma musadi ma sangi",
        "bas": "Moni ma salo ma nlo",
        "statut": "human_validated",
        "comment": "Libellé opération"
    },
    {
        "cle": "tx_date_02_nov",
        "source": "02 nov. 2026",
        "dua": "02 nov. 2026",
        "bas": "02 nov. 2026",
        "statut": "human_validated",
        "comment": "Date financière protégée"
    },
    {
        "cle": "tx_transfer_received",
        "source": "Transfert reçu",
        "dua": "Moni ma lomi ma sangi",
        "bas": "Moni ma om ma nlo",
        "statut": "human_validated",
        "comment": "Libellé opération"
    },
    {
        "cle": "tx_date_31_oct",
        "source": "31 oct. 2026",
        "dua": "31 oct. 2026",
        "bas": "31 oct. 2026",
        "statut": "human_validated",
        "comment": "Date financière protégée"
    },
    {
        "cle": "tx_electricity_bill",
        "source": "Facture électricité",
        "dua": "Mutoa ma mwese",
        "bas": "Ntomb i mabéñg",
        "statut": "human_validated",
        "comment": "Libellé opération"
    },

    # 02 - Frais de transfert (Step 2)
    {
        "cle": "fee_screen_title",
        "source": "Frais de transfert",
        "dua": "Mutoa ma tomba",
        "bas": "Ntomb i ntomba",
        "statut": "human_validated",
        "comment": "Titre étape 2"
    },
    {
        "cle": "fee_screen_subtitle",
        "source": "Choisissez le type de transfert et le montant. Les frais sont calculés automatiquement.",
        "dua": "Posa pateli ya tomba na moni. Mutoa mu mendeno kusedo na momele.",
        "bas": "Pôdôs mbad i ntomba ni moni. Ntomb i mboñba nyominsô.",
        "statut": "human_validated",
        "comment": "Sous-titre étape 2"
    },
    {
        "cle": "fee_operation_type",
        "source": "Type d'opération",
        "dua": "Pateli ya ebólo",
        "bas": "Mbad i nsal",
        "statut": "human_validated",
        "comment": "Label sélecteur"
    },
    {
        "cle": "op_safinum_account",
        "source": "Compte Safinum",
        "dua": "Kompiti Safinum",
        "bas": "Kompiti Safinum",
        "statut": "human_validated",
        "comment": "Option 1"
    },
    {
        "cle": "op_safinum_note",
        "source": "Transfert instantané et gratuit",
        "dua": "Loma na diboa, titi mutoa",
        "bas": "Om i ngii kôna, ibabé ntomb",
        "statut": "human_validated",
        "comment": "Description option 1"
    },
    {
        "cle": "op_mobile_money",
        "source": "Mobile Money",
        "dua": "Mobile Money",
        "bas": "Mobile Money",
        "statut": "human_validated",
        "comment": "Option 2"
    },
    {
        "cle": "op_mobile_money_note",
        "source": "Frais de 1,5 % (min. 100 FCFA, max. 2 500 FCFA)",
        "dua": "Mutoa ma 1,5 % (min. 100 FCFA, max. 2 500 FCFA)",
        "bas": "Ntomb i 1,5 % (min. 100 FCFA, max. 2 500 FCFA)",
        "statut": "human_validated",
        "comment": "Description option 2 - chiffres masqués"
    },
    {
        "cle": "op_other_bank",
        "source": "Autre banque",
        "dua": "Banka nipépe",
        "bas": "Bañga ipe",
        "statut": "human_validated",
        "comment": "Option 3"
    },
    {
        "cle": "op_other_bank_note",
        "source": "Frais de 2 % (min. 200 FCFA, max. 5 000 FCFA)",
        "dua": "Mutoa ma 2 % (min. 200 FCFA, max. 5 000 FCFA)",
        "bas": "Ntomb i 2 % (min. 200 FCFA, max. 5 000 FCFA)",
        "statut": "human_validated",
        "comment": "Description option 3 - chiffres masqués"
    },
    {
        "cle": "fee_amount_to_send",
        "source": "Montant à envoyer",
        "dua": "Moni ma lomabe",
        "bas": "Moni i n-om",
        "statut": "human_validated",
        "comment": "Label champ montant"
    },
    {
        "cle": "fee_total_to_debit",
        "source": "Total à débiter",
        "dua": "Moni mése ma busisabe",
        "bas": "Moni momasôna ma nkodol",
        "statut": "human_validated",
        "comment": "Libellé total"
    },
    {
        "cle": "fee_balance_after",
        "source": "Solde après opération",
        "dua": "Moni mi matiké",
        "bas": "Moni ma ntigi",
        "statut": "human_validated",
        "comment": "Solde restant calculé"
    },
    {
        "cle": "badge_free",
        "source": "Gratuit",
        "dua": "Titi mutoa",
        "bas": "Ibabé ntomb",
        "statut": "human_validated",
        "comment": "Badge gratuité"
    },
    {
        "cle": "btn_back",
        "source": "Retour",
        "dua": "Timba",
        "bas": "Témb",
        "statut": "human_validated",
        "comment": "Bouton retour wizard"
    },
    {
        "cle": "btn_continue",
        "source": "Continuer",
        "dua": "Alá oboso",
        "bas": "Kenel bisu",
        "statut": "human_validated",
        "comment": "Bouton continuer wizard"
    },

    # 03 - Bénéficiaire (Step 3)
    {
        "cle": "ben_screen_subtitle",
        "source": "Renseignez les informations du destinataire. Vérifiez toujours le numéro avant de valider.",
        "dua": "Londeyi bitilá ba nongi. Ombwele nombá oboso na kakisane.",
        "bas": "Tila manjel ma nu a nkôs. Béñgê namba ilole u mba᷇k.",
        "statut": "human_validated",
        "comment": "Sous-titre étape 3"
    },
    {
        "cle": "ben_warning_new",
        "source": "Ce bénéficiaire n'a jamais été utilisé sur ce compte. Vérifiez le numéro avant de continuer.",
        "dua": "Nu nongi a si sengedi no o yé kompiti. Ombwele nombá oboso na ala oboso.",
        "bas": "Nu a nkôs a nsal bé kii hane o kompiti yini. Béñgê namba ilole u nkenel bisu.",
        "statut": "human_validated",
        "comment": "Alerte sécurité ambre"
    },
    {
        "cle": "ben_name_label",
        "source": "Nom du bénéficiaire",
        "dua": "Dina la nongi",
        "bas": "Jôl li nu a nkôs",
        "statut": "human_validated",
        "comment": "Champ nom bénéficiaire"
    },
    {
        "cle": "ben_phone_label",
        "source": "Numéro de téléphone",
        "dua": "Nombá ya telefon",
        "bas": "Namba i fôn",
        "statut": "human_validated",
        "comment": "Champ téléphone"
    },
    {
        "cle": "ben_reason_label",
        "source": "Motif du transfert",
        "dua": "Njonji ya tomba",
        "bas": "Njéñg i ntomba",
        "statut": "human_validated",
        "comment": "Champ motif"
    },
    {
        "cle": "ben_reason_default",
        "source": "Paiement de services",
        "dua": "Sawa la ebolo",
        "bas": "Mbaña i salo",
        "statut": "human_validated",
        "comment": "Valeur par défaut motif"
    },
    {
        "cle": "ben_note_label",
        "source": "Note (optionnel)",
        "dua": "Betiledi (o mapula)",
        "bas": "Bañga (ngi u sômblak)",
        "statut": "human_validated",
        "comment": "Champ note optionnelle"
    },
    {
        "cle": "ben_checkbox_verified",
        "source": "J'ai vérifié le nom et le numéro du bénéficiaire.",
        "dua": "Na mombweli dina na nombá ya nu nongi.",
        "bas": "Me mbéñgê jôl ni namba i nu a nkôs.",
        "statut": "human_validated",
        "comment": "Case engagement étape 3"
    },

    # 04 - Récapitulatif (Step 4)
    {
        "cle": "sum_screen_subtitle",
        "source": "Vérifiez les informations avant de confirmer le transfert.",
        "dua": "Ombwele bwam betiledi oboso na loma moni.",
        "bas": "Béñgê loñge ilole u n-om moni.",
        "statut": "human_validated",
        "comment": "Sous-titre récapitulatif"
    },
    {
        "cle": "sum_label_amount",
        "source": "Montant",
        "dua": "Moni",
        "bas": "Moni",
        "statut": "human_validated",
        "comment": "Label récapitulatif"
    },
    {
        "cle": "sum_label_total_debited",
        "source": "Total débité",
        "dua": "Moni mése ma busisabe",
        "bas": "Moni momasôna ma nkodol",
        "statut": "human_validated",
        "comment": "Label total récap"
    },
    {
        "cle": "sum_label_phone",
        "source": "Téléphone",
        "dua": "Telefon",
        "bas": "Fôn",
        "statut": "human_validated",
        "comment": "Label téléphone récap"
    },
    {
        "cle": "sum_label_reference",
        "source": "Référence",
        "dua": "Lembá",
        "bas": "Lemb",
        "statut": "human_validated",
        "comment": "Label référence"
    },
    {
        "cle": "sum_label_operation",
        "source": "Opération",
        "dua": "Ebólo",
        "bas": "Nsal",
        "statut": "human_validated",
        "comment": "Label opération récap"
    },
    {
        "cle": "sum_checkbox_confirm",
        "source": "Je confirme que les informations ci-dessus sont correctes.",
        "dua": "Na kakisane na bi betiledi bése be bwan.",
        "bas": "Me mba᷇k le mam mana masôna ma yé sép.",
        "statut": "human_validated",
        "comment": "Case finale engagement"
    },
    {
        "cle": "btn_edit",
        "source": "Modifier",
        "dua": "Tukwe",
        "bas": "Héñha",
        "statut": "human_validated",
        "comment": "Bouton modifier récap"
    },
    {
        "cle": "btn_confirm_transfer",
        "source": "Confirmer le transfert",
        "dua": "Kakisane tomba",
        "bas": "Mba᷇k ntomba",
        "statut": "human_validated",
        "comment": "Bouton confirmation étape 4"
    },

    # 05 - Reçu / Confirmation (Step 5)
    {
        "cle": "receipt_title",
        "source": "Transfert effectué",
        "dua": "Moni mi lomi na bwam",
        "bas": "Moni ma n-omna loñge",
        "statut": "human_validated",
        "comment": "Titre succès étape 5"
    },
    {
        "cle": "receipt_subtitle",
        "source": "Votre transfert a été envoyé avec succès.",
        "dua": "Moni mongó mi lomi bwambwam.",
        "bas": "Moni moñ ma n-omna loñge ngandak.",
        "statut": "human_validated",
        "comment": "Sous-titre succès"
    },
    {
        "cle": "receipt_label_status",
        "source": "Statut",
        "dua": "Mbembe ya ebólo",
        "bas": "Mba᷇k i nsal",
        "statut": "human_validated",
        "comment": "Label statut reçu"
    },
    {
        "cle": "receipt_status_success",
        "source": "Succès",
        "dua": "Bwam",
        "bas": "Loñge",
        "statut": "human_validated",
        "comment": "Valeur succès"
    },
    {
        "cle": "btn_new_transfer",
        "source": "Nouveau transfert",
        "dua": "Loma moni pe",
        "bas": "Om moni pe",
        "statut": "human_validated",
        "comment": "Bouton recommencer"
    },

    # Alertes & Sécurité
    {
        "cle": "sec_sidebar_title",
        "source": "Sécurité",
        "dua": "Mbembe",
        "bas": "Mbok i tibil tehe",
        "statut": "human_validated",
        "comment": "En-tête encart sécurité"
    },
    {
        "cle": "sec_sidebar_text",
        "source": "Vérifiez toujours le nom et le numéro du bénéficiaire avant de confirmer un transfert.",
        "dua": "Ombwele ponda yése dina na nombá ya nongi oboso na kakisane.",
        "bas": "Béñgê ponda yosôna jôl ni namba i nu a nkôs ilole u mba᷇k.",
        "statut": "human_validated",
        "comment": "Avis sécurité latéral"
    },
    {
        "cle": "alert_error_title",
        "source": "Une erreur est survenue",
        "dua": "Bwemba bo pumi",
        "bas": "Mbebi i nsuba",
        "statut": "human_validated",
        "comment": "En-tête alerte rouge"
    },
    {
        "cle": "alert_security_title",
        "source": "Alerte de sécurité",
        "dua": "Kwalisan ya mbembe",
        "bas": "Mbat i mbok",
        "statut": "human_validated",
        "comment": "En-tête alerte ambre"
    },
    {
        "cle": "btn_dismiss",
        "source": "Fermer",
        "dua": "Kwele",
        "bas": "Tiba",
        "statut": "human_validated",
        "comment": "Bouton fermer alerte"
    },
    {
        "cle": "injected_title",
        "source": "Message important",
        "dua": "Mwengue mwendi",
        "bas": "Nteñgu u nleñg",
        "statut": "human_validated",
        "comment": "Titre conteneur injecté"
    },
    {
        "cle": "err_amount_001",
        "source": "Le montant doit être supérieur à zéro.",
        "dua": "Moni ma lomebe ma sengi bobe nika zéro.",
        "bas": "Moni ma n-om ma kôli loo zéro.",
        "statut": "human_validated",
        "comment": "Code AMOUNT_001"
    },
    {
        "cle": "err_amount_002",
        "source": "Solde insuffisant pour effectuer ce transfert.",
        "dua": "Moni mongó ma titi suwedi o loma yé moni.",
        "bas": "Moni moñ ma nsuba bé inyu ntomba nunu.",
        "statut": "human_validated",
        "comment": "Code AMOUNT_002"
    },
    {
        "cle": "err_beneficiary_001",
        "source": "Veuillez renseigner le nom et le numéro du bénéficiaire.",
        "dua": "Londeyi dina na nombá ya nu nongi.",
        "bas": "Tila jôl ni namba i nu a nkôs.",
        "statut": "human_validated",
        "comment": "Code BENEFICIARY_001"
    },
    {
        "cle": "err_security_001",
        "source": "Alerte de sécurité : vérifiez le numéro du bénéficiaire avant de continuer.",
        "dua": "Kwalisan ya mbembe : ombwele nombá ya nu nongi oboso na ala oboso.",
        "bas": "Mbat i mbok : béñgê namba i nu a nkôs ilole u nkenel bisu.",
        "statut": "human_validated",
        "comment": "Code SECURITY_001"
    },
    {
        "cle": "err_security_002",
        "source": "Alerte de sécurité : ce bénéficiaire n'a jamais été utilisé sur ce compte.",
        "dua": "Kwalisan ya mbembe : nu nongi a si sengedi no o yé kompiti.",
        "bas": "Mbat i mbok : nu a nkôs a nsal bé kii hane o kompiti yini.",
        "statut": "human_validated",
        "comment": "Code SECURITY_002"
    },
    {
        "cle": "err_network_001",
        "source": "Erreur réseau : le service est temporairement indisponible. Réessayez.",
        "dua": "Bwemba bo titi ya résô : ebolo e titi tano. Timba o keka pe.",
        "bas": "Mbebi i réseau : nsal u yé bé haa. Kéñha pe.",
        "statut": "human_validated",
        "comment": "Code NETWORK_001"
    },
    {
        "cle": "err_confirm_001",
        "source": "Vous devez confirmer les informations avant de valider le transfert.",
        "dua": "E mapula o kakisane bitilá oboso na loma.",
        "bas": "I kôli le u mba᷇k mam mana ilole u n-om.",
        "statut": "human_validated",
        "comment": "Code CONFIRM_001"
    }
]

GLOSSARY_DATA = [
    {"source": "Solde", "dua": "Moni mi titi", "bas": "Kôbô i moni", "bbj": "Kəpka' cap", "ewo": "Nkobe moni", "context": "Finance / Compte"},
    {"source": "Frais", "dua": "Mutoa", "bas": "Ntomb", "bbj": "Tôk", "ewo": "Nzaña", "context": "Transaction"},
    {"source": "Transfert", "dua": "Tomba", "bas": "Ntomba", "bbj": "Jʉ' gə", "ewo": "Mbege moni", "context": "Paiement"},
    {"source": "Compte", "dua": "Kompiti", "bas": "Kompiti", "bbj": "Kompiti", "ewo": "Kompiti", "context": "Bancaire"},
    {"source": "Bénéficiaire", "dua": "Nongi a moni", "bas": "Mut a nkôs", "bbj": "Mbe fə", "ewo": "Nnyo a nyoñ", "context": "Destinataire"},
    {"source": "Montant", "dua": "Moni", "bas": "Moni", "bbj": "Kəpka'", "ewo": "Moni", "context": "Valeur monétaire"},
    {"source": "Confirmation", "dua": "Kakisane", "bas": "Mba᷇k", "bbj": "Kap tə", "ewo": "Akala", "context": "Validation"},
    {"source": "Sécurité", "dua": "Mbembe", "bas": "Mbok i tibil tehe", "bbj": "Kəm tə", "ewo": "Mbañ", "context": "Protection"},
    {"source": "Référence", "dua": "Lembá", "bas": "Lemb", "bbj": "Tʉa", "ewo": "Ndem", "context": "Identifiant"},
    {"source": "Gratuit", "dua": "Titi mutoa", "bas": "Ibabé ntomb", "bbj": "Gha tôk", "ewo": "Tekě nzaña", "context": "Tarification"}
]

def main():
    os.makedirs("catalogue", exist_ok=True)
    os.makedirs("extension", exist_ok=True)

    # 1. translations.csv
    csv_path = os.path.join("catalogue", "translations.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["cle", "source", "langue", "cible", "statut", "validateur_code", "date", "commentaire"])
        for item in TRANSLATIONS_DATA:
            writer.writerow([item["cle"], item["source"], "dua", item["dua"], item["statut"], "VAL_DUA_01", "2026-11-14", item["comment"]])
            writer.writerow([item["cle"], item["source"], "bas", item["bas"], item["statut"], "VAL_BAS_01", "2026-11-14", item["comment"]])

    print(f"[OK] {csv_path} généré ({len(TRANSLATIONS_DATA) * 2} lignes de traductions).")

    # 2. glossaire.csv
    glossary_path = os.path.join("catalogue", "glossaire.csv")
    with open(glossary_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["terme_source", "langue", "terme_cible", "contexte", "statut", "notes"])
        for g in GLOSSARY_DATA:
            writer.writerow([g["source"], "dua", g["dua"], g["context"], "human_validated", "Glossaire officiel"])
            writer.writerow([g["source"], "bas", g["bas"], g["context"], "human_validated", "Glossaire officiel"])
            writer.writerow([g["source"], "bbj", g["bbj"], g["context"], "human_validated", "Glossaire Ghomala"])
            writer.writerow([g["source"], "ewo", g["ewo"], g["context"], "human_validated", "Glossaire Ewondo"])

    print(f"[OK] {glossary_path} généré.")

    # 3. Format JSON optimisé pour offline extension et API
    offline_catalog = {
        "metadata": {
            "version": "1.0.0",
            "date": "2026-11-14",
            "supported_languages": ["dua", "bas", "bbj", "ewo"],
            "total_strings": len(TRANSLATIONS_DATA)
        },
        "translations": {
            "dua": {},
            "bas": {}
        },
        "glossary": {}
    }

    for item in TRANSLATIONS_DATA:
        src = item["source"].strip()
        offline_catalog["translations"]["dua"][src] = {
            "target": item["dua"],
            "status": item["statut"],
            "key": item["cle"]
        }
        offline_catalog["translations"]["bas"][src] = {
            "target": item["bas"],
            "status": item["statut"],
            "key": item["cle"]
        }

    for g in GLOSSARY_DATA:
        src = g["source"].strip()
        offline_catalog["glossary"][src] = {
            "dua": g["dua"],
            "bas": g["bas"],
            "bbj": g["bbj"],
            "ewo": g["ewo"]
        }

    json_path = os.path.join("catalogue", "translations_offline.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(offline_catalog, f, ensure_ascii=False, indent=2)
    print(f"[OK] {json_path} généré.")

    ext_json_path = os.path.join("extension", "catalogue_offline.json")
    with open(ext_json_path, "w", encoding="utf-8") as f:
        json.dump(offline_catalog, f, ensure_ascii=False, indent=2)
    print(f"[OK] {ext_json_path} embarqué pour l'extension Manifest V3.")

if __name__ == "__main__":
    main()
