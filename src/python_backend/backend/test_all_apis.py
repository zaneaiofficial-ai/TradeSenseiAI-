"""Comprehensive test for all three APIs: OpenAI, ElevenLabs, Supabase."""
from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from backend.main import app
import os

client = TestClient(app)

print("=" * 70)
print("COMPREHENSIVE API TEST: OpenAI + ElevenLabs + Supabase")
print("=" * 70)

# Check env vars
print("\n1. ENV VARIABLES CHECK")
print(f"   ✓ OPENAI_API_KEY: {'set' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
print(f"   ✓ ELEVENLABS_API_KEY: {'set' if os.getenv('ELEVENLABS_API_KEY') else 'NOT SET'}")
print(f"   ✓ SUPABASE_KEY: {'set' if os.getenv('SUPABASE_KEY') else 'NOT SET'}")
print(f"   ✓ SUPABASE_SECRET: {'set' if os.getenv('SUPABASE_SECRET') else 'NOT SET'}")

# Test Root endpoint
print("\n2. BACKEND ROOT ENDPOINT")
r = client.get('/')
print(f"   GET / → {r.status_code} {r.json()['status']}")

# Test OpenAI/Mentor
print("\n3. OPENAI GPT MENTOR (with trading context)")
payload = {
    'user_input': 'I see price at 1.1050, SMA-20 at 1.1020, SMA-50 at 1.0980, slope positive. Should I go long?',
    'context': {
        'asset': 'EURUSD',
        'price': 1.1050,
        'sma_short': 1.1020,
        'sma_long': 1.0980,
        'slope': 'positive'
    }
}
r = client.post('/mentor/ask', json=payload)
print(f"   POST /mentor/ask → {r.status_code}")
if r.status_code == 200:
    resp_json = r.json()
    response_text = resp_json.get('response', '')
    if 'error' in response_text.lower():
        print(f"   ✗ Error: {response_text[:100]}")
    else:
        print(f"   ✓ Response: {response_text[:120]}...")
else:
    print(f"   ✗ Error: {r.text[:200]}")

# Test ElevenLabs TTS
print("\n4. ELEVENLABS TEXT-TO-SPEECH")
r = client.post('/tts', json={'text': 'Hello, this is TradeSensei AI. Market analysis ready.'})
print(f"   POST /tts → {r.status_code}")
if r.status_code == 200:
    resp_json = r.json()
    audio_b64 = resp_json.get('audio_base64', '')
    if audio_b64:
        print(f"   ✓ Audio generated: {len(audio_b64)} base64 chars")
    else:
        print(f"   ✗ No audio in response: {resp_json}")
else:
    print(f"   ✗ Error: {r.text[:200]}")

# Test Supabase Auth (mock)
print("\n5. SUPABASE AUTH CHECK (mock)")
r = client.post('/auth/signin', json={'email': 'alice@example.com', 'password': 'password123'})
print(f"   POST /auth/signin → {r.status_code}")
if r.status_code == 200:
    resp_json = r.json()
    if resp_json.get('ok'):
        print(f"   ✓ Auth successful: user_id={resp_json.get('user_id')}")
    else:
        print(f"   ✗ Auth failed: {resp_json}")
else:
    print(f"   ✗ Error: {r.text[:200]}")

# Test Subscriptions endpoint
print("\n6. SUBSCRIPTIONS CHECK (mock)")
r = client.get('/subscriptions/check?user_id=user_alice')
print(f"   GET /subscriptions/check → {r.status_code}")
if r.status_code == 200:
    resp_json = r.json()
    print(f"   ✓ Tier: {resp_json.get('tier')}, Premium: {resp_json.get('is_premium')}")
else:
    print(f"   ✗ Error: {r.text[:200]}")

# Test Transcription (mock audio)
print("\n7. SPEECH TRANSCRIPTION (mock)")
import base64
mock_audio = b'\xff\xfb\x90\x00' + b'\x00' * 100  # Fake MP3 header + padding
r = client.post('/transcribe', json={'audio_base64': base64.b64encode(mock_audio).decode()})
print(f"   POST /transcribe → {r.status_code}")
if r.status_code == 200:
    resp_json = r.json()
    text = resp_json.get('transcription', '')
    print(f"   ✓ Transcription: {text[:80]}...")
else:
    print(f"   ✗ Error: {r.text[:200]}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
