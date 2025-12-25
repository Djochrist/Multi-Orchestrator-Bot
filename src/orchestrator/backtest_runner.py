"""Exécution des backtests pour évaluation des stratégies."""

import logging
from typing import Dict, Optional

import numpy as np
import pandas as pd

from .strategy_interface import StrategyAdapter

logger = logging.getLogger(__name__)


class BacktestError(Exception):
    """Exception de base pour les erreurs de backtest."""
    pass


class InvalidDataError(BacktestError):
    """Exception pour données invalides."""
    pass


class StrategyExecutionError(BacktestError):
    """Exception pour erreurs d'exécution de stratégie."""
    pass


class CalculationError(BacktestError):
    """Exception pour erreurs de calcul."""
    pass


def _validate_data(df: pd.DataFrame) -> None:
    """Valide les données de marché.

    Args:
        df: DataFrame à valider

    Raises:
        InvalidDataError: Si les données sont invalides
    """
    if df is None:
        raise InvalidDataError("DataFrame est None")

    if df.empty:
        raise InvalidDataError("DataFrame est vide")

    if len(df) < 2:
        raise InvalidDataError(f"DataFrame trop petit: {len(df)} lignes, minimum 2 requises")

    required_columns = ["open", "high", "low", "close", "volume"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise InvalidDataError(f"Colonnes manquantes dans le DataFrame: {missing_columns}")

    # Vérifier les types de données
    numeric_columns = ["open", "high", "low", "close"]
    for col in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise InvalidDataError(f"Colonne '{col}' doit contenir des valeurs numériques")

    if not pd.api.types.is_integer_dtype(df["volume"]):
        raise InvalidDataError("Colonne 'volume' doit contenir des entiers")

    # Vérifier les valeurs négatives
    for col in numeric_columns:
        if (df[col] <= 0).any():
            raise InvalidDataError(f"Colonne '{col}' contient des valeurs négatives ou nulles")

    if (df["volume"] < 0).any():
        raise InvalidDataError("Colonne 'volume' contient des valeurs négatives")

    # Vérifier les relations OHLC
    invalid_ohlc = (
        (df["high"] < df["low"]) |
        (df["open"] < df["low"]) |
        (df["open"] > df["high"]) |
        (df["close"] < df["low"]) |
        (df["close"] > df["high"])
    )
    if invalid_ohlc.any():
        raise InvalidDataError("Relations OHLC invalides détectées")

    # Vérifier les valeurs NaN
    nan_count = df.isnull().sum().sum()
    if nan_count > 0:
        logger.warning(f"Le DataFrame contient {nan_count} valeurs NaN")


def _calculate_metrics(df_signals: pd.DataFrame) -> Dict[str, float]:
    """Calcule les métriques de performance.

    Args:
        df_signals: DataFrame avec signaux et prix

    Returns:
        Dictionnaire des métriques

    Raises:
        CalculationError: En cas d'erreur de calcul
    """
    try:
        # Calculer les rendements
        df_signals = df_signals.copy()
        df_signals["returns"] = df_signals["close"].pct_change()

        # Éviter les signaux NaN
        df_signals["signal"] = df_signals["signal"].fillna(0)

        # Calculer les rendements de la stratégie
        df_signals["strategy_returns"] = df_signals["returns"] * df_signals["signal"].shift(1)
        df_signals["strategy_returns"] = df_signals["strategy_returns"].fillna(0)

        # Calculer le PnL cumulé
        df_signals["cumulative_returns"] = (1 + df_signals["strategy_returns"]).cumprod() - 1

        # Métriques de base
        total_return = df_signals["cumulative_returns"].iloc[-1] if not df_signals.empty else 0.0

        # Sharpe ratio (annualisé, rf=0)
        strategy_returns = df_signals["strategy_returns"].dropna()
        if len(strategy_returns) > 1 and strategy_returns.std() > 0:
            sharpe = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
        else:
            sharpe = 0.0

        # Max drawdown
        if not df_signals.empty:
            cumulative = (1 + df_signals["strategy_returns"]).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
        else:
            max_drawdown = 0.0

        # Nombre de trades (changements de signal)
        signals = df_signals["signal"].dropna()
        trades_count = ((signals != signals.shift(1)) & (signals != 0)).sum()

        # Métriques supplémentaires pour analyse
        win_rate = 0.0
        avg_win = 0.0
        avg_loss = 0.0

        if trades_count > 0:
            winning_trades = df_signals[df_signals["strategy_returns"] > 0]["strategy_returns"]
            losing_trades = df_signals[df_signals["strategy_returns"] < 0]["strategy_returns"]

            if len(winning_trades) > 0:
                win_rate = len(winning_trades) / trades_count
                avg_win = winning_trades.mean()

            if len(losing_trades) > 0:
                avg_loss = losing_trades.mean()

        return {
            "total_return": float(total_return),
            "sharpe": float(sharpe),
            "max_drawdown": float(max_drawdown),
            "trades_count": int(trades_count),
            "win_rate": float(win_rate),
            "avg_win": float(avg_win),
            "avg_loss": float(avg_loss),
        }

    except Exception as e:
        logger.error(f"Erreur lors du calcul des métriques: {e}")
        raise CalculationError(f"Échec du calcul des métriques: {e}") from e


def run_backtest(strategy: StrategyAdapter, df: pd.DataFrame) -> Dict[str, float]:
    """Exécute un backtest sur une stratégie avec gestion d'erreurs robuste.

    Args:
        strategy: Instance de stratégie à tester
        df: DataFrame OHLCV avec données de marché

    Returns:
        Dictionnaire avec métriques de performance

    Raises:
        InvalidDataError: Si les données sont invalides
        StrategyExecutionError: Si la stratégie échoue
        CalculationError: Si le calcul des métriques échoue
    """
    logger.info(f"Démarrage du backtest pour la stratégie: {strategy.name}")

    # Validation des paramètres d'entrée
    if strategy is None:
        raise InvalidDataError("Stratégie non spécifiée")

    try:
        _validate_data(df)
        logger.debug("Validation des données réussie")
    except InvalidDataError:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la validation: {e}")
        raise InvalidDataError(f"Validation échouée: {e}") from e

    # Exécution de la stratégie
    try:
        logger.debug("Génération des signaux de trading")
        df_signals = strategy.generate_signals(df.copy())

        if df_signals is None or df_signals.empty:
            raise StrategyExecutionError("La stratégie n'a généré aucun signal")

        if "signal" not in df_signals.columns:
            raise StrategyExecutionError("La stratégie n'a pas retourné de colonne 'signal'")

        logger.debug(f"Signaux générés: {len(df_signals)} périodes")

    except StrategyExecutionError:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la stratégie {strategy.name}: {e}")
        raise StrategyExecutionError(f"Échec de génération des signaux: {e}") from e

    # Calcul des métriques
    try:
        logger.debug("Calcul des métriques de performance")
        metrics = _calculate_metrics(df_signals)
        logger.info(f"Backtest terminé pour {strategy.name}: "
                   f"rendement={metrics['total_return']:.2%}, "
                   f"sharpe={metrics['sharpe']:.2f}, "
                   f"drawdown_max={metrics['max_drawdown']:.2%}")
        return metrics

    except CalculationError:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors du calcul: {e}")
        raise CalculationError(f"Calcul des métriques échoué: {e}") from e
