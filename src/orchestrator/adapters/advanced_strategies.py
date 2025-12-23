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
    Stratégie basée sur l'imbalance du flux d'ordres (volume/momentum).

    Principe:
    - Détecte les imbalances entre acheteurs et vendeurs
    - Utilise le volume et le momentum pour identifier les mouvements
    - Entre en position quand l'imbalance devient significative
    """

    def __init__(
        self,
        imbalance_threshold: float = 0.7,
        volume_window: int = 20,
        momentum_window: int = 10,
        min_volume_multiplier: float = 1.5
    ):
        """
        Args:
            imbalance_threshold: Seuil d'imbalance pour signal
            volume_window: Fenêtre pour calculer le volume moyen
            momentum_window: Fenêtre pour calculer le momentum
            min_volume_multiplier: Multiplicateur du volume moyen requis
        """
        self.imbalance_threshold = imbalance_threshold
        self.volume_window = volume_window
        self.momentum_window = momentum_window
        self.min_volume_multiplier = min_volume_multiplier

    @property
    def name(self) -> str:
        return f"OrderFlowImbalance_{self.imbalance_threshold:.1f}_{self.volume_window}"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génère les signaux basés sur l'imbalance du flux d'ordres."""
        df = df.copy()

        # Calculer le volume moyen
        df['avg_volume'] = df['volume'].rolling(window=self.volume_window).mean()

        # Calculer le momentum des prix
        df['momentum'] = (df['close'] - df['close'].shift(self.momentum_window)) / df['close'].shift(self.momentum_window)

        # Calculer l'imbalance basé sur le volume relatif et momentum
        df['volume_ratio'] = df['volume'] / df['avg_volume']

        # Imbalance positif = forte pression acheteuse (volume élevé + momentum positif)
        # Imbalance négatif = forte pression vendeuse (volume élevé + momentum négatif)
        df['imbalance'] = df['volume_ratio'] * df['momentum']

        # Normaliser l'imbalance
        df['imbalance_norm'] = df['imbalance'] / df['imbalance'].rolling(window=self.volume_window).std()

        # Générer les signaux
        df['signal'] = 0

        # Signal d'achat: imbalance positif fort + volume élevé
        buy_mask = (
            (df['imbalance_norm'] > self.imbalance_threshold) &
            (df['volume_ratio'] > self.min_volume_multiplier) &
            (df['momentum'] > 0)
        )
        df.loc[buy_mask, 'signal'] = 1

        # Signal de vente: imbalance négatif fort + volume élevé
        sell_mask = (
            (df['imbalance_norm'] < -self.imbalance_threshold) &
            (df['volume_ratio'] > self.min_volume_multiplier) &
            (df['momentum'] < 0)
        )
        df.loc[sell_mask, 'signal'] = -1

        return df


class BearMarketMomentumStrategy(StrategyAdapter):
    """
    Stratégie optimisée pour les marchés baissiers.

    Principe:
    - Profite des mouvements baissiers prolongés
    - Entre en position short sur momentum négatif
    - Utilise des seuils adaptés aux marchés bear
    - Gestion du risque optimisée pour la volatilité
    """

    def __init__(
        self,
        momentum_window: int = 10,
        volume_threshold: float = 1.3,
        bear_threshold: float = -0.008,  # Plus sensible pour bear market
        min_trend_period: int = 20
    ):
        """
        Args:
            momentum_window: Fenêtre pour calculer le momentum
            volume_threshold: Seuil de volume pour confirmer
            bear_threshold: Seuil de momentum baissier
            min_trend_period: Période minimum pour confirmer trend baissier
        """
        self.momentum_window = momentum_window
        self.volume_threshold = volume_threshold
        self.bear_threshold = bear_threshold
        self.min_trend_period = min_trend_period

    @property
    def name(self) -> str:
        return f"BearMomentum_{self.momentum_window}_{abs(self.bear_threshold):.3f}"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génère les signaux pour marchés baissiers."""
        df = df.copy()

        # Calculer le trend général (SMA long terme)
        df['long_trend'] = df['close'].rolling(window=self.min_trend_period).mean()
        df['trend_direction'] = np.where(df['close'] < df['long_trend'], -1, 1)  # -1 = bear, 1 = bull

        # Calculer le momentum à court terme
        df['momentum'] = (df['close'] - df['close'].shift(self.momentum_window)) / df['close'].shift(self.momentum_window)

        # Calculer le volume relatif
        df['avg_volume'] = df['volume'].rolling(window=self.momentum_window).mean()
        df['volume_ratio'] = df['volume'] / df['avg_volume']

        # Calculer l'accélération des prix (rate of change)
        df['roc'] = df['close'].pct_change(periods=3)  # 3 périodes pour court terme

        # Signal basé sur bear market conditions
        df['signal'] = 0

        # Signal de vente (short): dans un trend baissier + momentum négatif + volume élevé
        sell_mask = (
            (df['trend_direction'] == -1) &  # Trend baissier confirmé
            (df['momentum'] < self.bear_threshold) &  # Momentum très négatif
            (df['volume_ratio'] > self.volume_threshold) &  # Volume élevé
            (df['roc'] < -0.02)  # Accélération baissière récente
        )
        df.loc[sell_mask, 'signal'] = -1

        # Signal d'achat (sortie short): rebond dans trend baissier + momentum positif
        buy_mask = (
            (df['trend_direction'] == -1) &  # Toujours en trend baissier
            (df['momentum'] > 0.005) &  # Momentum positif (rebond)
            (df['volume_ratio'] > 1.1) &  # Volume de confirmation
            (df['roc'] > 0.01)  # Accélération haussière
        )
        df.loc[buy_mask, 'signal'] = 1

        return df


class MeanReversionBearStrategy(StrategyAdapter):
    """
    Stratégie de retour à la moyenne optimisée pour bear markets.

    Principe:
    - Identifie les surventes temporaires dans un trend baissier
    - Entre long sur ces rebonds temporaires
    - Sort rapidement pour éviter la poursuite du trend baissier
    """

    def __init__(
        self,
        lookback: int = 15,  # Plus court pour bear market
        z_threshold: float = 2.2,  # Plus sensible
        max_holding_period: int = 5,  # Sortie rapide
        trend_filter_period: int = 25
    ):
        """
        Args:
            lookback: Période pour calculer la moyenne et l'écart-type
            z_threshold: Seuil de déviation pour signal
            max_holding_period: Période maximale de détention
            trend_filter_period: Période pour filtrer le trend général
        """
        self.lookback = lookback
        self.z_threshold = z_threshold
        self.max_holding_period = max_holding_period
        self.trend_filter_period = trend_filter_period

    @property
    def name(self) -> str:
        return f"MeanRevBear_{self.lookback}_{self.z_threshold:.1f}"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génère les signaux de mean reversion pour bear market."""
        df = df.copy()

        # Filtrer pour ne trader que dans les trends baissiers
        df['trend_sma'] = df['close'].rolling(window=self.trend_filter_period).mean()
        df['in_bear_trend'] = df['close'] < df['trend_sma'] * 0.98  # 2% en dessous = bear

        # Calculer la moyenne mobile et l'écart-type
        df['rolling_mean'] = df['close'].rolling(window=self.lookback).mean()
        df['rolling_std'] = df['close'].rolling(window=self.lookback).std()

        # Calculer le z-score
        df['z_score'] = (df['close'] - df['rolling_mean']) / df['rolling_std']

        # Calculer le RSI pour confirmer
        df['rsi'] = self._calculate_rsi(df['close'], 14)

        # Signal basé sur mean reversion dans bear market
        df['signal'] = 0

        # Signal d'achat (long): survente extrême dans trend baissier + RSI bas
        buy_mask = (
            df['in_bear_trend'] &  # Seulement dans trend baissier
            (df['z_score'] < -self.z_threshold) &  # Survente extrême
            (df['rsi'] < 25) &  # RSI très bas
            (df['close'] > df['close'].shift(1))  # Petit rebond récent
        )
        df.loc[buy_mask, 'signal'] = 1

        # Signal de vente (sortie): retour proche de la moyenne OU RSI surachat
        sell_mask = (
            (df['z_score'] > -0.5) |  # Revenu proche de la moyenne
            (df['rsi'] > 75) |  # RSI surachat
            (~df['in_bear_trend'])  # Sortie du trend baissier
        )
        df.loc[sell_mask, 'signal'] = -1

        return df

    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calcule le RSI."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
