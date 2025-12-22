"""Configuration du système de trading."""

import os
from typing import Dict, Any


class Config:
    """Configuration centralisée."""

    # Paramètres par défaut
    DEFAULTS = {
        'trading': {
            'symbol': 'BTC/USD',
            'default_quantity': 0.01,
            'max_position_size': 0.1,
        },
        'backtest': {
            'recent_days': 30,
            'min_data_points': 50,
        },
        'risk': {
            'max_drawdown': 0.1,  # 10%
            'max_trades_per_day': 5,
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        }
    }

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration."""
        keys = key.split('.')
        value = cls.DEFAULTS

        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default

    @classmethod
    def is_live_mode(cls) -> bool:
        """Vérifie si le mode live est activé."""
        return os.getenv('LIVE', 'false').lower() == 'true'
