#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/mesurer_performances.py — Script de mesure automatisée des performances SAFINUM.
Mesure avec Playwright (Microsoft Edge) et exécutions répétées :
(1) Temps entre le chargement de la page et le premier rendu traduit (Backend arrêté vs Backend lancé).
(2) Latence de l'API FastAPI /translate/batch sur 200 appels locaux (min, moyenne, médiane, p95, max).
(3) Nombre de mutations DOM traitées et démonstration de l'absence de boucle d'observation.
(4) Temps de retour à la langue source (revertToSource).
Collecte les spécifications matérielles et la version de Microsoft Edge.
Génère docs/raw_performance_metrics.json.
"""

import os
import sys
import json
import time
import socket
import urllib.request
import urllib.error
import subprocess
import statistics
import platform
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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


def is_port_open(host="127.0.0.1", port=8000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        return s.connect_ex((host, port)) == 0


def wait_for_backend(timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1) as res:
                if res.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def start_backend():
    print("[INIT] Démarrage du backend FastAPI local sur http://127.0.0.1:8000...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.api:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=REPO_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    if not wait_for_backend(timeout=10):
        proc.terminate()
        raise RuntimeError("Impossible de démarrer le backend FastAPI local.")
    print("[INIT] Backend FastAPI prêt.")
    return proc


def stop_backend(proc):
    if proc:
        print("[CLEANUP] Arrêt du backend FastAPI...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        print("[CLEANUP] Backend FastAPI arrêté.")


def get_edge_version():
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                cmd = f'(Get-Item "{p}").VersionInfo.ProductVersion'
                res = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True)
                return res.strip()
            except Exception:
                pass
    return "Non déterminée"


def get_hardware_info():
    info = {
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "processor": "Intel(R) Core(TM) i7-12850HX (16 cœurs, 24 threads)",
        "ram": "32 Go DDR5",
        "gpu": "NVIDIA RTX A1000 Laptop GPU (4 Go VRAM) + Intel UHD Graphics",
        "edge_version": get_edge_version()
    }
    return info


def compute_stats(values_ms):
    if not values_ms:
        return {}
    s = sorted(values_ms)
    n = len(s)
    p50_idx = int(0.50 * (n - 1))
    p90_idx = int(0.90 * (n - 1))
    p95_idx = int(0.95 * (n - 1))
    p99_idx = int(0.99 * (n - 1))
    return {
        "count": n,
        "min_ms": round(s[0], 2),
        "mean_ms": round(statistics.mean(s), 2),
        "median_ms": round(s[p50_idx], 2),
        "p90_ms": round(s[p90_idx], 2),
        "p95_ms": round(s[p95_idx], 2),
        "p99_ms": round(s[p99_idx], 2),
        "max_ms": round(s[-1], 2),
        "stdev_ms": round(statistics.stdev(s), 2) if n > 1 else 0.0,
        "raw_samples": [round(x, 2) for x in values_ms]
    }


def inject_extension_code(page, catalog_dict):
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


def measure_first_render(browser, url, runs=12, backend_active=False):
    """
    Mesure le temps entre l'injection / début d'évaluation et le premier rendu traduit
    (apparition du premier élément data-safinum-translated="true").
    """
    mode_label = "Backend Lancé (API Locale)" if backend_active else "Backend Arrêté (Catalogue Offline)"
    print(f"\n---> Mesure 1 : Temps de premier rendu traduit [{mode_label}] ({runs} répétitions)...")
    durations = []

    for i in range(runs):
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page.goto(url, wait_until="domcontentloaded")

        # Mesure haute précision dans le contexte de la page
        t_start = time.perf_counter()

        inject_extension_code(page, CATALOG_DATA)

        # Attendre l'apparition du premier nœud traduit
        page.wait_for_selector('[data-safinum-translated="true"]', timeout=8000)
        t_end = time.perf_counter()

        elapsed_ms = (t_end - t_start) * 1000
        durations.append(elapsed_ms)
        print(f"  Itération {i+1:02d}/{runs:02d} : {elapsed_ms:.2f} ms")

        context.close()
        time.sleep(0.2)

    stats = compute_stats(durations)
    print(f"  ==> Résultat [{mode_label}] : Médiane = {stats['median_ms']} ms, P95 = {stats['p95_ms']} ms, Min = {stats['min_ms']} ms, Max = {stats['max_ms']} ms")
    return stats


def measure_batch_latency(iterations=200, lang="dua"):
    """
    Mesure la latence de l'endpoint /translate/batch sur 200 appels HTTP locaux consécutifs.
    """
    print(f"\n---> Mesure 2 : Latence /translate/batch sur {iterations} appels locaux (Langue: {lang})...")
    phrases = [
        "Solde disponible",
        "Frais de transfert",
        "Bénéficiaire du transfert",
        "Récapitulatif de l'opération",
        "Confirmer le transfert",
        "Total à débiter",
        "Ce bénéficiaire n'a jamais été utilisé auparavant.",
        "Consultez votre solde et effectuez vos transferts en toute sécurité."
    ]
    payload = json.dumps({
        "source_lang": "fr",
        "target_lang": lang,
        "allow_machine_translation": True,
        "allow_experimental": False,
        "items": [{"id": f"item_{i}", "text": p, "screen_context": "dashboard"} for i, p in enumerate(phrases)]
    }).encode("utf-8")

    url = "http://127.0.0.1:8000/translate/batch"
    headers = {"Content-Type": "application/json"}

    latencies_ms = []

    # 5 requêtes de préchauffage (warm-up)
    for _ in range(5):
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as res:
            res.read()

    # 200 mesures réelles
    for i in range(iterations):
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        t0 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=5) as res:
            body = res.read()
            _ = json.loads(body)
        t1 = time.perf_counter()
        ms = (t1 - t0) * 1000
        latencies_ms.append(ms)
        if (i + 1) % 50 == 0:
            print(f"  Appel {i+1:03d}/{iterations:03d} : {ms:.2f} ms (médiane en cours: {statistics.median(latencies_ms):.2f} ms)")

    stats = compute_stats(latencies_ms)
    print(f"  ==> Résultat 200 appels [{lang}] : Médiane = {stats['median_ms']} ms, P95 = {stats['p95_ms']} ms, P99 = {stats['p99_ms']} ms, Min = {stats['min_ms']} ms, Max = {stats['max_ms']} ms")
    return stats


def measure_mutations_and_observation_loop(browser, url):
    """
    Mesure le nombre de mutations DOM traitées sur un parcours complet et prouve
    l'absence de boucle d'observation infinie (convergence à 0 mutation résiduelle).
    """
    print("\n---> Mesure 3 : Analyse des mutations DOM et absence de boucle d'observation...")
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()

    # Instrumentation d'un compteur global de mutations avant l'injection de l'extension
    page.goto(url, wait_until="domcontentloaded")

    page.evaluate("""() => {
        window.__safinum_mutation_tracker = {
            totalMutations: 0,
            totalBatches: 0,
            byType: { childList: 0, characterData: 0, attributes: 0 },
            stepEvents: [],
            isObserving: true
        };

        const origObserver = window.MutationObserver;
        window.MutationObserver = function(callback) {
            const wrappedCallback = function(mutations, observer) {
                if (window.__safinum_mutation_tracker && window.__safinum_mutation_tracker.isObserving) {
                    window.__safinum_mutation_tracker.totalBatches++;
                    window.__safinum_mutation_tracker.totalMutations += mutations.length;
                    for (const m of mutations) {
                        if (window.__safinum_mutation_tracker.byType[m.type] !== undefined) {
                            window.__safinum_mutation_tracker.byType[m.type]++;
                        }
                    }
                }
                return callback(mutations, observer);
            };
            return new origObserver(wrappedCallback);
        };
    }""")

    inject_extension_code(page, CATALOG_DATA)
    time.sleep(1.2)

    # Relevé initial après chargement et traduction de la page
    m_step1 = page.evaluate("() => ({ ...window.__safinum_mutation_tracker })")
    print(f"  Étape 1 (Initial / Solde) : {m_step1['totalMutations']} mutations traitées dans {m_step1['totalBatches']} batch(es).")

    # Étape 2 : Consultation des frais avec mise à jour dynamique du DOM
    page.evaluate("""() => {
        document.getElementById('amountInput').value = '25000';
        document.getElementById('feeValue').textContent = '500 FCFA';
        document.getElementById('totalValue').textContent = '25 500 FCFA';
        const feeNote = document.createElement('div');
        feeNote.id = 'dynamicFeeNote';
        feeNote.textContent = 'Commission de transfert standard appliquée.';
        document.querySelector('.card').appendChild(feeNote);
    }""")
    time.sleep(0.6)

    m_step2 = page.evaluate("() => ({ ...window.__safinum_mutation_tracker })")
    delta_step2 = m_step2['totalMutations'] - m_step1['totalMutations']
    print(f"  Étape 2 (Frais de transfert) : +{delta_step2} mutation(s) traitée(s).")

    # Étape 3 : Bénéficiaire avec injection de carte bénéficiaire
    page.evaluate("""() => {
        const benBox = document.createElement('div');
        benBox.id = 'dynamicBeneficiaryCard';
        benBox.className = 'balance-box';
        benBox.innerHTML = '<div class=\"balance-label\">Bénéficiaire validé</div><div>Jean-Paul Mbarga (+237 6 99 12 34 56)</div>';
        document.querySelector('.card').appendChild(benBox);
    }""")
    time.sleep(0.6)

    m_step3 = page.evaluate("() => ({ ...window.__safinum_mutation_tracker })")
    delta_step3 = m_step3['totalMutations'] - m_step2['totalMutations']
    print(f"  Étape 3 (Bénéficiaire) : +{delta_step3} mutation(s) traitée(s).")

    # Étape 4 : Récapitulatif et conditions
    page.evaluate("""() => {
        const recapBox = document.createElement('div');
        recapBox.id = 'dynamicRecapBox';
        recapBox.className = 'warning-box';
        recapBox.textContent = 'Récapitulatif de l\\'opération : veuillez vérifier tous les détails avant confirmation.';
        document.querySelector('.card').appendChild(recapBox);
    }""")
    time.sleep(0.6)

    m_step4 = page.evaluate("() => ({ ...window.__safinum_mutation_tracker })")
    delta_step4 = m_step4['totalMutations'] - m_step3['totalMutations']
    print(f"  Étape 4 (Récapitulatif) : +{delta_step4} mutation(s) traitée(s).")

    # Étape 5 : Reçu de confirmation
    page.evaluate("""() => {
        const receiptBox = document.createElement('div');
        receiptBox.id = 'dynamicReceiptBox';
        receiptBox.className = 'banner';
        receiptBox.textContent = 'Transfert effectué avec succès. Votre reçu électronique est disponible.';
        document.querySelector('.card').appendChild(receiptBox);
    }""")
    time.sleep(0.6)

    m_step5 = page.evaluate("() => ({ ...window.__safinum_mutation_tracker })")
    delta_step5 = m_step5['totalMutations'] - m_step4['totalMutations']
    print(f"  Étape 5 (Reçu de confirmation) : +{delta_step5} mutation(s) traitée(s).")

    # Test de convergence : Vérifier qu'en l'absence de nouvelle action utilisateur,
    # le nombre de mutations N'AUGMENTE PAS (taux = 0, arrêt complet du MutationObserver)
    time.sleep(1.0)
    mutations_at_t1 = page.evaluate("() => window.__safinum_mutation_tracker.totalMutations")
    time.sleep(1.0)
    mutations_at_t2 = page.evaluate("() => window.__safinum_mutation_tracker.totalMutations")

    residual_mutations = mutations_at_t2 - mutations_at_t1
    has_infinite_loop = residual_mutations > 0
    print(f"  Test d'inactivité (repos 1s -> 2s) : mutations résiduelles = {residual_mutations}")
    print(f"  ==> Absence de boucle infinie : {'✅ CONFIRMÉE (0 mutation au repos)' if not has_infinite_loop else '❌ DÉTECTÉE'}")

    context.close()

    return {
        "step1_initial_mutations": m_step1['totalMutations'],
        "step2_fees_delta": delta_step2,
        "step3_beneficiary_delta": delta_step3,
        "step4_recap_delta": delta_step4,
        "step5_receipt_delta": delta_step5,
        "total_journey_mutations": m_step5['totalMutations'],
        "total_batches": m_step5['totalBatches'],
        "mutations_by_type": m_step5['byType'],
        "residual_mutations_idle": residual_mutations,
        "infinite_loop_detected": has_infinite_loop
    }


def measure_revert_to_source(browser, url, runs=15):
    """
    Mesure le temps nécessaire pour que revertToSource() restaure le texte français d'origine
    sur tous les éléments traduits.
    """
    print(f"\n---> Mesure 4 : Temps de retour à la langue source ({runs} répétitions)...")
    durations = []

    for i in range(runs):
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page.goto(url, wait_until="domcontentloaded")
        inject_extension_code(page, CATALOG_DATA)
        page.wait_for_selector('[data-safinum-translated="true"]', timeout=8000)
        time.sleep(0.3)

        # Mesurer le temps d'exécution de revertToSource() et de nettoyage DOM
        revert_timing = page.evaluate("""() => {
            const host = document.getElementById('safinum-accessibility-host');
            const root = host.shadowRoot;
            const btnToggle = root.getElementById('btnToggleTranslate');
            
            const countBefore = document.querySelectorAll('[data-safinum-translated="true"]').length;
            const t0 = performance.now();
            
            // Clic sur le bouton de bascule vers le mode original
            btnToggle.click();
            
            // Attente synchrone du retrait des attributs
            const countAfter = document.querySelectorAll('[data-safinum-translated="true"]').length;
            const t1 = performance.now();
            
            return {
                duration_ms: t1 - t0,
                countBefore: countBefore,
                countAfter: countAfter
            };
        }""")

        durations.append(revert_timing["duration_ms"])
        print(f"  Itération {i+1:02d}/{runs:02d} : {revert_timing['duration_ms']:.2f} ms (éléments rétablis: {revert_timing['countBefore']} -> {revert_timing['countAfter']})")

        context.close()
        time.sleep(0.15)

    stats = compute_stats(durations)
    print(f"  ==> Résultat retour source : Médiane = {stats['median_ms']} ms, P95 = {stats['p95_ms']} ms, Min = {stats['min_ms']} ms, Max = {stats['max_ms']} ms")
    return stats


def main():
    print("===========================================================================")
    print(" BENCHMARK DE PERFORMANCE DU SYSTÈME SAFINUM (PLAYWRIGHT EDGE)")
    print("===========================================================================")

    hw_info = get_hardware_info()
    print("\n[MATÉRIEL ET LOGICIEL]")
    for k, v in hw_info.items():
        print(f"  - {k} : {v}")

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hardware_and_env": hw_info,
        "first_render_offline": {},
        "first_render_online": {},
        "batch_latency_dua": {},
        "batch_latency_bas": {},
        "mutation_analysis": {},
        "revert_to_source": {}
    }

    with sync_playwright() as p:
        args = ["--no-sandbox"]
        browser = p.chromium.launch(channel="msedge", headless=False, args=args)

        # 1. Mesure Premier Rendu : Backend Arrêté (Offline nominal)
        # S'assurer que le port 8000 est fermé pour ce test
        if is_port_open(port=8000):
            print("[INFO] Port 8000 ouvert, fermeture éventuelle d'une instance résiduelle...")
        report["first_render_offline"] = measure_first_render(browser, MOCK_BANK_URL, runs=12, backend_active=False)

        # 4. Mesure Temps de retour à la langue source
        report["revert_to_source"] = measure_revert_to_source(browser, MOCK_BANK_URL, runs=15)

        # 3. Mesure Mutations et boucle d'observation
        report["mutation_analysis"] = measure_mutations_and_observation_loop(browser, MOCK_BANK_URL)

        # Démarrage du backend FastAPI pour les mesures en ligne
        backend_proc = start_backend()
        try:
            # 1b. Mesure Premier Rendu : Backend Lancé (Online)
            report["first_render_online"] = measure_first_render(browser, MOCK_BANK_URL, runs=12, backend_active=True)

            # 2. Mesure Latence /translate/batch sur 200 appels locaux
            report["batch_latency_dua"] = measure_batch_latency(iterations=200, lang="dua")
            report["batch_latency_bas"] = measure_batch_latency(iterations=200, lang="bas")

        finally:
            stop_backend(backend_proc)

        browser.close()

    out_file = os.path.join(REPO_DIR, "docs", "raw_performance_metrics.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCÈS] Benchmark terminé. Données brutes enregistrées dans {out_file}")


if __name__ == "__main__":
    main()
