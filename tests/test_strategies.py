"""Tests pour les stratégies de trading."""

import pytest
import pandas as pd
import numpy as np

from orchestrator.adapters.simple_strategies import SMACrossover, EMACrossover, MeanReversion
from orchestrator.data_loader import generate_synthetic_data


class TestSMACrossover:
    """Tests pour la stratégie SMA Crossover."""

    def test_sma_crossover_initialization(self):
        """Test d'initialisation."""
        strategy = SMACrossover(short=5, long=10)
        assert strategy.name == "SMA_5_10"

    def test_sma_crossover_signals(self):
        """Test de génération des signaux."""
        strategy = SMACrossover(short=3, long=5)

        # Créer des données simples
        data = {
            'timestamp': pd.date_range('2023-01-01', periods=10, freq='D'),
            'open': [100] * 10,
            'high': [105] * 10,
            'low': [95] * 10,
            'close': [100, 101, 102, 103, 104, 105, 104, 103, 102, 101],
            'volume': [1000] * 10
        }
        df = pd.DataFrame(data).set_index('timestamp')

        result = strategy.generate_signals(df)

        # Vérifier que la colonne signal existe
        assert 'signal' in result.columns
        # Vérifier que les signaux sont dans {-1, 0, 1}
        assert all(result['signal'].isin([-1, 0, 1]))


class TestEMACrossover:
    """Tests pour la stratégie EMA Crossover."""

    def test_ema_crossover_initialization(self):
        """Test d'initialisation."""
        strategy = EMACrossover(short=5, long=10)
        assert strategy.name == "EMA_5_10"

    def test_ema_crossover_signals(self):
        """Test de génération des signaux."""
        strategy = EMACrossover()

        df = generate_synthetic_data(days=20)
        result = strategy.generate_signals(df)

        assert 'signal' in result.columns
        assert all(result['signal'].isin([-1, 0, 1]))


class TestMeanReversion:
    """Tests pour la stratégie Mean Reversion."""

    def test_mean_reversion_initialization(self):
        """Test d'initialisation."""
        strategy = MeanReversion(lookback=15, z_thresh=2.0)
        assert strategy.name == "MeanRev_15_2.0"

    def test_mean_reversion_signals(self):
        """Test de génération des signaux."""
        strategy = MeanReversion(lookback=5, z_thresh=1.0)

        # Créer des données avec une forte déviation
        data = {
            'timestamp': pd.date_range('2023-01-01', periods=10, freq='D'),
            'open': [100] * 10,
            'high': [105] * 10,
            'low': [95] * 10,
            'close': [100, 100, 100, 100, 100, 110, 100, 100, 100, 100],  # Spike puis retour
            'volume': [1000] * 10
        }
        df = pd.DataFrame(data).set_index('timestamp')

        result = strategy.generate_signals(df)

        assert 'signal' in result.columns
        assert 'z_score' in result.columns
        assert all(result['signal'].isin([-1, 0, 1]))

        # Vérifier qu'un signal de vente est généré au spike
        spike_signals = result[result['close'] == 110]['signal']
        if not spike_signals.empty:
            assert spike_signals.iloc[0] == -1  # Vendre le spike élevé
