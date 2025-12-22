"""Exécution des backtests pour évaluation des stratégies."""

import numpy as np
import pandas as pd
from typing import Dict

from .strategy_interface import StrategyAdapter


def run_backtest(strategy: StrategyAdapter, df: pd.DataFrame) -> Dict[str, float]:
    """Exécute un backtest sur une stratégie.

    Args:
        strategy: Instance de stratégie
        df: DataFrame OHLCV

    Returns:
        Dictionnaire avec métriques: total_return, sharpe, max_drawdown, trades_count
    """
    # Générer les signaux
    df_signals = strategy.generate_signals(df)

    # Calculer les rendements
    df_signals['returns'] = df_signals['close'].pct_change()
    df_signals['strategy_returns'] = df_signals['returns'] * df_signals['signal'].shift(1)

    # Calculer le PnL cumulé
    df_signals['cumulative_returns'] = (1 + df_signals['strategy_returns']).cumprod() - 1

    # Métriques
    total_return = df_signals['cumulative_returns'].iloc[-1] if not df_signals.empty else 0.0

    # Sharpe ratio (annualisé, rf=0)
    strategy_returns = df_signals['strategy_returns'].dropna()
    if len(strategy_returns) > 1:
        std_returns = strategy_returns.std()
        if std_returns > 0:
            sharpe = strategy_returns.mean() / std_returns * np.sqrt(252)
        else:
            sharpe = 0.0
    else:
        sharpe = 0.0

    # Max drawdown
    cumulative = (1 + df_signals['strategy_returns']).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min() if not drawdown.empty else 0.0

    # Nombre de trades (changements de signal)
    signals = df_signals['signal'].dropna()
    trades_count = ((signals != signals.shift(1)) & (signals != 0)).sum()

    return {
        "total_return": float(total_return),
        "sharpe": float(sharpe),
        "max_drawdown": float(max_drawdown),
        "trades_count": int(trades_count)
    }
