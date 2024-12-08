import os
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# Initialize ElevenLabs client
client = ElevenLabs(api_key=os.environ.get('ELEVENLABS_API_KEY'))

def start_conversation(agent_id=None):
    """
    Start a new conversational AI session
    Args:
        agent_id (str): Optional agent ID to use
    Returns:
        tuple: (conversation_id, conversation)
    """
    try:
        conversation = Conversation(
            client=client,
            agent_id=agent_id or os.environ.get('AGENT_ID'),
            audio_interface=DefaultAudioInterface(),
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
    try:
        response = conversation.send_message(message)
        return {
            'text': response.text,
            'audio': response.audio
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
    try:
        conversation.end_session()
    except Exception as e:
        print(f"Error ending conversation: {str(e)}")
