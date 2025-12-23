"""Interface en ligne de commande."""

import argparse
import logging
import os
import sys

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
    parser.add_argument("command", choices=["papertrade"], help="Commande à exécuter")
    parser.add_argument(
        "--days", type=int, default=10, help="Nombre de jours pour la simulation"
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

    if args.command == "papertrade":
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
