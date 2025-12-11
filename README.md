# TradeSensei AI (Prototype)

TradeSensei AI is a laptop-first desktop application concept: a real-time AI trading mentor and trade advisor.

Architecture (scaffold):
- `src\csharp_ui` — C# WPF frontend for UI, transparent layered overlay, Desktop Duplication capture stub, webcam capture stub.
- `src\python_backend` — Python backend for vision (OpenCV), AI logic, OpenAI & ElevenLabs wrappers, WebSocket server to receive frames and provide overlay commands.
- `docs` — Design notes and UI mockups (from provided PDF).
- `assets` — Icons, images, and UI assets.

Quick start (prototype):
1. Backend: open a Python environment and install dependencies in `src/python_backend/requirements.txt`.
2. Run the backend: `uvicorn backend.main:app --host 127.0.0.1 --port 8000`.
3. Frontend: open Visual Studio, load the WPF project files in `src/csharp_ui` and run. The example WPF app will connect to backend WebSocket at `ws://127.0.0.1:8000/ws`.

Notes:
- This repository is a scaffold and prototype. Core features (Desktop Duplication capture, real-time DSP, overlay drawing, full AI models, payment integration) are stubbed with clear TODOs.
- Follow `docs/ARCHITECTURE.md` for full implementation guidance and prioritized milestones.

Next actions:
- Implement Desktop Duplication capture in C# and stream frames to backend WebSocket.
- Implement OpenCV-based chart detection pipelines in Python.
- Implement OpenAI Realtime speech and ElevenLabs TTS wrappers.
- Implement subscription + Supabase + Stripe integration.

Developer instructions (Windows)

- Setup Python backend

	1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r src\python_backend\requirements.txt
```

	2. Copy `.env.example` to `.env` and set API keys.

	3. Run backend:

```powershell
cd src\python_backend
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

- Run the WPF UI (Visual Studio / dotnet)

	1. Open `src\csharp_ui\TradeSensei.UI.csproj` in Visual Studio 2022/2023 or VS Code with the C# extension.
	2. Build and run. Use the buttons in the UI to open the overlay and start/stop streaming.

- Quick test

	- Start the backend.
	- Open the WPF app and `Start Streaming` at FPS=1 or 2.
	- The overlay will capture screenshots and send them to the backend; the backend will draw a demo POI rectangle and occasionally a prototype BUY/SELL suggestion.

Speech endpoints (prototype)

- `POST /tts` — synthesize text to audio (stub). Request JSON: `{"text":"...","voice":"alloy"}`. Response JSON: `{"audio_base64":"..."}`.
- `POST /transcribe` — transcribe audio bytes (stub). Request JSON: `{"audio_base64":"..."}`. Response JSON: `{"transcription":"..."}`.

Example (PowerShell):

```powershell
# TTS (get base64 audio)
$b64 = (Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/tts -Body '{"text":"Hello world"}' -ContentType 'application/json').audio_base64
[System.IO.File]::WriteAllBytes('out.wav', [System.Convert]::FromBase64String($b64))

# Transcribe (send audio file)
$b = [System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes('out.wav'))
$text = (Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/transcribe -Body (ConvertTo-Json @{ audio_base64 = $b }) -ContentType 'application/json').transcription
Write-Host $text
```

Notes & next steps

- The current screen capture uses a GDI fallback (`CaptureService`). For production replace with the Windows Desktop Duplication API (higher FPS + lower CPU).
- The vision pipeline is a simple prototype. Replace `backend/vision.py` with real chart parsing, candle detection, and indicator analysis.
- Replace `trading_advisor.py` with a rules engine and/or GPT-driven assistant integrated with OpenAI for explainability and richer trade signals.

