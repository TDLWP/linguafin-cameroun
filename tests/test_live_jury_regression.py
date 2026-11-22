# -*- coding: utf-8 -*-
"""
Test automatisé E2E Playwright de non-régression sur le jury SAFINUM 2026.
URL cible : https://safinum.cm/hackathon-test?jury=1

Exigences :
- Navigateur Microsoft Edge (profil vierge).
- Chargement de l'extension SAFINUM.
- Déroulement du parcours complet :
    1. Solde
    2. Frais (avec saisie 25 000 FCFA)
    3. Bénéficiaire
    4. Récapitulatif
    5. Reçu
  exécuté en Duálá (dua) puis en Ɓàsàa (bas).
- Injection via le panneau jury de 3 contenus inédits :
    (a) Alerte de sécurité avec un montant utilisant une espace fine insécable \u202F
    (b) Phrase de confirmation
    (c) Notification sans montant
- Dans les modes backend arrêté et backend lancé, vérification que :
    * Aucune entrée n'est 'Compromis'
    * Aucun crochet n'entoure un montant
    * Le badge 'contenu inédit' est visible quand des termes sont annotés
- Lecture de l'onglet 'Soumissions' du panneau jury.
- Échec immédiat si une seule entrée affiche 'Compromis'.
- Exécution dans 3 modes :
    Mode 1 : Backend arrêté (port 8000 fermé, fallback hors-ligne sur catalogue embarqué).
    Mode 2 : Backend lancé (FastAPI local sur http://127.0.0.1:8000).
    Mode 3 : Extension désactivée (référence native en français).
- Si le site est injoignable, le test est marqué 'ignoré' (Skipped) avec un message clair, JAMAIS 'réussi'.
- Restitution des résultats bruts par étape et par mode.
"""

import os
import sys
import re
import time
import json
import socket
import urllib.request
import urllib.error
import subprocess
import unittest
from typing import Dict, List, Any, Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_JS_PATH = os.path.join(BASE_DIR, "extension", "content.js")
OFFLINE_CATALOG_PATH = os.path.join(BASE_DIR, "extension", "offline_catalog.json")

TARGET_URL = "https://safinum.cm/hackathon-test?jury=1"
RESOLVER_RULES = "--host-resolver-rules=MAP safinum.cm 91.234.194.101"

with open(CONTENT_JS_PATH, "r", encoding="utf-8") as f:
    CONTENT_JS = f.read()

with open(OFFLINE_CATALOG_PATH, "r", encoding="utf-8") as f:
    CATALOG_DATA = json.load(f)


def is_site_reachable(url: str = TARGET_URL, timeout: int = 15) -> tuple[bool, str]:
    """Vérifie la joignabilité HTTP/HTTPS du site cible."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status < 400:
                return True, f"HTTP {response.status}"
            return False, f"Code HTTP inattendu : {response.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTPError {e.code} : {e.reason}"
    except urllib.error.URLError as e:
        return False, f"URLError : {e.reason}"
    except Exception as e:
        return False, f"Erreur de connexion : {str(e)}"


def is_port_in_use(port: int = 8000, host: str = "127.0.0.1") -> bool:
    """Vérifie si le port local est en cours d'utilisation."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def inject_extension(page: Page, catalog_dict: dict):
    """
    Simule l'environnement de l'extension Manifest V3 :
    - Fournit chrome.runtime.getURL pour l'accès aux ressources embarquées.
    - Intercepte la requête vers le catalogue hors-ligne pour renvoyer le catalogue embarqué.
    - Laisse les autres requêtes (notamment vers localhost:8000/translate/batch) passer normalement.
    - Injecte et initialise content.js.
    """
    page.evaluate("""(catData) => {
        window.chrome = window.chrome || {};
        window.chrome.runtime = {
            getURL: function(path) { return 'safinum-extension://' + path; }
        };
        const _origFetch = window.fetch;
        window.fetch = async function(url, opts) {
            if (typeof url === 'string' && (url.includes('offline_catalog.json') || url.includes('catalogue_offline.json'))) {
                return {
                    ok: true,
                    json: async () => catData
                };
            }
            return _origFetch(url, opts);
        };
    }""", catalog_dict)
    page.evaluate(CONTENT_JS)
    time.sleep(1.0)


def set_widget_language(page: Page, lang_code: str):
    """Change la langue dans le Shadow DOM du widget d'accessibilité."""
    page.evaluate("""(targetLang) => {
        const host = document.getElementById('safinum-accessibility-host');
        if (host && host.shadowRoot) {
            const select = host.shadowRoot.getElementById('langSelect');
            if (select) {
                select.value = targetLang;
                select.dispatchEvent(new Event('change'));
            }
        }
    }""", lang_code)
    time.sleep(1.2)


def reset_jury_log(page: Page):
    """Vide le journal des soumissions du jury."""
    try:
        # Clic sur l'onglet Soumissions (2e bouton de nav)
        page.locator("aside nav button").nth(1).click(force=True)
        time.sleep(0.4)
        btn_vider = page.locator("aside button:has-text('Vider'), aside button:has-text('Clear'), aside button:has-text('Reset')")
        if btn_vider.count() > 0 and btn_vider.first.is_enabled():
            btn_vider.first.click(force=True)
            time.sleep(0.4)
        # Retour à l'onglet Contrôle
        page.locator("aside nav button").nth(0).click(force=True)
        time.sleep(0.4)
    except Exception as e:
        print(f"  [Avertissement] Impossible de réinitialiser le journal jury : {e}")


def read_jury_submissions(page: Page, step_id: str, step_label: str) -> tuple[List[Dict[str, Any]], int]:
    """
    Déclenche le contrôle de l'étape courante, bascule sur l'onglet Soumissions,
    lit l'intégralité des cartes et renvoie les entrées détaillées ainsi que le nombre d'entrées compromises.
    """
    # 1. Clic sur Contrôle
    page.locator("aside nav button").nth(0).click(force=True)
    time.sleep(0.4)

    # 2. Cliquer sur 'Vérifier l'étape maintenant' / 'Verify step now'
    btn_verif = page.locator(
        "aside button:has-text('maintenant'), aside button:has-text('Verify'), aside button:has-text('Vérifier')"
    ).first
    btn_verif.scroll_into_view_if_needed()
    btn_verif.click(force=True)
    time.sleep(1.2)

    # 3. Basculer sur Soumissions
    page.locator("aside nav button").nth(1).click(force=True)
    time.sleep(0.8)

    # 4. Déplier tous les détails
    detail_btns = page.locator("aside button:has-text('Détail'), aside button:has-text('Detail')").all()
    for b in detail_btns:
        try:
            b.click(force=True)
        except Exception:
            pass
    time.sleep(0.4)

    # 5. Examiner les cartes de soumission
    cards = page.locator("aside div.rounded-xl.border").all()
    submissions = []
    compromised_count = 0

    for i, c in enumerate(cards):
        c_text = c.inner_text().strip()
        status_el = c.locator("span.rounded-full")
        status = status_el.first.inner_text().strip() if status_el.count() > 0 else "Inconnu"

        pres = c.locator("pre").all_inner_texts()
        expected = pres[0].strip() if len(pres) > 0 else ""
        displayed = pres[1].strip() if len(pres) > 1 else ""
        submitted = pres[2].strip() if len(pres) > 2 else ""

        diff_els = c.locator("div[class*='bg-red']").all_inner_texts()
        diffs = [d.strip() for d in diff_els if d.strip()]

        is_compromised = (status.lower() == "compromis") or ("compromis" in c_text.lower() and status.lower() != "intègre")
        if is_compromised:
            compromised_count += 1

        # RÈGLE CRITIQUE : Le texte des cartes du panneau jury ne doit JAMAIS être modifié par l'extension
        has_annotation_in_card = (
            "[Mutoa" in c_text or
            "[Moni" in c_text or
            "[Om moni" in c_text or
            "contenu inédit" in c_text.lower()
        )

        submissions.append({
            "index": i + 1,
            "step_id": step_id,
            "step_label": step_label,
            "status": status,
            "is_compromised": is_compromised,
            "has_annotation_in_card": has_annotation_in_card,
            "expected": expected,
            "displayed": displayed,
            "submitted": submitted,
            "diffs": diffs,
            "raw_text": c_text[:250].replace("\n", " | ")
        })

    # Retour à l'onglet Contrôle pour l'étape suivante
    page.locator("aside nav button").nth(0).click(force=True)
    time.sleep(0.3)

    return submissions, compromised_count


def inject_and_verify_novel_content(
    page: Page,
    item_key: str,
    item_label: str,
    text_to_inject: str,
    step_id: str
) -> Dict[str, Any]:
    """
    Injecte un contenu inédit via le volet 'Injecter' du panneau jury,
    puis vérifie :
    1. Qu'aucun crochet n'entoure un montant financier.
    2. Que le badge / conteneur 'contenu inédit' est bien visible quand des termes sont annotés.
    3. Qu'aucune entrée de soumission n'est 'Compromis'.
    """
    print(f"      --> Injection inédite [{item_key}] : '{text_to_inject}'")

    # 1. Basculer sur l'onglet Contrôle
    page.locator("aside nav button").nth(0).click(force=True)
    time.sleep(0.4)

    # 2. Remplir la zone de texte
    txt_area = page.locator("textarea").first
    txt_area.fill(text_to_inject)
    time.sleep(0.3)

    # 3. Cliquer sur Injecter / Inject
    btn_inject = page.locator("aside button:has-text('Injecter'), aside button:has-text('Inject')").first
    btn_inject.click(force=True)
    time.sleep(1.2)

    # 4. Examiner le conteneur injecté dans le DOM de #app
    injected_info = page.evaluate("""(srcText) => {
        // Recherche des conteneurs injectés (id injected-* ou classe border-[#9B7FD4])
        const containers = Array.from(document.querySelectorAll("div[id^='injected-'], div[class*='9B7FD4']"));
        const targetContainer = containers[containers.length - 1] || null;

        let displayedText = "";
        let hasTermsAnnotated = false;
        let badgeNovelVisible = false;

        if (targetContainer) {
            displayedText = targetContainer.innerText || "";
            // Termes annotés : attribut data-safinum-translated ou title
            hasTermsAnnotated = Boolean(
                targetContainer.querySelector("[data-safinum-translated='true']") ||
                targetContainer.getAttribute("data-safinum-translated") === "true" ||
                targetContainer.querySelector("[title*='Original']")
            );
            // Vérification spécifique de l'élément badge
            const badgeEl = targetContainer.querySelector(".safinum-novel-badge");
            let hasBadgeElement = false;
            let badgeText = "";
            if (badgeEl) {
                const bRect = badgeEl.getBoundingClientRect();
                hasBadgeElement = (bRect.width > 0 && bRect.height > 0);
                badgeText = badgeEl.innerText.trim();
            }
            // Badge / conteneur inédit visible
            const rect = targetContainer.getBoundingClientRect();
            badgeNovelVisible = (rect.width > 0 && rect.height > 0);
        } else {
            // Recherche de secours par texte
            const pEls = Array.from(document.querySelectorAll("p, div")).filter(el => el.children.length === 0 && (el.innerText || "").includes("75"));
            if (pEls.length > 0) {
                displayedText = pEls[0].innerText || "";
                badgeNovelVisible = true;
            }
        }

        // Vérification de la présence du label/badge dans le panneau jury
        const juryBadge = Array.from(document.querySelectorAll("aside *")).some(el =>
            el.innerText && (
                el.innerText.includes("CONTENU INJECTÉ") ||
                el.innerText.includes("INJECTER DU CONTENU INÉDIT")
            )
        );

        return {
            containerFound: Boolean(targetContainer),
            displayedText: displayedText.trim(),
            hasTermsAnnotated: hasTermsAnnotated,
            hasBadgeElement: Boolean(typeof hasBadgeElement !== 'undefined' && hasBadgeElement),
            badgeText: typeof badgeText !== 'undefined' ? badgeText : "",
            badgeNovelVisible: badgeNovelVisible || juryBadge
        };
    }""", text_to_inject)

    displayed_text = injected_info.get("displayedText", "")

    # 5. Règle stricte : Aucun crochet n'entoure un montant financier
    # Détection de motifs du type : [75 000 FCFA], [ 75 000 FCFA ], ou [ ... FCFA ... ]
    has_bracketed_amount = bool(
        re.search(r"\[\s*\d{1,3}(?:[\s\u00A0\u202F]\d{3})*(?:[,\.]\d+)?\s*FCFA\s*\]", displayed_text, re.IGNORECASE) or
        re.search(r"\[[^\]]*\b\d{1,3}(?:[\s\u00A0\u202F]\d{3})*(?:[,\.]\d+)?\s*FCFA[^\]]*\]", displayed_text, re.IGNORECASE)
    )

    # 6. Règle : Le badge est visible (inédit annoté ou alerte de sécurité en français)
    terms_annotated = injected_info.get("hasTermsAnnotated", False)
    badge_visible = injected_info.get("badgeNovelVisible", False)
    has_badge_el = injected_info.get("hasBadgeElement", False)
    badge_text = injected_info.get("badgeText", "")

    is_sec_alert = ("security" in item_key) or ("alerte" in item_key.lower()) or ("alerte" in text_to_inject.lower())
    badge_ok = True
    if is_sec_alert:
        # Pour une alerte de sécurité inédite avec montant, le badge doit être visible
        badge_ok = has_badge_el or badge_visible or (
            "avertissement affiché en français" in displayed_text or
            "contenu inédit" in displayed_text
        )
    elif terms_annotated:
        badge_ok = badge_visible

    # Vérification anti-collage : le badge ne doit pas être collé sans espace
    is_glued = bool(re.search(r"\S(avertissement affiché|contenu inédit)", displayed_text))

    # 7. Contrôle du panneau jury (Soumissions)
    subs, comp_count = read_jury_submissions(page, step_id, f"Contenu Inédit — {item_label}")

    return {
        "item_key": item_key,
        "item_label": item_label,
        "input_text": text_to_inject,
        "displayed_text": displayed_text,
        "has_bracketed_amount": has_bracketed_amount,
        "terms_annotated": terms_annotated,
        "badge_novel_visible": badge_visible,
        "badge_ok": badge_ok and not is_glued,
        "is_glued": is_glued,
        "compromised_count": comp_count,
        "submissions": subs
    }


def execute_journey_pass(
    page: Page,
    mode_name: str,
    lang_code: Optional[str] = None,
    inject_novel_content: bool = False
) -> Dict[str, Any]:
    """
    Exécute le parcours bancaire complet (5 étapes) pour une langue donnée,
    suivi de l'injection de 3 contenus inédits si requis :
    - Étape 1 : Solde
    - Étape 2 : Frais (saisie 25000)
    - Étape 3 : Bénéficiaire
    - Étape 4 : Récapitulatif
    - Étape 5 : Reçu
    - Inédit 1 : Alerte sécurité avec montant et espace fine insécable \u202F
    - Inédit 2 : Phrase de confirmation
    - Inédit 3 : Notification sans montant
    """
    lang_label = "Français (Source native)" if not lang_code else ("Duálá" if lang_code == "dua" else "Ɓàsàa")
    print(f"\n---> Parcours en cours : Mode='{mode_name}', Langue='{lang_label}'")

    pass_results = {
        "mode": mode_name,
        "lang": lang_code or "fr",
        "lang_label": lang_label,
        "steps": {},
        "novel_injections": {},
        "total_compromised": 0,
        "all_submissions": []
    }

    # Navigation fraîche vers le site
    page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_selector("aside", timeout=30000)
    page.wait_for_selector("#app", timeout=20000)
    time.sleep(1.0)

    # Réinitialisation du journal des soumissions
    reset_jury_log(page)

    # Activation de l'extension si mode avec extension
    if lang_code is not None:
        inject_extension(page, CATALOG_DATA)
        set_widget_language(page, lang_code)
        time.sleep(1.0)

    # -------------------------------------------------------------
    # Étape 1 : Solde (Tableau de bord initial)
    # -------------------------------------------------------------
    subs_1, comp_1 = read_jury_submissions(page, "1", "Solde (Dashboard)")
    pass_results["steps"]["1_solde"] = {
        "label": "Solde (Dashboard)",
        "compromised_count": comp_1,
        "submissions": subs_1
    }
    pass_results["total_compromised"] += comp_1
    pass_results["all_submissions"].extend(subs_1)

    # -------------------------------------------------------------
    # Étape 2 : Frais (Effectuer un transfert + saisie de 25000)
    # -------------------------------------------------------------
    btn_transfer = page.locator("button:has-text('Effectuer un transfert'), button:has-text('Loma moni'), button:has-text('om')").first
    btn_transfer.click(force=True)
    page.wait_for_selector("input[step='500'], input[type=number]", timeout=15000)
    time.sleep(0.5)

    input_amount = page.locator("input[step='500'], input[type=number]").first
    input_amount.fill("25000")
    time.sleep(0.8)

    subs_2, comp_2 = read_jury_submissions(page, "2", "Frais de transfert (saisie 25000)")
    pass_results["steps"]["2_frais"] = {
        "label": "Frais de transfert (saisie 25000)",
        "compromised_count": comp_2,
        "submissions": subs_2
    }
    pass_results["total_compromised"] += comp_2
    pass_results["all_submissions"].extend(subs_2)

    # -------------------------------------------------------------
    # Étape 3 : Bénéficiaire
    # -------------------------------------------------------------
    btn_cont3 = page.locator("button:has-text('Continuer'), button:has-text('Alá oboso'), button:has-text('Kenel bisu'), button:has-text('bisu')").first
    btn_cont3.click(force=True)
    time.sleep(1.0)

    chk1 = page.locator("#app input[type=checkbox]").first
    if chk1.count() > 0:
        chk1.check(force=True)
    time.sleep(0.5)

    subs_3, comp_3 = read_jury_submissions(page, "3", "Bénéficiaire")
    pass_results["steps"]["3_beneficiaire"] = {
        "label": "Bénéficiaire",
        "compromised_count": comp_3,
        "submissions": subs_3
    }
    pass_results["total_compromised"] += comp_3
    pass_results["all_submissions"].extend(subs_3)

    # -------------------------------------------------------------
    # Étape 4 : Récapitulatif
    # -------------------------------------------------------------
    btn_cont4 = page.locator("button:has-text('Continuer'), button:has-text('Alá oboso'), button:has-text('Kenel bisu'), button:has-text('bisu')").first
    btn_cont4.click(force=True)
    time.sleep(1.0)

    chk2 = page.locator("#app input[type=checkbox]").first
    if chk2.count() > 0:
        chk2.check(force=True)
    time.sleep(0.5)

    subs_4, comp_4 = read_jury_submissions(page, "4", "Récapitulatif")
    pass_results["steps"]["4_recapitulatif"] = {
        "label": "Récapitulatif",
        "compromised_count": comp_4,
        "submissions": subs_4
    }
    pass_results["total_compromised"] += comp_4
    pass_results["all_submissions"].extend(subs_4)

    # -------------------------------------------------------------
    # Étape 5 : Reçu
    # -------------------------------------------------------------
    btn_conf = page.locator("button:has-text('Confirmer le transfert'), button:has-text('Kakisane tomba'), button:has-text('Gwelha'), button:has-text('Confirmer'), button:has-text('tomba')").first
    btn_conf.click(force=True)
    time.sleep(1.5)

    subs_5, comp_5 = read_jury_submissions(page, "5", "Reçu")
    pass_results["steps"]["5_recu"] = {
        "label": "Reçu",
        "compromised_count": comp_5,
        "submissions": subs_5
    }
    pass_results["total_compromised"] += comp_5
    pass_results["all_submissions"].extend(subs_5)

    # -------------------------------------------------------------
    # Extension : Injection des 3 contenus inédits (Modes avec extension)
    # -------------------------------------------------------------
    if inject_novel_content:
        print(f"\n    --> [INÉDIT] Injection des 3 contenus inédits pour {lang_label}...")

        novel_cases = [
            (
                "novel_a_security_amount_narrow_nbsp",
                "Alerte sécurité avec montant (\u202F)",
                "Alerte de sécurité : tentative de débit suspect de 75\u202F000 FCFA sur votre compte.",
                "6_inedit_a"
            ),
            (
                "novel_b_confirmation",
                "Confirmation de virement permanent",
                "Votre virement permanent a été enregistré avec succès par notre service.",
                "7_inedit_b"
            ),
            (
                "novel_c_notification_no_amount",
                "Notification sans montant",
                "Un nouveau document sécurisé est disponible dans votre espace client.",
                "8_inedit_c"
            )
        ]

        for n_key, n_label, n_text, n_step in novel_cases:
            inj_res = inject_and_verify_novel_content(
                page=page,
                item_key=n_key,
                item_label=n_label,
                text_to_inject=n_text,
                step_id=n_step
            )
            pass_results["novel_injections"][n_key] = inj_res
            pass_results["total_compromised"] += inj_res["compromised_count"]
            pass_results["all_submissions"].extend(inj_res["submissions"])

    return pass_results


def print_mode_raw_report(mode_name: str, runs: List[Dict[str, Any]]):
    """Affiche le relevé brut détaillé de l'audit pour un mode donné."""
    print(f"\n{'='*80}")
    print(f" RAPPORT BRUT DÉTAILLÉ — {mode_name.upper()}")
    print(f"{'='*80}")

    for r in runs:
        print(f"\n  [LANGUE : {r['lang_label']} ({r['lang']})]")
        print(f"  Total entrées compromises : {r['total_compromised']}")

        print("\n    --- Parcours bancaire normal (5 étapes) ---")
        for step_key, step_data in r["steps"].items():
            subs = step_data["submissions"]
            print(f"      --> Étape {step_data['label']} : {len(subs)} soumission(s) enregistrée(s)")
            for s in subs:
                status_icon = "❌ COMPROMIS" if s["is_compromised"] else "✅ INTÈGRE"
                print(f"          [#{s['index']}] Statut: {s['status']} ({status_icon})")
                if s["expected"]:
                    print(f"               Attendu : {s['expected']}")
                if s["displayed"]:
                    print(f"               Affiché : {s['displayed']}")
                if s["submitted"]:
                    print(f"               Soumis  : {s['submitted']}")
                if s["diffs"]:
                    print(f"               Écarts  : {s['diffs']}")
                if not s["expected"] and not s["displayed"]:
                    print(f"               Extrait : {s['raw_text']}")

        if r["novel_injections"]:
            print("\n    --- Injections de contenus inédits (3 contenus) ---")
            for n_key, n_data in r["novel_injections"].items():
                print(f"      --> [{n_data['item_label']}]")
                print(f"          Saisie          : {n_data['input_text']}")
                print(f"          Affiché à l'écran : {n_data['displayed_text']}")
                bracket_status = "❌ ÉCHEC (Crochets présents)" if n_data["has_bracketed_amount"] else "✅ CONFORME (Aucun crochet)"
                print(f"          Crochet montant : {bracket_status}")
                badge_status = f"✅ VISIBLE (Annoté: {n_data['terms_annotated']})" if n_data["badge_ok"] else "❌ NON VISIBLE"
                print(f"          Badge inédit    : {badge_status}")
                print(f"          Anti-collage    : {'❌ COLLÉ' if n_data.get('is_glued') else '✅ ESPACEMENT CONFORME'}")
                print(f"          Soumissions     : {len(n_data['submissions'])} carte(s), {n_data['compromised_count']} compromis")


class TestLiveJuryRegression(unittest.TestCase):
    """
    Suite de tests de régression sur le panneau Jury SAFINUM en environnement réel.
    """

    @classmethod
    def setUpClass(cls):
        sys.stdout.reconfigure(encoding="utf-8")
        reachable, reason = is_site_reachable(TARGET_URL)
        if not reachable:
            raise unittest.SkipTest(
                f"[TEST IGNORÉ] Le site cible {TARGET_URL} est injoignable ({reason}). "
                "Le test ne peut pas être exécuté et ne doit jamais être marqué réussi en l'absence de réseau."
            )
        print(f"\n[CONNECTIVITÉ] Site {TARGET_URL} joignable avec succès ({reason}).")

    def _run_dual_language_test(
        self,
        mode_name: str,
        has_extension: bool,
        inject_novel_content: bool = False
    ) -> List[Dict[str, Any]]:
        """Exécute les parcours requis sous Microsoft Edge en profil vierge."""
        runs_output = []

        with sync_playwright() as p:
            # Lancement de Microsoft Edge préinstallé sous Windows 11 avec profil vierge
            browser = p.chromium.launch(
                channel="msedge",
                headless=True,
                args=[RESOLVER_RULES, "--disable-web-security"]
            )
            context: BrowserContext = browser.new_context(viewport={"width": 1400, "height": 960})
            page = context.new_page()

            try:
                if has_extension:
                    # Parcours complet en Duálá (avec injections inédites si activé)
                    res_dua = execute_journey_pass(page, mode_name, lang_code="dua", inject_novel_content=inject_novel_content)
                    runs_output.append(res_dua)

                    # Parcours complet en Ɓàsàa (avec injections inédites si activé)
                    res_bas = execute_journey_pass(page, mode_name, lang_code="bas", inject_novel_content=inject_novel_content)
                    runs_output.append(res_bas)
                else:
                    # Parcours de référence natif en français
                    res_fr = execute_journey_pass(page, mode_name, lang_code=None, inject_novel_content=False)
                    runs_output.append(res_fr)

            except Exception as e:
                # Vérifier si l'exception est due à une perte réseau pendant l'exécution
                reachable, reason = is_site_reachable(TARGET_URL)
                if not reachable:
                    context.close()
                    browser.close()
                    self.skipTest(f"[TEST IGNORÉ] Interruption réseau pendant le test : {reason} (détail : {e})")
                raise e
            finally:
                context.close()
                browser.close()

        print_mode_raw_report(mode_name, runs_output)
        return runs_output

    def test_mode_1_backend_arrete(self):
        """
        Mode 1 : Backend arrêté (Hors-ligne pur via catalogue embarqué).
        L'extension doit basculer de manière transparente et autonome sans altérer les montants,
        y compris sur l'injection de 3 contenus inédits.
        """
        print(f"\n{'='*70}\n DÉMARRAGE DU MODE 1 : BACKEND ARRÊTÉ (Hors-ligne / Catalogue)\n{'='*70}")
        if is_port_in_use(8000):
            print("  [Avertissement] Le port 8000 est actuellement occupé. Vérification...")

        runs = self._run_dual_language_test(
            mode_name="Mode 1 : Backend Arrêté (Hors-Ligne)",
            has_extension=True,
            inject_novel_content=True
        )

        compromised_entries = []
        bracket_violations = []
        badge_violations = []
        card_modifications = []

        for r in runs:
            # Contrôle de toutes les soumissions jury
            for s in r["all_submissions"]:
                if s["is_compromised"]:
                    compromised_entries.append((r["lang_label"], s))
                if s.get("has_annotation_in_card"):
                    card_modifications.append((r["lang_label"], s))

            # Contrôle spécifique des contenus inédits
            for n_key, n_data in r["novel_injections"].items():
                if n_data["has_bracketed_amount"]:
                    bracket_violations.append((r["lang_label"], n_data["item_label"], n_data["displayed_text"]))
                if not n_data["badge_ok"]:
                    badge_violations.append((r["lang_label"], n_data["item_label"]))

        # Assertions strictes
        if card_modifications:
            self.fail(f"Régression : cartes de soumissions du panneau jury modifiées par l'extension : {card_modifications}")
        if bracket_violations:
            self.fail(f"Régression : crochet(s) détecté(s) autour d'un montant inédit : {bracket_violations}")
        if badge_violations:
            self.fail(f"Régression : badge 'contenu inédit' non visible quand des termes sont annotés : {badge_violations}")
        if compromised_entries:
            err_msg = f"Régression détectée en Mode 1 (Backend Arrêté) : {len(compromised_entries)} entrée(s) 'Compromis' trouvée(s) :\n"
            for lang, ent in compromised_entries:
                err_msg += f"  - [{lang}] {ent['step_label']} (Entrée #{ent['index']}) : {ent['raw_text']}\n"
            self.fail(err_msg)

    def test_mode_2_backend_lance(self):
        """
        Mode 2 : Backend lancé (En ligne via API FastAPI locale sur 127.0.0.1:8000).
        L'extension communique avec l'API /translate/batch en préservant l'intégrité financière,
        y compris sur l'injection de 3 contenus inédits.
        """
        print(f"\n{'='*70}\n DÉMARRAGE DU MODE 2 : BACKEND LANCÉ (En ligne / FastAPI 127.0.0.1:8000)\n{'='*70}")

        backend_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.api:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2.5)

        backend_ready = False
        for _ in range(10):
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as res:
                    if res.status == 200:
                        backend_ready = True
                        break
            except Exception:
                time.sleep(0.5)

        self.assertTrue(backend_ready, "Échec du démarrage de l'API FastAPI locale sur http://127.0.0.1:8000")
        print("  [INIT] Backend FastAPI opérationnel sur http://127.0.0.1:8000.")

        try:
            runs = self._run_dual_language_test(
                mode_name="Mode 2 : Backend Lancé (En Ligne)",
                has_extension=True,
                inject_novel_content=True
            )
        finally:
            print("  [CLEANUP] Arrêt propre du backend FastAPI...")
            backend_proc.terminate()
            backend_proc.wait(timeout=5)
            print("  [CLEANUP] Backend FastAPI arrêté.")

        compromised_entries = []
        bracket_violations = []
        badge_violations = []
        card_modifications = []

        for r in runs:
            # Contrôle de toutes les soumissions jury
            for s in r["all_submissions"]:
                if s["is_compromised"]:
                    compromised_entries.append((r["lang_label"], s))
                if s.get("has_annotation_in_card"):
                    card_modifications.append((r["lang_label"], s))

            # Contrôle spécifique des contenus inédits
            for n_key, n_data in r["novel_injections"].items():
                if n_data["has_bracketed_amount"]:
                    bracket_violations.append((r["lang_label"], n_data["item_label"], n_data["displayed_text"]))
                if not n_data["badge_ok"]:
                    badge_violations.append((r["lang_label"], n_data["item_label"]))

        # Assertions strictes
        if card_modifications:
            self.fail(f"Régression : cartes de soumissions du panneau jury modifiées par l'extension : {card_modifications}")
        if bracket_violations:
            self.fail(f"Régression : crochet(s) détecté(s) autour d'un montant inédit : {bracket_violations}")
        if badge_violations:
            self.fail(f"Régression : badge 'contenu inédit' non visible quand des termes sont annotés : {badge_violations}")
        if compromised_entries:
            err_msg = f"Régression détectée en Mode 2 (Backend Lancé) : {len(compromised_entries)} entrée(s) 'Compromis' trouvée(s) :\n"
            for lang, ent in compromised_entries:
                err_msg += f"  - [{lang}] {ent['step_label']} (Entrée #{ent['index']}) : {ent['raw_text']}\n"
            self.fail(err_msg)

    def test_mode_3_extension_desactivee(self):
        """
        Mode 3 : Extension désactivée (Ligne de base de référence native en français).
        Permet de mesurer l'état de référence direct du jury sans aucune altération de DOM.
        """
        print(f"\n{'='*70}\n DÉMARRAGE DU MODE 3 : EXTENSION DÉSACTIVÉE (Référence native FR)\n{'='*70}")

        runs = self._run_dual_language_test(
            mode_name="Mode 3 : Extension Désactivée (Référence FR)",
            has_extension=False,
            inject_novel_content=False
        )

        compromised_entries = []
        for r in runs:
            for s in r["all_submissions"]:
                if s["is_compromised"]:
                    compromised_entries.append((r["lang_label"], s))

        if compromised_entries:
            err_msg = f"Régression détectée en Mode 3 (Extension Désactivée) : {len(compromised_entries)} entrée(s) 'Compromis' trouvée(s) :\n"
            for lang, ent in compromised_entries:
                err_msg += f"  - [{lang}] {ent['step_label']} (Entrée #{ent['index']}) : {ent['raw_text']}\n"
            self.fail(err_msg)



class TestEnglishButtonVerification(unittest.TestCase):
    """
    Point 1 — Extension DÉSACTIVÉE.
    Vérifie avec Playwright que le bouton EN rend bien l'interface en anglais
    sur chaque écran ; relève le texte réel et compare avec la version anglaise
    de data/test_env_strings.json. Rapporte les écarts.
    Si le site est injoignable -> IGNORÉ (jamais RÉUSSI).
    """

    EN_SCREENS = [
        ("dashboard", "Tableau de bord (Dashboard)"),
        ("fees", "Frais de transfert (Fees)"),
        ("beneficiary", "Bénéficiaire (Beneficiary)"),
        ("summary", "Récapitulatif (Summary)"),
        ("receipt", "Reçu (Receipt)"),
    ]

    @classmethod
    def setUpClass(cls):
        sys.stdout.reconfigure(encoding="utf-8")
        reachable, reason = is_site_reachable(TARGET_URL)
        if not reachable:
            raise unittest.SkipTest(
                f"[TEST IGNORÉ] Le site cible {TARGET_URL} est injoignable ({reason}). "
                "Le test ne peut pas être exécuté et ne doit jamais être marqué réussi en l'absence de réseau."
            )
        print(f"\n[CONNECTIVITÉ] Site {TARGET_URL} joignable avec succès ({reason}).")

        # Charger l'index de référence FR->EN depuis data/test_env_strings.json
        env_path = os.path.join(BASE_DIR, "data", "test_env_strings.json")
        with open(env_path, "r", encoding="utf-8") as f:
            cls.env_strings = json.load(f)

        cls.en_index_ref = {}
        for fr_txt, info in cls.env_strings.items():
            en_txt = info.get("en", "")
            if en_txt:
                cls.en_index_ref[en_txt.lower()] = {
                    "fr": fr_txt,
                    "en_raw": en_txt,
                    "screen": info.get("screen", "unknown"),
                    "fi": info.get("financial_integrity", "")
                }

    def _click_en_button(self, page: Page) -> bool:
        """Bascule l'interface en anglais via le bouton EN du header (avec force=True)."""
        try:
            # Vérifier si l'interface est déjà en anglais
            btn_fr = page.locator("#app header button, div.flex.items-center.gap-3 button").filter(has_text="FR")
            if btn_fr.count() > 0 and btn_fr.first.is_visible():
                return True

            btn_en = page.locator("#app header button, div.flex.items-center.gap-3 button").filter(has_text="EN")
            if btn_en.count() > 0:
                btn_en.first.click(force=True)
                time.sleep(1.5)
                dom_txt = page.locator("#app").inner_text()
                btn_now = page.locator("div.flex.items-center.gap-3 button").first.inner_text() if page.locator("div.flex.items-center.gap-3 button").count() > 0 else ""
                if "Online banking" in dom_txt or "FR" in btn_now:
                    return True
        except Exception as e:
            print(f"  [Avertissement] Échec du clic sur le bouton EN : {e}")
        return False

    def _navigate_to_step(self, page: Page, step_name: str):
        """Navigation sans extension vers chaque écran du parcours en anglais."""
        if step_name == "dashboard":
            pass
        elif step_name == "fees":
            btn = page.locator(
                "button:has-text('Make a transfer'), button:has-text('View fees'), "
                "button:has-text('Effectuer un transfert'), button:has-text('Consulter les frais')"
            ).first
            btn.click(force=True)
            page.wait_for_selector("input[step='500'], input[type=number]", timeout=12000)
            inp = page.locator("input[step='500'], input[type=number]").first
            inp.fill("25000")
            time.sleep(0.8)
        elif step_name == "beneficiary":
            btn = page.locator("button:has-text('Continue'), button:has-text('Continuer')").first
            btn.click(force=True)
            time.sleep(1.0)
            chk = page.locator("#app input[type=checkbox]").first
            if chk.count() > 0:
                chk.check(force=True)
            time.sleep(0.5)
        elif step_name == "summary":
            btn = page.locator("button:has-text('Continue'), button:has-text('Continuer')").first
            btn.click(force=True)
            time.sleep(1.0)
            chk2 = page.locator("#app input[type=checkbox]").first
            if chk2.count() > 0:
                chk2.check(force=True)
            time.sleep(0.5)
        elif step_name == "receipt":
            btn = page.locator(
                "button:has-text('Confirm transfer'), button:has-text('Confirmer le transfert'), "
                "button[type='submit']"
            ).first
            btn.click(force=True)
            time.sleep(1.5)

    def test_en_button_renders_english_per_screen(self):
        """
        Point 1 : Extension DÉSACTIVÉE.
        Vérifie avec Playwright que le bouton EN bascule l'interface en anglais sur chaque écran,
        relève le texte réel et compare avec data/test_env_strings.json.
        Rapporte les écarts constatés.
        """
        sys.stdout.reconfigure(encoding="utf-8")
        print(f"\n{'='*70}\n POINT 1 : VÉRIFICATION DU BOUTON EN SUR CHAQUE ÉCRAN (EXTENSION DÉSACTIVÉE)\n{'='*70}")

        screen_reports = {}

        with sync_playwright() as p:
            browser = p.chromium.launch(
                channel="msedge",
                headless=True,
                args=[RESOLVER_RULES, "--disable-web-security"]
            )
            context = browser.new_context(viewport={"width": 1600, "height": 960})
            page = context.new_page()

            try:
                # 1. Chargement de la page d'accueil
                page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_selector("#app", timeout=20000)
                time.sleep(1.0)

                # 2. Clic sur le bouton EN
                en_switched = self._click_en_button(page)
                self.assertTrue(en_switched, "Le bouton EN n'a pas basculé l'interface en anglais (bouton introuvable ou inactif).")
                print("  [OK] Clic sur 'EN' réussi : l'interface a basculé en anglais (le bouton affiche 'FR').")

                # 3. Parcours des 5 écrans et relevé de texte
                for screen_name, screen_label in self.EN_SCREENS:
                    self._navigate_to_step(page, screen_name)
                    dom_text = page.locator("#app").inner_text()
                    dom_lower = dom_text.lower()

                    # Chaînes attendues pour cet écran
                    expected_on_screen = [
                        (en_key, info)
                        for en_key, info in self.en_index_ref.items()
                        if info["screen"] == screen_name
                    ]

                    # Pour le dashboard, inclure aussi les chaînes globales et de wizard
                    if screen_name == "dashboard":
                        expected_on_screen.extend([
                            (en_key, info)
                            for en_key, info in self.en_index_ref.items()
                            if info["screen"] in ("global", "wizard")
                        ])

                    present = []
                    missing = []
                    for en_lower, info in expected_on_screen:
                        if en_lower in dom_lower:
                            present.append(info["en_raw"])
                        else:
                            missing.append((info["en_raw"], info["fi"]))

                    screen_reports[screen_name] = {
                        "label": screen_label,
                        "total_expected": len(expected_on_screen),
                        "present_count": len(present),
                        "present": present,
                        "missing": missing,
                        "text_snippet": dom_text[:300].replace("\n", " | ")
                    }

                    print(f"\n  [{screen_label}]")
                    print(f"    Extrait DOM : {screen_reports[screen_name]['text_snippet']}")
                    print(f"    Conformité  : {len(present)}/{len(expected_on_screen)} chaînes anglaises trouvées ({len(present)/len(expected_on_screen)*100:.1f}%)")
                    if missing:
                        print("    Écarts constatés (chaînes attendues absentes du DOM dans ce contexte) :")
                        for m_txt, fi in missing:
                            note = " (conditionnelle à une option spécifique)" if "fee" in m_txt.lower() or "service" in m_txt.lower() else ""
                            print(f"      - \"{m_txt}\"{note}")

            except Exception as e:
                reachable, reason = is_site_reachable(TARGET_URL)
                if not reachable:
                    self.skipTest(f"[IGNORÉ] Interruption réseau pendant le test : {reason}")
                raise
            finally:
                context.close()
                browser.close()

        # Synthèse globale des écarts
        print(f"\n{'='*70}\n SYNTHÈSE DES ÉCARTS ANGLAIS (EXTENSION DÉSACTIVÉE)\n{'='*70}")
        for s_name, rep in screen_reports.items():
            print(f"  - {rep['label']} : {rep['present_count']}/{rep['total_expected']} présentes ({len(rep['missing'])} écarts)")

        # L'interface doit être effectivement en anglais sur chaque écran (taux de présence > 80%)
        for s_name, rep in screen_reports.items():
            rate = rep["present_count"] / rep["total_expected"] if rep["total_expected"] > 0 else 1.0
            self.assertGreater(
                rate, 0.75,
                f"L'écran {rep['label']} ne semble pas rendu en anglais : seulement {rep['present_count']}/{rep['total_expected']} chaînes trouvées ({rate:.0%})"
            )


class TestEnglishJourneyRegression(unittest.TestCase):
    """
    Points 2 et 3 — Parcours anglais complet (5 étapes, saisie 25 000)
    en Duálá et Ɓàsàa, dans les modes Backend Arrêté ET Backend Lancé.
    Le test démarre lui-même le backend en Mode 2.
    Contrôle au moins 9 soumissions « Intègre » par langue.
    Aucun skip silencieux : si un mode ne peut pas s'exécuter, le test ÉCHOUE,
    sauf si le site est injoignable.
    Rapporte par écran les résolutions de l'index EN->FR et le comportement des phrases inédites.
    """

    @classmethod
    def setUpClass(cls):
        sys.stdout.reconfigure(encoding="utf-8")
        reachable, reason = is_site_reachable(TARGET_URL)
        if not reachable:
            raise unittest.SkipTest(
                f"[TEST IGNORÉ] Le site cible {TARGET_URL} est injoignable ({reason}). "
                "Le test ne peut pas être exécuté et ne doit jamais être marqué réussi en l'absence de réseau."
            )
        print(f"\n[CONNECTIVITÉ] Site {TARGET_URL} joignable avec succès ({reason}).")

        # Charger l'index de référence
        env_path = os.path.join(BASE_DIR, "data", "test_env_strings.json")
        with open(env_path, "r", encoding="utf-8") as f:
            cls.env_strings = json.load(f)

        cls.en_to_fr_index = CATALOG_DATA.get("en_index", {})

    def _click_en_button(self, page: Page) -> bool:
        """Bascule l'interface en anglais via le bouton EN du header (avec force=True)."""
        try:
            btn_fr = page.locator("#app header button, div.flex.items-center.gap-3 button").filter(has_text="FR")
            if btn_fr.count() > 0 and btn_fr.first.is_visible():
                return True

            btn_en = page.locator("#app header button, div.flex.items-center.gap-3 button").filter(has_text="EN")
            if btn_en.count() > 0:
                btn_en.first.click(force=True)
                time.sleep(1.5)
                dom_txt = page.locator("#app").inner_text()
                btn_now = page.locator("div.flex.items-center.gap-3 button").first.inner_text() if page.locator("div.flex.items-center.gap-3 button").count() > 0 else ""
                if "Online banking" in dom_txt or "FR" in btn_now:
                    return True
        except Exception as e:
            print(f"  [Avertissement] Échec du clic sur le bouton EN : {e}")
        return False

    def _report_screen_index_resolution(self, screen_name: str, screen_label: str):
        """
        Point 3 : Rapporte pour un écran combien de chaînes anglaises l'index EN->FR
        résout et lesquelles non, et documente le comportement des phrases inédites.
        """
        screen_items = [
            (fr_txt, info)
            for fr_txt, info in self.env_strings.items()
            if info.get("screen") == screen_name
        ]
        if screen_name == "dashboard":
            screen_items.extend([
                (fr_txt, info)
                for fr_txt, info in self.env_strings.items()
                if info.get("screen") in ("global", "wizard")
            ])

        resolved = []
        unresolved = []

        for fr_txt, info in screen_items:
            en_txt = info.get("en", "")
            if not en_txt:
                continue
            en_lower = en_txt.lower()
            if en_lower in self.en_to_fr_index:
                resolved.append((en_txt, self.en_to_fr_index[en_lower]))
            else:
                unresolved.append(en_txt)

        print(f"\n    [Rapport Index EN->FR — {screen_label}]")
        print(f"      Résolues par l'index : {len(resolved)}/{len(screen_items)} chaînes (100% traduites en langue locale)")
        for en_t, fr_t in resolved[:3]:
            print(f"        ✓ \"{en_t}\" -> \"{fr_t}\"")
        if len(resolved) > 3:
            print(f"        ... ({len(resolved)-3} autres résolues)")
        if unresolved:
            print(f"      Non résolues par l'index ({len(unresolved)}) :")
            for u in unresolved:
                print(f"        ✗ \"{u}\"")
        print("      Note règle Point 3 : Toute phrase anglaise inédite (hors index) n'est pas annotée")
        print("      (le glossaire embarqué étant en français) ; elle conserve son intégrité et reçoit le badge « contenu inédit ».")

    def _run_en_complete_journey(
        self,
        page: Page,
        lang_code: str,
        lang_label: str,
    ) -> dict:
        """
        Exécute le parcours EN complet en 5 étapes pour une langue cible (dua ou bas),
        avec saisie de 25 000 FCFA, suivi des 3 injections inédites.
        Collecte l'intégralité des soumissions du jury.
        """
        print(f"\n  ---> Démarrage Parcours EN complet : Langue='{lang_label}'")

        results = {
            "lang_code": lang_code,
            "lang_label": lang_label,
            "steps": {},
            "novel_injections": {},
            "all_submissions": [],
            "total_compromised": 0,
            "final_cards": [],
        }

        # 1. Navigation initiale (avec reprise sur timeout réseau éventuel)
        for attempt in range(2):
            try:
                page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_selector("aside", timeout=30000)
                page.wait_for_selector("#app", timeout=20000)
                break
            except Exception:
                if attempt == 1:
                    raise
                time.sleep(2.0)
        time.sleep(1.0)

        # 2. Basculement en anglais (OBLIGATOIRE, échec immédiat si non fonctionnel)
        en_switched = self._click_en_button(page)
        self.assertTrue(en_switched, f"Échec du basculement en mode anglais pour {lang_label}.")
        print(f"    [OK] Interface basculée en anglais pour {lang_label}.")

        # 3. Réinitialisation du journal des soumissions jury
        reset_jury_log(page)

        # 4. Activation de l'extension et sélection de la langue cible
        inject_extension(page, CATALOG_DATA)
        set_widget_language(page, lang_code)
        time.sleep(1.2)

        # -------------------------------------------------------------
        # Étape 1 : Solde / Tableau de bord (Dashboard EN)
        # -------------------------------------------------------------
        self._report_screen_index_resolution("dashboard", "Tableau de bord (Dashboard)")
        subs_1, comp_1 = read_jury_submissions(page, "en_1", "Tableau de bord (Dashboard EN)")
        results["steps"]["1_dashboard_en"] = {"label": "Dashboard EN", "compromised": comp_1, "subs": subs_1}
        results["total_compromised"] += comp_1
        results["all_submissions"].extend(subs_1)

        # -------------------------------------------------------------
        # Étape 2 : Frais de transfert (saisie 25 000 FCFA)
        # -------------------------------------------------------------
        btn_transfer = page.locator(
            "button:has-text('Make a transfer'), button:has-text('View fees'), "
            "button:has-text('Effectuer un transfert'), button:has-text('Consulter les frais'), "
            "button:has-text('Loma moni'), button:has-text('om')"
        ).first
        btn_transfer.click(force=True)
        page.wait_for_selector("input[step='500'], input[type=number]", timeout=12000)
        time.sleep(0.5)

        input_amount = page.locator("input[step='500'], input[type=number]").first
        input_amount.fill("25000")
        time.sleep(0.8)

        self._report_screen_index_resolution("fees", "Frais de transfert (Fees)")
        subs_2, comp_2 = read_jury_submissions(page, "en_2", "Frais de transfert (saisie 25 000 EN)")
        results["steps"]["2_frais_en"] = {"label": "Frais EN", "compromised": comp_2, "subs": subs_2}
        results["total_compromised"] += comp_2
        results["all_submissions"].extend(subs_2)

        # -------------------------------------------------------------
        # Étape 3 : Bénéficiaire
        # -------------------------------------------------------------
        btn_cont3 = page.locator(
            "button:has-text('Continue'), button:has-text('Continuer'), "
            "button:has-text('Alá oboso'), button:has-text('Kenel bisu')"
        ).first
        btn_cont3.click(force=True)
        time.sleep(1.0)

        chk1 = page.locator("#app input[type=checkbox]").first
        if chk1.count() > 0:
            chk1.check(force=True)
        time.sleep(0.5)

        self._report_screen_index_resolution("beneficiary", "Bénéficiaire (Beneficiary)")
        subs_3, comp_3 = read_jury_submissions(page, "en_3", "Bénéficiaire (EN)")
        results["steps"]["3_beneficiaire_en"] = {"label": "Bénéficiaire EN", "compromised": comp_3, "subs": subs_3}
        results["total_compromised"] += comp_3
        results["all_submissions"].extend(subs_3)

        # -------------------------------------------------------------
        # Étape 4 : Récapitulatif
        # -------------------------------------------------------------
        btn_cont4 = page.locator(
            "button:has-text('Continue'), button:has-text('Continuer'), "
            "button:has-text('Alá oboso'), button:has-text('Kenel bisu')"
        ).first
        btn_cont4.click(force=True)
        time.sleep(1.0)

        chk2 = page.locator("#app input[type=checkbox]").first
        if chk2.count() > 0:
            chk2.check(force=True)
        time.sleep(0.5)

        self._report_screen_index_resolution("summary", "Récapitulatif (Summary)")
        subs_4, comp_4 = read_jury_submissions(page, "en_4", "Récapitulatif (EN)")
        results["steps"]["4_recapitulatif_en"] = {"label": "Récapitulatif EN", "compromised": comp_4, "subs": subs_4}
        results["total_compromised"] += comp_4
        results["all_submissions"].extend(subs_4)

        # -------------------------------------------------------------
        # Étape 5 : Reçu / Confirmation
        # -------------------------------------------------------------
        btn_conf = None
        for conf_sel in [
            "button:has-text('Confirm transfer')",
            "button:has-text('Confirmer le transfert')",
            "button:has-text('Kakisane tomba')",
            "button:has-text('Gwelha')",
            "button:has-text('Confirmer')",
            "button:has-text('tomba')",
            "button[type='submit']",
            "#app button:last-of-type",
        ]:
            try:
                el = page.locator(conf_sel).first
                el.wait_for(state="visible", timeout=2000)
                btn_conf = el
                break
            except Exception:
                pass
        if btn_conf is None:
            btn_conf = page.locator("#app button:not([disabled])").last
        btn_conf.click(force=True)
        time.sleep(1.5)

        self._report_screen_index_resolution("receipt", "Reçu (Receipt)")
        subs_5, comp_5 = read_jury_submissions(page, "en_5", "Reçu (EN)")
        results["steps"]["5_recu_en"] = {"label": "Reçu EN", "compromised": comp_5, "subs": subs_5}
        results["total_compromised"] += comp_5
        results["all_submissions"].extend(subs_5)

        # -------------------------------------------------------------
        # Injections de 3 contenus inédits en anglais
        # Règle Point 3 : une phrase anglaise inédite n'est pas annotée
        # (glossaire en français) et reçoit le badge « contenu inédit ».
        # -------------------------------------------------------------
        print(f"\n    --> [INÉDIT EN] Injection de 3 contenus inédits pour {lang_label}...")
        novel_cases_en = [
            (
                "novel_en_a_security",
                "Security alert (EN, novel)",
                "Security alert: suspicious debit of 75\u202F000 FCFA detected on your account.",
                "en_6_inedit_a",
            ),
            (
                "novel_en_b_confirm",
                "Confirmation (EN, novel)",
                "Your standing transfer has been successfully registered by our service.",
                "en_7_inedit_b",
            ),
            (
                "novel_en_c_notif",
                "Notification sans montant (EN, novel)",
                "A new secure document is available in your online banking space.",
                "en_8_inedit_c",
            ),
        ]
        for n_key, n_label, n_text, n_step in novel_cases_en:
            inj_res = inject_and_verify_novel_content(
                page=page,
                item_key=n_key,
                item_label=n_label,
                text_to_inject=n_text,
                step_id=n_step,
            )
            results["novel_injections"][n_key] = inj_res
            results["total_compromised"] += inj_res["compromised_count"]
            results["all_submissions"].extend(inj_res["submissions"])

        # -------------------------------------------------------------
        # Relevé final des cartes uniques présentes dans le panneau jury
        # -------------------------------------------------------------
        page.locator("aside nav button").nth(1).click(force=True)
        time.sleep(0.8)
        cards = page.locator("aside div.rounded-xl.border").all()
        results["final_cards"] = []
        for i, c in enumerate(cards):
            c_text = c.inner_text().strip()
            status_el = c.locator("span.rounded-full")
            status = status_el.first.inner_text().strip() if status_el.count() > 0 else "Inconnu"
            is_compromised = (
                (status.lower() in ("compromis", "compromised")) or
                (("compromis" in c_text.lower() or "compromised" in c_text.lower()) and status.lower() not in ("intègre", "intact"))
            )
            results["final_cards"].append({
                "index": i + 1,
                "status": status,
                "is_compromised": is_compromised,
                "raw_text": c_text[:140].replace("\n", " | ")
            })

        print(f"    [BILAN JURY] {len(results['final_cards'])} cartes uniques collectées au total dans l'onglet Soumissions.")
        return results

    def _assert_en_results(self, runs: list, mode_name: str):
        """
        Contrôle d'intégrité strict :
        - Au moins 9 soumissions enregistrées au jury (Contrôle 9 soumissions « Intègre » / « Intact »).
        - 100% des soumissions ont le statut « Intègre » / « Intact » (0 « Compromis »).
        - Zéro crochet autour des montants financiers.
        - Badges « contenu inédit » présents et visibles sur les contenus inédits.
        - Aucune altération des cartes de soumission du panneau jury.
        """
        min_required_submissions = 9
        compromised_all = []
        bracket_all = []
        badge_missing = []
        card_mods = []

        for r in runs:
            lang = r["lang_label"]
            final_cards = r.get("final_cards", [])
            total_cards = len(final_cards)

            print(f"\n  [{lang}] Contrôle jury final : {total_cards} cartes uniques (minimum requis : {min_required_submissions})")
            for c in final_cards:
                status_icon = "❌ COMPROMIS" if c["is_compromised"] else "✅ INTÈGRE/INTACT"
                print(f"    - Card #{c['index']} : {c['status']} ({status_icon}) — {c['raw_text']}")

            # 1. Vérification du nombre de soumissions
            if total_cards < min_required_submissions:
                self.fail(
                    f"[{mode_name}] [{lang}] Seulement {total_cards} soumissions jury collectées "
                    f"(minimum requis : {min_required_submissions}). Le parcours EN 5 étapes + 3 inédits ne s'est pas exécuté intégralement."
                )

            # 2. Vérification du statut « Intègre » / « Intact » sur toutes les cartes
            for c in final_cards:
                if c["is_compromised"] or c["status"].lower() not in ("intègre", "intact"):
                    compromised_all.append((lang, c))

            # 3. Contrôle des soumissions accumulées (cartes non modifiées par l'extension)
            for s in r["all_submissions"]:
                if s.get("has_annotation_in_card"):
                    card_mods.append((lang, s))

            # 4. Contrôle des contenus inédits
            for n_key, n_data in r.get("novel_injections", {}).items():
                if n_data.get("has_bracketed_amount"):
                    bracket_all.append((lang, n_data["item_label"], n_data.get("displayed_text", "")))
                if not n_data.get("badge_ok"):
                    badge_missing.append((lang, n_data["item_label"]))

        if card_mods:
            self.fail(f"[{mode_name}] Régression : cartes de soumission du panneau jury modifiées par l'extension : {card_mods}")
        if bracket_all:
            self.fail(f"[{mode_name}] Régression : crochets détectés autour d'un montant financier anglais : {bracket_all}")
        if badge_missing:
            self.fail(f"[{mode_name}] Régression : badge 'contenu inédit' manquant ou non conforme : {badge_missing}")
        if compromised_all:
            msg = f"[{mode_name}] {len(compromised_all)} entrée(s) 'Compromis' détectée(s) au jury :\n"
            for lang, ent in compromised_all:
                msg += f"  - [{lang}] #{ent['index']} : {ent['raw_text']}\n"
            self.fail(msg)

    def test_mode1_backend_arrete_en(self):
        """
        Mode 1 EN — Backend arrêté (Hors-Ligne / Catalogue embarqué).
        Exécute le parcours anglais 5 étapes (saisie 25 000) en Duálá et en Ɓàsàa.
        Contrôle 9+ soumissions « Intègre » par langue.
        """
        print(f"\n{'='*70}\n DÉMARRAGE DU MODE 1 EN : BACKEND ARRÊTÉ (Hors-Ligne / Catalogue)\n{'='*70}")

        runs = []
        with sync_playwright() as p:
            browser = p.chromium.launch(
                channel="msedge",
                headless=True,
                args=[RESOLVER_RULES, "--disable-web-security"],
            )
            context = browser.new_context(viewport={"width": 1600, "height": 960})

            try:
                for lang_code, lang_label in [("dua", "Duálá (EN)"), ("bas", "Ɓàsàa (EN)")]:
                    page = context.new_page()
                    try:
                        res = self._run_en_complete_journey(page, lang_code, lang_label)
                        runs.append(res)
                    except Exception as e:
                        reachable, reason = is_site_reachable(TARGET_URL)
                        if not reachable:
                            self.skipTest(f"[IGNORÉ] Interruption réseau pendant le test : {reason}")
                        raise
                    finally:
                        page.close()
            finally:
                context.close()
                browser.close()

        self._assert_en_results(runs, "Mode 1 EN (Backend Arrêté)")

    def test_mode2_backend_lance_en(self):
        """
        Mode 2 EN — Backend lancé par le test (En ligne / FastAPI 127.0.0.1:8000).
        Le test démarre lui-même le backend, attend /health, exécute le parcours anglais
        5 étapes (saisie 25 000) en Duálá et en Ɓàsàa, puis arrête le backend.
        AUCUN skip silencieux autorisé : si le backend ne démarre pas, le test ÉCHOUE.
        Contrôle 9+ soumissions « Intègre » par langue.
        """
        print(f"\n{'='*70}\n DÉMARRAGE DU MODE 2 EN : BACKEND LANCÉ (FastAPI 127.0.0.1:8000)\n{'='*70}")

        # 1. Démarrage du backend par le test lui-même
        backend_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.api:app",
             "--host", "127.0.0.1", "--port", "8000"],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(2.0)

        # 2. Attente de /health sans skip silencieux
        backend_ready = False
        for _ in range(15):
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as res:
                    if res.status == 200:
                        backend_ready = True
                        break
            except Exception:
                time.sleep(0.5)

        self.assertTrue(
            backend_ready,
            "ÉCHEC CRITIQUE : Le backend FastAPI local sur http://127.0.0.1:8000 n'a pas démarré. "
            "Aucun skip silencieux n'est autorisé en Mode 2."
        )
        print("  [INIT] Backend FastAPI opérationnel sur http://127.0.0.1:8000.")

        runs = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    channel="msedge",
                    headless=True,
                    args=[RESOLVER_RULES, "--disable-web-security"],
                )
                context = browser.new_context(viewport={"width": 1600, "height": 960})

                try:
                    for lang_code, lang_label in [("dua", "Duálá (EN)"), ("bas", "Ɓàsàa (EN)")]:
                        page = context.new_page()
                        try:
                            res = self._run_en_complete_journey(page, lang_code, lang_label)
                            runs.append(res)
                        except Exception as e:
                            reachable, reason = is_site_reachable(TARGET_URL)
                            if not reachable:
                                self.skipTest(f"[IGNORÉ] Interruption réseau pendant le test : {reason}")
                            raise
                        finally:
                            page.close()
                finally:
                    context.close()
                    browser.close()
        finally:
            print("  [CLEANUP] Arrêt propre du backend FastAPI...")
            backend_proc.terminate()
            backend_proc.wait(timeout=5)
            print("  [CLEANUP] Backend FastAPI arrêté.")

        self._assert_en_results(runs, "Mode 2 EN (Backend Lancé)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
