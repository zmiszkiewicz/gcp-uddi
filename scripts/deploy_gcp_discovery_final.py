import os
import json
import requests
import time
import random

class GCPInfobloxSession:
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
        self._save_to_file("gcp_jwt.txt", self.jwt)
        print("✅ Logged in and saved JWT to gcp_jwt.txt")

    def switch_account(self):
        sandbox_id = self._read_file("sandbox_id.txt")
        payload = {"id": f"identity/accounts/{sandbox_id}"}
        headers = self._auth_headers()
        response = self.session.post(f"{self.base_url}/v2/session/account_switch", headers=headers, json=payload)
        response.raise_for_status()
        self.jwt = response.json().get("jwt")
        self._save_to_file("gcp_jwt.txt", self.jwt)
        print(f"✅ Switched to sandbox {sandbox_id} and updated JWT")

    def create_gcp_key(self):
        sa_key_file = "/root/infoblox-lab/sa-key.json"
        if not os.path.exists(sa_key_file):
            raise FileNotFoundError("❌ GCP service account key (sa-key.json) not found.")

        with open(sa_key_file, "r") as f:
            sa_data = json.load(f)

        payload = {
            "name": "gcp-key-instruqt",
            "source_id": "gcp",
            "active": True,
            "key_type": "service_account_key",
            "key_data": sa_data
        }

        response = self.session.post(f"{self.base_url}/api/iam/v2/keys", headers=self._auth_headers(), json=payload)

        if response.status_code == 409:
            print("⚠️ GCP key already exists, skipping creation.")
        elif response.status_code != 200:
            print("❌ Failed to create GCP key:")
            print(response.status_code)
            print(response.text)
            response.raise_for_status()
        else:
            print("🔐 GCP key created successfully.")

    def fetch_cloud_credential_id(self, timeout=240):
        url = f"{self.base_url}/api/iam/v1/cloud_credential"
        print("⏳ Waiting for GCP Cloud Credential to appear...")
        start = time.monotonic()
        interval = 3

        while time.monotonic() - start < timeout:
            try:
                response = self.session.get(url, headers=self._auth_headers())
                if response.status_code == 429:
                    time.sleep(5)
                    continue
                response.raise_for_status()
                creds = response.json().get("results", [])
                for cred in creds:
                    if cred.get("credential_type") == "Google Cloud Platform":
                        cred_id = cred.get("id")
                        self._save_to_file("gcp_cloud_credential_id.txt", cred_id)
                        print(f"✅ GCP Cloud Credential ID saved: {cred_id}")
                        return cred_id
            except Exception as e:
                print(f"⚠️ Retry due to: {e}")
            time.sleep(interval)
            interval = min(interval * 1.7, 20)
        raise RuntimeError("❌ GCP Cloud Credential did not appear in time.")

    def fetch_dns_view_id(self, timeout=240):
        url = f"{self.base_url}/api/ddi/v1/dns/view"
        print("⏳ Waiting for DNS View...")
        start = time.monotonic()
        interval = 3

        while time.monotonic() - start < timeout:
            try:
                response = self.session.get(url, headers=self._auth_headers())
                response.raise_for_status()
                view_id = response.json().get("results", [{}])[0].get("id")
                if view_id:
                    self._save_to_file("gcp_dns_view_id.txt", view_id)
                    print(f"✅ DNS View ID saved: {view_id}")
                    return view_id
            except Exception as e:
                print(f"⚠️ Retry due to: {e}")
            time.sleep(interval)
            interval = min(interval * 1.7, 20)
        raise RuntimeError("❌ DNS View ID not available in time.")

    def inject_variables_into_payload(self, template_file, output_file, dns_view_id, cloud_credential_id, project_id):
        with open(template_file, "r") as f:
            payload = json.load(f)

        payload["destinations"][0]["config"]["dns"]["view_id"] = dns_view_id
        payload["source_configs"][0]["cloud_credential_id"] = cloud_credential_id
        payload["source_configs"][0]["restricted_to_accounts"] = [project_id]
        payload["source_configs"][0]["credential_config"]["access_identifier"] = project_id

        with open(output_file, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"📦 GCP payload created in {output_file} with injected variables")

    def wait_discovery_api_ready(self, timeout=300):
        url = f"{self.base_url}/api/cloud_discovery/v2/providers"
        print("🔎 Waiting for Discovery API to be ready...")
        start = time.monotonic()
        interval = 3
        while time.monotonic() - start < timeout:
            r = self.session.get(url, headers=self._auth_headers())
            if r.status_code < 400:
                print("✅ Discovery API ready")
                return
            time.sleep(interval)
            interval = min(interval * 1.5, 30)
        raise RuntimeError("❌ Discovery API not ready in time.")

    def submit_discovery_job(self, payload_file, timeout=300):
        with open(payload_file, "r") as f:
            payload = json.load(f)

        self.wait_discovery_api_ready()
        url = f"{self.base_url}/api/cloud_discovery/v2/providers"
        start = time.monotonic()
        interval = 3
        while time.monotonic() - start < timeout:
            r = self.session.post(url, headers=self._auth_headers(), json=payload)
            if r.status_code < 400:
                print("🚀 GCP Cloud Discovery Job submitted:")
                print(json.dumps(r.json(), indent=2))
                return
            print(f"⚠️ Discovery POST failed: {r.status_code} {r.text[:200]}")
            time.sleep(interval)
            interval = min(interval * 1.7, 30)
        raise RuntimeError("❌ Timed out submitting GCP discovery job")

    def _auth_headers(self):
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.jwt}"}

    def _save_to_file(self, filename, content):
        with open(filename, "w") as f:
            f.write(content.strip())

    def _read_file(self, filename):
        with open(filename, "r") as f:
            return f.read().strip()

if __name__ == "__main__":
    project_id = os.getenv("INSTRUQT_GCP_PROJECT_INFOBLOX_DEMO_PROJECT_ID")
    session = GCPInfobloxSession()
    session.login()
    session.switch_account()
    session.create_gcp_key()
    cred_id = session.fetch_cloud_credential_id()
    dns_id = session.fetch_dns_view_id()
    session.inject_variables_into_payload("gcp_payload_template.json", "gcp_payload.json", dns_id, cred_id, project_id)
    session.submit_discovery_job("gcp_payload.json")
