import os
import signal
import logging
from typing import Optional, Callable
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceConversationManager:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.agent_id = os.getenv("AGENT_ID")
        self.active_conversations = {}
        
        if not self.api_key or not self.agent_id:
            raise ValueError("Missing required environment variables: ELEVENLABS_API_KEY or AGENT_ID")
            
        # Initialize ElevenLabs client
        self.client = ElevenLabs(api_key=self.api_key)

        if not self.api_key or not self.agent_id:
            raise ValueError("Missing required environment variables: ELEVENLABS_API_KEY or AGENT_ID")

        self.client = ElevenLabs(api_key=self.api_key)

    def create_conversation(self, session_id: str, 
                          on_agent_response: Optional[Callable] = None,
                          on_user_transcript: Optional[Callable] = None) -> Conversation:
        """Create a new conversation instance"""
        conversation = Conversation(
            self.client,
            self.agent_id,
            requires_auth=True,
            audio_interface=DefaultAudioInterface(),
            callback_agent_response=on_agent_response or (lambda response: logger.info(f"Agent: {response}")),
            callback_user_transcript=on_user_transcript or (lambda transcript: logger.info(f"User: {transcript}")),
            callback_agent_response_correction=lambda original, corrected: logger.info(f"Agent correction: {original} -> {corrected}"),
        )
        self.active_conversations[session_id] = conversation
        return conversation

    def start_conversation(self, session_id: str) -> bool:
        """Start a conversation session"""
        try:
            conversation = self.active_conversations.get(session_id)
            if not conversation:
                logger.error(f"No conversation found for session {session_id}")
                return False

            conversation.start_session()
            return True
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            return False

    def end_conversation(self, session_id: str) -> bool:
        """End a conversation session"""
        try:
            conversation = self.active_conversations.get(session_id)
            if conversation:
                conversation.stop_session()
                del self.active_conversations[session_id]
            return True
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}")
            return False

# Create a global instance
voice_manager = VoiceConversationManager()
