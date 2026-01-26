import os
import requests

TOKEN = os.environ.get("Infoblox_Token")
INPUT_FILE = "azure_credential_id"

if not TOKEN:
    raise EnvironmentError("❌ 'Infoblox_Token' is not set.")
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"❌ File '{INPUT_FILE}' not found. Did you run the credential lookup script?")

with open(INPUT_FILE, "r") as f:
    cred_id = f.read().strip()

if not cred_id:
    raise ValueError("❌ Credential ID is empty in the file.")

url = f"https://csp.infoblox.com/api/iam/v2/keys/{cred_id}"
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

print(f"❌ Deleting credential ID: {cred_id}")
response = requests.delete(url, headers=headers)

if response.status_code == 200:
    print("✅ Credential deleted successfully.")
elif response.status_code == 404:
    print("⚠️ Credential not found or already deleted.")
else:
    print(f"❌ Failed to delete: {response.status_code}")
    print(response.text)
