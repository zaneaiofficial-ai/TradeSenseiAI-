# TradeSensei AI - Architecture & Implementation Notes

Goal: laptop-only, Windows-first AI trading mentor. Prototype uses C# WPF for UI/overlay and Python backend for vision and AI logic.

High-level components

- C# WPF (Frontend)
  - Transparent layered overlay window using Layered Windows API.
  - Desktop Duplication capture module to capture chart region at high FPS.
  - Webcam capture (MediaCapture) to feed webcam frames to backend and to virtual camera composite.
  - WebSocket client to stream frames (base64 PNG) to Python backend at `ws://127.0.0.1:8000/ws`.
  - Overlay renderer that accepts overlay commands from backend and draws arrows/labels.

- Python Backend
  - FastAPI + WebSocket server to receive frames and send overlay commands.
  - OpenCV pipelines for chart analysis and pattern detection.
  - OpenAI Realtime & ElevenLabs wrappers for speech in/out.
  - Supabase + Stripe integration for auth and subscriptions.

- OBS / Virtual Camera
  - Optionally use OBS VirtualCam or OBS WebSocket to stream the composite (chart + overlay + webcam) as a virtual camera for TikTok Live.

Implementation roadmap

1. Basic IPC and frame streaming (C# -> Python WebSocket).
2. Simple vision pipeline that identifies central POI and returns overlay commands.
3. WPF overlay draws returned commands.
4. Add speech-to-text and TTS integration.
5. Implement subscription checks via Supabase and Stripe.
6. Implement advanced chart analysis modules.

Security & keys

- Store API keys in environment variables or `.env` for the backend.
- Do not commit keys to source control.

