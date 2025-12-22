"""Échange simulé pour le paper trading."""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Order:
    """Représentation d'un ordre."""
    order_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    price: float
    timestamp: datetime
    status: str = 'filled'  # 'pending', 'filled', 'cancelled'


@dataclass
class Position:
    """Représentation d'une position."""
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    pnl: float


class MockExchange:
    """Échange simulé pour les tests et paper trading."""

    def __init__(self, initial_balance: float = 10000.0):
        self.balance = initial_balance
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.order_counter = 0
        self.current_prices: Dict[str, float] = {'BTC/USD': 50000.0}  # Prix par défaut

    def set_current_price(self, symbol: str, price: float):
        """Met à jour le prix actuel pour un symbole."""
        self.current_prices[symbol] = price

    def place_order(self, symbol: str, side: str, quantity: float, price: Optional[float] = None) -> str:
        """Place un ordre (simulé comme immédiatement exécuté)."""
        if price is None:
            price = self.current_prices.get(symbol, 100.0)

        self.order_counter += 1
        order_id = f"order_{self.order_counter}"

        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            timestamp=datetime.now(),
            status='filled'
        )

        self.orders.append(order)

        # Mettre à jour la position
        self._update_position(order)

        logger.info(f"Ordre exécuté: {side} {quantity} {symbol} @ {price}")
        return order_id

    def _update_position(self, order: Order):
        """Met à jour la position après exécution d'un ordre."""
        symbol = order.symbol
        cost = order.quantity * order.price

        if symbol not in self.positions:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=0,
                avg_price=0,
                current_price=order.price,
                pnl=0
            )

        position = self.positions[symbol]

        if order.side == 'buy':
            # Calculer le nouveau prix moyen
            total_quantity = position.quantity + order.quantity
            if total_quantity > 0:
                total_cost = position.quantity * position.avg_price + cost
                position.avg_price = total_cost / total_quantity
            position.quantity = total_quantity
            self.balance -= cost
        else:  # sell
            position.quantity -= order.quantity
            self.balance += cost

            # Calculer PnL réalisé
            pnl_realized = (order.price - position.avg_price) * order.quantity
            logger.info(f"PnL réalisé: {pnl_realized:.2f}")

        # Mettre à jour le PnL non réalisé
        if position.quantity != 0:
            position.current_price = self.current_prices.get(symbol, order.price)
            position.pnl = (position.current_price - position.avg_price) * position.quantity
        else:
            position.pnl = 0

    def get_positions(self) -> Dict[str, Position]:
        """Retourne les positions actuelles."""
        return self.positions.copy()

    def get_balance(self) -> float:
        """Retourne la balance actuelle."""
        return self.balance

    def get_total_pnl(self) -> float:
        """Calcule le PnL total (réalisé + non réalisé)."""
        realized_pnl = sum(
            (order.price - self._get_avg_price_at_time(order.symbol, order.timestamp)) * order.quantity
            for order in self.orders
            if order.side == 'sell'
        )

        unrealized_pnl = sum(pos.pnl for pos in self.positions.values())

        return float(realized_pnl + unrealized_pnl)

    def _get_avg_price_at_time(self, symbol: str, timestamp: datetime) -> float:
        """Prix moyen au moment de l'ordre (simplifié)."""
        # Dans un vrai système, il faudrait tracker l'historique des prix moyens
        return self.positions.get(symbol, Position(symbol, 0, 0, 0, 0)).avg_price
