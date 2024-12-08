import os
import signal
import sys
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

def main():
    AGENT_ID = os.getenv('AGENT_ID')
    API_KEY = os.getenv('ELEVEN_API_KEY')

    if not AGENT_ID:
        sys.stderr.write("AGENT_ID environment variable must be set\n")
        sys.exit(1)

    if not API_KEY:
        sys.stderr.write("ELEVENLABS_API_KEY not set, assuming the agent is public\n")

    client = ElevenLabs(api_key=API_KEY)
    conversation = Conversation(
        client=client,
        AGENT_ID=AGENT_ID,
        audio_interface=DefaultAudioInterface(),
        requires_auth=bool(API_KEY),
    )
    
    # Assume auth is required when API_KEY is set
    requires_auth = bool(API_KEY)
    
    def callback_agent_response(response):
        print(f"Agent: {response}")
    
    def callback_agent_response_correction(original, corrected):
        print(f"Agent: {original} -> {corrected}")
    
    def callback_user_transcript(transcript):
        print(f"User: {transcript}")
    
    conversation.callback_agent_response = callback_agent_response
    conversation.callback_agent_response_correction = callback_agent_response_correction
    conversation.callback_user_transcript = callback_user_transcript
    
    # Start the conversation session
    conversation.start_session()
    
    # Run until Ctrl+C is pressed
    signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())
    
    conversation_id = conversation.wait_for_session_end()
    print(f"Conversation ID: {conversation_id}")

def create_conversation():
    """
    Create and return a new conversation instance
    Returns:
        Conversation: New conversation instance
    """
    AGENT_ID = os.getenv('AGENT_ID')
    API_KEY = os.getenv('ELEVEN_API_KEY')

    if not AGENT_ID or not API_KEY:
        return None

    client = ElevenLabs(api_key=API_KEY)
    conversation = Conversation(
        client=client,
        AGENT_ID=AGENT_ID,
        audio_interface=DefaultAudioInterface(),
        requires_auth=True
    )
    
    return conversation

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
            'audio': response.audio,
            'conversation_id': conversation.conversation_id
        }
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return None

if __name__ == '__main__':
    main()
