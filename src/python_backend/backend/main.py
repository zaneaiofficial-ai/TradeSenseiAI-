from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
import base64
import cv2
import numpy as np
import json
from . import vision
from . import trading_advisor
from . import speech
from . import subscriptions
from . import supabase
from . import mentor
from . import webcam_vision

app = FastAPI()


@app.get('/')
async def root():
    return {"status": "TradeSensei AI backend running"}


@app.websocket('/ws')
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()

            if data.get('type') == 'frame':
                b64 = data.get('data')
                try:
                    img_bytes = base64.b64decode(b64)
                    nparr = np.frombuffer(img_bytes, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                except Exception:
                    await ws.send_json({"type": "error", "message": "invalid image"})
                    continue

                # Run vision pipeline
                features = vision.detect_chart_features(img)

                # If a POI was detected, send a rectangle + label
                poi = features.get('poi')
                if poi:
                    x, y = poi
                    h, w = img.shape[:2]
                    rect_w, rect_h = 120, 60
                    rect_x = max(0, x - rect_w // 2)
                    rect_y = max(0, y - rect_h // 2)
                    overlay_rect = {"type": "overlay", "action": "draw_rect", "x": int(rect_x), "y": int(rect_y), "w": int(rect_w), "h": int(rect_h)}
                    await ws.send_json(overlay_rect)

                    overlay_text = {"type": "overlay", "action": "draw_text", "x": int(rect_x), "y": int(rect_y) - 18, "text": "POI"}
                    await ws.send_json(overlay_text)

                # Evaluate trading advisor (prototype)
                try:
                    signal = trading_advisor.evaluate(features)
                    if signal:
                        # Determine user tier (frame payload may include 'user_id')
                        user_id = data.get('user_id') if isinstance(data, dict) else None
                        tier = subscriptions.get_user_tier(user_id) if user_id else 'free'

                        # Gate signals by tier: free -> no signals, pro -> limited, master -> full
                        if tier == 'free':
                            # Do not send trade signals to free users
                            pass
                        else:
                            side = signal.get('side')
                            price = signal.get('price')
                            sl = signal.get('sl')
                            tp1 = signal.get('tp1')

                            if tier == 'pro':
                                # Pro: send basic TP1 signal
                                sig_text = f"{side} @ {price} TP1 {tp1}"
                            else:
                                # Master: full details
                                sig_text = f"{side} @ {price} SL {sl} TP1 {tp1}"

                            sig_cmd = {"type": "overlay", "action": "draw_text", "x": int(x), "y": int(y) - 36, "text": sig_text, "ttl": 8}
                            await ws.send_json(sig_cmd)

                            sig_rect = {"type": "overlay", "action": "draw_rect", "x": int(x - 60), "y": int(y - 20), "w": 120, "h": 40, "ttl": 8}
                            await ws.send_json(sig_rect)
                except Exception:
                    pass

                # Heartbeat
                await ws.send_json({"type": "info", "message": "processed_frame"})

            elif data.get('type') == 'ping':
                await ws.send_json({"type": "pong"})
            else:
                await ws.send_json({"type": "error", "message": "unknown message type"})

    except WebSocketDisconnect:
        print('Client disconnected')
    except Exception as e:
        print('WS error', e)
        try:
            await ws.close()
        except Exception:
            pass


@app.post('/tts')
async def tts_endpoint(payload: dict):
    """Synthesize text to audio (stub).

    Expects JSON: {"text": "...", "voice": "alloy", "api_key": "..."}
    Returns JSON: {"audio_base64": "..."}
    """
    text = payload.get('text', '')
    voice = payload.get('voice', 'alloy')
    api_key = payload.get('api_key')
    audio_bytes = speech.synthesize_text_to_audio_bytes(text, voice=voice, api_key=api_key)
    import base64
    b64 = base64.b64encode(audio_bytes).decode('ascii')
    return {"audio_base64": b64}


@app.post('/transcribe')
async def transcribe_endpoint(payload: dict):
    """Transcribe audio bytes (stub).

    Expects JSON: {"audio_base64": "...", "api_key": "..."}
    Returns JSON: {"transcription": "..."}
    """
    import base64
    b64 = payload.get('audio_base64', '')
    api_key = payload.get('api_key')
    try:
        audio_bytes = base64.b64decode(b64)
    except Exception:
        return {"transcription": ""}
    text = speech.transcribe_audio_bytes(audio_bytes, api_key)
    return {"transcription": text}


@app.post('/auth/signin')
async def auth_signin(payload: dict):
    """Sign in endpoint. Expects {"email": "...", "password": "..."}.

    Returns {"user_id":..., "access_token":...} on success.
    """
    email = payload.get('email')
    password = payload.get('password')
    if not email or not password:
        return {"ok": False, "reason": "email and password required"}
    res = supabase.sign_in(email, password)
    if not res:
        return {"ok": False, "reason": "invalid credentials"}
    return {"ok": True, "user_id": res.get('user_id'), "access_token": res.get('access_token')}


@app.get('/auth/me')
async def auth_me(user_id: str):
    """Return user profile for `user_id` (mock/simple)."""
    profile = supabase.get_user_profile(user_id)
    if not profile:
        return {"ok": False, "reason": "not found"}
    return {"ok": True, "profile": profile}


@app.get('/subscriptions/check')
async def subscription_check(user_id: str):
    """Return a user's subscription tier and flags.

    Query params: `user_id`.
    """
    tier = subscriptions.get_user_tier(user_id)
    return {"user_id": user_id, "tier": tier, "is_premium": subscriptions.is_premium(user_id)}


@app.post('/subscriptions/webhook')
async def subscription_webhook(request: Request):
    """Receive webhook from Flawter Flow / Flutterwave (prototype).

    This endpoint validates the webhook signature using the configured
    Flutterwave secret via `subscriptions.verify_flw_webhook`. If verification
    fails, it returns HTTP 403.
    Expected JSON payload: {"user_id": "...", "tier": "pro"}
    """
    raw_body = await request.body()
    headers = {k: v for k, v in request.headers.items()}

    # Verify signature
    try:
        valid = subscriptions.verify_flw_webhook(raw_body, headers)
    except Exception:
        valid = False

    if not valid:
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    user_id = payload.get('user_id')
    tier = payload.get('tier')
    if not user_id or tier not in ('free', 'pro', 'master'):
        raise HTTPException(status_code=400, detail="Invalid payload")

    subscriptions.set_mock_tier(user_id, tier)
    return {"ok": True, "user_id": user_id, "tier": tier}


@app.post('/subscriptions/create_checkout')
async def create_checkout(payload: dict):
    """Create a Flutterwave checkout/payment link.

    Expects JSON: {"user_id": "...", "amount": 9.99, "currency": "USD", "redirect_url": "https://..."}
    """
    user_id = payload.get('user_id')
    amount = payload.get('amount')
    currency = payload.get('currency', 'USD')
    redirect = payload.get('redirect_url')
    if not user_id or not amount:
        return {"ok": False, "reason": "user_id and amount required"}

    res = subscriptions.create_flutterwave_payment_link(user_id, float(amount), currency=currency, redirect_url=redirect)
    return res


@app.post('/webcam/analyze')
async def webcam_analyze(payload: dict):
    """Analyze a webcam frame.

    Expects JSON: {"image_base64": "..."}
    Returns JSON with detection results from `webcam_vision.analyze_base64_image`.
    """
    b64 = payload.get('image_base64')
    if not b64:
        return {"ok": False, "error": "image_base64 required"}
    try:
        result = webcam_vision.analyze_base64_image(b64)
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "result": result}


@app.post('/mentor/ask')
async def mentor_ask(payload: dict):
    """Get AI mentor response to a trading question."""
    user_input = payload.get('user_input', '')
    context = payload.get('context')
    conversation_history = payload.get('conversation_history', [])
    vision_context = payload.get('vision_context')
    language = payload.get('language', 'en')
    openai_key = payload.get('openai_key')
    elevenlabs_key = payload.get('elevenlabs_key')
    if not user_input:
        return {"response": "", "advice": "Please ask a trading question."}
    try:
        response = mentor.get_mentor_response(user_input, context, conversation_history, vision_context, language, openai_key, elevenlabs_key)
    except Exception as e:
        print('Mentor error:', e)
        return {"response": "", "advice": "Mentor unavailable."}
    return {"response": response, "advice": response}


@app.post('/risk/position-size')
async def calculate_position_size_endpoint(payload: dict):
    """Calculate position size based on risk management."""
    account_balance = payload.get('account_balance', 0)
    risk_per_trade = payload.get('risk_per_trade', 1)  # % of account
    entry_price = payload.get('entry_price', 0)
    stop_loss_price = payload.get('stop_loss_price', 0)
    
    if account_balance <= 0 or entry_price <= 0:
        return {"error": "Invalid account balance or entry price"}
    
    result = mentor.calculate_position_size(account_balance, risk_per_trade, entry_price, stop_loss_price)
    return result


@app.post('/risk/management-advice')
async def risk_management_advice(payload: dict):
    """Get risk management advice."""
    account_balance = payload.get('account_balance', 0)
    current_positions = payload.get('current_positions', [])
    
    advice = mentor.get_risk_management_advice(account_balance, current_positions)
    return {"advice": advice}


@app.post('/journal/save')
async def save_journal_entry(payload: dict):
    """Save a conversation entry to the trading journal."""
    user_id = payload.get('user_id')
    entry = payload.get('entry', {})
    
    if not user_id or not entry:
        return {"error": "Missing user_id or entry"}
    
    try:
        # Save to Supabase (assuming a 'journal' table exists)
        result = supabase.save_journal_entry(user_id, entry)
        return {"success": True, "id": result.get('id')}
    except Exception as e:
        return {"error": str(e)}


@app.get('/journal/{user_id}')
async def get_journal_entries(user_id: str):
    """Get trading journal entries for a user."""
    try:
        entries = supabase.get_journal_entries(user_id)
        return {"entries": entries}
    except Exception as e:
        return {"error": str(e)}
