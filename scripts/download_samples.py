import json
import urllib.request

# 3. JW300 (bas-en translation)
url3 = "https://datasets-server.huggingface.co/rows?dataset=jw300&config=bas-en&split=train&offset=0&length=1"
try:
    with urllib.request.urlopen(url3) as response:
        data = json.loads(response.read().decode())
        with open(r"C:\Users\FLEX ZONE\Models_Langues\shared\data\bassa\samples\jw300_sample.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("JW300 sample downloaded successfully.")
except Exception as e:
    print(f"JW300 download failed: {e}")
