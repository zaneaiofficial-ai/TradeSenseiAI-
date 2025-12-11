# TradeSensei AI - Voice Chat Setup Guide

## API Keys Configured ✅

Your API keys have been stored in the backend `.env` file:

- **OpenAI API Key**: Configured for Whisper (transcription) + GPT (mentor reasoning)
- **ElevenLabs API Key**: Configured for TTS (text-to-speech)

## Backend Setup Required

### Step 1: Update Speech Module
The `speech.py` backend module needs to be updated to use the new OpenAI client library. Replace the file with the updated version that supports:
- OpenAI Whisper transcription
- ElevenLabs TTS with your configured API key

**File**: `src/python_backend/backend/speech.py`

Replace with modern OpenAI API calls using `from openai import OpenAI` client initialization.

### Step 2: Update Main Backend
The `main.py` needs the mentor import and `/mentor/ask` endpoint added.

**File**: `src/python_backend/backend/main.py`

Add to imports:
```python
from . import mentor
```

Add new endpoint:
```python
@app.post('/mentor/ask')
async def mentor_ask(payload: dict):
    """Get AI mentor response to a trading question."""
    user_input = payload.get('user_input', '')
    context = payload.get('context')
    if not user_input:
        return {"response": "", "advice": "Please ask a trading question."}
    response = mentor.get_mentor_response(user_input, context)
    return {"response": response, "advice": response}
```

### Step 3: Mentor Module
The `mentor.py` module has been created with GPT integration. It includes:
- `get_mentor_response(user_input, trading_context)` - Uses GPT-4 mini for AI reasoning
- `get_quick_advice(signal_type)` - Pre-canned advice for BUY/SELL/HOLD signals

## Frontend Setup Complete ✅

The C# WPF frontend has been fully configured:

1. **VoiceChatWindow** - Push-to-talk UI with:
   - Record button (holds to record)
   - Transcription display
   - AI response display
   - Play button for TTS

2. **VoiceChatService** - Handles:
   - Microphone capture via NAudio
   - Audio file writing to disk
   - Backend API calls for transcription
   - TTS playback from backend

3. **Main UI Integration**:
   - "🎤 Voice Chat" button on main window
   - Opens VoiceChatWindow dialog
   - Full lifecycle management

## End-to-End Voice Chat Flow

1. **User clicks "🎤 Voice Chat"** → VoiceChatWindow opens
2. **User holds "Talk to Mentor" button** → Audio recorded from microphone
3. **User releases button** → 
   - Audio sent to `/transcribe` endpoint (OpenAI Whisper)
   - Transcription displayed in UI
4. **Backend processes transcription** →
   - Calls `/mentor/ask` endpoint
   - GPT-4 mini generates trading advice
   - Response returned to frontend
5. **User clicks "Play Response"** →
   - Response text sent to `/tts` endpoint (ElevenLabs)
   - MP3 audio received
   - Audio played via WaveOutEvent

## Testing Checklist

- [ ] Backend running: `uvicorn backend.main:app --reload`
- [ ] OpenAI API key working (test with simple prompt)
- [ ] ElevenLabs API key working (test TTS)
- [ ] Frontend compiles and runs
- [ ] Microphone device detected by NAudio
- [ ] Voice Chat window opens
- [ ] Push-to-talk button records audio
- [ ] Transcription appears after release
- [ ] AI response appears in response box
- [ ] Play button produces audio output
- [ ] Audio plays through system speakers

## Troubleshooting

### Transcription fails
- Check `OPENAI_API_KEY` in `.env`
- Ensure audio file is valid WAV format
- Check internet connection to OpenAI API

### TTS plays no audio
- Check `ELEVENLABS_API_KEY` in `.env`
- Verify ElevenLabs account has remaining quota
- Check system audio device is working
- Ensure NAudio WaveOutEvent can access audio

### Mentor response is blank
- Verify backend `/mentor/ask` endpoint exists
- Check that mentor.py imports GPT client correctly
- Ensure OpenAI API key has GPT model access

### Microphone not detected
- Check NAudio can access Windows audio devices
- Ensure microphone is set as default in Windows Sound settings
- Try running as Administrator

## Next Steps After Testing

1. **Integrate Trading Context** - Pass current chart data to mentor for contextual advice
2. **Real-time Streaming** - Use OpenAI Realtime API for lower latency
3. **Voice Banking** - Save preferred mentor phrases and custom responses
4. **Tone Selection** - Let users choose mentor voice/personality via ElevenLabs
5. **Lesson Integration** - Link voice chat to lesson system for learning paths

---

**Status**: Ready for integration testing
**Last Updated**: December 8, 2025
