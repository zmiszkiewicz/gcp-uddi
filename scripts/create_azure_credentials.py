import os
import json
import requests

# === Config ===
API_URL = "https://csp.infoblox.com/api/iam/v2/keys"
TOKEN = os.environ.get("Infoblox_Token")
OUTPUT_FILE = "azure_credential_id"

TENANT_ID = os.environ.get("INSTRUQT_AZURE_SUBSCRIPTION_INFOBLOX_TENANT_TENANT_ID")
CLIENT_ID = os.environ.get("INSTRUQT_AZURE_SUBSCRIPTION_INFOBLOX_TENANT_SPN_ID")
CLIENT_SECRET = os.environ.get("INSTRUQT_AZURE_SUBSCRIPTION_INFOBLOX_TENANT_SPN_PASSWORD")
PARTICIPANT_ID = os.environ.get("INSTRUQT_PARTICIPANT_ID")

# === Validation ===
if not TOKEN:
    raise EnvironmentError("❌ 'Infoblox_Token' environment variable is not set.")
if not TENANT_ID or not CLIENT_ID or not CLIENT_SECRET:
    raise EnvironmentError("❌ Azure environment variables are not fully set.")
if not PARTICIPANT_ID:
    raise EnvironmentError("❌ 'INSTRUQT_PARTICIPANT_ID' environment variable is not set.")

# === Construct dynamic credential name ===
credential_name = f"Azure-Demo-Lab-{PARTICIPANT_ID}"
print(f"🔧 Creating credential with name: {credential_name}")

# === Construct Payload ===
payload = {
    "name": credential_name,
    "source_id": "azure",
    "active": True,
    "key_data": {
        "tenant_id": TENANT_ID,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    },
    "key_type": "id_and_secret"
}

# === Headers ===
headers = {
    "Authorization": f"Token {TOKEN}",  # Fixed prefix to 'Bearer'
    "Content-Type": "application/json"
}

# === API Call ===
print("🚀 Creating Azure credentials in Infoblox CSP...")

response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

try:
    response_data = response.json()
except Exception:
    response_data = {"raw": response.text}

print(f"📦 Status Code: {response.status_code}")
print("📥 Full API Response:")
print(json.dumps(response_data, indent=2))

# === Optional Handling and ID extraction ===
if response.status_code in [200, 201]:
    result = response_data.get("results", {})
    credential_id = result.get("id")
    if credential_id:
        with open(OUTPUT_FILE, "w") as f:
            f.write(credential_id)
        print(f"✅ Credential ID saved to {OUTPUT_FILE}: {credential_id}")
    else:
        print("⚠️ Credential ID not found in response.")
elif response.status_code == 409:
    print("⚠️ Credential already exists (409 Conflict).")
else:
    print("❌ Error occurred during credential creation.")
