import os
import json
from datasets import load_dataset
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_DIR = os.path.join(SCRIPT_DIR, "..", "shared", "data")
OUT_DIR = os.path.join(SHARED_DIR, "bassa", "samples")
OUT_FILE = os.path.join(OUT_DIR, "afrolingu_100.json")

os.makedirs(OUT_DIR, exist_ok=True)
load_dotenv(os.path.join(SCRIPT_DIR, "..", ".env"))

token = os.getenv("HF_TOKEN")

print("Chargement en mode stream...")
# Use streaming to avoid downloading the whole dataset
ds = load_dataset('UBC-NLP/AfroLingu-MT', 'default', token=token, split='train', streaming=True)

bassa_rows = []
print("Recherche de lignes avec langcode contenant 'bas'...")
for i, row in enumerate(ds):
    # 'bas' language code might be eng-bas, fra-bas, bas-eng, etc.
    if "bas" in row.get("langcode", ""):
        bassa_rows.append(row)
        if len(bassa_rows) >= 100:
            break
            
print(f"{len(bassa_rows)} lignes trouvées.")

if bassa_rows:
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(bassa_rows, f, ensure_ascii=False, indent=2)
    print(f"Sauvegardé dans {OUT_FILE}")
else:
    print("Aucune ligne trouvée pour 'bas'.")
