import json
import urllib.request
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_DIR = os.path.join(SCRIPT_DIR, "..", "shared", "data")
LEXIQUE_FILE = os.path.join(SHARED_DIR, "bassa", "lexique_bassa.json")
AUDIO_DIR = os.path.join(SHARED_DIR, "bassa", "audio")

os.makedirs(AUDIO_DIR, exist_ok=True)

if not os.path.exists(LEXIQUE_FILE):
    print("Lexique not found.")
    exit(1)

with open(LEXIQUE_FILE, "r", encoding="utf-8") as f:
    entries = json.load(f)

success_count = 0
fail_count = 0

for entry in entries:
    audio_url = entry.get("audio_src_url")
    # Si on n'a pas d'URL ou si c'est déjà téléchargé (audio_path est rempli avec le chemin local)
    if not audio_url:
        continue
    
    # On va nommer le fichier bas_<id>.wav
    # ex: id = bas_simba_0001 -> on va utiliser l'id complet
    file_name = f"{entry['id']}.wav"
    local_path = os.path.join(AUDIO_DIR, file_name)
    
    try:
        urllib.request.urlretrieve(audio_url, local_path)
        # Update entry
        entry["audio_path"] = f"audio/{file_name}"
        success_count += 1
        print(f"Downloaded: {file_name}")
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")
        fail_count += 1

# Save updated JSON
with open(LEXIQUE_FILE, "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"\nDownload complete. Success: {success_count}, Failed: {fail_count}")

# Check total size of AUDIO_DIR
total_size = sum(os.path.getsize(os.path.join(AUDIO_DIR, f)) for f in os.listdir(AUDIO_DIR) if os.path.isfile(os.path.join(AUDIO_DIR, f)))
print(f"Total audio directory size: {total_size / (1024*1024):.2f} MB")
