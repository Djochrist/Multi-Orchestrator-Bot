"""Tests pour le paper trader."""

import pytest

from orchestrator.adapters.mock_exchange import MockExchange
from orchestrator.orchestrator import TradingOrchestrator
from orchestrator.papertrader import PaperTrader


class TestPaperTrader:
    """Tests pour le paper trader."""

    def test_papertrader_initialization(self):
        """Test d'initialisation du paper trader."""
        trader = PaperTrader()
        assert trader.orchestrator is not None
        assert trader.exchange is not None
        assert trader.current_strategy is None
        assert trader.current_signal == 0

    def test_papertrader_with_custom_components(self):
        """Test avec composants personnalisés."""
        orchestrator = TradingOrchestrator()
        exchange = MockExchange(initial_balance=5000.0)

        trader = PaperTrader(orchestrator=orchestrator, exchange=exchange)

        assert trader.orchestrator is orchestrator
        assert trader.exchange is exchange
        assert trader.exchange.get_balance() == 5000.0

    def test_initialize_selects_strategy(self):
        """Test que initialize sélectionne une stratégie."""
        trader = PaperTrader()
        trader.initialize()

        assert trader.current_strategy is not None
        assert trader.current_strategy.name

    def test_run_simulation_basic(self):
        """Test de base de la simulation."""
        trader = PaperTrader()
        trader.initialize()

        result = trader.run_simulation(days=5, trade_quantity=0.001)

        # Vérifier les clés du résultat
        expected_keys = {"final_balance", "total_pnl", "orders_count", "strategy_name"}
        assert set(result.keys()) == expected_keys

        # Vérifier les types
        assert isinstance(result["final_balance"], float)
        assert isinstance(result["total_pnl"], float)
        assert isinstance(result["orders_count"], int)
        assert isinstance(result["strategy_name"], str)

        # Vérifier que le nom de stratégie correspond
        assert result["strategy_name"] == trader.current_strategy.name

    def test_run_simulation_no_crash(self):
        """Test que la simulation ne crash pas."""
        trader = PaperTrader()

        # Ne pas appeler initialize pour tester le comportement par défaut
        result = trader.run_simulation(days=3)

        assert "final_balance" in result
        assert "total_pnl" in result
        assert "orders_count" in result
        assert "strategy_name" in result

    def test_exchange_interaction(self):
        """Test de l'interaction avec l'échange."""
        exchange = MockExchange(initial_balance=1000.0)
        trader = PaperTrader(exchange=exchange)

        # Vérifier le balance initial
        assert trader.exchange.get_balance() == 1000.0

        # Après simulation, le balance peut changer
        trader.initialize()
        result = trader.run_simulation(days=2)

        # Le balance final devrait être différent ou identique selon les trades
        assert isinstance(result["final_balance"], (int, float))
