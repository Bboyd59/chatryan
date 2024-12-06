import os
from elevenlabs import Voice, VoiceSettings, generate, stream
from elevenlabs import set_api_key

def initialize_elevenlabs():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
    set_api_key(api_key)

def create_voice_response(text):
    try:
        initialize_elevenlabs()
        voice = Voice(
            voice_id="bella",  # Using bella voice ID
            settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
        )
        audio = generate(
            text=text,
            voice=voice,
            model="eleven_multilingual_v2"
        )
        return audio
    except Exception as e:
        print(f"Error generating voice response: {str(e)}")
        raise

def stream_voice_response(text):
    try:
        initialize_elevenlabs()
        audio_stream = stream(
            text=text,
            voice="Bella",
            model="eleven_multilingual_v2"
        )
        return audio_stream
    except Exception as e:
        print(f"Error streaming voice response: {str(e)}")
        raise

def start_voice_session():
    try:
        initialize_elevenlabs()
        return True
    except Exception as e:
        print(f"Error starting voice session: {str(e)}")
        return False

def end_voice_session(conversation_data=None):
    try:
        # Add any cleanup logic here if needed
        return True
    except Exception as e:
        print(f"Error ending voice session: {str(e)}")
        return False