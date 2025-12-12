"""Real-time price alerts and price feed management."""
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import aiohttp
from . import supabase

# In-memory price cache and active alerts
price_cache: Dict[str, float] = {}
active_alerts: Dict[str, List[Dict]] = {}
price_feed_tasks = {}


async def get_binance_price(symbol: str) -> Optional[float]:
    """Fetch current price from Binance."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    price = float(data['price'])
                    price_cache[symbol] = price
                    return price
    except Exception as e:
        print(f"Error fetching {symbol} price: {e}")
    return price_cache.get(symbol)


async def get_coinmarketcap_price(symbol: str, api_key: str) -> Optional[float]:
    """Fetch price from CoinMarketCap."""
    try:
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': api_key,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
                params={'symbol': symbol, 'convert': 'USD'},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    price = data['data'][symbol]['quote']['USD']['price']
                    price_cache[symbol] = price
                    return price
    except Exception as e:
        print(f"Error fetching {symbol} price from CMC: {e}")
    return price_cache.get(symbol)


def create_alert(user_id: str, symbol: str, condition: str, price: float, notification_type: str = "email") -> Dict:
    """
    Create a new price alert.
    
    Args:
        user_id: User identifier
        symbol: Trading pair (e.g., 'BTC', 'ETH')
        condition: 'above' or 'below'
        price: Trigger price level
        notification_type: 'email', 'sms', 'app'
    
    Returns:
        Alert ID and metadata
    """
    alert_id = f"{user_id}_{symbol}_{condition}_{datetime.now().timestamp()}"
    alert = {
        'id': alert_id,
        'user_id': user_id,
        'symbol': symbol,
        'condition': condition,
        'price': price,
        'notification_type': notification_type,
        'created_at': datetime.now().isoformat(),
        'triggered': False,
        'triggered_at': None,
        'triggered_price': None,
    }
    
    # Store in memory
    if user_id not in active_alerts:
        active_alerts[user_id] = []
    active_alerts[user_id].append(alert)
    
    # Persist to database
    try:
        supabase.save_alert(alert)
    except Exception as e:
        print(f"Error saving alert to database: {e}")
    
    return alert


def delete_alert(user_id: str, alert_id: str) -> bool:
    """Delete an alert."""
    if user_id in active_alerts:
        active_alerts[user_id] = [a for a in active_alerts[user_id] if a['id'] != alert_id]
        try:
            supabase.delete_alert(alert_id)
        except Exception:
            pass
        return True
    return False


async def check_alerts() -> List[Dict]:
    """Check all active alerts and return triggered ones."""
    triggered = []
    
    for user_id, alerts in active_alerts.items():
        for alert in alerts:
            if alert['triggered']:
                continue
            
            symbol = alert['symbol']
            current_price = await get_binance_price(symbol)
            
            if current_price is None:
                continue
            
            target_price = alert['price']
            condition = alert['condition']
            
            # Check if condition is met
            if (condition == 'above' and current_price >= target_price) or \
               (condition == 'below' and current_price <= target_price):
                alert['triggered'] = True
                alert['triggered_at'] = datetime.now().isoformat()
                alert['triggered_price'] = current_price
                triggered.append({
                    'user_id': user_id,
                    'alert_id': alert['id'],
                    'symbol': symbol,
                    'condition': condition,
                    'target_price': target_price,
                    'current_price': current_price,
                    'notification_type': alert['notification_type'],
                })
    
    return triggered


async def start_price_monitor(check_interval: int = 60):
    """Start background price monitoring task."""
    while True:
        try:
            triggered = await check_alerts()
            for trigger in triggered:
                await send_notification(trigger)
        except Exception as e:
            print(f"Error in price monitor: {e}")
        
        await asyncio.sleep(check_interval)


async def send_notification(trigger: Dict):
    """Send notification for triggered alert."""
    notification_type = trigger.get('notification_type', 'app')
    
    if notification_type == 'email':
        await send_email_notification(trigger)
    elif notification_type == 'sms':
        await send_sms_notification(trigger)
    elif notification_type == 'app':
        await send_app_notification(trigger)


async def send_email_notification(trigger: Dict):
    """Send email notification (stub - integrate with email service)."""
    print(f"📧 Email: {trigger['symbol']} hit ${trigger['current_price']} ({trigger['condition']} ${trigger['target_price']})")


async def send_sms_notification(trigger: Dict):
    """Send SMS notification (stub - integrate with SMS service)."""
    print(f"📱 SMS: {trigger['symbol']} hit ${trigger['current_price']} ({trigger['condition']} ${trigger['target_price']})")


async def send_app_notification(trigger: Dict):
    """Send in-app notification."""
    print(f"🔔 App: {trigger['symbol']} hit ${trigger['current_price']} ({trigger['condition']} ${trigger['target_price']})")


def get_user_alerts(user_id: str) -> List[Dict]:
    """Get all alerts for a user."""
    return active_alerts.get(user_id, [])


async def initialize_alerts_from_db():
    """Load saved alerts from database on startup."""
    try:
        alerts = supabase.get_all_alerts()
        for alert in alerts:
            user_id = alert['user_id']
            if user_id not in active_alerts:
                active_alerts[user_id] = []
            active_alerts[user_id].append(alert)
    except Exception as e:
        print(f"Error loading alerts from database: {e}")
