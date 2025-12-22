"""Tests pour le backtest runner."""

import pytest
import pandas as pd

from orchestrator.backtest_runner import run_backtest
from orchestrator.adapters.simple_strategies import SMACrossover
from orchestrator.data_loader import generate_synthetic_data


class TestBacktestRunner:
    """Tests pour le runner de backtests."""

    def test_run_backtest_returns_correct_metrics(self):
        """Test que run_backtest retourne les métriques attendues."""
        strategy = SMACrossover()
        df = generate_synthetic_data(days=50)

        result = run_backtest(strategy, df)

        # Vérifier les clés présentes
        expected_keys = {'total_return', 'sharpe', 'max_drawdown', 'trades_count'}
        assert set(result.keys()) == expected_keys

        # Vérifier les types
        assert isinstance(result['total_return'], float)
        assert isinstance(result['sharpe'], float)
        assert isinstance(result['max_drawdown'], float)
        assert isinstance(result['trades_count'], int)

        # Vérifier les plages raisonnables
        assert result['max_drawdown'] <= 0  # Drawdown est négatif ou nul
        assert result['trades_count'] >= 0

    def test_run_backtest_with_different_strategies(self):
        """Test avec différentes stratégies."""
        df = generate_synthetic_data(days=60)

        strategies = [
            SMACrossover(short=5, long=20),
            SMACrossover(short=10, long=30),
        ]

        for strategy in strategies:
            result = run_backtest(strategy, df)
            assert 'total_return' in result
            assert 'sharpe' in result
            assert 'max_drawdown' in result
            assert 'trades_count' in result

    def test_run_backtest_deterministic(self):
        """Test que les résultats sont déterministes."""
        strategy = SMACrossover()
        df = generate_synthetic_data(days=40, volatility=0.01)  # Faible volatilité pour stabilité

        result1 = run_backtest(strategy, df)
        result2 = run_backtest(strategy, df)

        # Les résultats devraient être identiques (même seed)
        assert result1['total_return'] == result2['total_return']
        assert result1['sharpe'] == result2['sharpe']
        assert result1['max_drawdown'] == result2['max_drawdown']
        assert result1['trades_count'] == result2['trades_count']
