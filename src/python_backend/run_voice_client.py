#!/usr/bin/env python3
"""
Simple Voice Chat Client for TradeSensei AI

This script provides end-to-end testing of the voice chat loop:
1. Capture audio from microphone
2. Send to backend for transcription (Whisper)
3. Get AI mentor advice (GPT-4o-mini)
4. Convert response to speech (ElevenLabs TTS)
5. Play audio response

Requirements: pyaudio, pydub
"""

import os
import sys
import json
import requests
import numpy as np
from pathlib import Path

# Try to import audio libraries
try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("WARNING: Audio libraries not installed. Install with: pip install sounddevice soundfile")

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"
SAMPLE_RATE = 16000
DURATION_SECONDS = 5  # Record for 5 seconds

def list_audio_devices():
    """List available audio devices"""
    if not AUDIO_AVAILABLE:
        print("Audio devices listing requires sounddevice library")
        return
    
    print("\nAvailable audio devices:")
    print(sd.query_devices())

def record_audio(duration=DURATION_SECONDS, sr=SAMPLE_RATE):
    """Record audio from default microphone"""
    if not AUDIO_AVAILABLE:
        print("ERROR: Audio recording requires sounddevice library")
        return None
    
    print(f"\nRecording for {duration} seconds... (speak now)")
    try:
        audio_data = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype=np.float32)
        sd.wait()
        print("Recording complete!")
        return audio_data, sr
    except Exception as e:
        print(f"Recording error: {e}")
        return None

def save_audio_wav(audio_data, sr, filename="temp_audio.wav"):
    """Save audio data to WAV file"""
    if not AUDIO_AVAILABLE:
        return None
    
    try:
        sf.write(filename, audio_data, sr)
        return filename
    except Exception as e:
        print(f"Error saving audio: {e}")
        return None

def transcribe_audio(audio_bytes):
    """Send audio to backend for transcription"""
    try:
        files = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
        response = requests.post(f"{BACKEND_URL}/transcribe", files=files)
        response.raise_for_status()
        result = response.json()
        return result.get('text', '')
    except Exception as e:
        print(f"Transcription error: {e}")
        return None

def get_mentor_response(user_input, context=None):
    """Get AI mentor response"""
    try:
        payload = {
            'user_input': user_input,
            'trading_context': context or {}
        }
        response = requests.post(f"{BACKEND_URL}/mentor/ask", json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get('response', '')
    except Exception as e:
        print(f"Mentor error: {e}")
        return None

def text_to_speech(text, voice='alloy'):
    """Convert text to speech"""
    try:
        payload = {
            'text': text,
            'voice': voice
        }
        response = requests.post(f"{BACKEND_URL}/tts", json=payload)
        response.raise_for_status()
        result = response.json()
        
        # audio_base64 contains the audio data
        audio_base64 = result.get('audio_base64', '')
        return audio_base64
    except Exception as e:
        print(f"TTS error: {e}")
        return None

def play_audio_base64(audio_base64):
    """Decode and play base64 audio"""
    if not AUDIO_AVAILABLE:
        print("Audio playback requires sounddevice library")
        return
    
    try:
        import base64
        import io
        
        # Decode base64
        audio_bytes = base64.b64decode(audio_base64)
        
        # Load audio from bytes
        audio_data, sr = sf.read(io.BytesIO(audio_bytes))
        
        # Play audio
        print("Playing response...")
        sd.play(audio_data, sr)
        sd.wait()
        print("Playback complete!")
    except Exception as e:
        print(f"Playback error: {e}")

def main():
    """Main voice chat loop"""
    print("=" * 70)
    print("TradeSensei AI - Voice Chat Client")
    print("=" * 70)
    print(f"\nBackend URL: {BACKEND_URL}")
    
    # Check backend connection
    try:
        response = requests.get(f"{BACKEND_URL}/")
        print(f"✓ Backend connected: {response.status_code}")
    except Exception as e:
        print(f"✗ Backend connection failed: {e}")
        print("Make sure backend is running: python run_server.py")
        return
    
    if not AUDIO_AVAILABLE:
        print("\n⚠ Audio libraries not installed!")
        print("Install with: pip install sounddevice soundfile")
        print("\nDemonstrating text-based voice loop instead:")
        
        # Test with hardcoded input
        test_input = "What's a good entry signal for a bullish trade?"
        print(f"\nUser: {test_input}")
        
        mentor_response = get_mentor_response(test_input)
        if mentor_response:
            print(f"Mentor: {mentor_response}")
            
            tts_audio = text_to_speech(mentor_response)
            if tts_audio:
                print(f"✓ TTS generated {len(tts_audio)} chars of audio")
        return
    
    # Audio-based loop
    print("\n" + "=" * 70)
    print("Voice Chat Loop")
    print("=" * 70)
    print("\nInstructions:")
    print("1. Recording will start automatically")
    print("2. Speak your question")
    print("3. AI mentor will respond with voice")
    print("4. Type 'quit' to exit\n")
    
    try:
        while True:
            # Record user audio
            audio_data = record_audio()
            if audio_data is None:
                break
            
            audio_arr, sr = audio_data
            
            # Save to WAV file for transmission
            wav_file = save_audio_wav(audio_arr, sr)
            if not wav_file:
                continue
            
            # Transcribe
            print("Transcribing...")
            with open(wav_file, 'rb') as f:
                user_text = transcribe_audio(f.read())
            
            if not user_text:
                print("Could not transcribe audio, try again")
                continue
            
            print(f"You said: {user_text}")
            
            # Get mentor response
            print("Getting mentor advice...")
            mentor_response = get_mentor_response(user_text)
            
            if not mentor_response:
                print("Could not get mentor response, try again")
                continue
            
            print(f"Mentor: {mentor_response}")
            
            # Convert to speech and play
            print("Generating speech...")
            audio_base64 = text_to_speech(mentor_response)
            
            if audio_base64:
                play_audio_base64(audio_base64)
            
            # Cleanup
            try:
                os.remove(wav_file)
            except:
                pass
            
            # Ask if user wants to continue
            again = input("\nContinue? (y/n): ").lower().strip()
            if again != 'y':
                break
    
    except KeyboardInterrupt:
        print("\n\nExiting...")

if __name__ == "__main__":
    main()
