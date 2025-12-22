"""Interface abstraite pour les stratégies de trading."""

from abc import ABC, abstractmethod
from typing import Protocol

import pandas as pd


class StrategyAdapter(Protocol):
    """Interface pour les adaptateurs de stratégie de trading."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom de la stratégie."""
        ...

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génère les signaux de trading.

        Args:
            df: DataFrame avec les données OHLCV (Open, High, Low, Close, Volume)

        Returns:
            DataFrame avec une colonne 'signal' contenant -1, 0, ou 1
        """
        ...
