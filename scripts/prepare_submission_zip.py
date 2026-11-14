# -*- coding: utf-8 -*-
"""
Script de préparation et de validation du livrable final zippé : dist/safinum_soumission.zip.
Règles strictes :
- Exclusion absolue : backend/models/, .env, .git, __pycache__, node_modules, feedback_submissions.json.
- Inclusions : extension/, backend/, catalogue/, docs/, tests/, scripts/, openapi.yaml, README.md,
  THIRD_PARTY.md, .env.example, requirements.txt, AGENTS.md, SUIVI.md.
- Audit de sécurité post-création : détection stricte de tokens ('sk-', 'hf_', 'api_key=').
- Test en environnement vierge décompressé : exécution réelle des tests unitaires et E2E.
"""

import os
import sys
import shutil
import zipfile
import tempfile
import subprocess
import re

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(REPO_ROOT, "dist")
ZIP_PATH = os.path.join(DIST_DIR, "safinum_soumission.zip")

EXCLUDE_PATTERNS = [
    r"[\\/]models([\\/]|$)",
    r"\.env$",               # Exclut le vrai .env mais conserve .env.example
    r"[\\/]\.git([\\/]|$)",
    r"[\\/]__pycache__([\\/]|$)",
    r"\.py[co]$",
    r"[\\/]node_modules([\\/]|$)",
    r"feedback_submissions\.json$",
    r"\.DS_Store$",
    r"Thumbs\.db$",
    r"[\\/]\.idea([\\/]|$)",
    r"[\\/]\.vscode([\\/]|$)"
]

INCLUDE_DIRS = [
    "extension",
    "backend",
    "catalogue",
    "data",
    "docs",
    "tests",
    "scripts"
]

INCLUDE_FILES = [
    "openapi.yaml",
    "README.md",
    "THIRD_PARTY.md",
    ".env.example",
    "requirements.txt",
    "AGENTS.md",
    "SUIVI.md"
]


def should_exclude(rel_path: str) -> bool:
    norm_path = rel_path.replace("\\", "/")
    # Vérification explicite des fichiers sensibles
    if norm_path == ".env" or norm_path.endswith("/.env"):
        return True
    if norm_path.endswith("feedback_submissions.json"):
        return True
    if "backend/models" in norm_path or "/models/" in norm_path:
        return True
    if "__pycache__" in norm_path or norm_path.endswith(".pyc"):
        return True
    if ".git" in norm_path.split("/"):
        return True
    if "node_modules" in norm_path.split("/"):
        return True

    # Règle d'optimisation livrable : conserver uniquement le jeu complet passB_*
    if norm_path.startswith("docs/screens/"):
        if not norm_path.startswith("docs/screens/final/passB_"):
            return True

    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, rel_path, re.IGNORECASE):
            return True
    return False


def create_submission_zip():
    print(f"======================================================================")
    print(f" 1. CRÉATION DU LIVRABLE ZIP : {ZIP_PATH}")
    print(f"======================================================================")

    os.makedirs(DIST_DIR, exist_ok=True)
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    files_added = []

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Ajout des fichiers individuels racine
        for fname in INCLUDE_FILES:
            fpath = os.path.join(REPO_ROOT, fname)
            if os.path.isfile(fpath) and not should_exclude(fname):
                arcname = fname.replace("\\", "/")
                zf.write(fpath, arcname)
                files_added.append(arcname)
                print(f"  + [FICHIER] {arcname}")

        # 2. Ajout des dossiers inclus
        for dname in INCLUDE_DIRS:
            dir_full = os.path.join(REPO_ROOT, dname)
            if not os.path.isdir(dir_full):
                continue
            for root, dirs, files in os.walk(dir_full):
                # Filtrer les dossiers exclus pour ne pas les parcourir inutilement
                dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
                for file in sorted(files):
                    file_full = os.path.join(root, file)
                    rel_path = os.path.relpath(file_full, REPO_ROOT)
                    if not should_exclude(rel_path):
                        arcname = rel_path.replace("\\", "/")
                        zf.write(file_full, arcname)
                        files_added.append(arcname)

    zip_size_bytes = os.path.getsize(ZIP_PATH)
    zip_size_mb = zip_size_bytes / (1024 * 1024)
    print(f"\nZIP créé avec succès : {len(files_added)} fichiers ({zip_size_mb:.2f} Mo, {zip_size_bytes:,} octets).")
    return files_added


def list_and_inspect_zip():
    print(f"\n======================================================================")
    print(f" 2. INVENTAIRE COMPLET DU CONTENU DU ZIP ({ZIP_PATH})")
    print(f"======================================================================")

    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        infolist = zf.infolist()
        total_uncompressed = sum(info.file_size for info in infolist)
        total_compressed = sum(info.compress_size for info in infolist)

        print(f"Nombre total d'éléments : {len(infolist)}")
        print(f"Taille non compressée   : {total_uncompressed:,} octets ({total_uncompressed / (1024 * 1024):.2f} Mo)")
        print(f"Taille compressée       : {total_compressed:,} octets ({total_compressed / (1024 * 1024):.2f} Mo)")
        print(f"Taux de compression     : {(1 - total_compressed / total_uncompressed) * 100:.1f}%\n")

        print("--- Liste détaillée des fichiers archivés ---")
        for info in sorted(infolist, key=lambda x: x.filename):
            print(f"  {info.filename:<55} {info.file_size:>10,} o  -> {info.compress_size:>9,} o")


def audit_secrets_in_zip():
    print(f"\n======================================================================")
    print(f" 3. AUDIT DE SÉCURITÉ : RECHERCHE DE CLÉS D'API ET TOKENS")
    print(f"======================================================================")

    suspicious_patterns = [
        ("sk-", re.compile(r"sk-[a-zA-Z0-9_\-]{15,}")),
        ("hf_", re.compile(r"hf_[a-zA-Z0-9_\-]{15,}")),
        ("api_key=", re.compile(r"api_key\s*=\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE)),
        ("Bearer token", re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]{15,}", re.IGNORECASE)),
        ("Private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"))
    ]

    findings = []

    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        for name in zf.namelist():
            # Ne tester que les fichiers texte
            if any(name.lower().endswith(ext) for ext in [".png", ".jpg", ".wav", ".bin", ".spm", ".zip"]):
                continue

            # Ne pas s'auto-scanner
            if name.endswith("prepare_submission_zip.py"):
                continue

            try:
                content = zf.read(name).decode("utf-8", errors="ignore")
            except Exception:
                continue

            lines = content.splitlines()
            for line_no, line in enumerate(lines, start=1):
                # 1. Vérification des 3 patterns littéraux demandés par l'utilisateur
                for lit_pat in ["sk-", "hf_", "api_key="]:
                    if lit_pat in line:
                        # Filtrer les simples arguments python ou commentaires sans valeur secrète
                        if line.strip() == "super().__init__(api_key=api_key, timeout_seconds=timeout_seconds)":
                            continue
                        if "TRANSLATION_API_KEY=\"\"" in line:
                            continue
                        findings.append({
                            "file": name,
                            "line": line_no,
                            "type": lit_pat,
                            "snippet": line.strip()[:100]
                        })

                # 2. Vérification des regex de tokens d'authentification réels
                for label, regex in suspicious_patterns:
                    match = regex.search(line)
                    if match:
                        matched_str = match.group(0)
                        if "your_api_key" in matched_str or "TRANSLATION_API_KEY=\"\"" in line:
                            continue
                        if not any(f["file"] == name and f["line"] == line_no for f in findings):
                            findings.append({
                                "file": name,
                                "line": line_no,
                                "type": label,
                                "snippet": line.strip()[:100]
                            })

    print(f"Résultat du scan de sécurité dans le ZIP :")
    if not findings:
        print("  -> [SUCCÈS] 0 secret, clé d'API ou token détecté dans l'archive.")
        print("  -> Aucun pattern 'sk-', 'hf_', 'api_key=' suspect présent.")
    else:
        print(f"  -> [ALERTE] {len(findings)} motif(s) suspect(s) trouvé(s) :")
        for f in findings:
            print(f"     ! {f['file']}:{f['line']} [{f['type']}] -> {f['snippet']}")

    return len(findings) == 0


def test_in_clean_temp_dir():
    print(f"\n======================================================================")
    print(f" 4. DÉCOMPRESSION ET EXÉCUTION DES TESTS EN DOSSIER TEMPORAIRE PROPRE")
    print(f"======================================================================")

    temp_dir = tempfile.mkdtemp(prefix="safinum_clean_test_")
    print(f"Dossier temporaire créé : {temp_dir}")

    try:
        with zipfile.ZipFile(ZIP_PATH, "r") as zf:
            zf.extractall(temp_dir)
        print("Décompression intégrale effectuée avec succès.")

        # 1. Tests racine
        print("\n--- [A] Exécution des tests racine (tests/) depuis le dossier extrait ---")
        res_root = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        print(res_root.stdout)
        if res_root.stderr:
            print(res_root.stderr)
        print(f"Code de sortie tests racine : {res_root.returncode}")

        # 2. Tests backend
        print("\n--- [B] Exécution des tests backend (backend/tests/) depuis le dossier extrait ---")
        res_backend = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "backend/tests"],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        print(res_backend.stdout)
        if res_backend.stderr:
            print(res_backend.stderr)
        print(f"Code de sortie tests backend : {res_backend.returncode}")

        # 3. Décompte unitaire par fichier de test
        print("\n--- [C] Décompte certifié des tests par fichier (TestLoader) ---")
        count_script = (
            "import os, unittest\n"
            "loader = unittest.TestLoader()\n"
            "print('Tests backend/tests/ :')\n"
            "b_total = 0\n"
            "for f in sorted(os.listdir('backend/tests')):\n"
            "    if f.startswith('test_') and f.endswith('.py'):\n"
            "        suite = loader.loadTestsFromName('backend.tests.' + f[:-3])\n"
            "        cnt = suite.countTestCases()\n"
            "        b_total += cnt\n"
            "        print(f'  - backend/tests/{f} : {cnt} tests')\n"
            "print(f'Total backend : {b_total} tests\\n')\n"
            "print('Tests racine tests/ :')\n"
            "r_total = 0\n"
            "for f in sorted(os.listdir('tests')):\n"
            "    if f.startswith('test_') and f.endswith('.py'):\n"
            "        suite = loader.loadTestsFromName('tests.' + f[:-3])\n"
            "        cnt = suite.countTestCases()\n"
            "        r_total += cnt\n"
            "        print(f'  - tests/{f} : {cnt} tests')\n"
            "print(f'Total racine  : {r_total} tests\\n')\n"
            "print(f'TOTAL GÉNÉRAL : {b_total + r_total} tests')\n"
        )
        res_count = subprocess.run(
            [sys.executable, "-c", count_script],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        print(res_count.stdout)

        success = (res_root.returncode == 0 and res_backend.returncode == 0)
        print(f"\nBilan validation dossier temporaire : {'SUCCÈS TOTAL (PASS)' if success else 'ÉCHEC (FAIL)'}")
        return success

    finally:
        print(f"\nNettoyage du dossier temporaire {temp_dir}...")
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("Dossier temporaire nettoyé.")


def main():
    create_submission_zip()
    list_and_inspect_zip()
    secrets_ok = audit_secrets_in_zip()
    tests_ok = test_in_clean_temp_dir()

    print(f"\n======================================================================")
    print(f" SYNTHÈSE FINALE DE LIVRAISON")
    print(f"======================================================================")
    print(f"Archive        : {ZIP_PATH}")
    print(f"Audit secrets  : {'PASS (0 token)' if secrets_ok else 'FAIL'}")
    print(f"Tests propres  : {'PASS (100% réussis)' if tests_ok else 'FAIL'}")


if __name__ == "__main__":
    main()
