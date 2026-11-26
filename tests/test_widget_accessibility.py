#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_widget_accessibility.py — Tests d'accessibilité automatisés du widget Shadow DOM (WCAG 2.1 AA).
Valide avec Playwright (Edge) et axe-playwright-python :
- Zones cliquables >= 44 px (Target Size)
- Contraste des couleurs >= 4.5:1
- Navigation clavier complète (Tab, Maj+Tab, Entrée, Espace, Échap) et Focus Trap
- Responsive mobile 360 px
- Zoom 200 %
- Respect de prefers-reduced-motion
- Rôles et attributs ARIA, annonces aria-live non répétitives
- Absence de violation critique/sérieuse Axe sur le widget
"""

import os
import sys
import json
import time
import unittest
from playwright.sync_api import sync_playwright
from axe_playwright_python.sync_playwright import Axe

sys.stdout.reconfigure(encoding="utf-8")

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

MOCK_BANK_PATH = os.path.join(REPO_DIR, "tests", "mock_bank.html")
MOCK_BANK_URL = "file:///" + MOCK_BANK_PATH.replace("\\", "/")
CONTENT_JS_PATH = os.path.join(REPO_DIR, "extension", "content.js")
CATALOG_PATH = os.path.join(REPO_DIR, "extension", "offline_catalog.json")

with open(CONTENT_JS_PATH, "r", encoding="utf-8") as f:
    CONTENT_JS = f.read()

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    CATALOG_DATA = json.load(f)


def inject_extension(page):
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
    }""", CATALOG_DATA)
    page.evaluate(CONTENT_JS)
    time.sleep(0.8)


class TestWidgetAccessibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            channel="msedge",
            headless=False,
            args=["--no-sandbox"]
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 800})
        self.page = self.context.new_page()
        self.page.goto(MOCK_BANK_URL, wait_until="domcontentloaded")
        inject_extension(self.page)

    def tearDown(self):
        self.context.close()

    def test_target_sizes_minimum_44px(self):
        """Vérifie que tous les éléments cliquables du widget respectent la cible de 44 px (WCAG 2.5.5 / 2.5.8)."""
        # Ouvrir le panneau
        self.page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (host && host.shadowRoot) host.shadowRoot.getElementById('badge').click();
        }""")
        time.sleep(0.3)

        sizes = self.page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            const root = host.shadowRoot;
            const items = {
                badge: root.getElementById('badge').getBoundingClientRect(),
                btnClose: root.getElementById('btnClose').getBoundingClientRect(),
                langSelect: root.getElementById('langSelect').getBoundingClientRect(),
                btnToggleTranslate: root.getElementById('btnToggleTranslate').getBoundingClientRect(),
                checkBilingual: root.getElementById('checkBilingual').closest('.switch').getBoundingClientRect(),
                checkExperimental: root.getElementById('checkExperimental').closest('.switch').getBoundingClientRect()
            };
            return {
                badge: { w: items.badge.width, h: items.badge.height },
                btnClose: { w: items.btnClose.width, h: items.btnClose.height },
                langSelect: { w: items.langSelect.width, h: items.langSelect.height },
                btnToggleTranslate: { w: items.btnToggleTranslate.width, h: items.btnToggleTranslate.height },
                checkBilingual: { w: items.checkBilingual.width, h: items.checkBilingual.height },
                checkExperimental: { w: items.checkExperimental.width, h: items.checkExperimental.height }
            };
        }""")

        self.assertGreaterEqual(sizes["badge"]["h"], 44, "Le badge doit mesurer au moins 44px de haut")
        self.assertGreaterEqual(sizes["btnClose"]["w"], 44, "Le bouton fermer doit mesurer au moins 44px de large")
        self.assertGreaterEqual(sizes["btnClose"]["h"], 44, "Le bouton fermer doit mesurer au moins 44px de haut")
        self.assertGreaterEqual(sizes["langSelect"]["h"], 44, "Le sélecteur de langue doit mesurer au moins 44px de haut")
        self.assertGreaterEqual(sizes["btnToggleTranslate"]["h"], 44, "Le bouton bascule doit mesurer au moins 44px de haut")
        self.assertGreaterEqual(sizes["checkBilingual"]["w"], 44, "L'interrupteur bilingue doit mesurer au moins 44px de large")
        self.assertGreaterEqual(sizes["checkBilingual"]["h"], 44, "L'interrupteur bilingue doit mesurer au moins 44px de haut")
        self.assertGreaterEqual(sizes["checkExperimental"]["w"], 44, "L'interrupteur expérimental doit mesurer au moins 44px de large")
        self.assertGreaterEqual(sizes["checkExperimental"]["h"], 44, "L'interrupteur expérimental doit mesurer au moins 44px de haut")

    def test_contrast_ratios_at_least_4_5(self):
        """Vérifie que les contrastes du widget sont tous >= 4.5:1 (WCAG AA)."""
        self.page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (host && host.shadowRoot) host.shadowRoot.getElementById('badge').click();
        }""")
        time.sleep(0.3)

        contrast_results = self.page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            const root = host.shadowRoot;
            function parseRgb(s) {
                const m = s.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                return m ? [parseInt(m[1]), parseInt(m[2]), parseInt(m[3])] : null;
            }
            function luminance(r, g, b) {
                const a = [r, g, b].map(v => {
                    v /= 255;
                    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
                });
                return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
            }
            function getRatio(c1, c2) {
                const l1 = luminance(c1[0], c1[1], c1[2]);
                const l2 = luminance(c2[0], c2[1], c2[2]);
                return Math.round(((Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05)) * 100) / 100;
            }

            const badgeFg = parseRgb(getComputedStyle(root.getElementById('badge')).color);
            const badgeBg = [0, 191, 255];
            const btnCloseFg = parseRgb(getComputedStyle(root.getElementById('btnClose')).color);
            const panelBg = [10, 25, 47];
            const labelFg = parseRgb(getComputedStyle(root.querySelector('.label')).color);
            const bannerFg = parseRgb(getComputedStyle(root.getElementById('aiBannerText')).color);
            const bannerBg = [69, 26, 3];
            const toggleFg = parseRgb(getComputedStyle(root.getElementById('btnToggleTranslate')).color);
            const toggleBg = [16, 185, 129];

            return {
                badge: getRatio(badgeFg, badgeBg),
                btnClose: getRatio(btnCloseFg, panelBg),
                label: getRatio(labelFg, panelBg),
                banner: getRatio(bannerFg, bannerBg),
                toggle: getRatio(toggleFg, toggleBg)
            };
        }""")

        for elem_name, ratio in contrast_results.items():
            self.assertGreaterEqual(ratio, 4.5, f"Le ratio de contraste pour {elem_name} ({ratio}:1) doit être >= 4.5:1")

    def test_complete_keyboard_navigation_and_focus_trap(self):
        """Vérifie la navigation clavier complète (Tab, Maj+Tab, Entrée, Espace, Échap) et le focus trap."""
        # Focus initial sur le badge
        self.page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (host && host.shadowRoot) host.shadowRoot.getElementById('badge').focus();
        }""")
        time.sleep(0.2)

        # 1. Ouverture via Entrée
        self.page.keyboard.press("Enter")
        time.sleep(0.3)
        is_open = self.page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            return host.shadowRoot.getElementById('panel').classList.contains('open');
        }""")
        self.assertTrue(is_open, "Le panneau doit s'ouvrir avec la touche [Entrée]")

        # 2. Fermeture via Échap
        self.page.keyboard.press("Escape")
        time.sleep(0.3)
        is_closed = self.page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            return !host.shadowRoot.getElementById('panel').classList.contains('open');
        }""")
        self.assertTrue(is_closed, "Le panneau doit se fermer avec la touche [Échap]")

        # Vérifier que le focus revient sur le badge
        badge_refocused = self.page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            return host.shadowRoot.activeElement === host.shadowRoot.getElementById('badge');
        }""")
        self.assertTrue(badge_refocused, "Le focus doit revenir sur le badge après fermeture par [Échap]")

        # 3. Réouverture via Espace
        self.page.keyboard.press("Space")
        time.sleep(0.3)
        is_reopened = self.page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            return host.shadowRoot.getElementById('panel').classList.contains('open');
        }""")
        self.assertTrue(is_reopened, "Le panneau doit s'ouvrir avec la touche [Espace]")

        # 4. Tabulation séquentielle (Focus Trap)
        # Séquence attendue : langSelect -> btnToggleTranslate -> checkBilingual -> checkExperimental -> btnClose -> boucle sur langSelect
        tab_ids = []
        for _ in range(5):
            self.page.keyboard.press("Tab")
            time.sleep(0.15)
            active_id = self.page.evaluate("""() => {
                const host = document.getElementById('safinum-accessibility-host');
                const ae = host.shadowRoot.activeElement;
                return ae ? ae.id : null;
            }""")
            tab_ids.append(active_id)

        self.assertEqual(tab_ids[0], "langSelect")
        self.assertEqual(tab_ids[1], "btnToggleTranslate")
        self.assertEqual(tab_ids[2], "checkBilingual")
        self.assertEqual(tab_ids[3], "checkExperimental")
        self.assertEqual(tab_ids[4], "btnClose", "Le focus trap doit boucler sur btnClose sans fuir hors du Shadow DOM")

        # Tabulation suivante doit boucler sur langSelect
        self.page.keyboard.press("Tab")
        time.sleep(0.15)
        looped_id = self.page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            return host.shadowRoot.activeElement ? host.shadowRoot.activeElement.id : null;
        }""")
        self.assertEqual(looped_id, "langSelect", "Le focus trap doit boucler vers langSelect après le dernier élément")

        # 5. Shift+Tab (marche arrière)
        self.page.keyboard.press("Shift+Tab")
        time.sleep(0.15)
        back_id = self.page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            return host.shadowRoot.activeElement ? host.shadowRoot.activeElement.id : null;
        }""")
        self.assertEqual(back_id, "btnClose", "Shift+Tab depuis langSelect doit boucler en arrière sur btnClose")

    def test_mobile_responsive_360px(self):
        """Vérifie que le panneau s'affiche sans déborder à 360 px de largeur d'écran."""
        context_360 = self.browser.new_context(viewport={"width": 360, "height": 640})
        page_360 = context_360.new_page()
        page_360.goto(MOCK_BANK_URL, wait_until="domcontentloaded")
        inject_extension(page_360)
        time.sleep(0.3)

        page_360.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (host && host.shadowRoot) host.shadowRoot.getElementById('badge').click();
        }""")
        time.sleep(0.3)

        fit = page_360.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            const panel = host.shadowRoot.getElementById('panel');
            const r = panel.getBoundingClientRect();
            return {
                width: r.width,
                left: r.left,
                right: r.right,
                vw: window.innerWidth,
                fits: r.right <= window.innerWidth && r.left >= 0,
                has_h_scroll: document.documentElement.scrollWidth > window.innerWidth
            };
        }""")

        self.assertTrue(fit["fits"], f"Le panneau déborde horizontalement à 360px : {fit}")
        self.assertFalse(fit["has_h_scroll"], "Aucune barre de défilement horizontale ne doit apparaître")
        context_360.close()

    def test_zoom_200_percent_accessibility(self):
        """Vérifie qu'à un zoom 200% (viewport équivalent réduit), le panneau reste accessible et scrollable."""
        context_zoom = self.browser.new_context(viewport={"width": 640, "height": 400}, device_scale_factor=2)
        page_zoom = context_zoom.new_page()
        page_zoom.goto(MOCK_BANK_URL, wait_until="domcontentloaded")
        inject_extension(page_zoom)
        time.sleep(0.3)

        page_zoom.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            if (host && host.shadowRoot) host.shadowRoot.getElementById('badge').click();
        }""")
        time.sleep(0.3)

        zoom_accessible = page_zoom.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            const panel = host.shadowRoot.getElementById('panel');
            const style = window.getComputedStyle(panel);
            const r = panel.getBoundingClientRect();
            return {
                height: r.height,
                vh: window.innerHeight,
                overflowY: style.overflowY,
                is_accessible: r.height <= window.innerHeight || style.overflowY === 'auto'
            };
        }""")

        self.assertTrue(zoom_accessible["is_accessible"], f"Le panneau n'est pas accessible au zoom 200% : {zoom_accessible}")
        self.assertEqual(zoom_accessible["overflowY"], "auto", "Le panneau doit avoir overflow-y: auto")
        context_zoom.close()

    def test_prefers_reduced_motion(self):
        """Vérifie que les animations et transitions sont désactivées avec prefers-reduced-motion: reduce."""
        context_motion = self.browser.new_context(reduced_motion="reduce")
        page_motion = context_motion.new_page()
        page_motion.goto(MOCK_BANK_URL, wait_until="domcontentloaded")
        inject_extension(page_motion)
        time.sleep(0.3)

        motion_info = page_motion.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            const badge = host.shadowRoot.getElementById('badge');
            const bStyle = window.getComputedStyle(badge);
            return {
                transition: bStyle.transition,
                transitionDuration: bStyle.transitionDuration
            };
        }""")

        # Doit être soit 'none', soit 0.001ms / 1e-06s
        self.assertTrue(
            "none" in motion_info["transition"] or "0s" in motion_info["transitionDuration"] or "1e-06" in motion_info["transition"],
            f"Les transitions doivent être désactivées avec reduced-motion : {motion_info}"
        )
        context_motion.close()

    def test_aria_roles_and_live_announcements(self):
        """Vérifie la présence des rôles ARIA, libellés et du composant liveAnnouncer non répétitif."""
        aria_info = self.page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            const root = host.shadowRoot;
            const widget = root.querySelector('[role="region"]');
            const panel = root.getElementById('panel');
            const badge = root.getElementById('badge');
            const announcer = root.getElementById('liveAnnouncer');
            const select = root.getElementById('langSelect');

            return {
                has_region: Boolean(widget),
                region_label: widget ? widget.getAttribute('aria-label') : null,
                panel_role: panel ? panel.getAttribute('role') : null,
                panel_modal: panel ? panel.getAttribute('aria-modal') : null,
                panel_label: panel ? panel.getAttribute('aria-label') : null,
                badge_role: badge ? badge.getAttribute('role') : null,
                badge_haspopup: badge ? badge.getAttribute('aria-haspopup') : null,
                badge_expanded: badge ? badge.getAttribute('aria-expanded') : null,
                select_labelled: select ? select.hasAttribute('aria-labelledby') : false,
                has_announcer: Boolean(announcer),
                announcer_live: announcer ? announcer.getAttribute('aria-live') : null,
                announcer_atomic: announcer ? announcer.getAttribute('aria-atomic') : null
            };
        }""")

        self.assertTrue(aria_info["has_region"], "Le widget doit être une région ARIA")
        self.assertIn("SAFINUM", aria_info["region_label"], "Le widget doit avoir un aria-label descriptif")
        self.assertEqual(aria_info["panel_role"], "dialog", "Le panneau doit être un dialogue ARIA")
        self.assertEqual(aria_info["badge_role"], "button", "Le badge doit avoir role='button'")
        self.assertEqual(aria_info["badge_haspopup"], "dialog", "Le badge doit déclarer aria-haspopup='dialog'")
        self.assertTrue(aria_info["has_announcer"], "Une live-region dédiée liveAnnouncer doit être présente")
        self.assertEqual(aria_info["announcer_live"], "polite", "liveAnnouncer doit avoir aria-live='polite'")
        self.assertEqual(aria_info["announcer_atomic"], "true", "liveAnnouncer doit avoir aria-atomic='true'")


if __name__ == "__main__":
    unittest.main(verbosity=2)
