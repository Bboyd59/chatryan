import os
import requests
import logging
from typing import Optional, Dict, Any, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElevenLabsAPI:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.agent_id = os.getenv("AGENT_ID")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
        if not self.agent_id:
            raise ValueError("AGENT_ID not found in environment variables")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.current_conversation_id = None

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

    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents"""
        try:
            response = self._make_request("GET", "convai/agents")
            data = response.json()
            return data.get("agents", [])
        except Exception as e:
            logger.error(f"Error fetching agents: {str(e)}")
            return []

    def start_conversation(self) -> Optional[str]:
        """Start a new conversation with the AI agent"""
        try:
            # First verify the agent exists
            agents = self.get_available_agents()
            agent_exists = any(agent["agent_id"] == self.agent_id for agent in agents)
            
            if not agent_exists:
                logger.error(f"Agent ID {self.agent_id} not found in available agents")
                return None
                
            endpoint = f"convai/agents/{self.agent_id}/conversations"
            response = self._make_request("POST", endpoint)
            data = response.json()
            self.current_conversation_id = data.get("conversation_id")
            return self.current_conversation_id
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            return None

    def get_conversation_status(self) -> Dict[str, Any]:
        """Get the current status of the conversation"""
        if not self.current_conversation_id:
            return {}
        
        try:
            endpoint = f"convai/conversations/{self.current_conversation_id}"
            response = self._make_request("GET", endpoint)
            return response.json()
        except Exception as e:
            logger.error(f"Error getting conversation status: {str(e)}")
            return {}

    def send_user_input(self, text: str) -> Tuple[str, Optional[bytes]]:
        """Send user input and get AI response with audio"""
        try:
            if not self.current_conversation_id:
                if not self.start_conversation():
                    raise Exception("Failed to start conversation")

            # Send user message
            endpoint = f"convai/conversations/{self.current_conversation_id}/input"
            data = {
                "text": text,
                "source": "speech",
                "position": 0  # Starting position in audio
            }
            response = self._make_request("POST", endpoint, data)
            
            # Wait for and get AI response
            status = self.get_conversation_status()
            while status.get("status") == "processing":
                status = self.get_conversation_status()
            
            # Get the latest AI response from transcript
            transcript = status.get("transcript", [])
            ai_response = ""
            for message in reversed(transcript):
                if message.get("role") == "assistant":
                    ai_response = message.get("message", "")
                    break
            
            # Get audio response
            audio = None
            if ai_response:
                audio_endpoint = f"convai/conversations/{self.current_conversation_id}/audio"
                audio_response = self._make_request("GET", audio_endpoint)
                audio = audio_response.content
            
            return ai_response, audio
            
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")
            return "I'm sorry, I encountered an error processing your request.", None

    def end_conversation(self) -> bool:
        """End the current conversation"""
        if not self.current_conversation_id:
            return True
            
        try:
            endpoint = f"convai/conversations/{self.current_conversation_id}/end"
            self._make_request("POST", endpoint)
            self.current_conversation_id = None
            return True
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}")
            return False

# Create a global instance
elevenlabs_api = ElevenLabsAPI()

def create_voice_response(text: str) -> Tuple[str, Optional[bytes]]:
    """Process user input and get AI response with audio"""
    return elevenlabs_api.send_user_input(text)

def start_voice_session() -> bool:
    """Initialize voice session"""
    try:
        return bool(elevenlabs_api.start_conversation())
    except Exception as e:
        logger.error(f"Error starting voice session: {str(e)}")
        return False

def end_voice_session(conversation_data=None) -> bool:
    """End voice session"""
    return elevenlabs_api.end_conversation()
