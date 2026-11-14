# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import urllib.request
import time

"""
Script de téléchargement reproductible du modèle de traduction Français -> Fulfulde.
Source : dépôt Hugging Face flagship-ai/cameroon-int8 (dossier francais-fufulde seul).
Licence : CC BY-NC 4.0.
"""

REPO_ID = "flagship-ai/cameroon-int8"
BASE_URL = f"https://huggingface.co/{REPO_ID}/resolve/main/"
SUBDIR = "francais-fufulde"

FILES = [
    "config.json",
    "special_tokens_map.json",
    "tokenizer_config.json",
    "source.spm",
    "target.spm",
    "shared_vocabulary.json",
    "vocab.json",
    "model.bin"
]

def download_file_with_progress(url: str, dest_path: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    t0 = time.time()
    last_print = t0
    
    with urllib.request.urlopen(req, timeout=60) as resp:
        total_size = int(resp.headers.get("Content-Length", 0))
        total_mb = total_size / (1024 * 1024) if total_size else 0
        fname = os.path.basename(dest_path)
        print(f"Téléchargement : {fname} ({total_mb:.2f} Mo)...", flush=True)

        downloaded = 0
        chunk_size = 256 * 1024  # 256 Ko

        with open(dest_path, "wb") as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                now = time.time()
                if now - last_print >= 2.0 or downloaded == total_size:
                    elapsed = max(now - t0, 0.001)
                    speed_mb = (downloaded / (1024 * 1024)) / elapsed
                    pct = (downloaded / total_size * 100) if total_size else 0
                    cur_mb = downloaded / (1024 * 1024)
                    print(f"  [{pct:5.1f}%] {fname} : {cur_mb:.2f} Mo / {total_mb:.2f} Mo ({speed_mb:.2f} Mo/s)", flush=True)
                    last_print = now

    total_dur = time.time() - t0
    final_mb = downloaded / (1024 * 1024)
    print(f"OK : {os.path.basename(dest_path)} ({final_mb:.2f} Mo en {total_dur:.1f}s)", flush=True)

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    target_dir = os.path.join(root_dir, "backend", "models", SUBDIR)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"Destination : {target_dir}", flush=True)
    print(f"Vérification des 8 fichiers du modèle Fulfulde...", flush=True)

    for filename in FILES:
        rel_path = f"{SUBDIR}/{filename}"
        dest_path = os.path.join(target_dir, filename)
        file_url = BASE_URL + rel_path
        
        # Vérification si fichier déjà complet
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            sz = os.path.getsize(dest_path)
            print(f"Fichier déjà présent : {filename} ({sz / (1024*1024):.2f} Mo)", flush=True)
            continue

        temp_path = dest_path + ".tmp"
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

        try:
            download_file_with_progress(file_url, temp_path)
            if os.path.exists(dest_path):
                os.remove(dest_path)
            os.rename(temp_path, dest_path)
        except Exception as e:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            print(f"ERREUR sur {filename}: {e}", flush=True)
            raise e

    print(f"\nLes 8 fichiers du modèle Fulfulde sont présents et complets dans {target_dir}.", flush=True)

if __name__ == "__main__":
    main()
