import sys
import os
import requests
import logging

current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))))

if project_root not in sys.path:
    sys.path.insert(0, project_root)
from team10.infrastructure.ports.wiki_service_port import WikiServicePort

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HttpWikiClient(WikiServicePort):
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get_destination_basic_info(self, destination_name: str) -> str:

        endpoint = f"{self.base_url}/api/wiki/content"
        params = {"place": destination_name}

        try:
            response = requests.get(endpoint, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                content = data.get("summary")
                if not content:
                    content = data.get("description")
                
                return content if content else "No description available for this place."
            
            elif response.status_code == 404:
                logger.warning(f"Wiki content not found for place: {destination_name}")
                return "Description not found."
            
            else:
                logger.error(f"Wiki Service Error: Status {response.status_code} for {destination_name}")
                return "Wiki service error."

        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error to Wiki Service: {e}")
            return "Unable to connect to Wiki service."
