"""Chargement et génération de données de marché."""

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf


def download_market_data(
    symbol: str = "BTC-USD",
    days: int = 100,
    interval: str = "1d"
) -> pd.DataFrame:
    """Télécharge des données de marché réelles depuis Yahoo Finance.

    Args:
        symbol: Symbole de l'actif (ex: 'BTC-USD', 'AAPL', '^GSPC')
        days: Nombre de jours de données à récupérer
        interval: Intervalle des données ('1d', '1h', '15m', etc.)

    Returns:
        DataFrame avec colonnes: timestamp, open, high, low, close, volume
    """
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
        print(f"Erreur lors du téléchargement des données pour {symbol}: {e}")
        print("Retour aux données synthétiques...")
        return generate_synthetic_data(days=days)


def generate_synthetic_data(
    days: int = 100, start_price: float = 50000.0, volatility: float = 0.02
) -> pd.DataFrame:
    """Génère des données OHLCV synthétiques en cas d'échec du téléchargement.

    Args:
        days: Nombre de jours de données
        start_price: Prix de départ
        volatility: Volatilité quotidienne

    Returns:
        DataFrame avec colonnes: timestamp, open, high, low, close, volume
    """
    import numpy as np

    np.random.seed(42)  # Pour la reproductibilité

    # Générer les timestamps
    start_date = datetime.now() - timedelta(days=days)
    timestamps = [start_date + timedelta(days=i) for i in range(days)]

    # Générer les rendements aléatoires
    returns = np.random.normal(0, volatility, days)
    returns[0] = 0  # Premier jour pas de rendement

    # Calculer les prix de clôture
    closes = start_price * np.exp(np.cumsum(returns))

    # Générer OHLCV
    data = []
    for i, (ts, close) in enumerate(zip(timestamps, closes)):
        if i == 0:
            open_price = start_price
        else:
            open_price = data[-1]["close"]

        # Générer high/low autour du close avec un peu de bruit
        high_noise = np.random.uniform(0, volatility * 0.5)
        low_noise = np.random.uniform(0, volatility * 0.5)
        high = max(open_price, close) * (1 + high_noise)
        low = min(open_price, close) * (1 - low_noise)

        # Volume aléatoire
        volume = np.random.randint(1000000, 10000000)  # Volume plus réaliste

        data.append(
            {
                "timestamp": ts,
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "volume": volume,
            }
        )

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

    return df


def load_recent_data(symbol: str = "BTC-USD", days: int = 30) -> pd.DataFrame:
    """Charge les données récentes pour l'orchestration.

    Args:
        symbol: Symbole de l'actif
        days: Nombre de jours de données

    Returns:
        DataFrame avec les données de marché
    """
    return download_market_data(symbol=symbol, days=days)
