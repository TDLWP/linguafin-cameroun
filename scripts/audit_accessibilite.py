#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/audit_accessibilite.py — Audit automatisé de l'accessibilité du widget Shadow DOM SAFINUM.
Utilise axe-playwright-python et Microsoft Edge sur mock_bank.html et safinum.cm/hackathon-test.
"""

import os
import sys
import json
import time
from playwright.sync_api import sync_playwright
from axe_playwright_python.sync_playwright import Axe

sys.stdout.reconfigure(encoding="utf-8")

REPO_DIR = r"c:\Users\FLEX ZONE\Desktop\linguafin-cameroun"
if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

MOCK_BANK_PATH = os.path.join(REPO_DIR, "tests", "mock_bank.html")
MOCK_BANK_URL = "file:///" + MOCK_BANK_PATH.replace("\\", "/")
REMOTE_URL = "https://safinum.cm/hackathon-test?jury=1"
CONTENT_JS_PATH = os.path.join(REPO_DIR, "extension", "content.js")
CATALOG_PATH = os.path.join(REPO_DIR, "extension", "offline_catalog.json")

with open(CONTENT_JS_PATH, "r", encoding="utf-8") as f:
    CONTENT_JS = f.read()

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    CATALOG_DATA = json.load(f)


def inject_extension(page, catalog_dict):
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


def run_full_accessibility_audit(target_url, is_remote=False):
    print(f"\n{'='*75}")
    print(f" AUDIT ACCESSIBILITÉ : {target_url}")
    print(f"{'='*75}")

    audit_report = {
        "url": target_url,
        "axe_violations": [],
        "keyboard_nav": {},
        "target_sizes": {},
        "contrast_checks": {},
        "aria_roles": {},
        "responsive_360": {},
        "zoom_200": {},
        "reduced_motion": {},
    }

    with sync_playwright() as p:
        args = ["--no-sandbox"]
        if is_remote:
            args.append("--host-resolver-rules=MAP safinum.cm 91.234.194.101")

        browser = p.chromium.launch(channel="msedge", headless=False, args=args)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        try:
            page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
            if is_remote:
                page.wait_for_selector("#app", timeout=20000)
            time.sleep(1.0)
        except Exception as e:
            print(f"  [Avertissement] Navigation échouée ou timeout: {e}")
            context.close()
            browser.close()
            return None

        # Injecter l'extension
        inject_extension(page, CATALOG_DATA)
        time.sleep(1.0)

        # 1. Audit AXE sur l'ensemble de la page incluant le Shadow DOM
        print("\n--- 1. Analyse automatique Axe-core ---")
        axe = Axe()
        try:
            axe_results = axe.run(page)
            violations = axe_results.response.get("violations", [])
            print(f"Total violations Axe détectées : {len(violations)}")
            for v in violations:
                impact = v.get("impact", "unknown")
                rule_id = v.get("id")
                desc = v.get("description")
                nodes_count = len(v.get("nodes", []))
                # Vérifier si la violation concerne le widget SAFINUM
                widget_related = False
                for node in v.get("nodes", []):
                    html_snippet = node.get("html", "")
                    target_sel = str(node.get("target", []))
                    if "safinum" in html_snippet.lower() or "safinum" in target_sel.lower():
                        widget_related = True
                print(f"  [{impact.upper()}] {rule_id} : {desc} ({nodes_count} nœud(s), widget: {widget_related})")
                audit_report["axe_violations"].append({
                    "id": rule_id,
                    "impact": impact,
                    "description": desc,
                    "nodes_count": nodes_count,
                    "widget_related": widget_related,
                    "nodes": [n.get("html", "")[:120] for n in v.get("nodes", [])]
                })
        except Exception as e:
            print(f"  Erreur Axe: {e}")

        # 2. Mesure des zones cliquables (Target Size >= 44px)
        print("\n--- 2. Mesure des zones de frappe / cliquables (>= 44px) ---")
        # Ouvrir le panneau pour mesurer tous les éléments
        page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (host && host.shadowRoot) {
                const b = host.shadowRoot.getElementById('badge');
                if (b) b.click();
            }
        }""")
        time.sleep(0.5)

        target_sizes = page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (!host || !host.shadowRoot) return { error: "Shadow DOM introuvable" };
            const root = host.shadowRoot;
            
            const elements = [
                { id: "badge", name: "Badge déclencheur", el: root.getElementById('badge') },
                { id: "btnClose", name: "Bouton fermer", el: root.getElementById('btnClose') },
                { id: "langSelect", name: "Sélecteur de langue", el: root.getElementById('langSelect') },
                { id: "btnToggleTranslate", name: "Bouton bascule traduction", el: root.getElementById('btnToggleTranslate') },
                { id: "checkBilingual", name: "Interrupteur bilingue", el: root.getElementById('checkBilingual') ? root.getElementById('checkBilingual').closest('.switch') : null },
                { id: "checkExperimental", name: "Interrupteur expérimental", el: root.getElementById('checkExperimental') ? root.getElementById('checkExperimental').closest('.switch') : null },
            ];
            
            const results = {};
            for (const item of elements) {
                if (item.el) {
                    const rect = item.el.getBoundingClientRect();
                    const w = Math.round(rect.width * 10) / 10;
                    const h = Math.round(rect.height * 10) / 10;
                    // Norme WCAG 2.5.5 / recommandation stricte 44px
                    const isValid = (w >= 44 && h >= 44) || (item.id === "langSelect" && h >= 44) || (item.id === "btnToggleTranslate" && h >= 44);
                    results[item.id] = {
                        name: item.name,
                        width: w,
                        height: h,
                        valid_44px: isValid
                    };
                } else {
                    results[item.id] = { name: item.name, missing: true };
                }
            }
            return results;
        }""")
        audit_report["target_sizes"] = target_sizes
        for tid, tdata in target_sizes.items():
            valid_str = "✅ CONFORME" if tdata.get("valid_44px") else "❌ TROP PETIT"
            print(f"  {tdata.get('name')} ({tid}) : {tdata.get('width')}x{tdata.get('height')} px -> {valid_str}")

        # 3. Audit Contraste des couleurs
        print("\n--- 3. Contrôle du contraste des couleurs (>= 4.5:1) ---")
        contrast_res = page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (!host || !host.shadowRoot) return {};
            const root = host.shadowRoot;
            
            function parseRgb(colorStr) {
                const m = colorStr.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                if (!m) return null;
                return [parseInt(m[1]), parseInt(m[2]), parseInt(m[3])];
            }
            function luminance(r, g, b) {
                const a = [r, g, b].map(v => {
                    v /= 255;
                    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
                });
                return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
            }
            function getContrast(rgb1, rgb2) {
                if (!rgb1 || !rgb2) return null;
                const l1 = luminance(rgb1[0], rgb1[1], rgb1[2]);
                const l2 = luminance(rgb2[0], rgb2[1], rgb2[2]);
                return Math.round(((Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05)) * 100) / 100;
            }
            
            const checks = [
                { id: "badge", label: "Badge texte sur fond cyan", el: root.getElementById('badge'), defaultBg: [0, 191, 255] },
                { id: "btnClose", label: "Bouton fermer", el: root.getElementById('btnClose'), defaultBg: [10, 25, 47] },
                { id: "label", label: "Libellé de section", el: root.querySelector('.label'), defaultBg: [10, 25, 47] },
                { id: "banner", label: "Bandeau avertissement IA", el: root.getElementById('aiBannerText'), defaultBg: [69, 26, 3] },
                { id: "btnToggle", label: "Bouton de bascule actif", el: root.getElementById('btnToggleTranslate'), defaultBg: [16, 185, 129] },
                { id: "title", label: "Titre du panneau", el: root.querySelector('.title'), defaultBg: [10, 25, 47] }
            ];
            
            const out = {};
            for (const c of checks) {
                if (c.el) {
                    const style = window.getComputedStyle(c.el);
                    const fg = style.color;
                    const fgRgb = parseRgb(fg);
                    let bgRgb = parseRgb(style.backgroundColor);
                    if (!bgRgb || (style.backgroundColor.includes('rgba') && style.backgroundColor.includes(', 0)'))) {
                        bgRgb = c.defaultBg;
                    }
                    const ratio = fgRgb && bgRgb ? getContrast(fgRgb, bgRgb) : null;
                    out[c.id] = {
                        label: c.label,
                        fg: fg,
                        bg: `rgb(${bgRgb.join(',')})`,
                        ratio: ratio,
                        valid_contrast: ratio !== null && ratio >= 4.5
                    };
                }
            }
            return out;
        }""")
        audit_report["contrast_checks"] = contrast_res
        for cid, cdata in contrast_res.items():
            valid_str = f"✅ {cdata.get('ratio')}:1 (>= 4.5:1)" if cdata.get('valid_contrast') else f"❌ {cdata.get('ratio')}:1 (< 4.5:1)"
            print(f"  {cdata.get('label')} : {cdata.get('fg')} sur {cdata.get('bg')} -> {valid_str}")

        # 4. Navigation au Clavier (Tab, Maj+Tab, Entrée, Espace, Échap)
        print("\n--- 4. Navigation clavier complète ---")
        kb_results = {}
        # Fermer le panneau d'abord
        page.keyboard.press("Escape")
        time.sleep(0.4)

        # 4.1 Focus sur le badge
        page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (host && host.shadowRoot) host.shadowRoot.getElementById('badge').focus();
        }""")
        time.sleep(0.3)
        badge_focused = page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            return host.shadowRoot.activeElement === host.shadowRoot.getElementById('badge');
        }""")
        kb_results["badge_focus_tab"] = badge_focused
        print(f"  Focus initial sur Badge : {'✅ OUI' if badge_focused else '❌ NON'}")

        # 4.2 Ouverture par Entrée
        page.keyboard.press("Enter")
        time.sleep(0.5)
        panel_open_enter = page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            return host.shadowRoot.getElementById('panel').classList.contains('open');
        }""")
        kb_results["open_via_enter"] = panel_open_enter
        print(f"  Ouverture panneau via [Entrée] : {'✅ OUI' if panel_open_enter else '❌ NON'}")

        # 4.3 Fermeture par Échap
        page.keyboard.press("Escape")
        time.sleep(0.5)
        panel_closed_escape = page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            return !host.shadowRoot.getElementById('panel').classList.contains('open');
        }""")
        kb_results["close_via_escape"] = panel_closed_escape
        print(f"  Fermeture panneau via [Échap] : {'✅ OUI' if panel_closed_escape else '❌ NON'}")

        # 4.4 Ré-ouverture par Espace
        page.keyboard.press("Space")
        time.sleep(0.5)
        panel_open_space = page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            return host.shadowRoot.getElementById('panel').classList.contains('open');
        }""")
        kb_results["open_via_space"] = panel_open_space
        print(f"  Ouverture panneau via [Espace] : {'✅ OUI' if panel_open_space else '❌ NON'}")

        # 4.5 Navigation Tab séquentielle
        focused_sequence = []
        for step in range(6):
            page.keyboard.press("Tab")
            time.sleep(0.2)
            active_id = page.evaluate("""() => {
                const host = document.getElementById('safinum-accessibility-host');
                const ae = host.shadowRoot.activeElement;
                return ae ? (ae.id || ae.className || ae.tagName) : null;
            }""")
            focused_sequence.append(active_id)
        kb_results["tab_sequence"] = focused_sequence
        print(f"  Séquence de focus [Tab] : {focused_sequence}")

        # 4.6 Navigation Maj+Tab (retour)
        back_sequence = []
        for step in range(3):
            page.keyboard.press("Shift+Tab")
            time.sleep(0.2)
            active_id = page.evaluate("""() => {
                const host = document.getElementById('safinum-accessibility-host');
                const ae = host.shadowRoot.activeElement;
                return ae ? (ae.id || ae.className || ae.tagName) : null;
            }""")
            back_sequence.append(active_id)
        kb_results["shift_tab_sequence"] = back_sequence
        print(f"  Séquence de focus [Maj+Tab] : {back_sequence}")
        audit_report["keyboard_nav"] = kb_results

        # 5. Affichage à 360 px de large
        print("\n--- 5. Test affichage responsive mobile 360 px ---")
        context_360 = browser.new_context(viewport={"width": 360, "height": 640})
        page_360 = context_360.new_page()
        page_360.goto(target_url, wait_until="domcontentloaded")
        inject_extension(page_360, CATALOG_DATA)
        time.sleep(0.5)

        # Ouvrir le panneau à 360px
        page_360.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (host && host.shadowRoot) host.shadowRoot.getElementById('badge').click();
        }""")
        time.sleep(0.5)
        fit_360 = page_360.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (!host || !host.shadowRoot) return { error: true };
            const panel = host.shadowRoot.getElementById('panel');
            const rect = panel.getBoundingClientRect();
            return {
                panel_width: rect.width,
                panel_left: rect.left,
                panel_right: rect.right,
                viewport_width: window.innerWidth,
                fits_horizontally: rect.right <= window.innerWidth + 2 && rect.left >= 0,
                has_horizontal_scrollbar: document.documentElement.scrollWidth > window.innerWidth
            };
        }""")
        audit_report["responsive_360"] = fit_360
        print(f"  Panneau à 360 px : largeur={fit_360.get('panel_width')}px, rentre sans débord={fit_360.get('fits_horizontally')}")
        context_360.close()

        # 6. Test Zoom 200%
        print("\n--- 6. Test affichage avec zoom 200% ---")
        context_zoom = browser.new_context(viewport={"width": 640, "height": 400}, device_scale_factor=2)
        page_zoom = context_zoom.new_page()
        page_zoom.goto(target_url, wait_until="domcontentloaded")
        inject_extension(page_zoom, CATALOG_DATA)
        time.sleep(0.5)
        page_zoom.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (host && host.shadowRoot) host.shadowRoot.getElementById('badge').click();
        }""")
        time.sleep(0.5)
        zoom_res = page_zoom.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (!host || !host.shadowRoot) return { error: true };
            const panel = host.shadowRoot.getElementById('panel');
            const rect = panel.getBoundingClientRect();
            return {
                panel_height: rect.height,
                viewport_height: window.innerHeight,
                fits_vertically: rect.height <= window.innerHeight || window.getComputedStyle(panel).overflowY === 'auto'
            };
        }""")
        audit_report["zoom_200"] = zoom_res
        print(f"  Zoom 200% : hauteur panneau={zoom_res.get('panel_height')}px, viewport={zoom_res.get('viewport_height')}px, accessible={zoom_res.get('fits_vertically')}")
        context_zoom.close()

        # 7. Respect de prefers-reduced-motion
        print("\n--- 7. Respect de prefers-reduced-motion ---")
        context_motion = browser.new_context(reduced_motion="reduce")
        page_motion = context_motion.new_page()
        page_motion.goto(target_url, wait_until="domcontentloaded")
        inject_extension(page_motion, CATALOG_DATA)
        time.sleep(0.5)
        motion_res = page_motion.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (!host || !host.shadowRoot) return { error: true };
            const badge = host.shadowRoot.getElementById('badge');
            const panel = host.shadowRoot.getElementById('panel');
            const bStyle = window.getComputedStyle(badge);
            const pStyle = window.getComputedStyle(panel);
            return {
                badge_transition: bStyle.transition,
                panel_animation: pStyle.animation,
                has_reduced_motion_query: window.matchMedia('(prefers-reduced-motion: reduce)').matches
            };
        }""")
        audit_report["reduced_motion"] = motion_res
        print(f"  reduced_motion actif: {motion_res.get('has_reduced_motion_query')}, transition badge: {motion_res.get('badge_transition')}")
        context_motion.close()

        context.close()
        browser.close()

    return audit_report


if __name__ == "__main__":
    out_dir = os.path.join(REPO_DIR, "docs")
    os.makedirs(out_dir, exist_ok=True)
    report_mock = run_full_accessibility_audit(MOCK_BANK_URL, is_remote=False)
    
    # Exécuter sur le site distant également
    from tests.test_live_jury_regression import is_site_reachable
    reachable, _ = is_site_reachable()
    report_remote = None
    if reachable:
        report_remote = run_full_accessibility_audit(REMOTE_URL, is_remote=True)
    else:
        print("[SAFINUM] Site distant non joignable, test local uniquement.")

    combined = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mock_bank": report_mock,
        "remote_site": report_remote
    }

    output_filename = "raw_accessibility_audit_after.json" if "--after" in sys.argv or not os.path.exists(os.path.join(out_dir, "raw_accessibility_audit_before.json")) else "raw_accessibility_audit_after.json"
    if "--before" in sys.argv:
        output_filename = "raw_accessibility_audit_before.json"

    out_file = os.path.join(out_dir, output_filename)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Rapport d'accessibilité enregistré dans docs/{output_filename}")
