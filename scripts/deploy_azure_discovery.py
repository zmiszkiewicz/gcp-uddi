import os
import json
import requests
import time

class AzureInfobloxSession:
    def __init__(self):
        self.base_url = "https://csp.infoblox.com"
        self.email = os.getenv("INFOBLOX_EMAIL")
        self.password = os.getenv("INFOBLOX_PASSWORD")
        self.jwt = None
        self.session = requests.Session()
        self.headers = {"Content-Type": "application/json"}

    def login(self):
        payload = {"email": self.email, "password": self.password}
        response = self.session.post(f"{self.base_url}/v2/session/users/sign_in", headers=self.headers, json=payload)
        response.raise_for_status()
        self.jwt = response.json().get("jwt")
        self._save_to_file("azure_jwt.txt", self.jwt)
        print("✅ Logged in and saved JWT to azure_jwt.txt")

    def switch_account(self):
        sandbox_id = self._read_file("sandbox_id.txt")
        payload = {"id": f"identity/accounts/{sandbox_id}"}
        headers = self._auth_headers()
        response = self.session.post(f"{self.base_url}/v2/session/account_switch", headers=headers, json=payload)
        response.raise_for_status()
        self.jwt = response.json().get("jwt")
        self._save_to_file("azure_jwt.txt", self.jwt)
        print(f"✅ Switched to sandbox {sandbox_id} and updated JWT")

    def create_azure_key(self):
        tenant_id = os.getenv("INSTRUQT_AZURE_SUBSCRIPTION_INFOBLOX_TENANT_TENANT_ID")
        client_id = os.getenv("INSTRUQT_AZURE_SUBSCRIPTION_INFOBLOX_TENANT_SPN_ID")
        client_secret = os.getenv("INSTRUQT_AZURE_SUBSCRIPTION_INFOBLOX_TENANT_SPN_PASSWORD")

        if not tenant_id or not client_id or not client_secret:
            raise RuntimeError("❌ Azure credentials not found in environment variables.")

        payload = {
            "name": "azure-creds-instruqt",
            "source_id": "azure",
            "active": True,
            "key_data": {
                "tenant_id": tenant_id,
                "client_id": client_id,
                "client_secret": client_secret
            },
            "key_type": "id_and_secret"
        }

        response = self.session.post(
            f"{self.base_url}/api/iam/v2/keys",
            headers=self._auth_headers(),
            json=payload
        )

        if response.status_code == 409:
            print("⚠️ Azure key already exists, skipping creation.")
        else:
            response.raise_for_status()
            print("🔐 Azure key created successfully.")

    def fetch_cloud_credential_id(self):
        url = f"{self.base_url}/api/iam/v1/cloud_credential"
        print("⏳ Waiting up to 2 minutes for Azure Cloud Credential to appear...")

        timeout = 120  # total wait time in seconds
        interval = 10  # check every 10 seconds
        waited = 0

        while waited < timeout:
            try:
                response = self.session.get(url, headers=self._auth_headers())
                if response.status_code == 403:
                    print("🚫 403 Forbidden – likely no access yet or propagation delay")
                response.raise_for_status()
                creds = response.json().get("results", [])

                for cred in creds:
                    if cred.get("credential_type") == "Microsoft Azure":
                        credential_id = cred.get("id")
                        self._save_to_file("azure_cloud_credential_id.txt", credential_id)
                        print(f"✅ Azure Cloud Credential ID found and saved: {credential_id}")
                        return credential_id

            except requests.HTTPError as e:
                print(f"❌ Error fetching credentials: {e}")

            print(f"🕐 Still waiting... Checked at {waited}s")
            time.sleep(interval)
            waited += interval

        raise RuntimeError("❌ Timed out after 2 minutes waiting for Azure Cloud Credential to appear.")

    def fetch_dns_view_id(self):
        url = f"{self.base_url}/api/ddi/v1/dns/view"
        response = self.session.get(url, headers=self._auth_headers())
        response.raise_for_status()
        dns_view_id = response.json().get("results", [{}])[0].get("id")
        self._save_to_file("azure_dns_view_id.txt", dns_view_id)
        print(f"✅ DNS View ID saved: {dns_view_id}")
        return dns_view_id

    def inject_variables_into_payload(self, template_file, output_file, dns_view_id, cloud_credential_id, subscription_id):
        with open(template_file, "r") as f:
            payload = json.load(f)

        payload["destinations"][0]["config"]["dns"]["view_id"] = dns_view_id
        payload["source_configs"][0]["cloud_credential_id"] = cloud_credential_id
        payload["source_configs"][0]["restricted_to_accounts"] = [subscription_id]
        #payload["source_configs"][0]["credential_config"]["access_identifier"] = subscription_id

        with open(output_file, "w") as f:
            json.dump(payload, f, indent=2)

        print(f"📦 Azure payload created in {output_file} with injected variables")

    def submit_discovery_job(self, payload_file):
        with open(payload_file, "r") as f:
            payload = json.load(f)

        url = f"{self.base_url}/api/cloud_discovery/v2/providers"
        response = self.session.post(url, headers=self._auth_headers(), json=payload)
        response.raise_for_status()
        print("🚀 Azure Cloud Discovery Job submitted:")
        print(json.dumps(response.json(), indent=2))

    def _auth_headers(self):
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.jwt}"}

    def _save_to_file(self, filename, content):
        with open(filename, "w") as f:
            f.write(content.strip())

    def _read_file(self, filename):
        with open(filename, "r") as f:
            return f.read().strip()


if __name__ == "__main__":
    subscription_id = os.getenv("INSTRUQT_AZURE_SUBSCRIPTION_INFOBLOX_TENANT_SUBSCRIPTION_ID")
    session = AzureInfobloxSession()
    session.login()
    session.switch_account()
    session.create_azure_key()
    cred_id = session.fetch_cloud_credential_id()
    dns_id = session.fetch_dns_view_id()
    session.inject_variables_into_payload("azure_payload_template.json", "azure_payload.json", dns_id, cred_id, subscription_id)
    session.submit_discovery_job("azure_payload.json")
