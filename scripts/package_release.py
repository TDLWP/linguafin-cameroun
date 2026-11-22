# -*- coding: utf-8 -*-
"""
scripts/package_release.py
Produit les archives officielles de distribution pour LinguaFin SAFINUM 2026 :
1. dist/extension_linguafin_v2.zip :
   - Contient l extension Manifest V3 prete a l emploi.
   - manifest.json STRICTEMENT place a la racine de l archive.
2. dist/linguafin_v2_source.zip :
   - Contient l integralite du code source du projet.
   - Exclusions strictes : backend/models, .env, .git, __pycache__, dist, .pytest_cache, .vscode, .idea.

Garanties integrees :
- Scan anti-secrets (hf_, sk-, api_key=, tokens d acces reels).
- Verification des tailles de fichiers.
- Decompression de controle en sandbox temporaire.
"""

import os
import sys
import re
import shutil
import zipfile
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(REPO_ROOT, "dist")
EXT_DIR = os.path.join(REPO_ROOT, "extension")

ZIP_EXT_PATH = os.path.join(DIST_DIR, "extension_linguafin_v2.zip")
ZIP_SRC_PATH = os.path.join(DIST_DIR, "linguafin_v2_source.zip")

EXCLUDE_PATTERNS = [
    r"[\\/]models([\\/]|$)",
    r"\.env$",               # Exclut le fichier .env prive, garde .env.example
    r"[\\/]\.git([\\/]|$)",
    r"[\\/]__pycache__([\\/]|$)",
    r"\.py[co]$",
    r"[\\/]node_modules([\\/]|$)",
    r"[\\/]dist([\\/]|$)",
    r"feedback_submissions\.json$",
    r"\.DS_Store$",
    r"Thumbs\.db$",
    r"[\\/]\.idea([\\/]|$)",
    r"[\\/]\.vscode([\\/]|$)",
    r"[\\/]\.pytest_cache([\\/]|$)",
]


def should_exclude_source(rel_path: str) -> bool:
    norm = rel_path.replace("\\", "/")
    if norm == ".env" or norm.endswith("/.env"):
        return True
    if norm.endswith("feedback_submissions.json"):
        return True
    if "backend/models" in norm or "/models/" in norm:
        return True
    if "__pycache__" in norm or norm.endswith(".pyc"):
        return True
    if ".git" in norm.split("/"):
        return True
    if "dist" in norm.split("/"):
        return True
    for pat in EXCLUDE_PATTERNS:
        if re.search(pat, rel_path, re.IGNORECASE):
            return True
    return False


def build_extension_zip() -> tuple[str, int, list[str]]:
    print("=" * 70)
    print(" 1. CREATION DU LIVRABLE EXTENSION : dist/extension_linguafin_v2.zip")
    print("=" * 70)
    os.makedirs(DIST_DIR, exist_ok=True)
    if os.path.exists(ZIP_EXT_PATH):
        os.remove(ZIP_EXT_PATH)

    files_added = []
    with zipfile.ZipFile(ZIP_EXT_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(EXT_DIR):
            for file in sorted(files):
                full_path = os.path.join(root, file)
                # manifest.json et fichiers doivent etre a la racine du zip
                rel_path = os.path.relpath(full_path, EXT_DIR).replace("\\", "/")
                zf.write(full_path, rel_path)
                files_added.append(rel_path)
                print(f"  + [EXT ROOT] {rel_path} ({os.path.getsize(full_path):,} o)")

    size = os.path.getsize(ZIP_EXT_PATH)
    print(f"\n[OK] extension_linguafin_v2.zip cree : {len(files_added)} fichiers, {size:,} octets ({size / 1024:.1f} Ko).")
    return ZIP_EXT_PATH, size, files_added


def build_source_zip() -> tuple[str, int, list[str]]:
    print("\n" + "=" * 70)
    print(" 2. CREATION DU LIVRABLE SOURCE : dist/linguafin_v2_source.zip")
    print("=" * 70)
    os.makedirs(DIST_DIR, exist_ok=True)
    if os.path.exists(ZIP_SRC_PATH):
        os.remove(ZIP_SRC_PATH)

    files_added = []
    with zipfile.ZipFile(ZIP_SRC_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(REPO_ROOT):
            # Filtrer les repertoires exclus
            dirs[:] = [d for d in dirs if not should_exclude_source(os.path.relpath(os.path.join(root, d), REPO_ROOT))]
            for file in sorted(files):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, REPO_ROOT)
                if should_exclude_source(rel_path):
                    continue
                arcname = rel_path.replace("\\", "/")
                zf.write(full_path, arcname)
                files_added.append(arcname)

    size = os.path.getsize(ZIP_SRC_PATH)
    print(f"\n[OK] linguafin_v2_source.zip cree : {len(files_added)} fichiers, {size:,} octets ({size / (1024*1024):.2f} Mo).")
    return ZIP_SRC_PATH, size, files_added


def scan_secrets_in_zip(zip_path: str) -> list[dict]:
    suspicious_patterns = [
        ("sk-", re.compile(r"sk-[a-zA-Z0-9_\-]{20,}")),
        ("hf_", re.compile(r"hf_[a-zA-Z0-9_\-]{20,}")),
        ("api_key=", re.compile(r"api_key\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]", re.IGNORECASE)),
        ("Bearer token", re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE)),
        ("Private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"))
    ]

    findings = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            # Ne tester que les fichiers textes
            if any(name.lower().endswith(ext) for ext in [".png", ".jpg", ".wav", ".bin", ".spm", ".zip", ".woff", ".woff2", ".ttf"]):
                continue

            # Ne pas s auto-scanner
            if name.endswith("package_release.py") or name.endswith("prepare_submission_zip.py"):
                continue

            # Ignorer les rapports d audit et tests de securite qui citent les patterns comme exemples
            if "audit" in name.lower() or "test_security" in name.lower():
                continue

            try:
                content = zf.read(name).decode("utf-8", errors="ignore")
            except Exception:
                continue

            for line_no, line in enumerate(content.splitlines(), start=1):
                # Filtrer les placeholders inoffensifs
                if "TRANSLATION_API_KEY=\"\"" in line or "your_api_key" in line or "test_api_key" in line:
                    continue
                if line.strip() == "super().__init__(api_key=api_key, timeout_seconds=timeout_seconds)":
                    continue

                for label, regex in suspicious_patterns:
                    match = regex.search(line)
                    if match:
                        findings.append({
                            "zip": os.path.basename(zip_path),
                            "file": name,
                            "line": line_no,
                            "type": label,
                            "snippet": line.strip()[:100]
                        })

    return findings


def verify_and_test_decompression(zip_ext: str, zip_src: str):
    print("\n" + "=" * 70)
    print(" 3. DECOMPRESSION DE CONTROLE ET VERIFICATION DES EXCLUSIONS")
    print("=" * 70)

    # 1. Controle extension_linguafin_v2.zip
    with tempfile.TemporaryDirectory(prefix="linguafin_ext_test_") as tmp_ext:
        with zipfile.ZipFile(zip_ext, "r") as zf:
            zf.extractall(tmp_ext)
        
        extracted_files = os.listdir(tmp_ext)
        print(f"Contenu extrait de {os.path.basename(zip_ext)} : {extracted_files}")
        assert "manifest.json" in extracted_files, "ERREUR : manifest.json absent a la racine de l extension !"
        assert "content.js" in extracted_files, "ERREUR : content.js absent de l extension !"
        assert "offline_catalog.json" in extracted_files, "ERREUR : offline_catalog.json absent de l extension !"
        assert "catalogue_offline.json" not in extracted_files, "ERREUR : catalogue_offline.json (doublon divergent) ne doit pas être présent !"
        print("  -> [CONTROLE OK] manifest.json est bien situe a la racine du zip.")
        print("  -> [CONTROLE OK] Catalogue unique offline_catalog.json présent sans doublon divergent.")

    # 2. Controle linguafin_v2_source.zip
    with tempfile.TemporaryDirectory(prefix="linguafin_src_test_") as tmp_src:
        with zipfile.ZipFile(zip_src, "r") as zf:
            zf.extractall(tmp_src)

        forbidden_found = []
        for root, dirs, files in os.walk(tmp_src):
            for d in dirs:
                if d in [".git", "__pycache__", "models"]:
                    forbidden_found.append(os.path.join(root, d))
            for f in files:
                if f == ".env" or f.endswith(".pyc") or f == "feedback_submissions.json":
                    forbidden_found.append(os.path.join(root, f))

        if forbidden_found:
            raise RuntimeError(f"ERREUR : Fichiers/dossiers interdits detectes dans la source : {forbidden_found}")

        # Verifier presence des fichiers capitaux
        assert os.path.isfile(os.path.join(tmp_src, "README.md")), "README.md absent de la source !"
        assert os.path.isfile(os.path.join(tmp_src, "openapi.yaml")), "openapi.yaml absent de la source !"
        assert os.path.isfile(os.path.join(tmp_src, "backend", "api.py")), "backend/api.py absent de la source !"
        assert os.path.isfile(os.path.join(tmp_src, "extension", "manifest.json")), "extension/manifest.json absent de la source !"
        assert os.path.isfile(os.path.join(tmp_src, "scripts", "run_all_checks.ps1")), "run_all_checks.ps1 absent !"
        assert os.path.isfile(os.path.join(tmp_src, "scripts", "lancer_demo.ps1")), "lancer_demo.ps1 absent !"

        print("  -> [CONTROLE OK] Zero fichier sensible (models, .git, .env, __pycache__) dans l archive source.")
        print("  -> [CONTROLE OK] Tous les composants cles sont presents.")


def main():
    print("Demarrage de la generation des livrables de distribution v2...\n")

    # 1. Archive extension
    zip_ext, size_ext, files_ext = build_extension_zip()

    # 2. Archive source
    zip_src, size_src, files_src = build_source_zip()

    # 3. Verifications des tailles (seuils : extension < 5 Mo, source < 50 Mo)
    print("\n" + "=" * 70)
    print(" 4. VERIFICATION DES TAILLES DE DISTRIBUTION")
    print("=" * 70)
    print(f"Archive Extension : {size_ext / 1024:.2f} Ko (Seuil max : 5 000 Ko) -> {'CONFORME' if size_ext < 5*1024*1024 else 'DEPASSE'}")
    print(f"Archive Source    : {size_src / (1024*1024):.2f} Mo (Seuil max : 50 Mo)   -> {'CONFORME' if size_src < 50*1024*1024 else 'DEPASSE'}")
    assert size_ext < 5 * 1024 * 1024, "Taille de l extension excessive !"
    assert size_src < 50 * 1024 * 1024, "Taille du code source excessive !"

    # 4. Scan anti-secrets
    print("\n" + "=" * 70)
    print(" 5. SCAN DE SECURITE ANTI-SECRETS DANS LES ARCHIVES")
    print("=" * 70)
    findings_ext = scan_secrets_in_zip(zip_ext)
    findings_src = scan_secrets_in_zip(zip_src)

    if findings_ext or findings_src:
        print("[ALERTE CRITIQUE] Secrets detectes :")
        for f in findings_ext + findings_src:
            print(f"  ! [{f['zip']}] {f['file']}:{f['line']} ({f['type']})")
        sys.exit(1)
    else:
        print("[SUCCES] 0 secret detecte dans extension_linguafin_v2.zip.")
        print("[SUCCES] 0 secret detecte dans linguafin_v2_source.zip.")
        print("         Aucun token hf_, sk-, api_key= ou cle privee detecte.")

    # 5. Decompression de controle
    verify_and_test_decompression(zip_ext, zip_src)

    print("\n" + "=" * 70)
    print(" RECAPITULATIF FINAL DE PACKAGING REUSSI")
    print("=" * 70)
    print(f"1. Extension zip  : {zip_ext} ({size_ext / 1024:.1f} Ko, {len(files_ext)} fichiers)")
    print(f"2. Source zip     : {zip_src} ({size_src / (1024*1024):.2f} Mo, {len(files_src)} fichiers)")
    print("Statut global     : TOUS LES LIVRABLES GENERES ET CERTIFIES CONFORMES.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
