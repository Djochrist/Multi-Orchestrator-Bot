"""Paper trader pour simulation de trading en temps réel."""

import logging
import time
from typing import Optional

from .adapters.mock_exchange import MockExchange
from .data_loader import download_market_data
from .orchestrator import TradingOrchestrator

logger = logging.getLogger(__name__)


class PaperTrader:
    """Trader en papier utilisant la stratégie sélectionnée."""

    def __init__(
        self,
        orchestrator: Optional[TradingOrchestrator] = None,
        exchange: Optional[MockExchange] = None,
    ):
        self.orchestrator = orchestrator or TradingOrchestrator()
        self.exchange = exchange or MockExchange()
        self.current_strategy = None
        self.current_signal = 0
        self.symbol = "BTC/USD"

    def initialize(self):
        """Initialise le trader en sélectionnant la meilleure stratégie."""
        logger.info("Initialisation du paper trader...")
        self.current_strategy = self.orchestrator.select_best_strategy()
        logger.info(f"Stratégie sélectionnée: {self.current_strategy.name}")

    def run_simulation(self, days: int = 10, trade_quantity: float = 0.01):
        """Exécute une simulation de trading.

        Args:
            days: Nombre de jours à simuler
            trade_quantity: Quantité à trader par ordre
        """
        if not self.current_strategy:
            self.initialize()

        logger.info(f"Démarrage de la simulation sur {days} jours")

        # Générer des données de simulation avec suffisamment d'historique pour les moyennes
        # Les stratégies ont besoin d'au moins 50 points pour SMA/EMA 50
        min_history = 60
        total_days = max(days, min_history)
        df = download_market_data(symbol="BTC-USD", days=total_days)

        position_quantity = 0.0  # Quantité détenue (positive = long, négative = short)

        for timestamp, row in df.iterrows():
            # Mettre à jour le prix actuel sur l'échange
            self.exchange.set_current_price(self.symbol, row["close"])

            # Générer le signal pour cette période
            temp_df = df.loc[:timestamp].tail(50)  # Derniers 50 points pour calcul
            signals_df = self.current_strategy.generate_signals(temp_df)
            current_signal = (
                signals_df["signal"].iloc[-1] if not signals_df.empty else 0
            )

            # Vérifier si le signal a changé
            if current_signal != self.current_signal:
                logger.info(
                    f"Changement de signal à {timestamp}: {self.current_signal} -> {current_signal}"
                )

                # Fermer position existante si nécessaire
                if position_quantity != 0:
                    side = "sell" if position_quantity > 0 else "buy"
                    self.exchange.place_order(
                        self.symbol, side, abs(position_quantity), row["close"]
                    )
                    position_quantity = 0.0

                # Ouvrir nouvelle position si signal non nul
                if current_signal != 0:
                    side = "buy" if current_signal > 0 else "sell"
                    self.exchange.place_order(
                        self.symbol, side, trade_quantity, row["close"]
                    )
                    position_quantity = (
                        trade_quantity if current_signal > 0 else -trade_quantity
                    )

                self.current_signal = current_signal

            # Log périodique
            if timestamp.hour == 0:  # Minuit
                pnl = self.exchange.get_total_pnl()
                balance = self.exchange.get_balance()
                logger.info(f"{timestamp.date()}: Balance={balance:.2f}, PnL={pnl:.2f}")

        # Rapport final
        final_pnl = self.exchange.get_total_pnl()
        final_balance = self.exchange.get_balance()
        positions = self.exchange.get_positions()

        logger.info("=== RAPPORT FINAL ===")
        logger.info(f"Balance finale: {final_balance:.2f}")
        logger.info(f"PnL total: {final_pnl:.2f}")
        logger.info(f"Stratégie utilisée: {self.current_strategy.name}")
        logger.info(f"Nombre d'ordres: {len(self.exchange.orders)}")

        for symbol, pos in positions.items():
            if pos.quantity != 0:
                logger.info(
                    f"Position ouverte {symbol}: {pos.quantity} @ {pos.avg_price:.2f} (PnL: {pos.pnl:.2f})"
                )

        # Calculer des statistiques détaillées
        initial_balance = 10000.0  # Balance initiale par défaut
        total_return_pct = (final_balance - initial_balance) / initial_balance * 100

        # Analyser les trades - compter les paires ouverture/fermeture de position
        completed_trades = []
        i = 0
        while i < len(self.exchange.orders) - 1:
            current_order = self.exchange.orders[i]
            next_order = self.exchange.orders[i + 1]

            # Si c'est une ouverture de position suivie d'une fermeture
            if ((current_order.side == "buy" and next_order.side == "sell") or
                (current_order.side == "sell" and next_order.side == "buy")):

                if current_order.side == "buy":  # Long trade: buy -> sell
                    trade_pnl = (next_order.price - current_order.price) * current_order.quantity
                else:  # Short trade: sell -> buy
                    trade_pnl = (current_order.price - next_order.price) * current_order.quantity

                completed_trades.append(trade_pnl)
                i += 2  # Passer les deux ordres
            else:
                i += 1  # Avancer d'un ordre seulement

        winning_trades = sum(1 for pnl in completed_trades if pnl > 0)
        losing_trades = sum(1 for pnl in completed_trades if pnl <= 0)
        avg_trade_pnl = sum(completed_trades) / len(completed_trades) if completed_trades else 0
        win_rate = winning_trades / len(completed_trades) * 100 if completed_trades else 0

        return {
            "initial_balance": initial_balance,
            "final_balance": final_balance,
            "total_pnl": final_pnl,
            "total_return_pct": total_return_pct,
            "orders_count": len(self.exchange.orders),
            "trades_count": len(completed_trades),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "avg_trade_pnl": avg_trade_pnl,
            "strategy_name": self.current_strategy.name,
        }
