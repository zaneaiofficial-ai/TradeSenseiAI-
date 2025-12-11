from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print('Testing root...')
r = client.get('/')
print('GET / ->', r.status_code, r.json())

print('\nTesting /mentor/ask...')
resp = client.post('/mentor/ask', json={'user_input': 'Give me quick trading advice for EURUSD.'})
print('/mentor/ask ->', resp.status_code)
try:
    print(resp.json())
except Exception as e:
    print('Non-JSON response:', resp.text[:200])

print('\nTesting /tts...')
r2 = client.post('/tts', json={'text': 'Hello trader'})
print('/tts ->', r2.status_code)
try:
    data = r2.json()
    audio_b64 = data.get('audio_base64')
    print('audio_base64 length:', len(audio_b64) if audio_b64 else 'none')
except Exception as e:
    print('Non-JSON response or bytes length:', len(r2.content))

print('\nDone')
