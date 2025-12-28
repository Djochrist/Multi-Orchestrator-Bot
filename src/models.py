"""
Modèles de données pour le stockage en mémoire
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional


@dataclass
class BaseModel:
    """Modèle de base avec champs communs"""
    id: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1000000) % 1000000)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            **{k: v for k, v in self.__dict__.items() if k not in ['id', 'created_at', 'updated_at']}
        }

    def update(self, **kwargs) -> None:
        """Met à jour les attributs"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class Strategy(BaseModel):
    """Modèle de stratégie de trading"""
    name: str = ""
    description: str = ""
    type: str = "manual"  # 'rsi', 'macd', 'ml', 'manual'
    status: str = "inactive"  # 'active', 'inactive'
    config: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)

    def is_active(self) -> bool:
        """Vérifie si la stratégie est active"""
        return self.status == 'active'

    def activate(self) -> None:
        """Active la stratégie"""
        self.status = 'active'

    def deactivate(self) -> None:
        """Désactive la stratégie"""
        self.status = 'inactive'

    def update_performance(self, pnl: float, win_rate: float, **metrics) -> None:
        """Met à jour les performances"""
        self.performance.update({
            'total_pnl': pnl,
            'win_rate': win_rate,
            **metrics
        })

    @property
    def total_pnl(self) -> float:
        """PnL total depuis les performances"""
        return self.performance.get('total_pnl', 0.0)

    @property
    def win_rate(self) -> float:
        """Taux de réussite depuis les performances"""
        return self.performance.get('win_rate', 0.0)


@dataclass
class Trade(BaseModel):
    """Modèle de trade"""
    strategy_id: Optional[int] = None
    symbol: str = ""
    side: str = "buy"  # 'buy', 'sell'
    quantity: float = 0.0
    entry_price: float = 0.0
    exit_price: Optional[float] = None
    entry_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    exit_time: Optional[datetime] = None
    status: str = "open"  # 'open', 'closed', 'cancelled'
    pnl: Optional[float] = None
    fees: float = 0.0
    notes: str = ""

    @property
    def is_open(self) -> bool:
        """Vérifie si le trade est ouvert"""
        return self.status == 'open'

    @property
    def is_closed(self) -> bool:
        """Vérifie si le trade est fermé"""
        return self.status == 'closed'

    def close_trade(self, exit_price: float, exit_time: Optional[datetime] = None) -> None:
        """Ferme le trade"""
        self.exit_price = exit_price
        self.exit_time = exit_time or datetime.now(timezone.utc)
        self.status = 'closed'

        # Calcule le PnL
        if self.side == 'buy':
            self.pnl = (exit_price - self.entry_price) * self.quantity
        else:  # sell
            self.pnl = (self.entry_price - exit_price) * self.quantity

    def cancel_trade(self) -> None:
        """Annule le trade"""
        self.status = 'cancelled'
        self.exit_time = datetime.now(timezone.utc)
