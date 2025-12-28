"""
Stockage en mémoire thread-safe
"""

from typing import Dict, List, Optional, TypeVar, Generic
from threading import Lock
from datetime import datetime, timezone

from .models import Strategy, Trade

T = TypeVar('T')


class InMemoryStorage(Generic[T]):
    """Stockage en mémoire thread-safe"""

    def __init__(self):
        self._data: Dict[int, T] = {}
        self._lock = Lock()
        self._next_id = 1

    def create(self, item: T) -> T:
        """Crée un nouvel élément"""
        with self._lock:
            if hasattr(item, 'id') and item.id == 0:
                item.id = self._next_id
                self._next_id += 1
            self._data[item.id] = item
            return item

    def get(self, item_id: int) -> Optional[T]:
        """Récupère un élément par ID"""
        return self._data.get(item_id)

    def get_all(self) -> List[T]:
        """Récupère tous les éléments"""
        return list(self._data.values())

    def update(self, item_id: int, item: T) -> Optional[T]:
        """Met à jour un élément"""
        with self._lock:
            if item_id in self._data:
                if hasattr(item, 'updated_at'):
                    item.updated_at = datetime.now(timezone.utc)
                self._data[item_id] = item
                return item
            return None

    def delete(self, item_id: int) -> bool:
        """Supprime un élément"""
        with self._lock:
            if item_id in self._data:
                del self._data[item_id]
                return True
            return False

    def find_by(self, **kwargs) -> List[T]:
        """Trouve des éléments par attributs"""
        results = []
        for item in self._data.values():
            if all(getattr(item, k, None) == v for k, v in kwargs.items()):
                results.append(item)
        return results

    def clear(self) -> None:
        """Vide toutes les données"""
        with self._lock:
            self._data.clear()
            self._next_id = 1


# Instances globales de stockage
strategies_storage = InMemoryStorage[Strategy]()
trades_storage = InMemoryStorage[Trade]()


def initialize_sample_data():
    """Initialise des données d'exemple"""
    # Stratégies d'exemple
    strategy1 = Strategy(
        name="RSI Momentum",
        description="Stratégie basée sur l'indicateur RSI",
        type="rsi",
        status="active",
        config={"rsi_period": 14, "overbought": 70, "oversold": 30},
        performance={"total_pnl": 1250.50, "win_rate": 65.0}
    )
    strategies_storage.create(strategy1)

    strategy2 = Strategy(
        name="MACD Crossover",
        description="Stratégie de croisement MACD",
        type="macd",
        status="inactive",
        config={"fast": 12, "slow": 26, "signal": 9},
        performance={"total_pnl": -230.00, "win_rate": 45.0}
    )
    strategies_storage.create(strategy2)

    # Trades d'exemple
    trade1 = Trade(
        strategy_id=strategy1.id,
        symbol="BTC",
        side="buy",
        quantity=0.5,
        entry_price=92000.0,
        status="closed",
        pnl=1250.0
    )
    trade1.close_trade(94500.0)
    trades_storage.create(trade1)
