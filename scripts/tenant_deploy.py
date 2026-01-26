import json
import requests
import os
import yaml
import logging
from logging.handlers import RotatingFileHandler

# Setup logging
logger = logging.getLogger('ResourceCreatorLogger')
logger.setLevel(logging.DEBUG)  # You can set this to logging.INFO to reduce the verbosity if you wish
handler = RotatingFileHandler('ResourceCreator.log', maxBytes=5000000, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class ResourceCreator:
    def __init__(self, api_config):
        """
        Initialize the ResourceCreator class with proper error handling.
        """
        api_token = os.getenv('TF_VAR_prosimo_token')
        if not api_token:
            raise ValueError("API token must be provided.")

        self.base_url = api_config['base_url']
        self.resource_type = api_config['resource_type']
        self.session = requests.Session()
        self.session.headers.update({
            "Prosimo-ApiToken": api_token,
            "Content-Type": "application/json"
        })

    def create_resource(self, payload):
        """
        Create a new resource via HTTP POST request, with error handling.
        """
        api_endpoint = f"{self.base_url}/{self.resource_type}"
        try:
            response = self.session.post(api_endpoint, data=json.dumps(payload))
            response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
            logger.info(f"Resource created successfully at {api_endpoint}")
            return {'status': 'success', 'data': response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create resource at {api_endpoint}: {e}")
            return {'status': 'failure', 'error': str(e)}

def load_configuration(file_path='/root/prosimo-lab/assets/scripts/config.yaml'):
    """
    Load the API configuration from a YAML file.
    """
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        raise yaml.YAMLError(f"Error parsing YAML configuration: {e}")
    except FileNotFoundError:
        logger.error("Configuration file not found.")
        raise FileNotFoundError("Configuration file not found.")

if __name__ == "__main__":
    # Load API configuration
    try:
        config = load_configuration()
    except Exception as e:
        logger.exception("An error occurred while loading configuration.")
        raise e

    # Initialize the ResourceCreator with the API configuration
    resource_creator = ResourceCreator(config['api_config'])

    # Retrieve participant ID from environment variable
    team_name = os.environ.get('INSTRUQT_PARTICIPANT_ID')
    username = f"igor+{team_name}@prosimo.io"

    # Define the resource type and payload
    payload = {
        "comment": "Sample Comment",
        "company": "prosimo",
        "firstName": "John",
        "lastName": "Doe",
        "teamName": team_name,
        "username": username
    }

    # Create the resource
    response = resource_creator.create_resource(payload)

    # Output the response
    if response['status'] == 'success':
        print("Resource created successfully.")
    else:
        logger.error(f"Resource creation failed with error: {response['error']}")
    print(json.dumps(response, indent=4))
