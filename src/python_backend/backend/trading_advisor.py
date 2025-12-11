"""Simple rule-based trading advisor prototype.

This module demonstrates how the backend could generate BUY/SELL trade suggestions
based on vision features. It's intentionally simple and deterministic/randomized
for prototype purposes. Replace with GPT/OpenAI-driven logic for production.
"""
import random
from typing import Optional, Dict, Any


def evaluate(features: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Evaluate chart features and optionally return a trade signal.

    Returns a dict like:
    {
      'side': 'BUY'|'SELL',
      'price': 1234.56,
      'sl': 1230.0,
      'tp1': 1240.0,
      'reason': 'POI + momentum'
    }

    For the prototype, generate a signal randomly about 10% of the time.
    """
    # Use the richer features to produce a deterministic prototype signal.
    price_series = features.get('price_series') or []
    poi = features.get('poi')
    if not price_series or not poi:
        return None

    slope = features.get('slope', 0.0)
    sma_short = features.get('sma_short') or []
    sma_long = features.get('sma_long') or []

    # Heuristic: if short SMA exists and is above long SMA and slope positive -> BUY
    # if short SMA below long SMA and slope negative -> SELL
    side = None
    try:
        if sma_short and sma_long:
            last_short = sma_short[-1]
            last_long = sma_long[-1]
            if last_short < last_long and slope < -0.2:
                side = 'SELL'
            elif last_short > last_long and slope > 0.2:
                side = 'BUY'
        else:
            # Fallback: use slope only
            if slope > 0.8:
                side = 'BUY'
            elif slope < -0.8:
                side = 'SELL'
    except Exception:
        return None

    # Very small chance to avoid spamming signals
    if side is None or random.random() > 0.35:
        return None

    x, y = poi
    # Map screen y to a mock price (prototype only)
    # Higher y (lower on screen) -> lower price
    height = max(price_series) if price_series else 100
    last_y = y
    base_price = 1000.0 + (height - last_y) * 0.5

    # Position sizing and risk (prototype): SL 0.2% away, TP1 0.6% away
    sl = round(base_price * (1 - 0.002) if side == 'BUY' else base_price * (1 + 0.002), 2)
    tp1 = round(base_price * (1 + 0.006) if side == 'BUY' else base_price * (1 - 0.006), 2)

    signal = {
        'side': side,
        'price': round(base_price, 2),
        'sl': sl,
        'tp1': tp1,
        'reason': 'Prototype SMA crossover + slope'
    }
    return signal
