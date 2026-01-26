import os
import json
import requests

# === Config ===
TOKEN = os.environ.get("Infoblox_Token")
PARTICIPANT_ID = os.environ.get("INSTRUQT_PARTICIPANT_ID")
OUTPUT_FILE = "dns_view_ids.txt"

API_URL = "https://csp.infoblox.com/api/ddi/v1/dns/zone_child"
PARAMS = {
    "_filter": 'flat=="false"',
    "_order_by": "name asc",
    "_is_total_size_needed": "true",
    "_limit": "101",
    "_offset": "0"
}

# === Validation ===
if not TOKEN:
    raise EnvironmentError("❌ 'Infoblox_Token' is not set.")
if not PARTICIPANT_ID:
    raise EnvironmentError("❌ 'INSTRUQT_PARTICIPANT_ID' is not set.")

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

print(f"📡 Querying DNS views for participant ID: {PARTICIPANT_ID}...")

response = requests.get(API_URL, headers=headers, params=PARAMS)
try:
    data = response.json()
except Exception:
    data = {"raw": response.text}

zones = data.get("results", [])
print(f"🔍 Found {len(zones)} total DNS views.")

# === Filter and write matching views
matching = [
    (z["name"], z["id"]) for z in zones
    if PARTICIPANT_ID in z.get("name", "") and z.get("type") == "view"
]

with open(OUTPUT_FILE, "w") as f:
    for name, view_id in matching:
        f.write(view_id + "\n")

print(f"✅ Found {len(matching)} DNS views matching '{PARTICIPANT_ID}'")
for name, view_id in matching:
    print(f" - {name}: {view_id}")
print(f"📝 View IDs saved to {OUTPUT_FILE}")
