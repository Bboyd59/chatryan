import os
import io
import requests
import logging
from typing import Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElevenLabsAPI:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
            
        self.base_url = "https://api.elevenlabs.io/v1"
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice ID
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def text_to_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech using ElevenLabs API"""
        try:
            endpoint = f"{self.base_url}/text-to-speech/{self.voice_id}/stream"
            
            response = requests.post(
                endpoint,
                headers=self.headers,
                json={
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                },
                stream=True
            )
            
            if response.status_code == 200:
                audio_data = io.BytesIO()
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        audio_data.write(chunk)
                logger.info("Successfully generated speech")
                return audio_data.getvalue()
            else:
                logger.error(f"Text-to-speech API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return None

# Create a global instance
elevenlabs_api = ElevenLabsAPI()

def create_voice_response(text: str) -> Tuple[str, Optional[bytes]]:
    """Generate AI response and convert it to speech"""
    try:
        # For now, we'll use a simple response format
        ai_response = f"I understand you said: {text}"
        
        # Generate speech from the response
        audio = elevenlabs_api.text_to_speech(ai_response)
        
        return ai_response, audio
        
    except Exception as e:
        logger.error(f"Error creating voice response: {str(e)}")
        return "Sorry, there was an error processing your request.", None

def start_voice_session() -> bool:
    """Initialize voice session"""
    try:
        # Test the API connection with a simple message
        test_audio = elevenlabs_api.text_to_speech("Voice session initialized.")
        if test_audio:
            logger.info("Voice session started successfully")
            return True
        logger.error("Failed to generate test audio")
        return False
    except Exception as e:
        logger.error(f"Error starting voice session: {str(e)}")
        return False

def end_voice_session(conversation_data=None) -> bool:
    """End voice session"""
    try:
        logger.info("Voice session ended")
        return True
    except Exception as e:
        logger.error(f"Error ending voice session: {str(e)}")
        return False
