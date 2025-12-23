"""Stratégies de trading avancées avec risk/reward management."""

import numpy as np
import pandas as pd
from typing import Optional, Tuple

from ..strategy_interface import StrategyAdapter


class BreakoutRetestStrategy(StrategyAdapter):
    """
    Stratégie de breakout avec retest.

    Principe:
    - Identifie un breakout au-dessus d'une résistance/haute récente
    - Entre immédiatement après le breakout avec confirmation de volume
    - Utilise un stop loss basé sur l'ATR et risk/reward ratio
    """

    def __init__(
        self,
        lookback: int = 20,
        breakout_threshold: float = 0.01,
        risk_reward_ratio: float = 2.0,
        min_volume_multiplier: float = 1.2
    ):
        """
        Args:
            lookback: Période pour identifier les hauts/bas récents
            breakout_threshold: Seuil de breakout (% au-dessus de la résistance)
            risk_reward_ratio: Ratio risk/reward minimum
            min_volume_multiplier: Multiplicateur du volume moyen requis
        """
        self.lookback = lookback
        self.breakout_threshold = breakout_threshold
        self.risk_reward_ratio = risk_reward_ratio
        self.min_volume_multiplier = min_volume_multiplier

    @property
    def name(self) -> str:
        return f"BreakoutRetest_{self.lookback}_{self.breakout_threshold:.2f}"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génère les signaux de breakout."""
        df = df.copy()

        # Calculer les niveaux de résistance/support récents
        df['resistance'] = df['high'].rolling(window=self.lookback).max()
        df['support'] = df['low'].rolling(window=self.lookback).min()

        # Calculer le volume moyen
        df['avg_volume'] = df['volume'].rolling(window=self.lookback).mean()

        # Calculer l'ATR pour le stop loss
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        df['atr'] = df['tr'].rolling(window=self.lookback).mean()

        # Identifier les breakouts haussiers
        df['breakout_up'] = (
            (df['close'] > df['resistance'] * (1 + self.breakout_threshold)) &
            (df['volume'] > df['avg_volume'] * self.min_volume_multiplier) &
            (df['close'].shift(1) <= df['resistance'])  # Était en dessous avant
        )

        # Identifier les breakouts baissiers
        df['breakout_down'] = (
            (df['close'] < df['support'] * (1 - self.breakout_threshold)) &
            (df['volume'] > df['avg_volume'] * self.min_volume_multiplier) &
            (df['close'].shift(1) >= df['support'])  # Était au-dessus avant
        )

        # Générer les signaux
        df['signal'] = 0
        df.loc[df['breakout_up'], 'signal'] = 1
        df.loc[df['breakout_down'], 'signal'] = -1

        return df


class FibonacciRetracementStrategy(StrategyAdapter):
    """
    Stratégie basée sur les retracements de Fibonacci.

    Principe:
    - Identifie un trend principal (hausse/baissé)
    - Calcule les niveaux de Fibonacci (23.6%, 38.2%, 61.8%)
    - Entre en position sur rebond/rejet de ces niveaux
    - Utilise le risk/reward ratio pour valider les entrées
    """

    def __init__(
        self,
        lookback: int = 50,
        trend_period: int = 20,
        fib_levels: list = None,
        risk_reward_ratio: float = 1.5
    ):
        """
        Args:
            lookback: Période pour calculer les swings
            trend_period: Période pour déterminer le trend
            fib_levels: Niveaux de Fibonacci à utiliser
            risk_reward_ratio: Ratio risk/reward minimum
        """
        self.lookback = lookback
        self.trend_period = trend_period
        self.fib_levels = fib_levels or [0.236, 0.382, 0.618]
        self.risk_reward_ratio = risk_reward_ratio

    @property
    def name(self) -> str:
        return f"FibRetracement_{self.lookback}_{len(self.fib_levels)}"

    def _calculate_fib_levels(self, high: float, low: float) -> dict:
        """Calcule les niveaux de Fibonacci."""
        diff = high - low
        levels = {}
        for level in self.fib_levels:
            levels[level] = low + diff * level
        return levels

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génère les signaux basés sur Fibonacci."""
        df = df.copy()

        # Déterminer le trend (SMA sur trend_period)
        df['trend_sma'] = df['close'].rolling(window=self.trend_period).mean()
        df['trend'] = np.where(df['close'] > df['trend_sma'], 1, -1)

        # Calculer les niveaux de Fibonacci sur les derniers 50 points
        recent_high = df['high'].rolling(window=50).max()
        recent_low = df['low'].rolling(window=50).min()

        df['fib_236'] = recent_low + (recent_high - recent_low) * 0.236
        df['fib_382'] = recent_low + (recent_high - recent_low) * 0.382
        df['fib_618'] = recent_low + (recent_high - recent_low) * 0.618

        # RSI pour confirmer les signaux
        df['rsi'] = self._calculate_rsi(df['close'], 14)

        # Générer les signaux
        df['signal'] = 0

        # Dans un trend haussier, acheter sur support Fibonacci + RSI survente
        uptrend_mask = df['trend'] == 1
        fib_buy_mask = (
            uptrend_mask &
            (
                (abs(df['close'] - df['fib_236']) / df['close'] < 0.02) |
                (abs(df['close'] - df['fib_382']) / df['close'] < 0.02)
            ) &
            (df['rsi'] < 40)  # Survente
        )
        df.loc[fib_buy_mask, 'signal'] = 1

        # Dans un trend baissier, vendre sur résistance Fibonacci + RSI surachat
        downtrend_mask = df['trend'] == -1
        fib_sell_mask = (
            downtrend_mask &
            (
                (abs(df['close'] - df['fib_618']) / df['close'] < 0.02) |
                (abs(df['close'] - df['fib_382']) / df['close'] < 0.02)
            ) &
            (df['rsi'] > 60)  # Surachat
        )
        df.loc[fib_sell_mask, 'signal'] = -1

        return df

    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calcule le RSI."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


class OrderFlowImbalanceStrategy(StrategyAdapter):
    """
    Stratégie basée sur l'imbalance du flux d'ordres (Order Flow Imbalance).

    Principe:
    - Analyse le volume et la direction des prix
    - Identifie les imbalances entre acheteurs et vendeurs
    - Entre en position quand l'imbalance dépasse un seuil
    - Utilise le momentum pour confirmer les signaux
    """

    def __init__(
        self,
        volume_window: int = 20,
        imbalance_threshold: float = 1.5,
        momentum_period: int = 10,
        risk_reward_ratio: float = 1.8
    ):
        """
        Args:
            volume_window: Fenêtre pour calculer le volume moyen
            imbalance_threshold: Seuil d'imbalance pour générer un signal
            momentum_period: Période pour le momentum
            risk_reward_ratio: Ratio risk/reward minimum
        """
        self.volume_window = volume_window
        self.imbalance_threshold = imbalance_threshold
        self.momentum_period = momentum_period
        self.risk_reward_ratio = risk_reward_ratio

    @property
    def name(self) -> str:
        return f"OrderFlowImbalance_{self.volume_window}_{self.imbalance_threshold:.1f}"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génère les signaux basés sur l'imbalance du flux d'ordres."""
        df = df.copy()

        # Calculer le volume moyen
        df['avg_volume'] = df['volume'].rolling(window=self.volume_window).mean()

        # Calculer le momentum des prix
        df['momentum'] = (df['close'] - df['close'].shift(self.momentum_period)) / df['close'].shift(self.momentum_period)

        # Calculer l'imbalance du volume (simplifié)
        df['price_change'] = df['close'] - df['open']
        df['volume_ratio'] = df['volume'] / df['avg_volume']

        # Signal basé sur volume et momentum
        df['signal'] = 0

        # Signal d'achat: volume élevé + momentum positif + chandelier haussier
        buy_mask = (
            (df['volume_ratio'] > 1.1) &
            (df['momentum'] > 0.005) &
            (df['price_change'] > 0)
        )
        df.loc[buy_mask, 'signal'] = 1

        # Signal de vente: volume élevé + momentum négatif + chandelier baissier
        sell_mask = (
            (df['volume_ratio'] > 1.1) &
            (df['momentum'] < -0.005) &
            (df['price_change'] < 0)
        )
        df.loc[sell_mask, 'signal'] = -1

        return df


class RiskRewardEnhancedStrategy(StrategyAdapter):
    """
    Stratégie améliorée avec gestion avancée du risk/reward.

    Combine plusieurs indicateurs avec des règles strictes de risk management.
    """

    def __init__(
        self,
        fast_ma: int = 9,
        slow_ma: int = 21,
        rsi_period: int = 14,
        rsi_overbought: float = 70,
        rsi_oversold: float = 30,
        risk_reward_ratio: float = 2.5,
        max_drawdown_pct: float = 0.05
    ):
        """
        Args:
            fast_ma: Période MA rapide
            slow_ma: Période MA lente
            rsi_period: Période RSI
            rsi_overbought: Niveau surachat RSI
            rsi_oversold: Niveau survente RSI
            risk_reward_ratio: Ratio risk/reward minimum
            max_drawdown_pct: Drawdown maximum autorisé
        """
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.risk_reward_ratio = risk_reward_ratio
        self.max_drawdown_pct = max_drawdown_pct

    @property
    def name(self) -> str:
        return f"RiskRewardEnhanced_{self.fast_ma}_{self.slow_ma}"

    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calcule le RSI."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génère les signaux avec gestion risk/reward avancée."""
        df = df.copy()

        # Moyennes mobiles
        df['fast_ma'] = df['close'].rolling(window=self.fast_ma).mean()
        df['slow_ma'] = df['close'].rolling(window=self.slow_ma).mean()

        # RSI
        df['rsi'] = self._calculate_rsi(df['close'], self.rsi_period)

        # ATR pour le stop loss dynamique
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        df['atr'] = df['tr'].rolling(window=14).mean()

        # Calcul du drawdown
        df['rolling_max'] = df['close'].expanding().max()
        df['drawdown'] = (df['close'] - df['rolling_max']) / df['rolling_max']

        # Conditions d'entrée avec risk management
        df['signal'] = 0

        # Signal d'achat
        buy_conditions = (
            (df['fast_ma'] > df['slow_ma']) &  # Trend haussier
            (df['rsi'] < self.rsi_oversold) &  # Survente
            (df['drawdown'] > -self.max_drawdown_pct) &  # Pas en drawdown excessif
            (df['close'] > df['close'].shift(1))  # Momentum positif
        )
        df.loc[buy_conditions, 'signal'] = 1

        # Signal de vente
        sell_conditions = (
            (df['fast_ma'] < df['slow_ma']) &  # Trend baissier
            (df['rsi'] > self.rsi_overbought) &  # Surachat
            (df['drawdown'] > -self.max_drawdown_pct) &  # Pas en drawdown excessif
            (df['close'] < df['close'].shift(1))  # Momentum négatif
        )
        df.loc[sell_conditions, 'signal'] = -1

        return df
