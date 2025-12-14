from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {"status": "TradeSensei AI backend running (minimal)"}

@app.get('/health')
async def health():
    return {"status": "healthy"}

@app.post('/auth/signin')
async def auth_signin(payload: dict):
    # Mock login for testing
    email = payload.get('email')
    password = payload.get('password')
    if email == 'test@example.com' and password == 'password':
        return {"ok": True, "user_id": "test_user", "access_token": "mock_token"}
    return {"ok": False, "reason": "invalid credentials"}
