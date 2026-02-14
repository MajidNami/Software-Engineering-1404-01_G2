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
    """
    HTTP implementation of the WikiServicePort.
    Connects to the external Wiki microservice to retrieve destination details.
    """
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get_destination_basic_info(self, destination_name: str) -> str:
        """
        Retrieves a summary or description for a specific destination.
        
        Sends a GET request to /api/wiki/content?place={destination_name}.
        Prioritizes the 'summary' field; falls back to 'description'.
        
        :param destination_name: Name of the city or place (e.g., "Tehran").
        :return: A string containing the summary/description, or a fallback message if not found.
        """

        endpoint = f"{self.base_url}/api/wiki/content"
        params = {"place": destination_name}

        try:
            response = requests.get(endpoint, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                content = data.get("summary")
                if not content:
                    content = data.get("description")
                
                return content if content else ""
            
            elif response.status_code == 404:
                logger.warning(f"Wiki content not found for place: {destination_name}")
                return ""
            
            else:
                logger.error(f"Wiki Service Error: Status {response.status_code} for {destination_name}")
                return ""

        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error to Wiki Service: {e}")
            return "Unable to connect to Wiki service."
