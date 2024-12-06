import os
import requests
import logging
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElevenLabsAPI:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice ID for "Rachel"
        self.model_id = "eleven_monolingual_v1"

    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> requests.Response:
        """Make HTTP request to ElevenLabs API"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise

    def create_voice_response(self, text: str) -> Optional[bytes]:
        """Generate voice response using ElevenLabs API"""
        try:
            endpoint = f"text-to-speech/{self.voice_id}"
            data = {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = self._make_request("POST", endpoint, data)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating voice response: {str(e)}")
            return None

    def verify_api_key(self) -> bool:
        """Verify API key and connection"""
        try:
            self._make_request("GET", "voices")
            return True
        except Exception as e:
            logger.error(f"API key verification failed: {str(e)}")
            return False

# Create a global instance
elevenlabs_api = ElevenLabsAPI()

def create_voice_response(text: str) -> Optional[bytes]:
    """Wrapper function for backward compatibility"""
    return elevenlabs_api.create_voice_response(text)

def start_voice_session() -> bool:
    """Initialize voice session"""
    try:
        return elevenlabs_api.verify_api_key()
    except Exception as e:
        logger.error(f"Error starting voice session: {str(e)}")
        return False

def end_voice_session(conversation_data=None) -> bool:
    """End voice session - No cleanup needed for REST API"""
    return True
