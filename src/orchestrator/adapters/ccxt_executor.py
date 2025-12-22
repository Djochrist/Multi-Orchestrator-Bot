"""Exécuteur d'ordres utilisant CCXT pour les échanges réels."""

import logging
from typing import Any, Dict, Optional

import ccxt

from .mock_exchange import Order, Position

logger = logging.getLogger(__name__)


class CCXTExecutor:
    """Exécuteur d'ordres pour échanges réels via CCXT."""

    def __init__(
        self,
        exchange_id: str = "binance",
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        sandbox: bool = True,
    ):
        """
        Initialise l'exécuteur CCXT.

        Args:
            exchange_id: ID de l'échange (binance, kraken, etc.)
            api_key: Clé API
            api_secret: Secret API
            sandbox: Utiliser le mode sandbox si disponible
        """
        self.exchange_id = exchange_id

        # Configuration de l'échange
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class(
            {
                "apiKey": api_key,
                "secret": api_secret,
                "sandbox": sandbox,
                "enableRateLimit": True,
            }
        )

        logger.info(f"Initialisé CCXT executor pour {exchange_id} (sandbox: {sandbox})")

    def place_order(
        self, symbol: str, side: str, quantity: float, price: Optional[float] = None
    ) -> str:
        """
        Place un ordre sur l'échange réel.

        ⚠️ ATTENTION: Cette méthode exécute des ordres réels !

        Args:
            symbol: Symbole (ex: 'BTC/USDT')
            side: 'buy' ou 'sell'
            quantity: Quantité
            price: Prix (None pour market order)

        Returns:
            ID de l'ordre
        """
        try:
            if price is None:
                # Market order
                order = self.exchange.create_market_order(symbol, side, quantity)
            else:
                # Limit order
                order = self.exchange.create_limit_order(symbol, side, quantity, price)

            order_id = str(order["id"])
            logger.info(f"Ordre {side} {quantity} {symbol} placé: {order_id}")
            return order_id

        except Exception as e:
            logger.error(f"Erreur lors du placement d'ordre: {e}")
            raise

    def get_balance(self, currency: Optional[str] = None) -> Dict[str, Any]:
        """Récupère les balances."""
        try:
            balance = self.exchange.fetch_balance()
            if currency:
                return {currency: balance.get(currency, {})}
            return balance
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du balance: {e}")
            raise

    def get_positions(self) -> Dict[str, Any]:
        """Récupère les positions (pour exchanges avec positions)."""
        try:
            # Pour les exchanges spot, les positions sont dans le balance
            balance = self.exchange.fetch_balance()
            positions = {}

            for currency, data in balance.items():
                if data.get("total", 0) > 0:
                    positions[currency] = {
                        "quantity": data["total"],
                        "free": data.get("free", 0),
                        "used": data.get("used", 0),
                    }

            return positions
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des positions: {e}")
            raise

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Récupère les informations de ticker."""
        try:
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du ticker {symbol}: {e}")
            raise
