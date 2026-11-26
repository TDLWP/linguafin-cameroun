# -*- coding: utf-8 -*-
"""
Audit E2E final SAFINUM 2026 sous Microsoft Edge (profil vierge).
Exécute deux passes complètes :
  - Passe A : Backend FastAPI ARRÊTÉ (mode hors-ligne, repli catalogue)
  - Passe B : Backend FastAPI DÉMARRÉ (mode en ligne)

Pour chaque passe :
  - Parcours complet : Solde, Frais, Destinataire, Récapitulatif, Reçu, Erreur, Avertissement de sécurité
  - En Duala (dua), Bassa'a (bas) et retour source (fr)
  - Captures d'écran enregistrées dans docs/screens/final/
  - Vérification du panneau jury : 0 statut 'compromised', bandeau IA visible, 'ful' absent par défaut
  - Injection de 3 contenus inédits via le panneau jury et relevé du comportement réel
  - Mesure de la latence réelle du premier basculement hors ligne
"""

import os
import sys
import time
import json
import re
import subprocess
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL_SCREENS_DIR = os.path.join(BASE_DIR, "docs", "screens", "final")
os.makedirs(FINAL_SCREENS_DIR, exist_ok=True)

CONTENT_JS_PATH = os.path.join(BASE_DIR, "extension", "content.js")
OFFLINE_CATALOG_PATH = os.path.join(BASE_DIR, "extension", "offline_catalog.json")

with open(CONTENT_JS_PATH, "r", encoding="utf-8") as f:
    CONTENT_JS = f.read()

with open(OFFLINE_CATALOG_PATH, "r", encoding="utf-8") as f:
    CATALOG_DATA = json.load(f)

AUDIT_RESULTS = {
    "passA_offline": {
        "first_switch_latency_ms": None,
        "steps": {},
        "jury_checks": {},
        "novel_injections": {},
        "bugs": []
    },
    "passB_online": {
        "first_switch_latency_ms": None,
        "steps": {},
        "jury_checks": {},
        "novel_injections": {},
        "bugs": []
    }
}


def inject_extension_environment(page, catalog_dict):
    """Prépare l'environnement de l'extension non empaquetée et injecte content.js."""
    page.evaluate("""(catData) => {
        window.chrome = window.chrome || {};
        window.chrome.runtime = {
            getURL: (p) => 'safinum-ext://' + p
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
    # Ouvrir le panneau widget pour qu'il soit visible sur les captures
    page.evaluate("""() => {
        const host = document.getElementById('safinum-accessibility-host');
        if (host && host.shadowRoot) {
            const panel = host.shadowRoot.getElementById('panel');
            if (panel && !panel.classList.contains('open')) {
                panel.classList.add('open');
            }
        }
    }""")
    time.sleep(0.3)


def set_widget_language(page, lang):
    """Change la langue dans le widget via Shadow DOM."""
    page.evaluate("""(targetLang) => {
        const host = document.getElementById('safinum-accessibility-host');
        if (host && host.shadowRoot) {
            const select = host.shadowRoot.getElementById('langSelect');
            if (select) {
                select.value = targetLang;
                select.dispatchEvent(new Event('change'));
            }
        }
    }""", lang)
    time.sleep(1.0)


def toggle_widget_source(page):
    """Bascule vers le texte source (mode Original)."""
    page.evaluate("""() => {
        const host = document.getElementById('safinum-accessibility-host');
        if (host && host.shadowRoot) {
            const btn = host.shadowRoot.getElementById('btnToggleTranslate');
            if (btn) btn.click();
        }
    }""")
    time.sleep(0.6)


def get_widget_info(page):
    """Extrait les informations du Shadow DOM du widget."""
    return page.evaluate("""() => {
        const host = document.getElementById('safinum-accessibility-host');
        if (!host || !host.shadowRoot) return null;
        const sr = host.shadowRoot;
        const banner = sr.getElementById('aiBannerText');
        const select = sr.getElementById('langSelect');
        const options = select ? Array.from(select.options).map(o => o.value) : [];
        const btnToggle = sr.getElementById('btnToggleTranslate');
        const statHuman = sr.getElementById('statHuman');
        const statMachine = sr.getElementById('statMachine');
        const statFallback = sr.getElementById('statFallback');

        return {
            bannerText: banner ? banner.innerText.trim() : null,
            options: options,
            currentValue: select ? select.value : null,
            toggleText: btnToggle ? btnToggle.innerText.trim() : null,
            stats: {
                human: statHuman ? statHuman.innerText.trim() : '0',
                machine: statMachine ? statMachine.innerText.trim() : '0',
                fallback: statFallback ? statFallback.innerText.trim() : '0'
            }
        };
    }""")


def run_single_pass(pass_name, backend_active=False):
    print(f"\n{'='*70}")
    print(f" DÉBUT DE LA PASSE : {pass_name.upper()} (Backend {'LANCÉ' if backend_active else 'ARRÊTÉ'})")
    print(f"{'='*70}")

    pass_data = AUDIT_RESULTS[pass_name]
    prefix = "passA" if "passA" in pass_name else "passB"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=True,
            args=[
                "--host-resolver-rules=MAP safinum.cm 91.234.194.101"
            ]
        )
        context = browser.new_context(viewport={"width": 1400, "height": 960})
        page = context.new_page()

        # =====================================================================
        # PARTIE 1 : PARCOURS BANCAIRE SUR https://safinum.cm/hackathon-test
        # =====================================================================
        print("\n--- [1] Navigation sur https://safinum.cm/hackathon-test ---")
        page.goto("https://safinum.cm/hackathon-test", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector("#app", timeout=20000)
        time.sleep(1.0)

        # Mesure de latence lors de la première injection et switch
        t0 = time.perf_counter()
        inject_extension_environment(page, CATALOG_DATA)
        t_inject = (time.perf_counter() - t0) * 1000
        print(f"[{prefix}] Latence injection et initialisation : {t_inject:.2f} ms")

        # Mesure de latence du basculement hors-ligne vers Duala
        t_switch_start = time.perf_counter()
        set_widget_language(page, "dua")
        t_switch_dua = (time.perf_counter() - t_switch_start) * 1000
        pass_data["first_switch_latency_ms"] = round(t_switch_dua, 2)
        print(f"[{prefix}] Latence réelle du premier basculement (dua) : {t_switch_dua:.2f} ms")

        # ---------------------------------------------------------------------
        # Étape 1 : Solde / Dashboard
        # ---------------------------------------------------------------------
        print("\n--> Étape 1 : Solde / Dashboard")
        # Duala
        scr_dua_1 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_01_solde_dua.png")
        page.screenshot(path=scr_dua_1)
        text_dua_1 = page.locator("#app").inner_text()
        solde_dua_ok = "250 000 FCFA" in text_dua_1
        cpt_dua_ok = "CM 001 2345 6789 01" in text_dua_1

        # Bassa'a
        set_widget_language(page, "bas")
        scr_bas_1 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_01_solde_bas.png")
        page.screenshot(path=scr_bas_1)
        text_bas_1 = page.locator("#app").inner_text()
        solde_bas_ok = "250 000 FCFA" in text_bas_1
        cpt_bas_ok = "CM 001 2345 6789 01" in text_bas_1

        # Retour Source (FR)
        toggle_widget_source(page)
        scr_fr_1 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_01_solde_source_fr.png")
        page.screenshot(path=scr_fr_1)
        text_fr_1 = page.locator("#app").inner_text()
        fr_1_ok = ("Solde disponible" in text_fr_1 or "SOLDE DISPONIBLE" in text_fr_1)
        # Ré-activer la traduction
        toggle_widget_source(page)

        pass_data["steps"]["01_solde"] = {
            "montant_250k_preserve": solde_dua_ok and solde_bas_ok,
            "compte_preserve": cpt_dua_ok and cpt_bas_ok,
            "retour_source_ok": fr_1_ok,
            "status": "PASS" if (solde_dua_ok and solde_bas_ok and cpt_dua_ok and cpt_bas_ok and fr_1_ok) else "FAIL"
        }

        # ---------------------------------------------------------------------
        # Étape 2 : Frais de transfert
        # ---------------------------------------------------------------------
        print("\n--> Étape 2 : Frais de transfert")
        btn_transfer = page.locator("button:has-text('Effectuer un transfert'), button:has-text('Loma moni'), button:has-text('om')").first
        btn_transfer.click()
        page.wait_for_selector("input[type=number]", timeout=15000)
        time.sleep(0.5)

        # Saisie d'un montant de transfert (25000)
        page.locator("input[type=number]").fill("25000")
        time.sleep(0.8)

        # Duala
        set_widget_language(page, "dua")
        scr_dua_2 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_02_frais_dua.png")
        page.screenshot(path=scr_dua_2)
        text_dua_2 = page.locator("#app").inner_text()
        amt_dua_2_ok = "25 000 FCFA" in text_dua_2
        fee_dua_2_ok = "0 FCFA" in text_dua_2

        # Bassa'a
        set_widget_language(page, "bas")
        scr_bas_2 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_02_frais_bas.png")
        page.screenshot(path=scr_bas_2)
        text_bas_2 = page.locator("#app").inner_text()
        amt_bas_2_ok = "25 000 FCFA" in text_bas_2
        fee_bas_2_ok = "0 FCFA" in text_bas_2

        # Retour Source (FR)
        toggle_widget_source(page)
        scr_fr_2 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_02_frais_source_fr.png")
        page.screenshot(path=scr_fr_2)
        text_fr_2 = page.locator("#app").inner_text()
        fr_2_ok = "FRAIS DE TRANSFERT" in text_fr_2
        toggle_widget_source(page)

        pass_data["steps"]["02_frais"] = {
            "montant_25k_preserve": amt_dua_2_ok and amt_bas_2_ok,
            "frais_0fcfa_preserve": fee_dua_2_ok and fee_bas_2_ok,
            "retour_source_ok": fr_2_ok,
            "status": "PASS" if (amt_dua_2_ok and amt_bas_2_ok and fee_dua_2_ok and fee_bas_2_ok and fr_2_ok) else "FAIL"
        }

        # ---------------------------------------------------------------------
        # Étape 3 : Destinataire & Avertissement de sécurité
        # ---------------------------------------------------------------------
        print("\n--> Étape 3 : Destinataire & Avertissement de sécurité")
        btn_next3 = page.locator("button:has-text('Continuer'), button:has-text('Alá oboso'), button:has-text('Kenel bisu'), button:has-text('bisu')").first
        btn_next3.click()
        page.wait_for_selector("input[type=tel]", timeout=15000)
        time.sleep(0.5)

        # Duala
        set_widget_language(page, "dua")
        scr_dua_3 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_03_beneficiaire_dua.png")
        page.screenshot(path=scr_dua_3)
        input_benef = page.locator("input[type=text]").first.input_value()
        input_phone = page.locator("input[type=tel]").first.input_value()
        benef_dua_ok = "Jean-Paul Mbarga" in input_benef
        phone_dua_ok = "+237 6 99 12 34 56" in input_phone

        # Bassa'a
        set_widget_language(page, "bas")
        scr_bas_3 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_03_beneficiaire_bas.png")
        page.screenshot(path=scr_bas_3)

        # Retour Source (FR)
        toggle_widget_source(page)
        scr_fr_3 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_03_beneficiaire_source_fr.png")
        page.screenshot(path=scr_fr_3)
        text_fr_3 = page.locator("#app").inner_text()
        fr_3_ok = "BÉNÉFICIAIRE" in text_fr_3
        toggle_widget_source(page)

        pass_data["steps"]["03_beneficiaire"] = {
            "beneficiaire_preserve": benef_dua_ok,
            "telephone_preserve": phone_dua_ok,
            "retour_source_ok": fr_3_ok,
            "status": "PASS" if (benef_dua_ok and phone_dua_ok and fr_3_ok) else "FAIL"
        }

        # Coche de vérification obligatoire du bénéficiaire
        chk1 = page.locator("input[type=checkbox]").first
        if chk1.count() > 0:
            chk1.check()
        time.sleep(0.5)

        # ---------------------------------------------------------------------
        # Étape 4 : Récapitulatif
        # ---------------------------------------------------------------------
        print("\n--> Étape 4 : Récapitulatif")
        btn_next4 = page.locator("button:has-text('Continuer'), button:has-text('Alá oboso'), button:has-text('Kenel bisu'), button:has-text('bisu')").first
        btn_next4.click()
        page.wait_for_selector("text=25 000 FCFA", timeout=15000)
        time.sleep(0.8)

        # Duala
        set_widget_language(page, "dua")
        scr_dua_4 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_04_recapitulatif_dua.png")
        page.screenshot(path=scr_dua_4)
        text_dua_4 = page.locator("#app").inner_text()
        amt_dua_4_ok = "25 000 FCFA" in text_dua_4
        fee_dua_4_ok = "0 FCFA" in text_dua_4
        ref_match_dua = re.search(r"SAF-2026-[A-Z0-9]+", text_dua_4)
        ref_dua_ok = bool(ref_match_dua)
        ref_val = ref_match_dua.group(0) if ref_match_dua else "NON DÉTECTÉE"

        # Bassa'a
        set_widget_language(page, "bas")
        scr_bas_4 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_04_recapitulatif_bas.png")
        page.screenshot(path=scr_bas_4)
        text_bas_4 = page.locator("#app").inner_text()
        amt_bas_4_ok = "25 000 FCFA" in text_bas_4
        fee_bas_4_ok = "0 FCFA" in text_bas_4
        ref_bas_ok = ref_val in text_bas_4 if ref_dua_ok else False

        # Retour Source (FR)
        toggle_widget_source(page)
        scr_fr_4 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_04_recapitulatif_source_fr.png")
        page.screenshot(path=scr_fr_4)
        text_fr_4 = page.locator("#app").inner_text()
        fr_4_ok = "RÉCAPITULATIF" in text_fr_4
        toggle_widget_source(page)

        pass_data["steps"]["04_recapitulatif"] = {
            "montant_preserve": amt_dua_4_ok and amt_bas_4_ok,
            "frais_preserve": fee_dua_4_ok and fee_bas_4_ok,
            "reference": ref_val,
            "reference_preservee": ref_dua_ok and ref_bas_ok,
            "retour_source_ok": fr_4_ok,
            "status": "PASS" if (amt_dua_4_ok and amt_bas_4_ok and fee_dua_4_ok and fee_bas_4_ok and ref_dua_ok and ref_bas_ok and fr_4_ok) else "FAIL"
        }

        # Coche d'engagement final
        chk2 = page.locator("input[type=checkbox]").first
        if chk2.count() > 0:
            chk2.check()
        time.sleep(0.5)

        # ---------------------------------------------------------------------
        # Étape 5 : Reçu / Confirmation
        # ---------------------------------------------------------------------
        print("\n--> Étape 5 : Reçu / Confirmation")
        btn_confirm = page.locator("button:has-text('Confirmer le transfert'), button:has-text('Kakisane tomba'), button:has-text('Gwelha'), button:has-text('Confirmer'), button:has-text('tomba')").first
        btn_confirm.click()
        page.wait_for_selector("text=Transfert", timeout=15000)
        time.sleep(1.0)

        # Duala
        set_widget_language(page, "dua")
        scr_dua_5 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_05_recu_dua.png")
        page.screenshot(path=scr_dua_5)
        text_dua_5 = page.locator("#app").inner_text()
        amt_dua_5_ok = "25 000 FCFA" in text_dua_5
        ref_dua_5_ok = ref_val in text_dua_5 if ref_val != "NON DÉTECTÉE" else False

        # Bassa'a
        set_widget_language(page, "bas")
        scr_bas_5 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_05_recu_bas.png")
        page.screenshot(path=scr_bas_5)
        text_bas_5 = page.locator("#app").inner_text()
        amt_bas_5_ok = "25 000 FCFA" in text_bas_5
        ref_bas_5_ok = ref_val in text_bas_5 if ref_val != "NON DÉTECTÉE" else False

        # Retour Source (FR)
        toggle_widget_source(page)
        scr_fr_5 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_05_recu_source_fr.png")
        page.screenshot(path=scr_fr_5)
        text_fr_5 = page.locator("#app").inner_text()
        fr_5_ok = "Transfert effectué" in text_fr_5
        toggle_widget_source(page)

        pass_data["steps"]["05_recu"] = {
            "montant_preserve": amt_dua_5_ok and amt_bas_5_ok,
            "reference_preservee": ref_dua_5_ok and ref_bas_5_ok,
            "retour_source_ok": fr_5_ok,
            "status": "PASS" if (amt_dua_5_ok and amt_bas_5_ok and ref_dua_5_ok and ref_bas_5_ok and fr_5_ok) else "FAIL"
        }

        # =====================================================================
        # PARTIE 2 : PANNEAU JURY, ERREUR, SÉCURITÉ ET CONTENU INÉDIT
        # =====================================================================
        print("\n--- [2] Navigation sur https://safinum.cm/hackathon-test?jury=1 ---")
        page.goto("https://safinum.cm/hackathon-test?jury=1", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector("#app", timeout=20000)
        time.sleep(1.0)
        inject_extension_environment(page, CATALOG_DATA)

        # ---------------------------------------------------------------------
        # Étape 6 : Déclenchement d'une Erreur (Solde insuffisant)
        # ---------------------------------------------------------------------
        print("\n--> Étape 6 : Erreur (Solde insuffisant)")
        btn_err = page.locator("button:has-text('Solde insuffisant'), button[title*='Solde insuffisant']").first
        if btn_err.count() > 0:
            btn_err.click(force=True)
            time.sleep(0.8)

        # Duala
        set_widget_language(page, "dua")
        scr_dua_6 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_06_erreur_dua.png")
        page.screenshot(path=scr_dua_6)
        text_dua_6 = page.locator("#app").inner_text()
        err_dua_ok = ("Solde insuffisant" in text_dua_6 or "Moni mu titi" in text_dua_6 or "insuffisant" in text_dua_6.lower())

        # Bassa'a
        set_widget_language(page, "bas")
        scr_bas_6 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_06_erreur_bas.png")
        page.screenshot(path=scr_bas_6)

        # Retour Source (FR)
        toggle_widget_source(page)
        scr_fr_6 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_06_erreur_source_fr.png")
        page.screenshot(path=scr_fr_6)
        text_fr_6 = page.locator("#app").inner_text()
        fr_6_ok = "Solde insuffisant" in text_fr_6
        toggle_widget_source(page)

        pass_data["steps"]["06_erreur"] = {
            "erreur_detectee": err_dua_ok,
            "retour_source_ok": fr_6_ok,
            "status": "PASS" if (err_dua_ok and fr_6_ok) else "FAIL"
        }

        # ---------------------------------------------------------------------
        # Étape 7 : Avertissement de sécurité (Alerte de sécurité)
        # ---------------------------------------------------------------------
        print("\n--> Étape 7 : Avertissement de sécurité")
        btn_sec = page.locator("button:has-text('Alerte de sécurité'), button[title*='Alerte de sécurité']").first
        if btn_sec.count() > 0:
            btn_sec.click(force=True)
            time.sleep(0.8)

        # Duala
        set_widget_language(page, "dua")
        scr_dua_7 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_07_securite_dua.png")
        page.screenshot(path=scr_dua_7)
        text_dua_7 = page.locator("#app").inner_text()
        sec_dua_ok = ("Alerte de sécurité" in text_dua_7 or "sécurité" in text_dua_7.lower() or "mbembe" in text_dua_7.lower())

        # Bassa'a
        set_widget_language(page, "bas")
        scr_bas_7 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_07_securite_bas.png")
        page.screenshot(path=scr_bas_7)

        # Retour Source (FR)
        toggle_widget_source(page)
        scr_fr_7 = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_07_securite_source_fr.png")
        page.screenshot(path=scr_fr_7)
        text_fr_7 = page.locator("#app").inner_text()
        fr_7_ok = "Alerte de sécurité" in text_fr_7
        toggle_widget_source(page)

        pass_data["steps"]["07_securite"] = {
            "securite_detectee": sec_dua_ok,
            "retour_source_ok": fr_7_ok,
            "status": "PASS" if (sec_dua_ok and fr_7_ok) else "FAIL"
        }

        # ---------------------------------------------------------------------
        # Étape 8 : Vérification du panneau Jury (0 'compromised', bandeau, ful)
        # ---------------------------------------------------------------------
        print("\n--> Étape 8 : Vérification Panneau Jury")
        # Vérifier l'étape
        btn_verify = page.locator("button:has-text('Vérifier'), button[title*='Vérifier']").first
        if btn_verify.count() > 0:
            btn_verify.click(force=True)
            time.sleep(1.0)

        # Onglet Soumissions
        btn_soum = page.locator("button:has-text('Soumissions'), button[title*='Soumissions']").first
        if btn_soum.count() > 0:
            btn_soum.click(force=True)
            time.sleep(0.8)

        scr_jury = os.path.join(FINAL_SCREENS_DIR, f"{prefix}_08_jury_panel_intact.png")
        page.screenshot(path=scr_jury)

        jury_status = page.evaluate("""() => {
            const allElements = Array.from(document.querySelectorAll('*'));
            const compromisedBadges = allElements.filter(el => el.innerText && el.innerText.trim() === 'Compromis');
            const integreBadges = allElements.filter(el => el.innerText && el.innerText.trim() === 'Intègre');
            return {
                compromised_count: compromisedBadges.length,
                integre_count: integreBadges.length
            };
        }""")

        has_compromised = jury_status["compromised_count"] > 0
        is_integre = jury_status["integre_count"] > 0

        w_info = get_widget_info(page)
        banner_ok = (w_info and w_info["bannerText"] == "Traductions générées par IA, non validées par un locuteur natif.")
        ful_absent = (w_info and "ful" not in w_info["options"])

        pass_data["jury_checks"] = {
            "has_compromised": has_compromised,
            "is_integre": is_integre,
            "compromised_count": jury_status["compromised_count"],
            "integre_count": jury_status["integre_count"],
            "banner_text": w_info["bannerText"] if w_info else None,
            "banner_conforme": banner_ok,
            "ful_absent_par_defaut": ful_absent,
            "lang_options": w_info["options"] if w_info else [],
            "status": "PASS" if (not has_compromised and is_integre and banner_ok and ful_absent) else "FAIL"
        }
        print(f"[{prefix}] Panneau Jury : Compromis={has_compromised} (count={jury_status['compromised_count']}), Intègre={is_integre} (count={jury_status['integre_count']}), Bandeau Conforme={banner_ok}, Ful Absent={ful_absent}")

        # Revenir à l'onglet Contrôle pour l'injection
        btn_ctrl = page.locator("button:has-text('Contrôle'), button[title*='Contrôle']").first
        if btn_ctrl.count() > 0:
            btn_ctrl.click(force=True)
            time.sleep(0.5)

        # ---------------------------------------------------------------------
        # Étape 9 : Injection de 3 contenus inédits depuis le panneau Jury
        # ---------------------------------------------------------------------
        print("\n--> Étape 9 : Injection de 3 contenus inédits")
        injections = [
            (
                "inj1_securite_montant",
                "Alerte de sécurité : tentative de débit suspect de 75 000 FCFA sur votre compte.",
                f"{prefix}_09_injected_1_security_amount.png"
            ),
            (
                "inj2_confirmation",
                "Votre virement permanent a été enregistré avec succès par notre service.",
                f"{prefix}_10_injected_2_confirmation.png"
            ),
            (
                "inj3_notification_sans_montant",
                "Un nouveau document sécurisé est disponible dans votre espace client.",
                f"{prefix}_11_injected_3_notification_no_amount.png"
            )
        ]

        for inj_key, inj_text, scr_filename in injections:
            # Saisie dans la textarea du panneau jury
            txt_area = page.locator("textarea").first
            txt_area.fill(inj_text)
            time.sleep(0.3)
            btn_inject = page.locator("button:has-text('Injecter'), button[title*='Injecter']").first
            btn_inject.click(force=True)
            time.sleep(1.2)

            # Capture de l'élément injecté
            scr_path = os.path.join(FINAL_SCREENS_DIR, scr_filename)
            page.screenshot(path=scr_path)

            # Lecture du texte affiché pour le contenu injecté
            displayed_data = page.evaluate("""(srcText) => {
                const el = document.querySelector('div[class*="9B7FD4"] p') ||
                           Array.from(document.querySelectorAll('p')).find(p => p.parentElement && p.parentElement.className && p.parentElement.className.includes('9B7FD4'));
                if (!el) {
                    const fallback = Array.from(document.querySelectorAll('p, div')).find(p => p.children.length === 0 && (
                        p.innerText.includes('75 000') ||
                        p.innerText.includes('virement') ||
                        p.innerText.includes('document')
                    ));
                    if (!fallback) return { text: null, tag: null, title: null, dataset: {} };
                    return {
                        text: fallback.innerText.trim(),
                        tag: fallback.tagName,
                        title: fallback.getAttribute('title') || (fallback.parentElement ? fallback.parentElement.getAttribute('title') : null),
                        dataTranslated: fallback.parentElement ? fallback.parentElement.getAttribute('data-safinum-translated') : null
                    };
                }
                return {
                    text: el.innerText.trim(),
                    tag: el.tagName,
                    title: el.getAttribute('title') || (el.parentElement ? el.parentElement.getAttribute('title') : null),
                    dataTranslated: el.parentElement ? el.parentElement.getAttribute('data-safinum-translated') : null
                };
            }""", inj_text)

            w_stats = get_widget_info(page)

            # Vérification de préservation financière si montant présent
            preservation_ok = True
            if "75 000 FCFA" in inj_text:
                preservation_ok = ("75 000 FCFA" in (displayed_data.get("text") or ""))

            pass_data["novel_injections"][inj_key] = {
                "input_text": inj_text,
                "displayed_text": displayed_data.get("text"),
                "montant_preserve": preservation_ok,
                "hover_title": displayed_data.get("title"),
                "widget_stats": w_stats.get("stats") if w_stats else {},
                "status": "PASS" if preservation_ok else "FAIL"
            }
            print(f"[{prefix}] Ingestion {inj_key} -> Affiché : '{displayed_data.get('text')}' (Préservé: {preservation_ok})")

        browser.close()

    print(f"\nFIN DE LA PASSE : {pass_name.upper()}")


def main():
    # 1. Vérifier que le backend est arrêté pour la Passe A
    print("Vérification que le backend est arrêté...")
    try:
        import urllib.request
        urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1)
        print("ATTENTION : Un serveur tourne déjà sur le port 8000. Fermeture requise.")
    except Exception:
        print("Port 8000 libre. Mode hors-ligne vérifié.")

    # Exécution de la PASSE A (Hors-ligne)
    run_single_pass("passA_offline", backend_active=False)

    # 2. Démarrage du backend FastAPI pour la PASSE B
    print("\nDémarrage du backend local FastAPI pour la PASSE B (http://127.0.0.1:8000)...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.api:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3.0)

    # Vérification que le backend répond
    try:
        import urllib.request
        res = urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3)
        print("Backend démarré avec succès :", res.read().decode("utf-8"))
    except Exception as e:
        print("ERREUR démarrage backend :", e)

    try:
        # Exécution de la PASSE B (En ligne)
        run_single_pass("passB_online", backend_active=True)
    finally:
        print("\nArrêt propre du backend FastAPI...")
        backend_proc.terminate()
        backend_proc.wait()
        print("Backend arrêté.")

    # Sauvegarde des résultats bruts
    results_path = os.path.join(BASE_DIR, "catalogue", "audit_results_final.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(AUDIT_RESULTS, f, indent=2, ensure_ascii=False)
    print(f"\nRésultats enregistrés dans {results_path}")


if __name__ == "__main__":
    main()
