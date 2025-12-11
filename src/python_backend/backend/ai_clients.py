import os
from dotenv import load_dotenv
load_dotenv()

# Stubs for OpenAI & ElevenLabs integration

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

# TODO: implement realtime speech recognition and TTS wrappers


def transcribe_audio(audio_bytes):
    """Send audio to OpenAI Realtime speech-to-text (stub)."""
    # Placeholder
    return "(transcription placeholder)"


def speak_text(text, voice='alloy'):
    """Send text to ElevenLabs TTS and stream audio (stub)."""
    # Placeholder
    return b''
