import os
import requests

TOKEN = os.environ.get("Infoblox_Token")
INPUT_FILE = "provider_ids.txt"

if not TOKEN:
    raise EnvironmentError("❌ 'Infoblox_Token' environment variable is not set.")
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"❌ Input file '{INPUT_FILE}' not found.")

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

with open(INPUT_FILE, "r") as f:
    provider_ids = [line.strip() for line in f if line.strip()]

print(f"🧹 Deleting {len(provider_ids)} provider(s)...")

for provider_id in provider_ids:
    url = f"https://csp.infoblox.com/api/cloud_discovery/v2/providers/{provider_id}"
    print(f"❌ Deleting provider: {provider_id}")
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print("✅ Deleted successfully.")
    elif response.status_code == 404:
        print("⚠️ Not found.")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
