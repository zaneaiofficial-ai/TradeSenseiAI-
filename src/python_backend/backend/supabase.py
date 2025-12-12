"""Minimal Supabase auth wrapper with mock fallback.

Provides simple functions to sign up / sign in and fetch user profile. If
`SUPABASE_URL` and `SUPABASE_KEY` are set, it will call Supabase REST APIs.
Otherwise it falls back to in-memory mock users for development.
"""
import os
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

MOCK_USERS = {
    'alice@example.com': {'id': 'user_alice', 'email': 'alice@example.com', 'password': 'password123'},
}


def sign_in(email: str, password: str) -> Optional[dict]:
    """Sign in user. Returns a dict with `user_id` and `access_token` or None."""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            url = f"{SUPABASE_URL}/auth/v1/token"
            headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
            payload = {"grant_type": "password", "email": email, "password": password}
            r = requests.post(url, json=payload, headers=headers, timeout=8)
            if r.status_code == 200:
                data = r.json()
                return {"user_id": data.get('user', {}).get('id'), "access_token": data.get('access_token')}
        except Exception:
            return None

    # Mock fallback
    u = MOCK_USERS.get(email)
    if u and u.get('password') == password:
        return {"user_id": u['id'], "access_token": f"mock-token-{u['id']}"}
    return None


def get_user_profile(user_id: str) -> Optional[dict]:
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
            headers = {"apikey": SUPABASE_KEY}
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code == 200:
                data = r.json()
                if data:
                    return data[0]
        except Exception:
            return None

    # Mock lookup
    for u in MOCK_USERS.values():
        if u['id'] == user_id:
            return {"id": u['id'], "email": u['email']}
    return None


def save_journal_entry(user_id: str, entry: dict) -> dict:
    """Save a journal entry to Supabase."""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            url = f"{SUPABASE_URL}/rest/v1/journal"
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            payload = {"user_id": user_id, **entry}
            r = requests.post(url, json=payload, headers=headers, timeout=8)
            if r.status_code == 201:
                return r.json()
        except Exception:
            pass
    
    # Mock fallback - just return a mock ID
    return {"id": f"mock-journal-{user_id}-{len(entry)}"}


def get_journal_entries(user_id: str) -> list:
    """Get journal entries for a user."""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            url = f"{SUPABASE_URL}/rest/v1/journal?user_id=eq.{user_id}"
            headers = {"apikey": SUPABASE_KEY}
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
    
    # Mock fallback - return empty list
    return []


def save_alert(alert: dict) -> dict:
    """Save a price alert to Supabase."""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            url = f"{SUPABASE_URL}/rest/v1/price_alerts"
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            r = requests.post(url, json=alert, headers=headers, timeout=8)
            if r.status_code == 201:
                return r.json()
        except Exception:
            pass
    
    return {"id": alert.get('id')}


def delete_alert(alert_id: str) -> bool:
    """Delete a price alert."""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            url = f"{SUPABASE_URL}/rest/v1/price_alerts?id=eq.{alert_id}"
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            r = requests.delete(url, headers=headers, timeout=8)
            return r.status_code == 204
        except Exception:
            pass
    
    return True


def get_all_alerts() -> list:
    """Get all alerts from Supabase."""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            url = f"{SUPABASE_URL}/rest/v1/price_alerts"
            headers = {"apikey": SUPABASE_KEY}
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
    
    return []


def save_position(position: dict) -> dict:
    """Save a trading position to Supabase."""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            url = f"{SUPABASE_URL}/rest/v1/positions"
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            r = requests.post(url, json=position, headers=headers, timeout=8)
            if r.status_code == 201:
                return r.json()
        except Exception:
            pass
    
    return {"id": position.get('id')}


def close_position(position_id: str, exit_price: float) -> bool:
    """Close a trading position."""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            url = f"{SUPABASE_URL}/rest/v1/positions?id=eq.{position_id}"
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            payload = {"status": "closed", "exit_price": exit_price}
            r = requests.patch(url, json=payload, headers=headers, timeout=8)
            return r.status_code in [200, 204]
        except Exception:
            pass
    
    return True


def get_user_positions(user_id: str) -> list:
    """Get all positions for a user."""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            url = f"{SUPABASE_URL}/rest/v1/positions?user_id=eq.{user_id}"
            headers = {"apikey": SUPABASE_KEY}
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
    
    return []


def update_position(position_id: str, position: dict) -> bool:
    """Update a position."""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            url = f"{SUPABASE_URL}/rest/v1/positions?id=eq.{position_id}"
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            r = requests.patch(url, json=position, headers=headers, timeout=8)
            return r.status_code in [200, 204]
        except Exception:
            pass
    
    return True

