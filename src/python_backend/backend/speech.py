"""Speech helpers: OpenAI Whisper transcription + ElevenLabs TTS."""
import os
import tempfile
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

try:
    from openai import OpenAI
    if OPENAI_API_KEY:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    else:
        openai_client = None
except Exception:
    openai_client = None


def transcribe_audio_bytes(audio_bytes: bytes, api_key: str = None) -> str:
    """Transcribe audio bytes using OpenAI Whisper."""
    key = api_key or OPENAI_API_KEY
    if not key:
        return '(no API key)'
    
    try:
        client = OpenAI(api_key=key)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        
        try:
            with open(tmp_path, 'rb') as fh:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=fh,
                    language="en"
                )
            text = transcript.text if hasattr(transcript, 'text') else str(transcript)
            return text.strip() if text else ''
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
    except Exception as e:
        print(f'OpenAI transcription error: {e}')
        return '(transcription failed)'


def synthesize_text_to_audio_bytes(text: str, voice: str = '21m00Tcm4TlvDq8ikWAM', api_key: str = None) -> bytes:
    """Synthesize text to audio via ElevenLabs API. Returns WAV bytes when successful."""
    key = api_key or ELEVENLABS_API_KEY
    if not key:
        return b'(no API key)'
    
    try:
        # Map legacy or placeholder voice names to a known ElevenLabs voice id
        if not voice or voice in ('alloy', 'default'):
            voice = '21m00Tcm4TlvDq8ikWAM'

        # ElevenLabs API: POST /v1/text-to-speech/{voice_id}
        url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice}'
        headers = {
            'xi-api-key': key,
            'Content-Type': 'application/json'
        }
        payload = {
            'text': text,
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.75
            }
        }
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.content
        else:
            print('ElevenLabs TTS failed:', r.status_code, r.text)
    except Exception as e:
        print('ElevenLabs TTS error:', e)

    # Fallback stub: return empty bytes
    return b''
