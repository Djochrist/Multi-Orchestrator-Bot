"""Paper trader pour simulation de trading en temps réel."""

import logging
import time
from typing import Optional

from .orchestrator import TradingOrchestrator
from .adapters.mock_exchange import MockExchange
from .data_loader import generate_synthetic_data

logger = logging.getLogger(__name__)


class PaperTrader:
    """Trader en papier utilisant la stratégie sélectionnée."""

    def __init__(self, orchestrator: Optional[TradingOrchestrator] = None,
                 exchange: Optional[MockExchange] = None):
        self.orchestrator = orchestrator or TradingOrchestrator()
        self.exchange = exchange or MockExchange()
        self.current_strategy = None
        self.current_signal = 0
        self.symbol = 'BTC/USD'

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
        df = generate_synthetic_data(days=total_days, start_price=50000.0)

        position_quantity = 0.0  # Quantité détenue (positive = long, négative = short)

        for timestamp, row in df.iterrows():
            # Mettre à jour le prix actuel sur l'échange
            self.exchange.set_current_price(self.symbol, row['close'])

            # Générer le signal pour cette période
            temp_df = df.loc[:timestamp].tail(50)  # Derniers 50 points pour calcul
            signals_df = self.current_strategy.generate_signals(temp_df)
            current_signal = signals_df['signal'].iloc[-1] if not signals_df.empty else 0

            # Vérifier si le signal a changé
            if current_signal != self.current_signal:
                logger.info(f"Changement de signal à {timestamp}: {self.current_signal} -> {current_signal}")

                # Fermer position existante si nécessaire
                if position_quantity != 0:
                    side = 'sell' if position_quantity > 0 else 'buy'
                    self.exchange.place_order(self.symbol, side, abs(position_quantity), row['close'])
                    position_quantity = 0.0

                # Ouvrir nouvelle position si signal non nul
                if current_signal != 0:
                    side = 'buy' if current_signal > 0 else 'sell'
                    self.exchange.place_order(self.symbol, side, trade_quantity, row['close'])
                    position_quantity = trade_quantity if current_signal > 0 else -trade_quantity

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
                logger.info(f"Position ouverte {symbol}: {pos.quantity} @ {pos.avg_price:.2f} (PnL: {pos.pnl:.2f})")

        return {
            'final_balance': final_balance,
            'total_pnl': final_pnl,
            'orders_count': len(self.exchange.orders),
            'strategy_name': self.current_strategy.name
        }
