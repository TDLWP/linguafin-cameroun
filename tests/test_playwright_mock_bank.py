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

            # Capture de l'état textuel de référence des cartes de soumissions du jury (extension désactivée)
            initial_jury_cards = [c.inner_text().strip() for c in page.locator("aside .submission-card").all()]
            self.assertGreater(len(initial_jury_cards), 0, "Les cartes de soumissions doivent exister dans le panneau jury.")
            self.assertTrue(any("Consultation des frais" in c for c in initial_jury_cards))

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

            # 8. RÈGLE CRITIQUE : Sanctuarisation absolue du panneau jury (soumissions identiques avec/sans extension)
            after_jury_cards = [c.inner_text().strip() for c in page.locator("aside .submission-card").all()]
            self.assertEqual(
                initial_jury_cards,
                after_jury_cards,
                "RÈGLE CRITIQUE : Le texte des cartes de l'onglet Soumissions du panneau jury doit être STRICTEMENT IDENTIQUE "
                "avec et sans extension active. L'extension ne doit jamais modifier le panneau jury !"
            )
            # Vérifier qu'aucun élément du panneau jury n'a été annoté ou altéré
            translated_in_jury = page.locator("aside [data-safinum-translated='true']").count()
            self.assertEqual(translated_in_jury, 0, "Aucun élément dans le panneau jury ne doit porter data-safinum-translated.")
            badges_in_jury = page.locator("aside .safinum-novel-badge").count()
            self.assertEqual(badges_in_jury, 0, "Aucun badge 'contenu inédit' ne doit être injecté dans le panneau jury.")
            for card_str in after_jury_cards:
                self.assertNotIn("[Mutoa", card_str, "Le panneau jury ne doit pas contenir de traduction de 'Consultation des frais' !")
                self.assertNotIn("contenu inédit", card_str, "Le panneau jury ne doit pas contenir de badge de contenu inédit !")

            # 9. Capture d'écran du résultat dans docs/screens/
            os.makedirs(os.path.join(BASE_DIR, "docs", "screens"), exist_ok=True)
            screen_dest = os.path.join(BASE_DIR, "docs", "screens", "08_mock_bank_translated.png")
            page.screenshot(path=screen_dest)
            self.assertTrue(os.path.exists(screen_dest))

            browser.close()

        print("\n[OK] Test Playwright sur tests/mock_bank.html exécuté avec succès (Shadow DOM, Duálá, intégrité, sanctuarisation jury).")

    def test_configurable_exclusion_selectors(self):
        """
        Vérifie qu'un sélecteur d'exclusion configurable (via window.SAFINUM_EXCLUDED_SELECTORS)
        permet d'exclure arbitrairement n'importe quel conteneur de la collecte et de la traduction.
        """
        mock_html_path = os.path.abspath(os.path.join(BASE_DIR, "tests", "mock_bank.html"))
        content_js_path = os.path.abspath(os.path.join(BASE_DIR, "extension", "content.js"))
        catalog_path = os.path.abspath(os.path.join(BASE_DIR, "extension", "offline_catalog.json"))

        with open(content_js_path, "r", encoding="utf-8") as f:
            content_js = f.read()

        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog_dict = json.load(f)

        file_url = f"file:///{mock_html_path.replace(os.sep, '/')}"

        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            page = browser.new_page()
            page.goto(file_url)

            # Insérer dynamiquement une zone protégée avec un sélecteur custom
            page.evaluate("""() => {
                const customZone = document.createElement('div');
                customZone.id = 'my-custom-protected-container';
                customZone.innerHTML = '<span id="protectedText">Frais de transfert</span>';
                document.getElementById('app').appendChild(customZone);

                // Configurer le sélecteur d'exclusion avant l'injection
                window.SAFINUM_EXCLUDED_SELECTORS = ['#my-custom-protected-container', 'aside'];
            }""")

            # Injecter l'extension
            page.evaluate("""(catalogData) => {
                window.chrome = window.chrome || {};
                window.chrome.runtime = {
                    getURL: function(path) { return 'mock://' + path; }
                };
                window.fetch = async function(url, opts) {
                    if (typeof url === 'string' && url.includes('offline_catalog.json')) {
                        return { ok: true, json: async () => catalogData };
                    }
                    throw new TypeError('Offline fallback');
                };
            }""", catalog_dict)
            page.evaluate(content_js)
            page.wait_for_timeout(500)

            # Vérifier que le texte principal normal est traduit
            self.assertIn("Moni mi titi", page.locator("#lblBalance").inner_text())

            # Vérifier que la zone protégée custom n'a PAS été traduite
            protected_text = page.locator("#protectedText").inner_text().strip()
            self.assertEqual(
                protected_text,
                "Frais de transfert",
                "Le texte dans #my-custom-protected-container doit rester strictement 'Frais de transfert' sans traduction !"
            )
            self.assertEqual(page.locator("#protectedText").get_attribute("data-safinum-translated"), None)

            browser.close()


if __name__ == "__main__":
    unittest.main()
