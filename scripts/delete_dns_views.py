import os
import requests

# === Config ===
TOKEN = os.environ.get("Infoblox_Token")
INPUT_FILE = "dns_view_ids.txt"

# === Validation ===
if not TOKEN:
    raise EnvironmentError("❌ 'Infoblox_Token' is not set.")
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"❌ View ID file '{INPUT_FILE}' not found. Run extract script first.")

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# === Read view IDs from file
with open(INPUT_FILE, "r") as f:
    view_ids = [line.strip() for line in f if line.strip()]

print(f"🧹 Deleting {len(view_ids)} DNS view(s)...")

for view_id in view_ids:
    view_uuid = view_id.split("/")[-1]  # Extract only the UUID
    url = f"https://csp.infoblox.com/api/ddi/v1/dns/view/{view_uuid}"
    print(f"❌ Deleting DNS view: {view_id}")

    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print("✅ Deleted successfully.")
    elif response.status_code == 404:
        print("⚠️ Not found or already deleted.")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
