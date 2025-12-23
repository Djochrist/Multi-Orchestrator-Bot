"""Tests pour l'orchestrateur."""

import pytest

from orchestrator.adapters.advanced_strategies import (
    BearMarketMomentumStrategy,
    MeanReversionBearStrategy,
    OrderFlowImbalanceStrategy,
)
from orchestrator.orchestrator import TradingOrchestrator


class TestTradingOrchestrator:
    """Tests pour l'orchestrateur de trading."""

    def test_orchestrator_initialization(self):
        """Test d'initialisation de l'orchestrateur."""
        orchestrator = TradingOrchestrator()
        assert len(orchestrator.strategies) == 3
        assert isinstance(orchestrator.strategies[0], BearMarketMomentumStrategy)
        assert isinstance(orchestrator.strategies[1], MeanReversionBearStrategy)
        assert isinstance(orchestrator.strategies[2], OrderFlowImbalanceStrategy)

    def test_select_best_strategy(self):
        """Test de sélection de la meilleure stratégie."""
        orchestrator = TradingOrchestrator()
        best_strategy = orchestrator.select_best_strategy()

        # Vérifier que la stratégie sélectionnée est dans la liste
        assert best_strategy in orchestrator.strategies

        # Vérifier que la stratégie a un nom
        assert hasattr(best_strategy, "name")
        assert best_strategy.name

    def test_get_all_strategies(self):
        """Test de récupération de toutes les stratégies."""
        orchestrator = TradingOrchestrator()
        strategies = orchestrator.get_all_strategies()

        assert len(strategies) == 3
        assert strategies is not orchestrator.strategies  # Copie, pas référence
