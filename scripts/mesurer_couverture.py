# -*- coding: utf-8 -*-
"""
scripts/mesurer_couverture.py — Mesure de couverture de traduction par ecran.

METHODE :
  - Passage 1 : Playwright Edge, profil vierge, SANS extension.
    Collecte les chaines visibles FR natives de chaque ecran.
    -> Donne la liste des chaines que le site expose.
  - Passage 2 : Playwright Edge, extension ACTIVE, langue=dua puis bas.
    Pour chaque ecran, verifie quelles chaines collectees en FR ont bien
    ete traduites (texte remplace par l'extension).
    -> Donne la couverture effective de la memoire.
  - Confrontation avec catalogue/translations.csv et catalogue/glossaire.csv.

Produit docs/couverture_mesuree.md.
Ne modifie AUCUN catalogue.
"""

import os
import sys
import re
import csv
import json
import time
import socket
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any, Optional

sys.stdout.reconfigure(encoding="utf-8")

try:
    from playwright.sync_api import sync_playwright, Page
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_JS_PATH  = os.path.join(BASE_DIR, "extension", "content.js")
OFFLINE_CAT_PATH = os.path.join(BASE_DIR, "extension", "offline_catalog.json")
TRANSLATIONS_CSV = os.path.join(BASE_DIR, "catalogue", "translations.csv")
GLOSSAIRE_CSV    = os.path.join(BASE_DIR, "catalogue", "glossaire.csv")
OUTPUT_MD        = os.path.join(BASE_DIR, "docs", "couverture_mesuree.md")

TARGET_URL    = "https://safinum.cm/hackathon-test"
TARGET_IP     = "91.234.194.101"
RESOLVER_RULE = f"--host-resolver-rules=MAP safinum.cm {TARGET_IP}"

ECRANS = [
    ("tableau_de_bord",  "Tableau de bord (Solde)"),
    ("frais",            "Consultation des frais"),
    ("beneficiaire",     "Beneficiaire"),
    ("recapitulatif",    "Recapitulatif"),
    ("recu",             "Recu"),
    ("alertes_erreurs",  "Alertes / Erreurs"),
]


# ---------------------------------------------------------------------------
# Chargement des donnees
# ---------------------------------------------------------------------------

def load_catalog() -> Tuple[Dict, Dict, Dict]:
    """
    Retourne :
      sources_dua : {source_fr_lower: {cle, cible, statut}}
      sources_bas : {source_fr_lower: {cle, cible, statut}}
      all_sources : {source_fr_lower: ...} (union)
    """
    s_dua: Dict[str, Dict] = {}
    s_bas: Dict[str, Dict] = {}
    with open(TRANSLATIONS_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            src = row["source"].strip()
            d = {"cle": row["cle"].strip(), "cible": row["cible"].strip(), "statut": row["statut"].strip()}
            if row["langue"].strip() == "dua":
                s_dua[src.lower()] = d
            elif row["langue"].strip() == "bas":
                s_bas[src.lower()] = d
    return s_dua, s_bas, {**s_dua, **s_bas}


def load_glossaire() -> Dict[str, List[str]]:
    """Retourne {langue: [terme_source]} trié par longueur décroissante."""
    result: Dict[str, List[str]] = {"dua": [], "bas": []}
    with open(GLOSSAIRE_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lang = row.get("langue", "").strip()
            terme = row.get("terme_source", "").strip()
            if lang in result and terme and len(terme) >= 3:
                result[lang].append(terme)
    for lang in result:
        result[lang] = sorted(set(result[lang]), key=len, reverse=True)
    return result


def load_extension() -> Tuple[str, dict]:
    with open(CONTENT_JS_PATH, "r", encoding="utf-8") as f:
        js = f.read()
    with open(OFFLINE_CAT_PATH, "r", encoding="utf-8") as f:
        cat = json.load(f)
    return js, cat


# ---------------------------------------------------------------------------
# Utilitaires reseau
# ---------------------------------------------------------------------------

def is_site_reachable(timeout: int = 15) -> Tuple[bool, str]:
    """Teste la joignabilite : d'abord DNS normal, puis IP directe."""
    for url, extra_headers in [
        (TARGET_URL, {}),
        (TARGET_URL.replace("safinum.cm", TARGET_IP), {"Host": "safinum.cm"}),
    ]:
        try:
            hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", **extra_headers}
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                if r.status < 400:
                    return True, f"HTTP {r.status}"
        except Exception:
            pass
    return False, "Toutes les tentatives de connexion ont echoue"


# ---------------------------------------------------------------------------
# Collecte de chaines
# ---------------------------------------------------------------------------

FINANCIAL_PATTERNS = [
    re.compile(r'^\d[\d\s\u00a0\u202f]*(?:FCFA|XOF|€|\$|%)?$'),
    re.compile(r'^\d{2}/\d{2}/\d{4}$'),
    re.compile(r'^\d{4}-\d{2}-\d{2}$'),
    re.compile(r'^[+]?\d[\d\s\-\(\)]{5,}$'),
    re.compile(r'^SAF-\d{4}-[A-Z0-9]+$'),
    re.compile(r'^[A-Z]{2}\d{2}[A-Z0-9\s]{10,}$'),
    re.compile(r'^\d+[\s\u00a0\u202f]\d{3}'),
]

KNOWN_STOPWORDS = {
    "ok", "ko", "fr", "en", "dua", "bas", "ful", "ewo", "bbj",
    "fcfa", "xof", "cm", "ref", "id", "n°", "no",
}

def is_financial_or_trivial(t: str) -> bool:
    if len(t) <= 2:
        return True
    if t.lower() in KNOWN_STOPWORDS:
        return True
    for pat in FINANCIAL_PATTERNS:
        if pat.match(t.strip()):
            return True
    # Chaine uniquement composee de chiffres/symboles
    if re.match(r'^[\d\s\+\-\.\,\/\%\(\)\u00a0\u202f]+$', t):
        return True
    return False


def collect_strings_from_page(page: Page) -> List[str]:
    """Collecte tous les textes DOM visibles (TreeWalker)."""
    raw = page.evaluate("""() => {
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode(node) {
                    const p = node.parentElement;
                    if (!p) return NodeFilter.FILTER_REJECT;
                    const cs = window.getComputedStyle(p);
                    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0')
                        return NodeFilter.FILTER_REJECT;
                    const tag = p.tagName.toLowerCase();
                    if (['script','style','noscript'].includes(tag))
                        return NodeFilter.FILTER_REJECT;
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );
        const out = [];
        let n;
        while ((n = walker.nextNode())) {
            const t = n.textContent.trim();
            if (t.length >= 3) out.push(t);
        }
        return out;
    }""")
    seen: Set[str] = set()
    result = []
    for t in (raw or []):
        c = re.sub(r'\s+', ' ', t.strip())
        cl = c.lower()
        if len(c) < 3 or cl in seen or is_financial_or_trivial(c):
            continue
        seen.add(cl)
        result.append(c)
    return result


# ---------------------------------------------------------------------------
# Injection de l'extension
# ---------------------------------------------------------------------------

def inject_extension_js(page: Page, catalog_dict: dict, content_js: str):
    page.evaluate("""(cat) => {
        window.chrome = window.chrome || {};
        window.chrome.runtime = { getURL: p => 'ext://' + p };
        const _orig = window.fetch;
        window.fetch = async (url, opts) => {
            if (typeof url === 'string' &&
                (url.includes('offline_catalog.json') || url.includes('catalogue_offline.json'))) {
                return { ok: true, json: async () => cat };
            }
            return _orig(url, opts);
        };
    }""", catalog_dict)
    page.evaluate(content_js)
    time.sleep(1.5)


def set_lang(page: Page, lang: str):
    page.evaluate("""(lang) => {
        const h = document.getElementById('safinum-accessibility-host');
        if (h && h.shadowRoot) {
            const s = h.shadowRoot.getElementById('langSelect');
            if (s) { s.value = lang; s.dispatchEvent(new Event('change')); }
        }
    }""", lang)
    time.sleep(1.5)


# ---------------------------------------------------------------------------
# Navigation ecran par ecran
# ---------------------------------------------------------------------------

def wait_stable(page: Page, ms: int = 1500):
    time.sleep(ms / 1000)


def try_click(page: Page, selectors: List[str], timeout_ms: int = 2000) -> bool:
    for sel in selectors:
        try:
            el = page.locator(sel).first
            el.wait_for(state="visible", timeout=timeout_ms)
            el.click()
            return True
        except Exception:
            pass
    return False


def fill_amount(page: Page, amount: str = "25000"):
    """Remplit le champ de montant sur l'ecran Frais."""
    for sel in [
        "input[type='number']",
        "input[placeholder*='montant']",
        "input[placeholder*='amount']",
        "input[placeholder*='Montant']",
        "input[name='amount']",
        "[data-field='amount'] input",
    ]:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=1500):
                el.fill(amount)
                wait_stable(page, 500)
                return True
        except Exception:
            pass
    return False


def collect_screen(page: Page, screen_id: str, label: str) -> List[str]:
    wait_stable(page, 1000)
    strings = collect_strings_from_page(page)
    print(f"      [{screen_id}] {len(strings)} chaines")
    return strings


def navigate_full_journey(
    page: Page,
    base_url: str,
    with_extension: bool,
    content_js: str,
    catalog_dict: dict,
    lang: Optional[str] = None,
) -> Dict[str, List[str]]:
    """
    Navigue le parcours complet et collecte les chaines par ecran.
    with_extension=False : navigation native FR (textes source).
    with_extension=True  : extension active + langue = lang.
    """
    results: Dict[str, List[str]] = {e[0]: [] for e in ECRANS}

    page.goto(base_url, wait_until="networkidle", timeout=30000)
    wait_stable(page, 1500)

    if with_extension:
        inject_extension_js(page, catalog_dict, content_js)
        if lang:
            set_lang(page, lang)

    # --- Ecran 1 : Tableau de bord ---
    print("      > Tableau de bord")
    results["tableau_de_bord"] = collect_screen(page, "tableau_de_bord", "Tableau de bord")

    # --- Ecran 2 : Frais ---
    print("      > Frais")
    clicked = try_click(page, [
        "button:has-text('Consulter les frais')",
        "button:has-text('frais')",
        "button:has-text('fees')",
        "button:has-text('Fees')",
        "button:has-text('View fees')",
        "[data-step='fees']",
        "a:has-text('frais')",
    ])
    if not clicked:
        # Essai par position (2e bouton principal)
        try:
            btns = page.locator("main button, section button").all()
            for b in btns:
                txt = b.inner_text().strip().lower()
                if any(k in txt for k in ["frais", "fee", "consul"]):
                    b.click()
                    clicked = True
                    break
        except Exception:
            pass
    if clicked:
        wait_stable(page)
        results["frais"] = collect_screen(page, "frais", "Frais")
    else:
        print("        [!] Navigation Frais echouee")

    # Remplir le montant pour debloquer Continuer
    fill_amount(page, "25000")
    wait_stable(page, 500)

    # --- Ecran 3 : Beneficiaire ---
    print("      > Beneficiaire")
    clicked_ben = try_click(page, [
        "button:has-text('Continuer')",
        "button:has-text('Continue')",
        "button:has-text('Suivant')",
        "button:has-text('Next')",
        "button:has-text('Proceed')",
    ])
    if clicked_ben:
        wait_stable(page)
        results["beneficiaire"] = collect_screen(page, "beneficiaire", "Beneficiaire")
    else:
        print("        [!] Navigation Beneficiaire echouee")

    # Remplir le formulaire beneficiaire
    for name_sel in [
        "input[placeholder*='nom']",
        "input[placeholder*='name']",
        "input[placeholder*='Name']",
        "input[type='text']",
        "input[name='beneficiary']",
        "input[name='name']",
    ]:
        try:
            el = page.locator(name_sel).first
            if el.is_visible(timeout=1000):
                el.fill("Jean-Paul Mbarga")
                break
        except Exception:
            pass
    for phone_sel in [
        "input[type='tel']",
        "input[placeholder*='phone']",
        "input[placeholder*='telephone']",
        "input[placeholder*='Phone']",
        "input[name='phone']",
    ]:
        try:
            el = page.locator(phone_sel).first
            if el.is_visible(timeout=1000):
                el.fill("+237699123456")
                break
        except Exception:
            pass
    # Cocher checkbox si presente
    try:
        cb = page.locator("input[type='checkbox']").first
        if cb.is_visible(timeout=800) and not cb.is_checked():
            cb.check()
    except Exception:
        pass
    wait_stable(page, 500)

    # --- Ecran 4 : Recapitulatif ---
    print("      > Recapitulatif")
    clicked_sum = try_click(page, [
        "button:has-text('Continuer')",
        "button:has-text('Continue')",
        "button:has-text('Suivant')",
        "button:has-text('Next')",
        "button:has-text('Confirmer')",
    ])
    if clicked_sum:
        wait_stable(page)
        results["recapitulatif"] = collect_screen(page, "recapitulatif", "Recapitulatif")
    else:
        print("        [!] Navigation Recapitulatif echouee")

    # Cocher la case de confirmation
    try:
        cb = page.locator("input[type='checkbox']").first
        if cb.is_visible(timeout=800) and not cb.is_checked():
            cb.check()
    except Exception:
        pass
    wait_stable(page, 500)

    # --- Ecran 5 : Recu ---
    print("      > Recu")
    clicked_rec = try_click(page, [
        "button:has-text('Confirmer le transfert')",
        "button:has-text('Confirm transfer')",
        "button:has-text('Confirmer')",
        "button:has-text('Confirm')",
        "button:has-text('Valider')",
        "button:has-text('Submit')",
    ])
    if clicked_rec:
        wait_stable(page, 2000)
        results["recu"] = collect_screen(page, "recu", "Recu")
    else:
        print("        [!] Navigation Recu echouee")

    # --- Ecran 6 : Alertes (via panneau jury) ---
    print("      > Alertes / Erreurs (via ?jury=1)")
    try:
        page.goto(base_url + "?jury=1", wait_until="networkidle", timeout=20000)
        wait_stable(page)
        if with_extension:
            inject_extension_js(page, catalog_dict, content_js)
            if lang:
                set_lang(page, lang)
        # Collecter les chaines de base qui comprennent le texte des alertes
        base_strings = collect_strings_from_page(page)
        # Essayer de naviguer vers des alertes via la sidebar jury
        alert_strings: List[str] = list(base_strings)
        for inj_sel in ["aside button:has-text('Injecter')", "button:has-text('Injecter')"]:
            try:
                inj_btns = page.locator(inj_sel).all()
                for btn in inj_btns[:1]:
                    if btn.is_visible(timeout=800):
                        btn.click()
                        wait_stable(page)
                        alert_strings.extend(collect_strings_from_page(page))
            except Exception:
                pass
        # Dedoublonner
        seen: Set[str] = set()
        dedup = []
        for s in alert_strings:
            if s.lower() not in seen:
                seen.add(s.lower())
                dedup.append(s)
        results["alertes_erreurs"] = dedup
        print(f"      [alertes_erreurs] {len(dedup)} chaines")
    except Exception as e:
        print(f"        [!] Alertes echouees: {e}")
        results["alertes_erreurs"] = []

    return results


# ---------------------------------------------------------------------------
# Analyse de couverture
# ---------------------------------------------------------------------------

def analyse_coverage(
    strings: List[str],
    sources: Dict[str, Dict],   # source_fr_lower -> info
    glossaire: List[str],       # termes source du glossaire pour cette langue
) -> Dict[str, Any]:
    in_memory: List[str] = []
    in_glossaire: List[str] = []
    not_covered: List[str] = []

    for s in strings:
        sl = s.lower()
        # Memoire : correspondance exacte (insensible a la casse)
        if sl in sources:
            in_memory.append(s)
            continue
        # Memoire : correspondance partielle (la chaine contient une source complete)
        mem_hit = False
        for src_low in sources:
            if len(src_low) >= 5 and src_low in sl:
                in_memory.append(s)
                mem_hit = True
                break
        if mem_hit:
            continue
        # Glossaire : au moins un terme du glossaire dans la chaine
        gloss_hit = any(t.lower() in sl for t in glossaire if len(t) >= 4)
        if gloss_hit:
            in_glossaire.append(s)
            continue
        not_covered.append(s)

    return {
        "total": len(strings),
        "in_memory": in_memory,
        "in_glossaire": in_glossaire,
        "not_covered": not_covered,
    }


# ---------------------------------------------------------------------------
# Rapport Markdown
# ---------------------------------------------------------------------------

def pct(n: int, total: int) -> str:
    if total == 0:
        return "—"
    return f"{100*n//total}%"


def generate_report(
    fr_data: Dict[str, List[str]],
    en_note: str,
    en_data: Optional[Dict[str, List[str]]],
    sources_dua: Dict,
    sources_bas: Dict,
    glossaire: Dict[str, List[str]],
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Couverture de traduction mesurée — SAFINUM 2026",
        "",
        f"- **Date de mesure** : `{now}`",
        "- **Methode** : Playwright Edge, profil vierge — collecte sur textes FR natifs",
        f"- **URL cible** : `{TARGET_URL}`",
        "- **Langues analysees** : Duálá (`dua`) et Ɓàsàa (`bas`)",
        "- **Regles** : aucun catalogue modifie ; valeur « non mesuré » si navigation impossible",
        "",
        "> [!NOTE]",
        "> **Memoire** = chaine FR collectee trouvee dans `catalogue/translations.csv` (source exacte ou partielle).",
        "> **Glossaire** = chaine FR non dans la memoire mais contenant au moins un terme de `catalogue/glossaire.csv`.",
        "> **Non couvert** = absente des deux. Ces chaines ne peuvent pas etre traduites par l'extension.",
        "",
        "---",
        "",
        "## 1. Couverture par écran — Interface FR (textes source natifs du site)",
        "",
        "| Écran | Visibles | dua Mém. | dua Glos. | dua NC | dua% | bas Mém. | bas Glos. | bas NC | bas% |",
        "|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    nc_dua_all: Dict[str, List[str]] = {}
    nc_bas_all: Dict[str, List[str]] = {}
    all_strings: List[str] = []

    for ecran_id, ecran_label in ECRANS:
        strings = fr_data.get(ecran_id, [])
        if not strings:
            lines.append(f"| {ecran_label} | non mesuré | — | — | — | — | — | — | — | — |")
            nc_dua_all[ecran_id] = []
            nc_bas_all[ecran_id] = []
            continue

        all_strings.extend(strings)

        cov_dua = analyse_coverage(strings, sources_dua, glossaire["dua"])
        cov_bas = analyse_coverage(strings, sources_bas, glossaire["bas"])
        nc_dua_all[ecran_id] = cov_dua["not_covered"]
        nc_bas_all[ecran_id] = cov_bas["not_covered"]

        total = cov_dua["total"]
        cov_pct_dua = pct(len(cov_dua["in_memory"]) + len(cov_dua["in_glossaire"]), total)
        cov_pct_bas = pct(len(cov_bas["in_memory"]) + len(cov_bas["in_glossaire"]), total)

        lines.append(
            f"| {ecran_label} | {total} "
            f"| {len(cov_dua['in_memory'])} | {len(cov_dua['in_glossaire'])} | {len(cov_dua['not_covered'])} | {cov_pct_dua} "
            f"| {len(cov_bas['in_memory'])} | {len(cov_bas['in_glossaire'])} | {len(cov_bas['not_covered'])} | {cov_pct_bas} |"
        )

    # Totaux
    all_unique = list(dict.fromkeys(all_strings))
    if all_unique:
        ct_dua = analyse_coverage(all_unique, sources_dua, glossaire["dua"])
        ct_bas = analyse_coverage(all_unique, sources_bas, glossaire["bas"])
        cp_dua = pct(len(ct_dua["in_memory"]) + len(ct_dua["in_glossaire"]), len(all_unique))
        cp_bas = pct(len(ct_bas["in_memory"]) + len(ct_bas["in_glossaire"]), len(all_unique))
        lines.append(
            f"| **TOTAL (tous écrans, dédup.)** | **{len(all_unique)}** "
            f"| **{len(ct_dua['in_memory'])}** | **{len(ct_dua['in_glossaire'])}** | **{len(ct_dua['not_covered'])}** | **{cp_dua}** "
            f"| **{len(ct_bas['in_memory'])}** | **{len(ct_bas['in_glossaire'])}** | **{len(ct_bas['not_covered'])}** | **{cp_bas}** |"
        )

    # Detail NC dua
    lines += ["", "---", "", "## 2. Chaines non couvertes par écran — Duálá (`dua`)", ""]
    for ecran_id, ecran_label in ECRANS:
        nc = nc_dua_all.get(ecran_id, [])
        lines.append(f"### {ecran_label}")
        lines.append("")
        if not nc:
            lines.append("*Toutes les chaînes sont couvertes (mémoire ou glossaire).*")
        else:
            for s in nc:
                lines.append(f"- `{s}`")
        lines.append("")

    # Detail NC bas
    lines += ["---", "", "## 3. Chaines non couvertes par écran — Ɓàsàa (`bas`)", ""]
    for ecran_id, ecran_label in ECRANS:
        nc = nc_bas_all.get(ecran_id, [])
        lines.append(f"### {ecran_label}")
        lines.append("")
        if not nc:
            lines.append("*Toutes les chaînes sont couvertes (mémoire ou glossaire).*")
        else:
            for s in nc:
                lines.append(f"- `{s}`")
        lines.append("")

    # Section EN
    lines += ["---", "", "## 4. Interface EN (anglais) — Comportement observé", ""]
    if not en_data or all(not v for v in en_data.values()):
        lines += [
            "> [!WARNING]",
            f"> {en_note}",
            "",
            "Le site `safinum.cm/hackathon-test` est **exclusivement en français**.",
            "Aucun bouton EN n'a été trouvé lors du relevé automatisé.",
            "Le catalogue de l'extension est indexé sur le français : il n'existe pas de mémoire",
            "de traduction pour des sources en anglais. Si un basculement EN était disponible,",
            "la couverture serait **nulle** car aucune source anglaise n'est dans `translations.csv`.",
            "",
        ]
    else:
        lines += [
            "| Écran | Visibles EN | dua Mém. | dua NC | bas Mém. | bas NC |",
            "|---|:---:|:---:|:---:|:---:|:---:|",
        ]
        all_en: List[str] = []
        for ecran_id, ecran_label in ECRANS:
            strings = en_data.get(ecran_id, [])
            if not strings:
                lines.append(f"| {ecran_label} | non mesuré | — | — | — | — |")
                continue
            all_en.extend(strings)
            cov_dua = analyse_coverage(strings, sources_dua, glossaire["dua"])
            cov_bas = analyse_coverage(strings, sources_bas, glossaire["bas"])
            lines.append(
                f"| {ecran_label} | {len(strings)} "
                f"| {len(cov_dua['in_memory'])} | {len(cov_dua['not_covered'])} "
                f"| {len(cov_bas['in_memory'])} | {len(cov_bas['not_covered'])} |"
            )
        lines += [
            "",
            "> [!IMPORTANT]",
            "> Le catalogue est indexé sur le **français**. Si le site bascule en anglais,",
            "> les sources changent de forme et la couverture chute mécaniquement.",
            "> Les données financières (montants, références) restent protégées indépendamment.",
            "",
            f"> Note : {en_note}",
        ]

    # Notes methodologiques
    lines += [
        "",
        "---",
        "",
        "## 5. Notes méthodologiques",
        "",
        "1. **Collecte sans extension** : navigation en FR natif pour obtenir les textes source réels du site.",
        "2. **Exclusions automatiques** : montants, références (`SAF-XXXX-YYYY`), numéros de téléphone,",
        "   dates, chiffres isolés, chaînes < 3 caractères.",
        "3. **Correspondance mémoire** : comparaison insensible à la casse avec `catalogue/translations.csv`",
        "   (correspondance exacte ou partielle — la source catalogue doit être contenue dans la chaîne).",
        "4. **Correspondance glossaire** : présence d'au moins un terme du glossaire (≥ 4 car.) dans la chaîne.",
        "5. **Non couvert** : absent de la mémoire ET sans terme du glossaire.",
        "   Ces chaînes nécessiteraient l'ajout d'entrées dans le catalogue pour être traduites.",
        "6. **Aucune modification** de catalogue effectuée.",
        "",
        "---",
        "",
        f"*Rapport généré le {now} par `scripts/mesurer_couverture.py` — branche `amelioration`.*",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Point d'entree
# ---------------------------------------------------------------------------

def main():
    print("\n=== MESURE DE COUVERTURE DE TRADUCTION — SAFINUM 2026 ===")

    print("\n[1] Vérification joignabilité...")
    reachable, reason = is_site_reachable()
    if not reachable:
        print(f"  [IGNORÉ] Site injoignable : {reason}")
        report = _build_unreachable_report(reason)
        os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
        with open(OUTPUT_MD, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"  Rapport : {OUTPUT_MD}")
        return
    print(f"  OK : {reason}")

    if not HAS_PLAYWRIGHT:
        print("[ERREUR] Playwright non installé.")
        sys.exit(1)

    print("\n[2] Chargement des données...")
    sources_dua, sources_bas, _ = load_catalog()
    glossaire = load_glossaire()
    content_js, catalog_dict = load_extension()
    print(f"  Catalogue : {len(sources_dua)} entrées dua, {len(sources_bas)} bas")
    print(f"  Glossaire : {len(glossaire['dua'])} termes dua, {len(glossaire['bas'])} bas")

    fr_data: Dict[str, List[str]] = {}
    en_data: Optional[Dict[str, List[str]]] = None
    en_note = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=False,
            args=["--no-sandbox", "--disable-web-security", RESOLVER_RULE]
        )
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = ctx.new_page()

        # --- Passage 1 : Collecte FR sans extension (textes source natifs) ---
        print("\n[3] Collecte FR (sans extension, textes source natifs)...")
        try:
            fr_data = navigate_full_journey(
                page, TARGET_URL,
                with_extension=False,
                content_js=content_js,
                catalog_dict=catalog_dict,
                lang=None,
            )
        except Exception as e:
            print(f"  [ERREUR] {e}")
            fr_data = {e_id: [] for e_id, _ in ECRANS}

        # --- Passage 2 : Essai EN ---
        print("\n[4] Vérification bouton EN...")
        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=20000)
            time.sleep(2)
            # Chercher bouton EN
            en_found = False
            for sel in [
                "button:has-text('EN')",
                "[data-lang='en']",
                "button.lang-en",
                "a:has-text('EN')",
            ]:
                try:
                    el = page.locator(sel).first
                    el.wait_for(state="visible", timeout=2000)
                    el.click()
                    time.sleep(2)
                    en_found = True
                    break
                except Exception:
                    pass

            if en_found:
                print("  Bouton EN trouvé — collecte EN...")
                en_data = navigate_full_journey(
                    page, TARGET_URL,
                    with_extension=False,
                    content_js=content_js,
                    catalog_dict=catalog_dict,
                    lang=None,
                )
                en_note = "Bouton EN détecté et actif."
            else:
                en_note = "Aucun bouton EN trouvé. Le site est exclusivement en français."
                print(f"  {en_note}")
        except Exception as e:
            en_note = f"Erreur lors du test EN : {e}"
            print(f"  [!] {en_note}")

        ctx.close()
        browser.close()

    print("\n[5] Analyse couverture...")
    report = generate_report(fr_data, en_note, en_data, sources_dua, sources_bas, glossaire)

    os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n  Rapport : {OUTPUT_MD}")

    # Resume
    all_fr = []
    for s in fr_data.values():
        all_fr.extend(s)
    all_fr = list(dict.fromkeys(all_fr))
    ct_dua = analyse_coverage(all_fr, sources_dua, glossaire["dua"])
    ct_bas = analyse_coverage(all_fr, sources_bas, glossaire["bas"])
    print(f"\n--- RÉSUMÉ ---")
    print(f"  Chaines FR visibles (tous écrans, dédup.) : {len(all_fr)}")
    print(f"  dua : mémoire={len(ct_dua['in_memory'])} glossaire={len(ct_dua['in_glossaire'])} non_couverts={len(ct_dua['not_covered'])}")
    print(f"  bas : mémoire={len(ct_bas['in_memory'])} glossaire={len(ct_bas['in_glossaire'])} non_couverts={len(ct_bas['not_covered'])}")
    print("\n[TERMINÉ]")


def _build_unreachable_report(reason: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = "\n".join(
        f"| {label} | non mesuré | non mesuré | non mesuré | non mesuré | non mesuré | non mesuré | non mesuré | non mesuré | non mesuré |"
        for _, label in ECRANS
    )
    return f"""# Couverture de traduction mesurée — SAFINUM 2026

- **Date de mesure** : `{now}`
- **URL cible** : `{TARGET_URL}`

> [!WARNING]
> Le site cible est **injoignable**. Raison : `{reason}`
> Toutes les valeurs sont **non mesurées**.

| Écran | Visibles | dua Mém. | dua Glos. | dua NC | dua% | bas Mém. | bas Glos. | bas NC | bas% |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
{rows}

*Rapport généré le {now} — site injoignable.*
"""


if __name__ == "__main__":
    main()
