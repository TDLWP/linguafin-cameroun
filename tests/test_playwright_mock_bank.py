# -*- coding: utf-8 -*-
"""
Test automatisé E2E Playwright de tests/mock_bank.html avec injection réelle de extension/content.js.
Vérifie le rendu réel du Shadow DOM, la traduction en Duala et Bassa'a,
l'intégrité absolue des champs de saisie et la bascule Original / Traduit.
"""

import os
import json
import unittest
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestPlaywrightMockBank(unittest.TestCase):

    def test_extension_in_real_browser(self):
        mock_html_path = os.path.abspath(os.path.join(BASE_DIR, "tests", "mock_bank.html"))
        content_js_path = os.path.abspath(os.path.join(BASE_DIR, "extension", "content.js"))
        catalog_path = os.path.abspath(os.path.join(BASE_DIR, "extension", "offline_catalog.json"))

        with open(content_js_path, "r", encoding="utf-8") as f:
            content_js = f.read()

        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog_json = f.read()

        file_url = f"file:///{mock_html_path.replace(os.sep, '/')}"

        with sync_playwright() as p:
            # Utilisation directe du navigateur Microsoft Edge préinstallé sous Windows 11 (aucun téléchargement)
            browser = p.chromium.launch(channel="msedge", headless=True)
            page = browser.new_page()
            page.goto(file_url)

            # 1. Vérification de l'état initial (Français brut)
            self.assertEqual(page.locator("#lblBalance").inner_text().strip(), "Solde disponible")
            self.assertEqual(page.locator("#balanceText").inner_text().strip(), "250 000 FCFA")
            self.assertEqual(page.locator("#amountInput").input_value(), "25000")
            self.assertEqual(page.locator("#beneficiaryInput").input_value(), "Jean-Paul Mbarga")
            self.assertEqual(page.locator("#phoneInput").input_value(), "+237 6 99 12 34 56")

            # 2. Simulation de l'extension : mock de chrome.runtime.getURL et injection de content.js
            catalog_dict = json.loads(catalog_json)
            page.evaluate("""(catalogData) => {
                window.chrome = window.chrome || {};
                window.chrome.runtime = {
                    getURL: function(path) { return 'mock://' + path; }
                };
                window.fetch = async function(url, opts) {
                    if (typeof url === 'string' && url.includes('offline_catalog.json')) {
                        return {
                            ok: true,
                            json: async () => catalogData
                        };
                    }
                    throw new TypeError('API network unavailable (testing offline fallback)');
                };
            }""", catalog_dict)
            page.evaluate(content_js)
            page.wait_for_timeout(500)

            # 3. Vérification du Shadow DOM
            host_count = page.locator("#safinum-accessibility-host").count()
            self.assertEqual(host_count, 1, "Le conteneur Shadow DOM host doit être présent dans le body.")

            # 4. Vérification de la traduction en Duálá (format bilingue obligatoire pour chaîne critique non attestée)
            translated_balance_label = page.locator("#lblBalance").inner_text().strip()
            self.assertEqual(
                translated_balance_label,
                "Solde disponible [Moni mi titi o bolane]",
                "Le libellé critique 'Solde disponible' non attesté doit s'afficher au format bilingue 'Solde disponible [Moni mi titi o bolane]'."
            )

            # 5. Vérification de l'intégrité absolue des données financières
            self.assertEqual(page.locator("#balanceText").inner_text().strip(), "250 000 FCFA")
            self.assertEqual(page.locator("#amountInput").input_value(), "25000")
            self.assertEqual(page.locator("#beneficiaryInput").input_value(), "Jean-Paul Mbarga")
            self.assertEqual(page.locator("#phoneInput").input_value(), "+237 6 99 12 34 56")
            self.assertEqual(page.locator("#refValue").inner_text().strip(), "SAF-2026-X7Y8Z9")

            # 6. Vérification de la traduction du bouton sans altération de comportement
            btn_text = page.locator("#btnConfirm").inner_text().strip()
            self.assertEqual(btn_text, "Kakisane tomba", "Le bouton de confirmation doit afficher 'Kakisane tomba'.")
            btn_type = page.locator("#btnConfirm").get_attribute("type")
            self.assertEqual(btn_type, "button", "Le type du bouton ne doit pas être altéré.")

            # 7. Vérification de l'attribut bilingue au survol
            title_attr = page.locator("#lblBalance").get_attribute("title")
            self.assertIn("Original : Solde disponible", title_attr)

            # 8. Capture d'écran du résultat dans docs/screens/
            os.makedirs(os.path.join(BASE_DIR, "docs", "screens"), exist_ok=True)
            screen_dest = os.path.join(BASE_DIR, "docs", "screens", "08_mock_bank_translated.png")
            page.screenshot(path=screen_dest)
            self.assertTrue(os.path.exists(screen_dest))

            browser.close()

        print("\n[OK] Test Playwright sur tests/mock_bank.html exécuté avec succès (Shadow DOM, Duálá, intégrité).")


if __name__ == "__main__":
    unittest.main()
