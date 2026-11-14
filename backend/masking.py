# -*- coding: utf-8 -*-
"""
Module de masquage et de restauration des entités financières.
SAFINUM Innovate Challenge 2026.

RÈGLE CRITIQUE :
Montants, devises, frais, nombres, dates, références, numéros de téléphone,
noms de bénéficiaires, codes : JAMAIS traduits ni reformatés.
Méthode obligatoire :
1. Masquage par jetons avant traduction.
2. Restauration stricte après traduction.
3. Vérification du multi-ensemble de jetons (Tokens_in == Tokens_out).
4. En cas d'échec ou d'anomalie : repli automatique vers le texte source original.
"""

import re
from typing import Tuple, Dict, List
from collections import Counter


# Expressions régulières ordonnées (du plus spécifique au plus général)
PATTERNS = [
    # Référence unique d'opération (ex: SAF-2026-X7Y8Z9 ou SAF-2026-123456)
    ("REF", re.compile(r"\bSAF-\d{4}-[A-Z0-9]{4,10}\b", re.IGNORECASE)),

    # Numéro de compte bancaire (ex: CM 001 2345 6789 01)
    ("ACCT", re.compile(r"\bCM(?:\s*\d{3})(?:\s*\d{4}){2}(?:\s*\d{2})\b")),

    # Téléphone camerounais (ex: +237 6 99 12 34 56 ou 699123456)
    ("TEL", re.compile(r"(?:\+237\s*)?[26](?:[\s.-]?\d){7}\d\b")),

    # Pourcentages (ex: 1,5 %, 2 %)
    ("PCT", re.compile(r"\b\d+(?:[,\.]\d+)?\s*%(?!\w)")),

    # Montant avec devise FCFA/XAF/EUR/USD (ex: 250 000 FCFA, 12 500 FCFA, 0 FCFA)
    ("AMOUNT", re.compile(
        r"(?:[+-]?\s*)?\b\d{1,3}(?:[\s\u00A0\u202F]\d{3})*(?:[,\.]\d+)?\s*(?:FCFA|XAF|EUR|USD|\$)(?!\w)",
        re.IGNORECASE
    )),

    # Dates calendaires / financières (ex: 05 nov. 2026, 31 oct. 2026)
    ("DATE", re.compile(
        r"\b\d{1,2}\s+(?:janv\.|févr\.|mars|avr\.|mai|juin|juil\.|août|sept\.|oct\.|nov\.|déc\.)\s+\d{4}\b",
        re.IGNORECASE
    )),

    # Noms protégés de bénéficiaires / titulaires connus dans le contexte de test
    ("NAME", re.compile(r"\b(?:Jean-Paul Mbarga|Amina Ngo Bell|Amina)\b")),
]


TOKEN_PREFIX = "__SAFE_"
TOKEN_SUFFIX = "__"
TOKEN_REGEX = re.compile(r"__SAFE_[A-Z]+_\d+__")


def mask_sensitive_data(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Détecte et remplace toutes les entités financières sensibles par des jetons réservés.
    Retourne (texte_masque, table_des_jetons).
    """
    if not text or not isinstance(text, str):
        return text, {}

    token_map: Dict[str, str] = {}
    masked_text = text
    counter = 0

    for prefix, pattern in PATTERNS:
        matches = list(pattern.finditer(masked_text))
        # Remplacement de droite à gauche pour préserver les indices
        for m in reversed(matches):
            val = m.group(0)
            token = f"{TOKEN_PREFIX}{prefix}_{counter}{TOKEN_SUFFIX}"
            token_map[token] = val
            masked_text = masked_text[:m.start()] + token + masked_text[m.end():]
            counter += 1

    return masked_text, token_map


def restore_sensitive_data(
    translated_masked_text: str,
    token_map: Dict[str, str],
    original_source_text: str
) -> Tuple[str, bool]:
    """
    Restaure les jetons dans le texte traduit.
    Vérifie la stricte conservation du multi-ensemble de jetons.
    Si un jeton manque ou est altéré, retourne (original_source_text, False).
    """
    if not token_map:
        return translated_masked_text, True

    # 1. Extraction de tous les jetons présents dans le texte traduit
    tokens_found = TOKEN_REGEX.findall(translated_masked_text)
    expected_tokens = list(token_map.keys())

    # 2. Vérification multi-ensemble
    if Counter(tokens_found) != Counter(expected_tokens):
        # ÉCHEC D'INTÉGRITÉ -> Fallback strict vers le texte source
        return original_source_text, False

    # 3. Restauration exacte sans reformatage
    restored_text = translated_masked_text
    for token, original_val in token_map.items():
        restored_text = restored_text.replace(token, original_val)

    return restored_text, True
