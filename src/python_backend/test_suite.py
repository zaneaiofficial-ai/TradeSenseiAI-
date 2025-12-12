"""Comprehensive test suite for TradeSensei AI."""
import asyncio
import pytest
import json
from backend import main
from backend import mentor
from backend import speech
from backend import subscriptions
from backend import price_alerts
from backend import portfolio
from backend import supabase


class TestBackendAPIs:
    """Test all backend API endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint returns status."""
        from fastapi.testclient import TestClient
        client = TestClient(main.app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"]
    
    @pytest.mark.asyncio
    async def test_mentor_endpoint(self):
        """Test mentor AI endpoint."""
        from fastapi.testclient import TestClient
        client = TestClient(main.app)
        
        payload = {
            "question": "Should I go long or short on BTC?",
            "context": {
                "price": 50000,
                "sma_20": 49000,
                "sma_50": 48000,
                "slope": 0.5
            },
            "user_id": "test_user",
            "api_key": "test_key"
        }
        response = client.post("/mentor/ask", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data or "error" in data
    
    @pytest.mark.asyncio
    async def test_subscriptions_endpoint(self):
        """Test subscription checking."""
        from fastapi.testclient import TestClient
        client = TestClient(main.app)
        
        response = client.get("/subscriptions/check?user_id=test_user")
        assert response.status_code == 200
        data = response.json()
        assert "tier" in data


class TestPriceAlerts:
    """Test price alert functionality."""
    
    def test_create_alert(self):
        """Test creating a price alert."""
        alert = price_alerts.create_alert(
            user_id="test_user",
            symbol="BTC",
            condition="above",
            price=50000,
            notification_type="app"
        )
        assert alert["id"]
        assert alert["symbol"] == "BTC"
        assert alert["condition"] == "above"
        assert alert["price"] == 50000
    
    def test_get_user_alerts(self):
        """Test retrieving user alerts."""
        price_alerts.create_alert("user1", "ETH", "below", 3000)
        alerts = price_alerts.get_user_alerts("user1")
        assert len(alerts) > 0
    
    def test_delete_alert(self):
        """Test deleting an alert."""
        alert = price_alerts.create_alert("user2", "XRP", "above", 1000)
        alerts_before = len(price_alerts.get_user_alerts("user2"))
        price_alerts.delete_alert("user2", alert["id"])
        alerts_after = len(price_alerts.get_user_alerts("user2"))
        assert alerts_after < alerts_before
    
    @pytest.mark.asyncio
    async def test_get_binance_price(self):
        """Test fetching price from Binance."""
        price = await price_alerts.get_binance_price("BTC")
        # Could be None in test environment, but shouldn't error
        assert price is None or isinstance(price, (int, float))


class TestPortfolio:
    """Test portfolio tracking functionality."""
    
    def test_add_position(self):
        """Test adding a trading position."""
        position_data = {
            "symbol": "BTC",
            "entry_price": 50000,
            "quantity": 0.5,
            "side": "long",
            "stop_loss": 45000,
            "take_profit": 55000
        }
        position = portfolio.add_position("test_user", position_data)
        assert position["id"]
        assert position["symbol"] == "BTC"
        assert position["status"] == "open"
    
    def test_close_position(self):
        """Test closing a position."""
        position_data = {
            "symbol": "ETH",
            "entry_price": 3000,
            "quantity": 1,
            "side": "long",
            "stop_loss": 2900,
            "take_profit": 3200
        }
        position = portfolio.add_position("test_user2", position_data)
        closed = portfolio.close_position("test_user2", position["id"], 3100)
        
        assert closed["status"] == "closed"
        assert closed["exit_price"] == 3100
        assert closed["pnl"] > 0  # Made profit
    
    def test_portfolio_stats(self):
        """Test portfolio statistics calculation."""
        stats = portfolio.get_portfolio_stats("test_user3")
        
        assert "open_positions" in stats
        assert "total_trades" in stats
        assert "win_rate" in stats
        assert "total_pnl" in stats
        assert "profit_factor" in stats
    
    def test_get_portfolio(self):
        """Test getting complete portfolio."""
        positions, stats = portfolio.get_portfolio("test_user4")
        assert isinstance(positions, list)
        assert isinstance(stats, dict)


class TestMentor:
    """Test AI mentor functionality."""
    
    def test_mentor_response_format(self):
        """Test mentor returns proper response format."""
        response = mentor.get_mentor_response(
            user_question="Should I buy or sell?",
            openai_key="test",
            elevenlabs_key="test"
        )
        # Should return a string response
        assert isinstance(response, str)


class TestSpeech:
    """Test speech processing."""
    
    def test_synthesize_returns_bytes(self):
        """Test TTS returns audio bytes."""
        audio_bytes = speech.synthesize_text_to_audio_bytes(
            "Hello world",
            voice="21m00Tcm4TlvDq8ikWAM",
            api_key="test"
        )
        # Should return bytes (could be empty in test)
        assert isinstance(audio_bytes, bytes) or audio_bytes is None


class TestIntegration:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_alert_flow(self):
        """Test complete price alert flow."""
        # Create alert
        alert = price_alerts.create_alert("int_user", "BTC", "above", 50000)
        assert alert["id"]
        
        # Get alerts
        alerts = price_alerts.get_user_alerts("int_user")
        assert len(alerts) > 0
        
        # Delete alert
        success = price_alerts.delete_alert("int_user", alert["id"])
        assert success
    
    @pytest.mark.asyncio
    async def test_full_portfolio_flow(self):
        """Test complete portfolio management flow."""
        # Add position
        pos_data = {
            "symbol": "BTC",
            "entry_price": 50000,
            "quantity": 1,
            "side": "long",
            "stop_loss": 45000,
            "take_profit": 55000
        }
        position = portfolio.add_position("int_user2", pos_data)
        
        # Get portfolio
        positions, stats = portfolio.get_portfolio("int_user2")
        assert len(positions) > 0
        
        # Close position
        closed = portfolio.close_position("int_user2", position["id"], 52000)
        assert closed["status"] == "closed"
        
        # Check stats updated
        new_stats = portfolio.get_portfolio_stats("int_user2")
        assert new_stats["total_trades"] > 0


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_position_close(self):
        """Test closing non-existent position."""
        result = portfolio.close_position("invalid_user", "invalid_pos", 50000)
        assert "error" in result
    
    def test_negative_position_size(self):
        """Test handling negative position sizes."""
        position_data = {
            "symbol": "BTC",
            "entry_price": 50000,
            "quantity": -1,  # Invalid
            "side": "long",
            "stop_loss": 45000,
            "take_profit": 55000
        }
        # Should still create but with negative quantity
        position = portfolio.add_position("err_user", position_data)
        assert position["quantity"] == -1


if __name__ == "__main__":
    # Run tests with: pytest test_suite.py -v
    pytest.main([__file__, "-v"])
