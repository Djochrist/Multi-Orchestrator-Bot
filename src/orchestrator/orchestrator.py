"""Orchestrateur principal pour sélection de stratégie."""

import logging
from typing import List, Tuple

from .adapters.advanced_strategies import (
    BreakoutRetestStrategy,
    FibonacciRetracementStrategy,
    OrderFlowImbalanceStrategy,
    RiskRewardEnhancedStrategy
)
from .backtest_runner import run_backtest
from .data_loader import load_recent_data
from .strategy_interface import StrategyAdapter

logger = logging.getLogger(__name__)


class TradingOrchestrator:
    """Orchestrateur pour sélectionner la meilleure stratégie."""

    def __init__(self):
        self.strategies = [
            BreakoutRetestStrategy(),
            FibonacciRetracementStrategy(),
            OrderFlowImbalanceStrategy(),
            RiskRewardEnhancedStrategy()
        ]

    def select_best_strategy(self) -> StrategyAdapter:
        """Sélectionne la meilleure stratégie basée sur les métriques de backtest.

        Critères de sélection (par ordre de priorité):
        1. Sharpe ratio maximum
        2. Retour total maximum
        3. Drawdown maximum minimum (moins négatif)

        Returns:
            La stratégie sélectionnée
        """
        # Charger les données récentes (30 jours)
        df = load_recent_data(days=30)
        logger.info(
            f"Évaluation de {len(self.strategies)} stratégies sur {len(df)} points de données"
        )

        # Évaluer chaque stratégie
        results = []
        for strategy in self.strategies:
            metrics = run_backtest(strategy, df)
            results.append((strategy, metrics))
            logger.info(
                f"Stratégie {strategy.name}: Sharpe={metrics['sharpe']:.3f}, "
                f"Return={metrics['total_return']:.3f}, "
                f"Drawdown={metrics['max_drawdown']:.3f}, "
                f"Trades={metrics['trades_count']}"
            )

        # Trier selon les critères
        # 1. Sharpe max, 2. Return max, 3. Drawdown min (moins négatif = meilleur)
        results.sort(
            key=lambda x: (
                -x[1]["sharpe"],  # négatif pour descending
                -x[1]["total_return"],
                -x[1]["max_drawdown"],  # négatif car drawdown est négatif
            )
        )

        best_strategy = results[0][0]
        logger.info(f"Stratégie sélectionnée: {best_strategy.name}")

        return best_strategy

    def get_all_strategies(self) -> List[StrategyAdapter]:
        """Retourne toutes les stratégies disponibles."""
        return self.strategies.copy()
