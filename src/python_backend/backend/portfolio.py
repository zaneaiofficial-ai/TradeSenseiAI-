"""Portfolio tracking and position management."""
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from . import supabase

# In-memory portfolio storage
portfolios: Dict[str, List[Dict]] = {}
closed_positions: Dict[str, List[Dict]] = {}


def add_position(user_id: str, position_data: Dict) -> Dict:
    """
    Add a new trading position.
    
    Args:
        user_id: User identifier
        position_data: {
            'symbol': 'BTC',
            'entry_price': 50000,
            'quantity': 0.5,
            'side': 'long' or 'short',
            'stop_loss': 45000,
            'take_profit': 55000,
            'entry_time': datetime or None (auto-filled)
        }
    
    Returns:
        Position with ID and metadata
    """
    position_id = f"{user_id}_{position_data['symbol']}_{datetime.now().timestamp()}"
    
    position = {
        'id': position_id,
        'user_id': user_id,
        'symbol': position_data.get('symbol'),
        'entry_price': position_data.get('entry_price'),
        'quantity': position_data.get('quantity'),
        'side': position_data.get('side', 'long'),
        'stop_loss': position_data.get('stop_loss'),
        'take_profit': position_data.get('take_profit'),
        'entry_time': position_data.get('entry_time') or datetime.now().isoformat(),
        'status': 'open',
        'exit_price': None,
        'exit_time': None,
        'pnl': None,
        'pnl_percent': None,
    }
    
    # Store in memory
    if user_id not in portfolios:
        portfolios[user_id] = []
    portfolios[user_id].append(position)
    
    # Persist to database
    try:
        supabase.save_position(position)
    except Exception as e:
        print(f"Error saving position: {e}")
    
    return position


def close_position(user_id: str, position_id: str, exit_price: float) -> Dict:
    """Close an open position."""
    if user_id not in portfolios:
        return {'error': 'No positions found'}
    
    position = None
    for p in portfolios[user_id]:
        if p['id'] == position_id:
            position = p
            break
    
    if not position:
        return {'error': 'Position not found'}
    
    # Calculate P&L
    quantity = position['quantity']
    entry_price = position['entry_price']
    side = position['side']
    
    if side == 'long':
        pnl = (exit_price - entry_price) * quantity
        pnl_percent = ((exit_price - entry_price) / entry_price) * 100
    else:  # short
        pnl = (entry_price - exit_price) * quantity
        pnl_percent = ((entry_price - exit_price) / entry_price) * 100
    
    position['exit_price'] = exit_price
    position['exit_time'] = datetime.now().isoformat()
    position['pnl'] = pnl
    position['pnl_percent'] = pnl_percent
    position['status'] = 'closed'
    
    # Move to closed positions
    portfolios[user_id].remove(position)
    if user_id not in closed_positions:
        closed_positions[user_id] = []
    closed_positions[user_id].append(position)
    
    # Update database
    try:
        supabase.close_position(position_id, exit_price)
    except Exception as e:
        print(f"Error closing position: {e}")
    
    return position


def get_portfolio(user_id: str) -> Tuple[List[Dict], Dict]:
    """
    Get complete portfolio for a user.
    
    Returns:
        (open_positions, portfolio_stats)
    """
    open_positions = portfolios.get(user_id, [])
    stats = get_portfolio_stats(user_id)
    return open_positions, stats


def get_portfolio_stats(user_id: str) -> Dict:
    """Calculate portfolio statistics."""
    open_positions = portfolios.get(user_id, [])
    closed_pos = closed_positions.get(user_id, [])
    
    # Open position stats
    total_exposure = sum(p['entry_price'] * p['quantity'] for p in open_positions)
    long_count = len([p for p in open_positions if p['side'] == 'long'])
    short_count = len([p for p in open_positions if p['side'] == 'short'])
    
    # Closed position stats
    total_trades = len(closed_pos)
    winning_trades = len([p for p in closed_pos if p['pnl'] and p['pnl'] > 0])
    losing_trades = len([p for p in closed_pos if p['pnl'] and p['pnl'] < 0])
    
    total_pnl = sum(p['pnl'] for p in closed_pos if p['pnl'])
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    avg_win = (sum(p['pnl'] for p in closed_pos if p['pnl'] and p['pnl'] > 0) / winning_trades) if winning_trades > 0 else 0
    avg_loss = (sum(p['pnl'] for p in closed_pos if p['pnl'] and p['pnl'] < 0) / losing_trades) if losing_trades > 0 else 0
    
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    
    return {
        'open_positions': len(open_positions),
        'long_positions': long_count,
        'short_positions': short_count,
        'total_exposure': total_exposure,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
    }


def get_position(user_id: str, position_id: str) -> Optional[Dict]:
    """Get a specific position."""
    if user_id in portfolios:
        for p in portfolios[user_id]:
            if p['id'] == position_id:
                return p
    
    if user_id in closed_positions:
        for p in closed_positions[user_id]:
            if p['id'] == position_id:
                return p
    
    return None


def update_position_sl_tp(user_id: str, position_id: str, stop_loss: float = None, take_profit: float = None) -> Optional[Dict]:
    """Update stop loss and/or take profit for a position."""
    position = get_position(user_id, position_id)
    if not position:
        return None
    
    if stop_loss:
        position['stop_loss'] = stop_loss
    if take_profit:
        position['take_profit'] = take_profit
    
    try:
        supabase.update_position(position_id, position)
    except Exception as e:
        print(f"Error updating position: {e}")
    
    return position


def initialize_portfolio_from_db(user_id: str):
    """Load portfolio from database on user login."""
    try:
        positions = supabase.get_user_positions(user_id)
        portfolios[user_id] = [p for p in positions if p.get('status') == 'open']
        closed_positions[user_id] = [p for p in positions if p.get('status') == 'closed']
    except Exception as e:
        print(f"Error loading portfolio from database: {e}")
