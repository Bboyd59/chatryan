import os
import signal
import logging
import sounddevice as sd
from typing import Optional
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure sounddevice settings
sd.default.samplerate = 44100
sd.default.channels = 1

class VoiceConversationManager:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.agent_id = os.getenv("AGENT_ID")
        
        if not self.api_key or not self.agent_id:
            raise ValueError("Missing required environment variables: ELEVENLABS_API_KEY or AGENT_ID")
            
        self.client = ElevenLabs(api_key=self.api_key)
        self.conversation = None

    def create_conversation(self, on_response=None, on_transcript=None) -> Optional[str]:
        """Create and start a new conversation"""
        try:
            try:
                # Test audio device availability
                devices = sd.query_devices()
                logger.info(f"Available audio devices: {devices}")
                
                # Get default devices
                default_input = sd.query_devices(kind='input')
                default_output = sd.query_devices(kind='output')
                logger.info(f"Default input device: {default_input}")
                logger.info(f"Default output device: {default_output}")
                
                # Test audio stream
                duration = 0.1  # seconds
                with sd.Stream(samplerate=44100, channels=1):
                    logger.info("Audio stream test successful")
            except Exception as audio_error:
                logger.error(f"Audio device error: {str(audio_error)}")
                raise RuntimeError(f"Audio device initialization failed: {str(audio_error)}")
            
            # Create the conversation with audio interface
            self.conversation = Conversation(
                self.client,
                self.agent_id,
                requires_auth=True,
                audio_interface=DefaultAudioInterface(),
                callback_agent_response=on_response or (lambda response: logger.info(f"Agent: {response}")),
                callback_user_transcript=on_transcript or (lambda transcript: logger.info(f"User: {transcript}")),
                callback_agent_response_correction=lambda original, corrected: logger.info(f"Agent correction: {original} -> {corrected}"),
                callback_error=lambda error: logger.error(f"Conversation error: {error}"),
            )
            
            # Set up signal handler for graceful shutdown
            signal.signal(signal.SIGINT, lambda sig, frame: self.end_conversation())
            
            # Start the conversation
            logger.info("Starting conversation session...")
            self.conversation.start_session()
            
            # Wait for session to end and return conversation ID
            conversation_id = self.conversation.wait_for_session_end()
            logger.info(f"Conversation ended with ID: {conversation_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error in conversation: {str(e)}")
            return None

    def end_conversation(self) -> bool:
        """End the current conversation"""
        try:
            if self.conversation:
                self.conversation.end_session()
                self.conversation = None
            return True
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}")
            return False

# Create a global instance
voice_manager = VoiceConversationManager()
