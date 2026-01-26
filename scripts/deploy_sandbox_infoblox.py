import json
import os
import requests
import logging
from logging.handlers import RotatingFileHandler

from idna.idnadata import scripts

# Setup logging
logger = logging.getLogger('SandboxAccountLogger')
logger.setLevel(logging.DEBUG)  # Set to INFO in prod if needed
handler = RotatingFileHandler('SandboxAccount.log', maxBytes=5_000_000, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)can I have it in a seperate scripts

class SandboxAccountAPI:
    """
    Interacts with the /sandbox/accounts endpoint to create sandbox accounts.
    """

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def create_sandbox_account(self, sandbox_account_request: dict) -> dict:
        endpoint = f"{self.base_url}/sandbox/accounts"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if self.token:
            headers["Authorization"] = f"token {self.token}"

        try:
            logger.debug(f"Sending request to {endpoint} with payload: {json.dumps(sandbox_account_request)}")
            response = requests.post(url=endpoint, headers=headers, data=json.dumps(sandbox_account_request))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"status": "failure", "error": str(e)}

        try:
            result = response.json()
            logger.info(f"Sandbox account created successfully: {json.dumps(result, indent=2)}")
            return {"status": "success", "data": result}
        except json.JSONDecodeError:
            logger.warning("Received non-JSON response")
            return {"status": "success", "data": response.text}


if __name__ == "__main__":
    BASE_URL = "https://csp.infoblox.com/v2"
    TOKEN = os.environ.get('Infoblox_Token')

    if not TOKEN:
        logger.error("Missing Infoblox_Token in environment.")
        exit(1)

    team_id = os.environ.get('INSTRUQT_PARTICIPANT_ID', 'default-team')
    sandbox_request_body = {
        "name": team_id,
        "description": "Created via Python script Instruqt Demo",
        "state": "active",
        "tags": {
            "instruqt": "igor"
        },
        "admin_user": {
            "email": "iracic@infoblox.xom",
            "name": "Igor Racic"
        }
    }

    api = SandboxAccountAPI(base_url=BASE_URL, token=TOKEN)
    response = api.create_sandbox_account(sandbox_request_body)

    if response['status'] == 'success':
        print("Sandbox account created successfully.")
    else:
        logger.error(f"Sandbox account creation failed: {response['error']}")
        print("Failed to create sandbox account. See log for details.")

    print(json.dumps(response, indent=2))
