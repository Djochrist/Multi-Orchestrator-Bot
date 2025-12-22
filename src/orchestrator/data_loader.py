"""Chargement et génération de données de marché."""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_synthetic_data(days: int = 100, start_price: float = 100.0, volatility: float = 0.02) -> pd.DataFrame:
    """Génère des données OHLCV synthétiques pour les tests.

    Args:
        days: Nombre de jours de données
        start_price: Prix de départ
        volatility: Volatilité quotidienne

    Returns:
        DataFrame avec colonnes: timestamp, open, high, low, close, volume
    """
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
            open_price = data[-1]['close']

        # Générer high/low autour du close avec un peu de bruit
        high_noise = np.random.uniform(0, volatility * 0.5)
        low_noise = np.random.uniform(0, volatility * 0.5)
        high = max(open_price, close) * (1 + high_noise)
        low = min(open_price, close) * (1 - low_noise)

        # Volume aléatoire
        volume = np.random.randint(1000, 10000)

        data.append({
            'timestamp': ts,
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })

    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    return df


def load_recent_data(days: int = 30) -> pd.DataFrame:
    """Charge les données récentes pour l'orchestration (30 jours par défaut)."""
    return generate_synthetic_data(days=days)
