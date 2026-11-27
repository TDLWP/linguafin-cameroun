#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_performance_regression.py — Tests automatisés de non-régression de performance.
Vérifie avec Playwright (Microsoft Edge) :
- Premier rendu traduit (seuil < 1 000 ms)
- Temps de retour à la langue source (seuil < 10 ms)
- Absence de boucle infinie du MutationObserver (0 mutation résiduelle)
"""

import os
import sys
import json
import time
import unittest
from playwright.sync_api import sync_playwright

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


class TestPerformanceRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            channel="msedge",
            headless=True,
            args=["--no-sandbox"]
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def test_first_render_timing_below_threshold_backend_arrete(self):
        """
        Test de régression critique :
        Vérifie que le premier rendu traduit apparaît en moins de 1 000 ms lorsque le backend est arrêté
        (repli hors ligne pur avec timeout réduit à 400 ms maximum et un seul essai).
        Vérifie également la mémorisation de l'état indisponible pour la session.
        """
        # S'assurer que le backend est arrêté pour tester le repli hors ligne
        context = self.browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(MOCK_BANK_URL, wait_until="domcontentloaded")

        t0 = time.perf_counter()
        inject_extension(page)
        page.wait_for_selector('[data-safinum-translated="true"]', timeout=3000)
        t1 = time.perf_counter()

        elapsed_ms = (t1 - t0) * 1000
        print(f"\n[PERF] Premier rendu traduit (Backend arrêté) : {elapsed_ms:.2f} ms (seuil max 1000 ms)")

        # Vérification de la mémorisation de l'état indisponible pour la session
        backend_state = page.evaluate("() => window.SAFINUM_GET_BACKEND_STATE ? window.SAFINUM_GET_BACKEND_STATE() : null")
        if backend_state:
            self.assertFalse(backend_state["isAvailable"], "L'état du backend doit être mémorisé comme indisponible (false).")

        context.close()
        self.assertLess(elapsed_ms, 1000.0, f"Le premier rendu traduit a pris {elapsed_ms:.2f} ms (seuil max 1000 ms)")

    def test_session_caching_and_subsequent_render_speed(self):
        """
        Vérifie que lorsque l'indisponibilité du backend est mémorisée pour la session,
        les rendus suivants sont quasi-instantanés (< 500 ms) sans aucun blocage réseau.
        """
        context = self.browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(MOCK_BANK_URL, wait_until="domcontentloaded")

        # Initialiser avec état déjà mémorisé indisponible
        page.evaluate("""() => {
            try {
                sessionStorage.setItem('safinum_backend_status', 'unavailable');
                sessionStorage.setItem('safinum_backend_last_checked', String(Date.now()));
            } catch(e) {}
        }""")

        t0 = time.perf_counter()
        inject_extension(page)
        page.wait_for_selector('[data-safinum-translated="true"]', timeout=3000)
        t1 = time.perf_counter()

        elapsed_ms = (t1 - t0) * 1000
        print(f"[PERF] Rendu ultérieur en session mémorisée (0 attente réseau) : {elapsed_ms:.2f} ms")
        context.close()

        self.assertLess(elapsed_ms, 500.0, f"Le rendu en session mémorisée a pris {elapsed_ms:.2f} ms (seuil max 500 ms)")

    def test_revert_to_source_timing_below_threshold(self):
        """Vérifie que le retour à la langue source s'exécute en moins de 10 ms."""
        context = self.browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(MOCK_BANK_URL, wait_until="domcontentloaded")
        inject_extension(page)
        page.wait_for_selector('[data-safinum-translated="true"]', timeout=3000)
        time.sleep(0.3)

        revert_ms = page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            const root = host.shadowRoot;
            const btnToggle = root.getElementById('btnToggleTranslate');
            const t0 = performance.now();
            btnToggle.click();
            const t1 = performance.now();
            return t1 - t0;
        }""")
        context.close()

        self.assertLess(revert_ms, 10.0, f"Le retour à la source a pris {revert_ms:.2f} ms (seuil max 10 ms)")

    def test_mutation_observer_absence_of_infinite_loop(self):
        """Vérifie que le MutationObserver ne tourne pas en boucle (0 mutation résiduelle au repos)."""
        context = self.browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(MOCK_BANK_URL, wait_until="domcontentloaded")

        page.evaluate("""() => {
            window.__test_mutations = 0;
            const origObserver = window.MutationObserver;
            window.MutationObserver = function(callback) {
                const wrappedCallback = function(mutations, observer) {
                    window.__test_mutations += mutations.length;
                    return callback(mutations, observer);
                };
                return new origObserver(wrappedCallback);
            };
        }""")

        inject_extension(page)
        time.sleep(1.0)

        # Mesure d'inactivité pendant 1 seconde
        m_start = page.evaluate("() => window.__test_mutations")
        time.sleep(1.0)
        m_end = page.evaluate("() => window.__test_mutations")
        context.close()

        residual = m_end - m_start
        self.assertEqual(residual, 0, f"Détection de {residual} mutations résiduelles au repos (boucle infinie)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
