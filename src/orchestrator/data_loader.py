"""Chargement de données de marché."""

import logging
from datetime import datetime, timedelta
from typing import Optional

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
