import json
import urllib.request
import os

out_dir = r"C:\Users\FLEX ZONE\Models_Langues\shared\data\bassa\samples"
os.makedirs(out_dir, exist_ok=True)

# 1. Download SimbaBench (100 rows)
url_simba = "https://datasets-server.huggingface.co/rows?dataset=UBC-NLP%2FSimbaBench_dataset&config=asr_test_bas&split=test&offset=0&length=100"
out_file = os.path.join(out_dir, "simbabench_100.json")

try:
    with urllib.request.urlopen(url_simba) as response:
        data = json.loads(response.read().decode())
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"SimbaBench (100 rows) downloaded successfully. Total rows reported: {data.get('num_rows_total')}")
except Exception as e:
    print(f"SimbaBench download failed: {e}")

# 2. Check AfroLingu-MT access
url_afro = "https://datasets-server.huggingface.co/rows?dataset=UBC-NLP%2FAfroLingu-MT&config=bas&split=train&offset=0&length=1"
try:
    with urllib.request.urlopen(url_afro) as response:
        print("AfroLingu-MT is accessible!")
except Exception as e:
    print(f"AfroLingu-MT access check: {e}")

# Try to get dataset info for AfroLingu-MT to estimate size
url_afro_info = "https://datasets-server.huggingface.co/info?dataset=UBC-NLP%2FAfroLingu-MT"
try:
    with urllib.request.urlopen(url_afro_info) as response:
        info_data = json.loads(response.read().decode())
        print("AfroLingu-MT info accessible.")
except Exception as e:
    print(f"AfroLingu-MT info check: {e}")
