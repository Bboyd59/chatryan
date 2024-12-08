import os
import signal
import sys
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# Initialize ElevenLabs client
client = ElevenLabs(api_key=os.environ.get('ELEVENLABS_API_KEY'))

def start_conversation():
    """
    Start a new conversational AI session
    Returns:
        Conversation: Active conversation instance
    """
    try:
        AGENT_ID = os.environ.get('AGENT_ID')
        if not AGENT_ID:
            print("AGENT_ID not set, using default agent")
        
        conversation = Conversation(
            client=client,
            agent_id=AGENT_ID,
            audio_interface=DefaultAudioInterface(),
            requires_auth=bool(os.environ.get('ELEVENLABS_API_KEY')),
        )
        conversation.start_session()
        return conversation
    except Exception as e:
        print(f"Error starting conversation: {str(e)}")
        return None

def send_message(conversation, message):
    """
    Send a message to the conversation and get the response
    Args:
        conversation: Active conversation instance
        message (str): Message to send
    Returns:
        dict: Response containing audio and text
    """
    if not conversation:
        return None
        
    try:
        response = conversation.send_message(message)
        # Get both text and audio from the response
        return {
            'text': response.text,
            'audio': response.audio.decode('utf-8') if response.audio else None,
            'conversation_id': conversation.conversation_id
        }
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return None

def end_conversation(conversation):
    """
    End the conversation session
    Args:
        conversation: Active conversation instance
    """
    if not conversation:
        return
        
    try:
        conversation.end_session()
        print(f"Conversation ID: {conversation.conversation_id}")
    except Exception as e:
        print(f"Error ending conversation: {str(e)}")

# Handle graceful shutdown
def signal_handler(sig, frame):
    print("\nGracefully shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
