import os
import json
import requests

TOKEN = os.environ.get("Infoblox_Token")
PARTICIPANT_ID = os.environ.get("INSTRUQT_PARTICIPANT_ID")
OUTPUT_FILE = "provider_ids.txt"

if not TOKEN:
    raise EnvironmentError("❌ 'Infoblox_Token' environment variable is not set.")
if not PARTICIPANT_ID:
    raise EnvironmentError("❌ 'INSTRUQT_PARTICIPANT_ID' environment variable is not set.")

url = "https://csp.infoblox.com/api/cloud_discovery/v2/providers"
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

print(f"📡 Fetching cloud providers created for participant: {PARTICIPANT_ID}...")

response = requests.get(url, headers=headers)
try:
    data = response.json()
except Exception:
    data = {"raw": response.text}

print(f"📦 Status Code: {response.status_code}")
providers = data.get("results", [])

# Filter providers by name suffix (e.g., AWS_Demo_XYZ, Azure_Demo_Lab_XYZ)
matching_providers = [
    p for p in providers
    if p.get("name", "").endswith(PARTICIPANT_ID)
    and (p.get("name", "").startswith("AWS_Demo") or p.get("name", "").startswith("Azure_Demo_Lab"))
]

with open(OUTPUT_FILE, "w") as f:
    for p in matching_providers:
        f.write(p["id"] + "\n")

print(f"✅ {len(matching_providers)} provider ID(s) for participant '{PARTICIPANT_ID}' written to {OUTPUT_FILE}")
