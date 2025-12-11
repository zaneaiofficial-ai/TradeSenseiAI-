"""Subscriptions module supporting Supabase auth + Flawter Flow payments (prototype).

This module provides a simple interface to get a user's tier and decide whether
they are allowed premium features. In production this will call Supabase to
fetch the user profile and Flawter Flow / Stripe to validate active subscriptions.

Behavior in this prototype:
- If `SUPABASE_URL` and `SUPABASE_KEY` are set, this module will attempt to use
  Supabase (not yet fully implemented). Otherwise it falls back to an in-memory
  mock mapping `MOCK_TIERS` which can be used for testing.
- If `FLAWTER_API_KEY` is provided, the module exposes a webhook endpoint in
  `main.py` that can be used to flip user tiers (simulated).
"""
import os
from typing import Literal
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
FLAWTER_API_KEY = os.getenv('FLAWTER_API_KEY')
FLUTTERWAVE_CLIENT_ID = os.getenv('FLUTTERWAVE_CLIENT_ID')
FLUTTERWAVE_SECRET = os.getenv('FLUTTERWAVE_SECRET')
FLUTTERWAVE_ENCRYPTION_KEY = os.getenv('FLUTTERWAVE_ENCRYPTION_KEY')

# Simple in-memory tiers for prototype/testing. In real deployment, remove this.
MOCK_TIERS = {
    # user_id: tier
    'user_free': 'free',
    'user_pro': 'pro',
    'user_master': 'master'
}


def get_user_tier(user_id: str) -> Literal['free', 'pro', 'master']:
    """Return subscription tier for a user.

    Order of resolution:
      1. If Supabase is configured, fetch user profile and return stored tier (TODO)
      2. Else, return from MOCK_TIERS or 'free' by default
    """
    # TODO: implement Supabase lookup when keys provided
    if not user_id:
        return 'free'

    tier = MOCK_TIERS.get(user_id)
    if tier:
        return tier
    return 'free'


def is_premium(user_id: str) -> bool:
    return get_user_tier(user_id) in ('pro', 'master')


def is_master(user_id: str) -> bool:
    return get_user_tier(user_id) == 'master'


def set_mock_tier(user_id: str, tier: Literal['free', 'pro', 'master']):
    """Set the mock tier for a user (used by webhook/testing).

    This only affects the in-memory MOCK_TIERS mapping.
    """
    MOCK_TIERS[user_id] = tier


def verify_flw_webhook(raw_body: bytes, headers: dict) -> bool:
    """Verify Flutterwave webhook signature using HMAC-SHA256.

    Flutterwave sends a header `verif-hash` which is HMAC-SHA256 of the
    request body using the client secret. This function computes the HMAC and
    compares it to the header. Returns True if valid.
    """
    import hmac
    import hashlib

    secret = FLUTTERWAVE_SECRET
    if not secret:
        # No secret configured; in prototype allow the call (or return False to be strict)
        return False

    # Header name variations
    sig = None
    for key in ('verif-hash', 'verif_hash', 'verifhash', 'x-flw-signature'):
        if key in headers:
            sig = headers.get(key)
            break
        # case-insensitive
        for hkey, hval in headers.items():
            if hkey.lower() == key:
                sig = hval
                break
        if sig:
            break

    if not sig:
        return False

    if isinstance(sig, bytes):
        sig = sig.decode('utf-8')

    computed = hmac.new(secret.encode('utf-8'), raw_body, digestmod=hashlib.sha256).hexdigest()
    # Flutterwave sometimes provides uppercase hex; normalize
    return hmac.compare_digest(computed.lower(), sig.lower())


def create_flutterwave_payment_link(user_id: str, amount: float, currency: str = 'USD', redirect_url: str | None = None) -> dict:
    """Create a Flutterwave checkout/payment link for the given user.

    Returns a dict with keys: `ok`, `checkout_url`, `tx_ref` on success.
    Falls back to a mock URL if Flutterwave keys aren't configured or the request fails.
    """
    import requests
    import uuid

    if not FLUTTERWAVE_SECRET:
        # Return a mocked checkout URL for testing
        tx_ref = f"mock-{uuid.uuid4()}"
        return {"ok": True, "checkout_url": f"https://example.com/mock_checkout/{tx_ref}", "tx_ref": tx_ref}

    # Build payload for Flutterwave Payments v3
    tx_ref = f"ts-{user_id}-{uuid.uuid4()}"
    payload = {
        "tx_ref": tx_ref,
        "amount": str(amount),
        "currency": currency,
        "redirect_url": redirect_url or "",
        "payment_options": "card,ussd,banktransfer",
        "customer": {
            "email": f"{user_id}@example.com",
            "phonenumber": "",
            "name": user_id
        },
        "customizations": {
            "title": "TradeSensei AI Subscription",
            "description": f"Subscription for {user_id}"
        }
    }

    headers = {
        "Authorization": f"Bearer {FLUTTERWAVE_SECRET}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers, timeout=10)
        if r.status_code in (200, 201):
            body = r.json()
            # Response formats vary; attempt to read common fields
            data = body.get('data') or {}
            link = data.get('link') or data.get('authorization_url') or data.get('checkout_url')
            if not link:
                # Attempt common structure
                link = data.get('meta', {}).get('authorization', {}).get('redirect')
            if link:
                return {"ok": True, "checkout_url": link, "tx_ref": tx_ref}
            return {"ok": False, "error": body}
        else:
            return {"ok": False, "status_code": r.status_code, "text": r.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}

