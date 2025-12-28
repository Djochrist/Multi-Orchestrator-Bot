"""
Tests unitaires pour les modèles
"""

import pytest
from datetime import datetime, timezone

from src.models import Strategy, Trade, BaseModel


class TestBaseModel:
    """Tests pour BaseModel"""

    def test_base_model_creation(self):
        """Test création d'un modèle de base"""
        model = BaseModel()
        assert model.id > 0
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)

    def test_to_dict(self):
        """Test conversion en dictionnaire"""
        model = BaseModel()
        data = model.to_dict()
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_update(self):
        """Test mise à jour"""
        model = BaseModel()
        original_time = model.updated_at

        model.update()
        assert model.updated_at > original_time


class TestStrategyModel:
    """Tests pour Strategy"""

    def test_strategy_creation(self):
        """Test création d'une stratégie"""
        strategy = Strategy(
            name="Test Strategy",
            description="Description test",
            type="rsi",
            config={"period": 14}
        )

        assert strategy.name == "Test Strategy"
        assert strategy.type == "rsi"
        assert strategy.status == "inactive"
        assert not strategy.is_active()

    def test_strategy_activation(self):
        """Test activation/désactivation"""
        strategy = Strategy(name="Test", type="rsi")

        assert not strategy.is_active()
        strategy.activate()
        assert strategy.is_active()
        assert strategy.status == "active"

        strategy.deactivate()
        assert not strategy.is_active()
        assert strategy.status == "inactive"

    def test_strategy_performance(self):
        """Test gestion des performances"""
        strategy = Strategy(name="Test", type="rsi")

        strategy.update_performance(pnl=1000.0, win_rate=75.0)
        assert strategy.total_pnl == 1000.0
        assert strategy.win_rate == 75.0


class TestTradeModel:
    """Tests pour Trade"""

    def test_trade_creation(self):
        """Test création d'un trade"""
        trade = Trade(
            symbol="BTC",
            side="buy",
            quantity=0.5,
            entry_price=50000.0
        )

        assert trade.symbol == "BTC"
        assert trade.side == "buy"
        assert trade.quantity == 0.5
        assert trade.entry_price == 50000.0
        assert trade.status == "open"
        assert trade.is_open

    def test_trade_close(self):
        """Test fermeture d'un trade"""
        trade = Trade(
            symbol="BTC",
            side="buy",
            quantity=1.0,
            entry_price=50000.0
        )

        trade.close_trade(exit_price=55000.0)

        assert trade.exit_price == 55000.0
        assert trade.status == "closed"
        assert trade.pnl == 5000.0  # (55000 - 50000) * 1.0
        assert trade.is_closed

    def test_trade_cancel(self):
        """Test annulation d'un trade"""
        trade = Trade(symbol="BTC", side="buy", quantity=1.0, entry_price=50000.0)

        trade.cancel_trade()

        assert trade.status == "cancelled"
        assert trade.exit_time is not None

    def test_sell_trade_pnl(self):
        """Test PnL pour un trade de vente"""
        trade = Trade(
            symbol="BTC",
            side="sell",
            quantity=1.0,
            entry_price=55000.0
        )

        trade.close_trade(exit_price=50000.0)

        assert trade.pnl == 5000.0  # (55000 - 50000) * 1.0
