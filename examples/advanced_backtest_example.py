#!/usr/bin/env python3
"""Exemple d'utilisation du backtesting avancé avec backtrader."""

import os
import sys
import logging

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from orchestrator.advanced_backtester import AdvancedBacktester

def main():
    """Fonction principale pour l'exemple de backtesting avancé."""

    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=== Backtesting Avancé Multi-Stratégies ===")
    print("Test des stratégies sur 1 an de données BTC-USD")
    print("=" * 50)

    # Créer le backtester avancé
    backtester = AdvancedBacktester(
        symbol="BTC-USD",
        initial_cash=10000
    )

    # Exécuter les backtests sur 1 an
    results = backtester.run_all_strategies(years=1)

    print("\n" + "=" * 60)
    print("RÉSULTATS DU BACKTESTING SUR 1 AN")
    print("=" * 60)
    print(results.to_string(index=False))

    # Sauvegarder les résultats
    results.to_csv('backtest_results_1year.csv', index=False)
    print(f"\nRésultats sauvegardés dans: backtest_results_1year.csv")

    # Créer les graphiques de comparaison
    try:
        backtester.plot_comparison(results, save_path='strategy_comparison_1year.png')
        print("Graphiques sauvegardés dans: strategy_comparison_1year.png")
    except Exception as e:
        print(f"Erreur lors de la création des graphiques: {e}")

    # Analyse détaillée
    print("\n" + "=" * 40)
    print("ANALYSE DÉTAILLÉE")
    print("=" * 40)

    # Identifier la meilleure stratégie selon différents critères
    best_by_sharpe = results.loc[results['Sharpe Ratio'].idxmax()]
    best_by_return = results.loc[results['Total Return (%)'].idxmax()]
    best_by_winrate = results.loc[results['Win Rate (%)'].idxmax()]

    print(f"Meilleure selon Sharpe Ratio: {best_by_sharpe['Strategy']} ({best_by_sharpe['Sharpe Ratio']:.3f})")
    print(f"Meilleure selon Rendement: {best_by_return['Strategy']} ({best_by_return['Total Return (%)']:.2f}%)")
    print(f"Meilleure selon Win Rate: {best_by_winrate['Strategy']} ({best_by_winrate['Win Rate (%)']:.1f}%)")

    # Statistiques générales
    print("\nSTATISTIQUES GENERALES:")
    print(f"   • Nombre total de stratégies testées: {len(results)}")
    print(f"   • Capital initial: ${backtester.initial_cash:,.0f}")
    print(f"   • Période de test: 1 an")
    print(f"   • Symbole: {backtester.symbol}")

    # Performance moyenne
    avg_return = results['Total Return (%)'].mean()
    avg_sharpe = results['Sharpe Ratio'].mean()
    avg_winrate = results['Win Rate (%)'].mean()

    print("\nPERFORMANCES MOYENNES:")
    print(f"   • Rendement moyen: {avg_return:.2f}%")
    print(f"   • Sharpe Ratio moyen: {avg_sharpe:.3f}")
    print(f"   • Win Rate moyen: {avg_winrate:.1f}%")

    # Recommandations
    print("\nRECOMMANDATIONS:")
    if best_by_sharpe['Sharpe Ratio'] > 1.0:
        print(f"   La stratégie {best_by_sharpe['Strategy']} montre un excellent ratio risque/rendement")
    else:
        print("   Aucune stratégie ne montre un Sharpe Ratio supérieur à 1.0")

    profitable_strategies = results[results['Total Return (%)'] > 0]
    if len(profitable_strategies) > 0:
        print(f"   {len(profitable_strategies)} stratégie(s) sur {len(results)} sont rentables")
    else:
        print("   Aucune stratégie n'est rentable sur la période testée")

    print("\nPROCHAINES ETAPES:")
    print("   • Optimiser les paramètres des stratégies performantes")
    print("   • Tester sur d'autres marchés (ETH, altcoins, indices)")
    print("   • Implémenter des règles de money management avancées")
    print("   • Backtester sur plusieurs années pour la robustesse")


if __name__ == "__main__":
    main()
