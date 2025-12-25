"""Chargement de données de marché."""

import logging
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def download_market_data(
    symbol: str = "BTC-USD",
    days: int = 100,
    interval: str = "1d"
) -> pd.DataFrame:
    """Télécharge des données de marché réelles depuis Yahoo Finance.

    Args:
        symbol: Symbole de l'actif (ex: 'BTC-USD', 'AAPL', '^GSPC')
        days: Nombre de jours de données à récupérer (1-365)
        interval: Intervalle des données ('1d', '1h', '15m', etc.)

    Returns:
        DataFrame avec colonnes: timestamp, open, high, low, close, volume

    Raises:
        ValueError: Si les paramètres sont invalides
    """
    # Validation des paramètres
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Le symbole doit être une chaîne non vide")
    if not (1 <= days <= 365):
        raise ValueError("Le nombre de jours doit être entre 1 et 365")
    valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
    if interval not in valid_intervals:
        raise ValueError(f"Interval invalide. Valeurs possibles: {valid_intervals}")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    try:
        # Télécharger les données
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)

        if df.empty:
            raise ValueError(f"Aucune donnée trouvée pour le symbole {symbol}")

        # Renommer les colonnes pour cohérence
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })

        # S'assurer que l'index est datetime
        df.index = pd.to_datetime(df.index)

        # Convertir le volume en int si nécessaire
        df['volume'] = df['volume'].astype(int)

        return df

    except Exception as e:
        logger.error(f"Erreur lors du téléchargement des données pour {symbol}: {e}")
        raise ValueError(f"Impossible de télécharger les données pour {symbol}: {e}") from e


def load_recent_data(symbol: str = "BTC-USD", days: int = 30) -> pd.DataFrame:
    """Charge les données récentes pour l'orchestration.

    Args:
        symbol: Symbole de l'actif
        days: Nombre de jours de données (min 7 pour les calculs de stratégies)

    Returns:
        DataFrame avec les données de marché

    Raises:
        ValueError: Si les paramètres sont invalides
    """
    if days < 7:
        raise ValueError("Au minimum 7 jours de données sont requis pour les calculs de stratégies")
    return download_market_data(symbol=symbol, days=days)


def generate_synthetic_data(
    days: int = 100,
    start_price: float = 100.0,
    volatility: float = 0.02,
    seed: Optional[int] = 42
) -> pd.DataFrame:
    """Génère des données de marché synthétiques pour les tests.

    Args:
        days: Nombre de jours de données à générer
        start_price: Prix de départ
        volatility: Volatilité quotidienne (pourcentage)
        seed: Graine pour la reproductibilité

    Returns:
        DataFrame avec colonnes OHLCV synthétiques

    Raises:
        ValueError: Si les paramètres sont invalides
    """
    if days <= 0:
        raise ValueError("Le nombre de jours doit être positif")
    if start_price <= 0:
        raise ValueError("Le prix de départ doit être positif")
    if volatility < 0:
        raise ValueError("La volatilité doit être non négative")

    # Configuration du générateur aléatoire pour reproductibilité
    rng = np.random.RandomState(seed)

    # Génération des dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Génération des rendements aléatoires (marche aléatoire géométrique)
    returns = rng.normal(0, volatility, len(dates))
    returns[0] = 0  # Le premier jour n'a pas de rendement

    # Calcul des prix de clôture
    close_prices = start_price * np.exp(np.cumsum(returns))

    # Génération des prix OHLC avec relations réalistes
    high_low_spread = rng.uniform(0.005, 0.03, len(dates))  # Spread 0.5% à 3%

    open_prices = np.roll(close_prices, 1)
    open_prices[0] = start_price

    # Générer high et low de manière cohérente
    daily_ranges = close_prices * high_low_spread

    # Calculer les prix high et low autour du close
    high_prices = close_prices + daily_ranges * rng.uniform(0, 1, len(dates))
    low_prices = close_prices - daily_ranges * rng.uniform(0, 1, len(dates))

    # S'assurer que high >= max(open, close) et low <= min(open, close)
    for i in range(len(dates)):
        max_price = max(open_prices[i], close_prices[i])
        min_price = min(open_prices[i], close_prices[i])

        high_prices[i] = max(high_prices[i], max_price)
        low_prices[i] = min(low_prices[i], min_price)

    # Volume synthétique (corrélé positivement avec la volatilité)
    base_volume = 1000000  # Volume de base
    volume_noise = rng.uniform(0.5, 2.0, len(dates))
    volatility_factor = np.abs(returns) / volatility + 1
    volumes = (base_volume * volume_noise * volatility_factor).astype(int)

    # Création du DataFrame
    df = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=dates)

    return df
