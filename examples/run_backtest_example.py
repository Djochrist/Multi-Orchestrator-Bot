#!/usr/bin/env python3
"""Exemple d'exécution d'un backtest."""

import os
import sys

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from orchestrator.backtest_runner import run_backtest
from orchestrator.data_loader import generate_synthetic_data
from orchestrator.orchestrator import TradingOrchestrator


def main():
    """Fonction principale pour l'exemple de backtest."""
    print("=== Exemple de Backtest Multi-Stratégies ===\n")

    # Créer l'orchestrateur
    orchestrator = TradingOrchestrator()

    # Charger des données de test
    print("Génération des données de test...")
    df = generate_synthetic_data(days=100, start_price=50000.0, volatility=0.02)
    print(f"Données générées: {len(df)} points de données")
    print(f"Prix initial: ${df['close'].iloc[0]:.2f}")
    print(f"Prix final: ${df['close'].iloc[-1]:.2f}")
    print(
        f"Rendement total du marché: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%\n"
    )

    # Tester chaque stratégie individuellement
    print("Évaluation individuelle des stratégies:")
    print("-" * 50)

    for strategy in orchestrator.get_all_strategies():
        metrics = run_backtest(strategy, df)

        print(f"Stratégie: {strategy.name}")
        print(f"  Rendement total: {metrics['total_return']:.3f}")
        print(f"  Ratio Sharpe: {metrics['sharpe']:.3f}")
        print(f"  Max Drawdown: {metrics['max_drawdown']:.3f}")
        print(f"  Nombre de trades: {metrics['trades_count']}")
        print()

    # Sélectionner la meilleure stratégie
    print("Sélection de la meilleure stratégie:")
    print("-" * 50)

    best_strategy = orchestrator.select_best_strategy()
    best_metrics = run_backtest(best_strategy, df)

    print(f"Strategie selectionnee: {best_strategy.name}")
    print(f"  Rendement total: {best_metrics['total_return']:.3f}")
    print(f"  Ratio Sharpe: {best_metrics['sharpe']:.3f}")
    print(f"  Max Drawdown: {best_metrics['max_drawdown']:.3f}")
    print(f"Nombre de trades: {best_metrics['trades_count']}")
    print()

    # Resume
    print("=== Resume ===")
    print("Backtest termine avec succes")
    print(f"{len(orchestrator.get_all_strategies())} strategies evaluees")
    print("Selection deterministe basee sur Sharpe > Return > Drawdown")
    print("\nNote: Ces résultats sont basés sur des données synthétiques.")
    print("Dans un environnement réel, utilisez des données historiques authentiques.")


if __name__ == "__main__":
    main()
