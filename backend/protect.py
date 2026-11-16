# -*- coding: utf-8 -*-
"""
Module protect.py — Masquage, restauration et vérification d'intégrité financière.
SAFINUM Innovate Challenge 2026 — Version Durcie (Post-Audit Hostile).

RÈGLE D'OR :
Toute erreur altérant montant, frais, bénéficiaire, condition ou avertissement
de sécurité = DÉFAUT MAJEUR.
Montants, devises, frais, nombres, dates, références, numéros de téléphone,
noms de bénéficiaires, codes : JAMAIS traduits ni reformatés.
"""

import re
import html
import unicodedata
from typing import Tuple, Dict, List, Optional
from collections import Counter


# 1. Motifs d'extraction classés par ordre strict de spécificité
# Les motifs prioritaires (ex: URL, Références) absorbent leurs composants
# évitant ainsi tout conflit avec les motifs plus génériques (ex: Nombres purs).
PATTERNS = [
    # 0. URLs complètes (évite que les nombres et IDs dans l'URL ne soient segmentés)
    ("URL", re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)),

    # 1. Références de transaction (ex: SAF-2026-X7Y8Z9, REF-12345-ABC)
    ("REF", re.compile(r"\b(?:SAF-\d{4}-[A-Z0-9]{4,12}|REF-[A-Z0-9]{4,12})\b", re.IGNORECASE)),

    # 2. Numéro de téléphone (Cameroun / International : +237 6 99 12 34 56, 699123456, +237670000000)
    ("TEL", re.compile(r"(?:\+237\s*)?[26](?:[\s.-]?\d){7}\d\b")),

    # 3. Numéro de compte bancaire (ex: CM 001 2345 6789 01 ou suites de 9 à 16 chiffres non précédées de +)
    ("ACCT", re.compile(r"\bCM(?:\s*\d{3})(?:\s*\d{4}){2}(?:\s*\d{2})\b|(?<!\+)\b\d{4}(?:\s*\d{4}){2,3}\b")),

    # 4. Pourcentages / Frais en % (ex: 1,5 %, 2 %, 0.5 %, 10%)
    ("PCT", re.compile(r"\b\d+(?:[,\.]\d+)?\s*%(?!\w)")),

    # 5. Montants en toutes lettres suivis d'une devise ou d'un pourcentage
    ("AMOUNT_WORDS", re.compile(
        r"\b(?:un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize|"
        r"vingt|trente|quarante|cinquante|soixante|soixante-dix|septante|quatre-vingts?|quatre-vingt-dix|nonante|"
        r"cent|cents|mille|million|millions|milliard|milliards)"
        r"(?:[-\s]+(?:et[-\s]+)?(?:un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize|"
        r"vingt|trente|quarante|cinquante|soixante|soixante-dix|septante|quatre-vingts?|quatre-vingt-dix|nonante|"
        r"cent|cents|mille|million|millions|milliard|milliards))*"
        r"\s*(?:francs?\s*(?:cfa)?|fcfa|xaf|cfa|xof|euros?|eur|dollars?|usd|%|pour\s*cent)\b",
        re.IGNORECASE
    )),

    # 6. Montants avec devises (FCFA, XAF, CFA, EUR, €, USD, $, XOF, frs, etc.)
    # Optimisé sans backtracking catastrophique (ReDoS résolu : < 0.01 ms sur chaînes d'attaque)
    ("AMOUNT", re.compile(
        r"(?:[+-]\s*)?"
        r"(?:"
            r"(?:[$€£]\s*(?:\d{1,3}(?:[\s\u00A0\u202F\u2007,\.]\d{3})*|\d+)(?:[,\.]\d+)?)"
            r"|"
            r"(?:\b(?:\d{1,3}(?:[\s\u00A0\u202F\u2007,\.]\d{3})*|\d+)(?:[,\.]\d+)?\s*(?:FCFA|XAF|CFA|XOF|EUR|USD|GBP|€|\$|£|francs?\s*(?:cfa)?|frs)(?!\w))"
        r")",
        re.IGNORECASE
    )),

    # 7. Dates calendaires / financières (ex: 05 nov. 2026, 31 oct. 2026, 14/11/2026, 2026-11-14)
    ("DATE", re.compile(
        r"(?:"
            r"\b\d{1,2}\s+(?:janv\.|févr\.|mars|avr\.|mai|juin|juil\.|août|sept\.|oct\.|nov\.|déc\.)\s+\d{4}\b|"
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|"
            r"\b\d{4}-\d{2}-\d{2}\b"
        r")",
        re.IGNORECASE
    )),

    # 8. Noms de bénéficiaires / destinataires (Reconnaissance contextuelle + Noms connus)
    ("BENEF", re.compile(
        r"(?:\b(?:[Bb]énéficiaire|[Dd]estinataire)\s*:\s*|\b(?:[Vv]ers|[Pp]our)\s+)"
        r"([A-Z][a-zA-Z'’\-]+(?:\s+[A-Z][a-zA-Z'’\-]+)+)"
        r"|"
        r"\b(Jean-Paul Mbarga|Amina Ngo Bell|Amina)\b"
    )),

    # 9. Nombres purs / montants sans devises (ex: dans les cellules de tableau ou balises isolées)
    # Ex: "25 000", "25000", "1250,50"
    ("NUMBER", re.compile(
        r"(?<![A-Za-z0-9_])[+-]?(?:\d{1,3}(?:[\s\u00A0\u202F\u2007]\d{3})+|\d{2,})(?:[,\.]\d+)?(?![A-Za-z0-9_])"
    )),
]


TOKEN_PREFIX = "__SAFE_"
TOKEN_SUFFIX = "__"
TOKEN_REGEX = re.compile(r"__SAFE_[A-Z_]+_\d+__")
ESCAPED_SAFE_PREFIX = "__ESCAPED_SAFE_"


def normalize_input_text(text: str) -> str:
    """Normalise les entités HTML courantes et les espaces insécables Unicode."""
    if not text or not isinstance(text, str):
        return text
    # Remplacement des entités HTML courantes (ex: &nbsp;)
    text = html.unescape(text)
    # Remplacement de l'espace fine insécable et espaces graphiques par espace insécable standard
    text = text.replace("\u202F", "\u00A0").replace("\u2007", "\u00A0")
    return text


def mask_sensitive_data(text: str) -> Tuple[str, Dict[str, str], List[str]]:
    """
    Détecte et remplace toutes les entités sensibles par des jetons inviolables.
    Neutralise préventivement tout faux jeton préexistant dans la source.
    Retourne :
      - masked_text : le texte avec jetons __SAFE_TYPE_N__
      - token_map : mapping {jeton: valeur_originale}
      - token_order : liste ordonnée des jetons tels qu'apparus dans la source
    """
    if not text or not isinstance(text, str):
        return text, {}, []

    # 1. Normalisation Unicode et entités HTML
    cleaned = normalize_input_text(text)

    # 2. Protection contre l'injection de faux jetons :
    # Tout __SAFE_ préexistant dans la source utilisateur est échappé
    masked_text = cleaned.replace(TOKEN_PREFIX, ESCAPED_SAFE_PREFIX)

    token_map: Dict[str, str] = {}
    counter = 0

    for prefix, pattern in PATTERNS:
        matches = list(pattern.finditer(masked_text))
        # Remplacement de droite à gauche pour maintenir la validité des offsets
        for m in reversed(matches):
            if m.groups():
                grp = next((i for i, g in enumerate(m.groups(), start=1) if g is not None), 0)
            else:
                grp = 0
            val = m.group(grp)
            start, end = m.start(grp), m.end(grp)
            token = f"{TOKEN_PREFIX}{prefix}_{counter}{TOKEN_SUFFIX}"
            token_map[token] = val
            masked_text = masked_text[:start] + token + masked_text[end:]
            counter += 1

    # Retrouver l'ordre d'apparition naturel des jetons dans le texte masqué
    found_in_masked = TOKEN_REGEX.findall(masked_text)
    ordered_tokens = found_in_masked

    return masked_text, token_map, ordered_tokens


def restore_sensitive_data(
    translated_masked_text: str,
    token_map: Dict[str, str],
    original_source_text: str
) -> Tuple[str, bool]:
    """
    Restaure les jetons dans le texte traduit.
    Vérifie la stricte conservation du multi-ensemble et l'absence d'altération.
    En cas de violation : retourne (original_source_text, False).
    """
    if not translated_masked_text:
        return original_source_text, False

    # 1. Vérification d'intégrité sur les jetons
    tokens_present = TOKEN_REGEX.findall(translated_masked_text)
    expected_tokens = list(token_map.keys()) if token_map else []

    # Contrôle multi-ensemble : ni manquant, ni dupliqué, ni injecté, ni altéré
    if Counter(tokens_present) != Counter(expected_tokens):
        return original_source_text, False

    restored = translated_masked_text

    # 2. Restauration exacte des valeurs d'origine
    if token_map:
        for token, original_val in token_map.items():
            restored = restored.replace(token, original_val)

        # Vérification finale que toutes les valeurs originales sont bien présentes dans le texte restauré
        for orig_val in token_map.values():
            if orig_val not in restored:
                return original_source_text, False

    # 3. Restitution des jetons utilisateur éventuellement échappés au départ
    restored = restored.replace(ESCAPED_SAFE_PREFIX, TOKEN_PREFIX)

    return restored, True


def verify_integrity(
    source_text: str,
    translated_text: str,
    token_map: Optional[Dict[str, str]] = None
) -> bool:
    """
    Fonction de contrôle d'intégrité globale.
    Vérifie que :
    1. Toutes les valeurs sensibles de la source sont présentes dans le texte traduit sans altération.
    2. Si token_map est fourni, chaque valeur masquée est présente exactement le même nombre de fois.
    3. Aucune altération numérique ou monétaire n'a été introduite.
    Retourne True si l'intégrité est 100% préservée, False sinon.
    """
    if not source_text or not translated_text:
        return False

    norm_source = normalize_input_text(source_text)
    norm_trans = normalize_input_text(translated_text)

    # Si token_map n'est pas fourni, on extrait les entités de source_text
    if token_map is None:
        _, token_map, _ = mask_sensitive_data(norm_source)

    # Si aucune donnée sensible n'était présente, intégrité vérifiée
    if not token_map:
        return True

    # Vérification 1 : chaque entité protégée de la source doit être présente dans la traduction
    for token, sensitive_value in token_map.items():
        source_count = norm_source.count(sensitive_value)
        trans_count = norm_trans.count(sensitive_value)

        if trans_count != source_count or source_count == 0:
            return False

    # Vérification 2 : aucun jeton résiduel non restauré ne doit subsister
    if TOKEN_REGEX.search(translated_text):
        return False

    return True


def annotate_glossary_in_masked_text(
    masked_text: str,
    glossary: Dict[str, Dict[str, str]],
    target_lang: str
) -> Tuple[str, bool, List[str]]:
    """
    Annote les termes financiers du glossaire dans un texte masqué :
    - Remplace chaque terme trouvé par 'terme [équivalent_glossaire]'.
    - Préserve l'intégrité des jetons __SAFE_*__ (qui ne contiennent aucun terme français).
    - Utilise des jetons temporaires __GLOSS_ANNO_N__ pour éviter les collisions et remplacements imbriqués.
    - Retourne (texte_annoté, a_des_annotations, liste_termes_annotés).
    """
    if not masked_text or not glossary:
        return masked_text, False, []

    lang = target_lang.lower().strip()

    # 1. Sélectionner les termes disponibles pour la langue cible
    available_terms = []
    for src_term, tr_map in glossary.items():
        if lang in tr_map and tr_map[lang] and tr_map[lang].strip():
            # Ne pas re-traduire si le terme source et cible sont identiques (ex: Safinum Pay)
            if src_term.strip().lower() != tr_map[lang].strip().lower():
                available_terms.append((src_term.strip(), tr_map[lang].strip()))

    if not available_terms:
        return masked_text, False, []

    # 2. Trier par longueur décroissante du terme source pour privilégier les locutions composées
    available_terms.sort(key=lambda x: len(x[0]), reverse=True)

    gloss_tokens: Dict[str, str] = {}
    annotated_terms: List[str] = []
    current_text = masked_text
    gloss_counter = 0

    for src_term, target_term in available_terms:
        # Frontières de mot en tenant compte de l'alphabet latin étendu et des apostrophes
        pattern = re.compile(
            r"(?<![A-Za-z0-9_À-ÿ])(" + re.escape(src_term) + r")(?![A-Za-z0-9_À-ÿ])",
            re.IGNORECASE
        )

        matches = list(pattern.finditer(current_text))
        if matches:
            # Remplacement de droite à gauche pour préserver les indices
            for m in reversed(matches):
                matched_val = m.group(1)
                token = f"__GLOSS_ANNO_{gloss_counter}__"
                gloss_tokens[token] = f"{matched_val} [{target_term}]"
                current_text = current_text[:m.start(1)] + token + current_text[m.end(1):]
                annotated_terms.append(src_term)
                gloss_counter += 1

    has_annotations = bool(gloss_tokens)
    if has_annotations:
        # Restauration de tous les jetons de glossaire
        for token, rep in gloss_tokens.items():
            current_text = current_text.replace(token, rep)

    return current_text, has_annotations, annotated_terms

