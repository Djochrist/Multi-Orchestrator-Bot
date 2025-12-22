"""Stratégies de trading simples."""

import pandas as pd
from typing import Protocol

from ..strategy_interface import StrategyAdapter


class SMACrossover(StrategyAdapter):
    """Stratégie de croisement de moyennes mobiles simples."""

    def __init__(self, short: int = 10, long: int = 50):
        self._short = short
        self._long = long

    @property
    def name(self) -> str:
        return f"SMA_{self._short}_{self._long}"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génère les signaux basé sur le croisement SMA."""
        df = df.copy()
        df['sma_short'] = df['close'].rolling(window=self._short).mean()
        df['sma_long'] = df['close'].rolling(window=self._long).mean()

        # Signal: 1 quand short > long, -1 quand short < long
        df['signal'] = 0
        df.loc[df['sma_short'] > df['sma_long'], 'signal'] = 1
        df.loc[df['sma_short'] < df['sma_long'], 'signal'] = -1

        return df


class EMACrossover(StrategyAdapter):
    """Stratégie de croisement de moyennes mobiles exponentielles."""

    def __init__(self, short: int = 12, long: int = 26):
        self._short = short
        self._long = long

    @property
    def name(self) -> str:
        return f"EMA_{self._short}_{self._long}"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génère les signaux basé sur le croisement EMA."""
        df = df.copy()
        df['ema_short'] = df['close'].ewm(span=self._short, adjust=False).mean()
        df['ema_long'] = df['close'].ewm(span=self._long, adjust=False).mean()

        # Signal: 1 quand short > long, -1 quand short < long
        df['signal'] = 0
        df.loc[df['ema_short'] > df['ema_long'], 'signal'] = 1
        df.loc[df['ema_short'] < df['ema_long'], 'signal'] = -1

        return df


class MeanReversion(StrategyAdapter):
    """Stratégie de retour à la moyenne."""

    def __init__(self, lookback: int = 20, z_thresh: float = 1.5):
        self._lookback = lookback
        self._z_thresh = z_thresh

    @property
    def name(self) -> str:
        return f"MeanRev_{self._lookback}_{self._z_thresh}"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génère les signaux basé sur l'écart à la moyenne."""
        df = df.copy()

        # Calcul du z-score sur la fenêtre lookback
        rolling_mean = df['close'].rolling(window=self._lookback).mean()
        rolling_std = df['close'].rolling(window=self._lookback).std()
        df['z_score'] = (df['close'] - rolling_mean) / rolling_std

        # Signal: -1 quand z_score > thresh (prix élevé, vendre),
        # 1 quand z_score < -thresh (prix bas, acheter)
        df['signal'] = 0
        df.loc[df['z_score'] > self._z_thresh, 'signal'] = -1
        df.loc[df['z_score'] < -self._z_thresh, 'signal'] = 1

        return df
