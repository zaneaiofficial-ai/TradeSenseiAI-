#!/usr/bin/env python3
"""
Setup script to finalize voice chat integration.
This updates speech.py and main.py with proper API integration.
"""
import os

def update_speech_py():
    """Update speech.py with modern OpenAI API"""
    speech_content = '''"""Speech helpers: OpenAI Whisper transcription + ElevenLabs TTS.

These functions use environment variables `OPENAI_API_KEY` and
`ELEVENLABS_API_KEY`.
"""
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
except Exception as e:
    print(f"OpenAI import error: {e}")
    openai_client = None


def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    """Transcribe audio bytes using OpenAI Whisper."""
    if openai_client and OPENAI_API_KEY:
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                f.write(audio_bytes)
                tmp_path = f.name
            
            try:
                with open(tmp_path, 'rb') as fh:
                    transcript = openai_client.audio.transcriptions.create(
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

    return '(transcription placeholder - no API key)'


def synthesize_text_to_audio_bytes(text: str, voice: str = '21m00Tcm4TlvDq8ikWAM') -> bytes:
    """Synthesize text to audio via ElevenLabs API.
    
    Default voice is 'Adam' (21m00Tcm4TlvDq8ikWAM).
    Returns audio bytes (MP3 format).
    """
    if ELEVENLABS_API_KEY:
        try:
            # ElevenLabs API: POST /v1/text-to-speech/{voice_id}
            url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice}'
            headers = {
                'xi-api-key': ELEVENLABS_API_KEY,
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
                print(f'ElevenLabs TTS failed: {r.status_code} - {r.text}')
                return b''
        except Exception as e:
            print(f'ElevenLabs TTS error: {e}')
            return b''

    print('ElevenLabs API key not configured')
    return b''
'''
    
    path = 'backend/speech.py'
    with open(path, 'w') as f:
        f.write(speech_content)
    print(f"✅ Updated {path}")


def update_main_py():
    """Add mentor import and endpoint to main.py"""
    path = 'backend/main.py'
    
    with open(path, 'r') as f:
        content = f.read()
    
    # Add mentor import if not present
    if 'from . import mentor' not in content:
        # Find the import section and add mentor import
        import_section_end = content.find('\napp = FastAPI()')
        if import_section_end > 0:
            content = content[:import_section_end] + '\nfrom . import mentor' + content[import_section_end:]
    
    # Add mentor endpoint if not present
    if '@app.post(\'/mentor/ask\')' not in content:
        mentor_endpoint = '''

@app.post('/mentor/ask')
async def mentor_ask(payload: dict):
    """Get AI mentor response to a trading question.
    
    Expects JSON: {"user_input": "...", "context": {...}}
    Returns: {"response": "...", "advice": "..."}
    """
    user_input = payload.get('user_input', '')
    context = payload.get('context')
    if not user_input:
        return {"response": "", "advice": "Please ask a trading question."}
    
    response = mentor.get_mentor_response(user_input, context)
    return {"response": response, "advice": response}
'''
        # Insert before the final endpoints
        tts_endpoint_pos = content.find('@app.post(\'/tts\')')
        if tts_endpoint_pos > 0:
            content = content[:tts_endpoint_pos] + mentor_endpoint + '\n' + content[tts_endpoint_pos:]
    
    with open(path, 'w') as f:
        f.write(content)
    print(f"✅ Updated {path}")


if __name__ == '__main__':
    try:
        update_speech_py()
        update_main_py()
        print("\n✅ Backend setup complete!")
        print("Next steps:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Run: uvicorn backend.main:app --reload")
        print("3. Test voice chat in the frontend")
    except Exception as e:
        print(f"❌ Error: {e}")
