# -*- coding: utf-8 -*-
"""
Test de conformité du panneau jury SAFINUM par locators Playwright directs.
Compare les soumissions enregistrées pour :
- Mode A : Extension active en Duala
- Mode B : Page native FR (sans extension)
"""

import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_JS_PATH = os.path.join(BASE_DIR, "extension", "content.js")
OFFLINE_CATALOG_PATH = os.path.join(BASE_DIR, "extension", "offline_catalog.json")

with open(CONTENT_JS_PATH, "r", encoding="utf-8") as f:
    CONTENT_JS = f.read()

with open(OFFLINE_CATALOG_PATH, "r", encoding="utf-8") as f:
    CATALOG_DATA = json.load(f)


def inject_extension(page):
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
    }""", CATALOG_DATA)
    page.evaluate(CONTENT_JS)
    time.sleep(1.0)


def set_widget_language(page, lang):
    page.evaluate("""(l) => {
        const host = document.getElementById('safinum-accessibility-host');
        if (host && host.shadowRoot) {
            const select = host.shadowRoot.getElementById('langSelect');
            if (select) {
                select.value = l;
                select.dispatchEvent(new Event('change'));
            }
        }
    }""", lang)
    time.sleep(1.5)


def run_single_audit(scenario_name, use_extension=True):
    print(f"\n{'='*70}")
    print(f" SCÉNARIO : {scenario_name}")
    print(f"{'='*70}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=True,
            args=["--host-resolver-rules=MAP safinum.cm 91.234.194.101", "--disable-web-security"]
        )
        context = browser.new_context(viewport={"width": 1400, "height": 960})
        page = context.new_page()
        page.goto("https://safinum.cm/hackathon-test?jury=1", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("aside", timeout=30000)
        time.sleep(1.0)
        
        # Vider le journal du jury
        page.locator("aside nav button").nth(1).click(force=True)
        time.sleep(0.5)
        btn_vider = page.locator("aside button").filter(has_text="Vider")
        if btn_vider.count() > 0 and btn_vider.first.is_enabled():
            btn_vider.first.click(force=True)
            time.sleep(0.5)
        page.locator("aside nav button").nth(0).click(force=True)
        time.sleep(0.5)
        print("  [INIT] Journal vidé.")
        
        if use_extension:
            print("  [EXT] Chargement extension et sélection Duala...")
            inject_extension(page)
            set_widget_language(page, "dua")
        else:
            print("  [NATIVE] Page native en français.")
            
        def verify_and_report(step_id, step_label):
            # 1. Cliquer sur Contrôle
            page.locator("aside nav button").nth(0).click(force=True)
            time.sleep(0.5)
            # 2. Cliquer Vérifier l'étape maintenant
            btn_verif = page.locator("aside button").filter(has_text="maintenant").first
            btn_verif.scroll_into_view_if_needed()
            btn_verif.click(force=True)
            time.sleep(1.2)
            
            # 3. Basculer sur Soumissions
            page.locator("aside nav button").nth(1).click(force=True)
            time.sleep(1.0)
            
            # 4. Cliquer tous les boutons Détail
            detail_btns = page.locator("aside button").filter(has_text="Détail").all()
            for b in detail_btns:
                try:
                    b.click(force=True)
                except:
                    pass
            time.sleep(0.5)
            
            cards = page.locator("aside div.rounded-xl.border").all()
            print(f"\n--- [{step_id}] {step_label} : {len(cards)} soumission(s) ---")
            for i, c in enumerate(cards):
                c_text = c.inner_text()
                status_el = c.locator("span.rounded-full")
                status = status_el.first.inner_text().strip() if status_el.count() > 0 else "Inconnu"
                
                # Pre blocs (attendu, affiché, soumis)
                pres = c.locator("pre").all_inner_texts()
                expected = pres[0] if len(pres) > 0 else ""
                displayed = pres[1] if len(pres) > 1 else ""
                submitted = pres[2] if len(pres) > 2 else ""
                
                # Différences
                diff_els = c.locator("div[class*='bg-red']").all_inner_texts()
                
                print(f"  Entrée #{i+1} : Statut = {status}")
                if expected:
                    print(f"    Attendu   : {expected.replace(chr(10), ' ')}")
                if displayed:
                    print(f"    Affiché   : {displayed.replace(chr(10), ' ')}")
                if submitted:
                    print(f"    Soumis    : {submitted.replace(chr(10), ' ')}")
                if diff_els:
                    print(f"    ÉCARTS (Compromis) : {diff_els}")
                if not expected and not displayed:
                    print(f"    Texte carte : {c_text.replace(chr(10), ' | ')[:200]}")
                    
            # Revenir sur Contrôle pour la suite
            page.locator("aside nav button").nth(0).click(force=True)
            time.sleep(0.5)

        # -------------------------------------------------------------
        # Étape 1 : Solde
        # -------------------------------------------------------------
        verify_and_report("1", "Solde (Dashboard)")
        
        # -------------------------------------------------------------
        # Étape 2 : Frais (Effectuer un transfert + saisie 25000)
        # -------------------------------------------------------------
        btn_trans = page.locator("button:has-text('Effectuer un transfert'), button:has-text('Loma moni')").first
        btn_trans.click(force=True)
        page.wait_for_selector("input[step='500']", timeout=15000)
        time.sleep(0.5)
        
        # Saisie de 25000
        page.locator("input[step='500']").fill("25000")
        time.sleep(1.0)
        verify_and_report("2", "Frais de transfert (saisie 25000)")
        
        # -------------------------------------------------------------
        # Étape 3 : Bénéficiaire
        # -------------------------------------------------------------
        btn_cont3 = page.locator("button:has-text('Continuer'), button:has-text('Alá oboso')").first
        btn_cont3.click(force=True)
        time.sleep(1.0)
        
        chk1 = page.locator("#app input[type=checkbox]").first
        if chk1.count() > 0:
            chk1.check(force=True)
        time.sleep(0.5)
        verify_and_report("3", "Bénéficiaire")
        
        # -------------------------------------------------------------
        # Étape 4 : Récapitulatif
        # -------------------------------------------------------------
        btn_cont4 = page.locator("button:has-text('Continuer'), button:has-text('Alá oboso')").first
        btn_cont4.click(force=True)
        time.sleep(1.0)
        
        chk2 = page.locator("#app input[type=checkbox]").first
        if chk2.count() > 0:
            chk2.check(force=True)
        time.sleep(0.5)
        verify_and_report("4", "Récapitulatif")
        
        # -------------------------------------------------------------
        # Étape 5 : Reçu
        # -------------------------------------------------------------
        btn_conf = page.locator("button:has-text('Confirmer le transfert'), button:has-text('Kakisane tomba'), button:has-text('Confirmer')").first
        btn_conf.click(force=True)
        time.sleep(1.5)
        verify_and_report("5", "Reçu")
        
        browser.close()


if __name__ == "__main__":
    # Test 1 : Extension active en Duala
    run_single_audit("EXTENSION EN DUALA (Mode Hors-Ligne)", use_extension=True)
    
    # Test 2 : Page native FR (sans extension)
    run_single_audit("PAGE NATIVE FR (Sans Extension)", use_extension=False)
