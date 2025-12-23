"""Interface en ligne de commande."""

import argparse
import logging
import os
import sys

from .backtest_runner import run_backtest
from .data_loader import load_recent_data
from .orchestrator import TradingOrchestrator
from .papertrader import PaperTrader


def setup_logging():
    """Configure le logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="Multi-Orchestrator Trading Bot")
    parser.add_argument("command", choices=["backtest", "papertrade"], help="Commande à exécuter")
    parser.add_argument(
        "--symbol", type=str, default="BTC-USD", help="Symbole de l'actif"
    )
    parser.add_argument(
        "--days", type=int, default=30, help="Nombre de jours de données"
    )
    parser.add_argument(
        "--quantity", type=float, default=0.01, help="Quantité à trader"
    )
    parser.add_argument(
        "--live", action="store_true", help="Mode live (désactivé pour sécurité)"
    )

    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    # Vérification du mode live
    if args.live:
        live_env = os.getenv("LIVE", "false").lower() == "true"
        if not live_env:
            logger.error("Mode LIVE requis. Définissez LIVE=true dans l'environnement.")
            sys.exit(1)
        logger.warning("MODE LIVE ACTIVE - TRADING REEL")
        # Note: Dans une vraie implémentation, remplacer MockExchange par un vrai exchange

    if args.command == "backtest":
        logger.info(f"Démarrage du backtest pour {args.symbol} sur {args.days} jours...")

        try:
            # Charger les données
            df = load_recent_data(symbol=args.symbol, days=args.days)
            logger.info(f"Données chargées: {len(df)} points")

            # Initialiser l'orchestrateur
            orchestrator = TradingOrchestrator(symbol=args.symbol, evaluation_days=args.days)

            # Sélectionner la meilleure stratégie
            best_strategy = orchestrator.select_best_strategy()

            # Exécuter le backtest
            metrics = run_backtest(best_strategy, df)

            # Afficher les résultats
            print("\n" + "="*50)
            print("📊 RAPPORT DE BACKTEST")
            print("="*50)
            print(f"📈 Symbole: {args.symbol}")
            print(f"📅 Période: {args.days} jours")
            print(f"📋 Stratégie: {best_strategy.name}")
            print()
            print(f"💰 Rendement total: {metrics['total_return']:+.3f}")
            print(f"📊 Ratio Sharpe: {metrics['sharpe']:.3f}")
            print(f"📉 Drawdown max: {metrics['max_drawdown']:.3f}")
            print(f"🔄 Nombre de trades: {metrics['trades_count']}")
            print("="*50)

        except Exception as e:
            logger.error(f"Erreur lors du backtest: {e}")
            sys.exit(1)

    elif args.command == "papertrade":
        logger.info("Démarrage du paper trading...")

        trader = PaperTrader()
        try:
            result = trader.run_simulation(days=args.days, trade_quantity=args.quantity)
            logger.info("Paper trading terminé avec succès")

            # Afficher les résultats de manière formatée
            print("\n" + "="*50)
            print("📊 RAPPORT DE PERFORMANCE - PAPER TRADING")
            print("="*50)
            print(f"💰 Balance initiale: ${result['initial_balance']:,.2f}")
            print(f"💰 Balance finale: ${result['final_balance']:,.2f}")
            print(f"📈 PnL total: ${result['total_pnl']:,.2f}")
            print(f"📊 Rendement total: {result['total_return_pct']:+.2f}%")
            print()
            print(f"📋 Stratégie utilisée: {result['strategy_name']}")
            print(f"🔄 Nombre d'ordres: {result['orders_count']}")
            print(f"📊 Nombre de trades: {result['trades_count']}")
            print()
            if result['trades_count'] > 0:
                print(f"🎯 Trades gagnants: {result['winning_trades']}")
                print(f"❌ Trades perdants: {result['losing_trades']}")
                print(f"🏆 Taux de réussite: {result['win_rate']:.1f}%")
                print(f"📊 PnL moyen par trade: ${result['avg_trade_pnl']:,.2f}")
            print("="*50)

        except Exception as e:
            logger.error(f"Erreur lors du paper trading: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
