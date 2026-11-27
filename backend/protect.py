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


# Motifs de détection des secrets (OTP, PIN, mots de passe)
SECRET_PATTERNS = [
    re.compile(r"\b(?:otp|one-time\s+password|one-time\s+passcode|one-time\s+code)\b", re.IGNORECASE),
    re.compile(r"\b(?:code\s+pin|pin)\s*[:=\s]+\d+", re.IGNORECASE),
    re.compile(r"\bvotre\s+code\s+pin\s+est\s+\d+", re.IGNORECASE),
    re.compile(r"\b(?:mot\s+de\s+passe\s+temporaire|temporary\s+password)\b", re.IGNORECASE),
    re.compile(r"\b(?:mot\s+de\s+passe|password)\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"\bcode\s+(?:de\s+)?(?:validation|confirmation|sécurité|securite|vérification|verification|secret)\s*(?:est|:)\s*\d+", re.IGNORECASE),
]


def is_secret_text(text: str) -> bool:
    """
    Détecte si un texte contient un secret critique (OTP, PIN, mot de passe, code d'authentification).
    Règle absolue : un secret ne doit JAMAIS être envoyé à l'API ni modifié.
    """
    if not text or not isinstance(text, str):
        return False
    return any(pat.search(text) for pat in SECRET_PATTERNS)


AMOUNT_DIGITS = r"[\d\uff10-\uff19\u0660-\u0669]"
AMOUNT_SPACES = r"[\s\u00A0\u202F\u2007\u200B]"
CURRENCIES = r"(?:FCFA|F\s+CFA|XAF|CFA|XOF|EUR|USD|GBP|€|\$|£|francs?\s*(?:cfa)?|frs)"

# 1. Motifs d'extraction classés par ordre strict de spécificité
# Les motifs prioritaires absorbent leurs composants évitant tout conflit.
PATTERNS = [
    # 0. URLs complètes
    ("URL", re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)),

    # 0b. Adresses e-mail
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", re.IGNORECASE)),

    # 1. Variables de template
    ("TEMPLATE_VAR", re.compile(
        r"\{\{[a-zA-Z0-9_]+\}\}|\{[a-zA-Z0-9_]+\}|\$\{[a-zA-Z0-9_]+\}|%[sdf]|⟦\d+⟧|\u27e6\d+\u27e7"
    )),

    # 2. Références de transaction (ex: SAF-2026-X7Y8Z9, REF-12345, TX-ujineeje)
    ("REF", re.compile(r"\b(?:SAF-\d{4}-[A-Za-z0-9_-]{4,20}|REF-[A-Za-z0-9_-]{4,20}|TX-[A-Za-z0-9_-]{4,20})\b", re.IGNORECASE)),

    # 3. Marque commerciale protégée
    ("BRAND", re.compile(r"\bSafinum(?:\s+Pay)?\b", re.IGNORECASE)),

    # 4. Dates calendaires et horaires (Français et Anglais)
    ("DATE", re.compile(
        r"(?:"
        r"\b\d{1,2}\s+(?:janv\.|janvier|january|févr\.|février|february|mars|march|avr\.|avril|april|mai|may|juin|june|juil\.|juillet|july|août|august|sept\.|septembre|september|oct\.|octobre|october|nov\.|novembre|november|déc\.|décembre|december)\s+\d{4}\b|"
        r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},\s*\d{4}\b|"
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|"
        r"\b\d{4}-\d{2}-\d{2}(?:\s+\d{1,2}:\d{2})?\b|"
        r"\b\d{1,2}[h:]\d{2}\b"
        r")",
        re.IGNORECASE
    )),

    # 5. Montants en toutes lettres (Français et Anglais)
    ("AMOUNT_WORDS", re.compile(
        r"(?:"
        r"\b(?:un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize|"
        r"vingt|trente|quarante|cinquante|soixante|soixante-dix|septante|quatre-vingts?|quatre-vingt-dix|nonante|"
        r"cent|cents|mille|million|millions|milliard|milliards)"
        r"(?:[-\s]+(?:et[-\s]+)?(?:un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize|"
        r"vingt|trente|quarante|cinquante|soixante|soixante-dix|septante|quatre-vingts?|quatre-vingt-dix|nonante|"
        r"cent|cents|mille|million|millions|milliard|milliards))*"
        r"\s*(?:francs?\s*(?:cfa)?|fcfa|xaf|cfa|xof|euros?|eur|dollars?|usd|%|pour\s*cent)\b"
        r"|"
        r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
        r"seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion)"
        r"(?:[-\s]+(?:and\s+)?(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
        r"seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion))*"
        r"\s*(?:cfa\s*francs?|francs?\s*(?:cfa)?|fcfa|xaf|cfa|xof|euros?|eur|dollars?|usd|%|percent)\b"
        r")",
        re.IGNORECASE
    )),

    # 6. Pourcentages / Frais en %
    ("PCT", re.compile(r"\b\d+(?:[,\.]\d+)?\s*%(?!\w)")),

    # 7. Montants avec devises (placé AVANT TEL pour préserver les montants à 9 chiffres de type 250 000 000 FCFA)
    ("AMOUNT", re.compile(
        r"(?:[-+−\u2212]\s*)?"
        r"(?:"
            r"(?:[$€£]\s*" + AMOUNT_DIGITS + r"+(?:" + AMOUNT_SPACES + AMOUNT_DIGITS + r"{3})*(?:[,\.]" + AMOUNT_DIGITS + r"+)?)"
            r"|"
            r"(?:\bFCFA\s*" + AMOUNT_DIGITS + r"+(?:" + AMOUNT_SPACES + AMOUNT_DIGITS + r"{3})*(?:[,\.]" + AMOUNT_DIGITS + r"+)?)"
            r"|"
            r"(?:" + AMOUNT_DIGITS + r"+(?:" + AMOUNT_SPACES + AMOUNT_DIGITS + r"{3})*(?:[,\.]" + AMOUNT_DIGITS + r"+)?\s*" + CURRENCIES + r"(?!\w))"
        r")",
        re.IGNORECASE
    )),

    # 8. Noms de bénéficiaires / destinataires (Reconnaissance contextuelle + Noms connus)
    ("BENEF", re.compile(
        r"(?:\b(?:[Bb]énéficiaire|[Dd]estinataire|[Bb]eneficiary)\s*:\s*|\b(?:[Vv]ers|[Pp]our)\s+)"
        r"([A-Za-zÀ-ÿ'’\-]+(?:\s+[A-Za-zÀ-ÿ'’\-]+)+)"
        r"|"
        r"\b(Jean-Paul Mbarga|Solde Mbarga|Frais Ngo Bell|Amina Ngo Bell|Amina|N'Dongo Épée)\b"
    )),

    # 9. Numéro de téléphone (Cameroun / International)
    ("TEL", re.compile(r"(?:\+237\s*|\(\+237\)\s*|00237\s*)?[26](?:[\s.-]?\d){7}\d\b")),

    # 10. Numéro de compte bancaire et IBAN
    ("ACCT", re.compile(r"\bCM\d{2}(?:\s*\d{5}){2}(?:\s*\d{11})(?:\s*\d{2})\b|\bCM(?:\s*\d{3})(?:\s*\d{4}){2}(?:\s*\d{2})\b|(?<!\+)\b\d{4}(?:\s*\d{4}){2,3}\b")),

    # 11. Nombres purs / montants sans devises
    ("NUMBER", re.compile(
        r"(?<![A-Za-z0-9_])[-+−\u2212]?(?:" + AMOUNT_DIGITS + r"{1,3}(?:" + AMOUNT_SPACES + AMOUNT_DIGITS + r"{3})+|" + AMOUNT_DIGITS + r"{2,})(?:[,\.]" + AMOUNT_DIGITS + r"+)?(?![A-Za-z0-9_])"
    )),
]


TOKEN_PREFIX = "__SAFE_"
TOKEN_SUFFIX = "__"
TOKEN_REGEX = re.compile(r"__SAFE_[A-Z_]+_\d+__")
ESCAPED_SAFE_PREFIX = "__ESCAPED_SAFE_"


def normalize_input_text(text: str) -> str:
    """Normalise les entités HTML courantes sans altérer les espaces insécables."""
    if not text or not isinstance(text, str):
        return text
    return html.unescape(text)


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

    # 1. Normalisation HTML sans altération d'espaces
    cleaned = normalize_input_text(text)

    # 2. Protection contre l'injection de faux jetons :
    # Tout __SAFE_ préexistant dans la source utilisateur est neutralisé par préfixe d'échappement
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


# ---------------------------------------------------------------------------
# Mots-clés factorisés de sécurité et alertes
# ---------------------------------------------------------------------------
SECURITY_ALERT_KEYWORDS = {
    "alerte", "sécurité", "securite", "attention", "fraude", "suspect", "danger",
    "bloqué", "bloque", "confidentialité", "confidentiel", "warning", "alert",
    "security", "fraud", "avertissement",
}


def is_security_alert_text(text: str) -> bool:
    """
    Détecte si un texte est un avertissement de sécurité ou une alerte
    sur la base des mots-clés factorisés.
    """
    if not text or not isinstance(text, str):
        return False
    lower = text.lower()
    return any(kw in lower for kw in SECURITY_ALERT_KEYWORDS)


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
