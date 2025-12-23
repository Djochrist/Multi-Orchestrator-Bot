# Multi-Orchestrator-Bot

[![Python CI](https://github.com/Djochrist/Multi-Orchestrator-Bot/actions/workflows/python.yml/badge.svg)](https://github.com/Djochrist/Multi-Orchestrator-Bot/actions/workflows/python.yml)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Bot de trading multi-stratégies orchestré avec des algorithmes d'IA simples utilisant des données de marché réelles. Ce projet démontre une architecture claire pour l'orchestration de stratégies de trading, avec un focus sur la qualité logicielle et la reproductibilité.

## Fonctionnalités

- **Stratégies simples** : SMA Crossover, EMA Crossover, Mean Reversion
- **Orchestrateur** : Sélection déterministe de la meilleure stratégie basée sur Sharpe, retour total et drawdown
- **Backtesting** : Évaluation des stratégies sur données historiques
- **Paper Trading** : Simulation de trading sans risque réel
- **Interface CLI** : Exécution facile via ligne de commande

## Architecture

Le projet suit une architecture modulaire avec séparation claire des responsabilités :

- `orchestrator/` : Cœur du système
- `adapters/` : Interfaces avec les stratégies et échanges
- `tests/` : Suite de tests complète*
- `examples/` : Exemples d'utilisation
- `docs/` : Documentation détaillée

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/Djochrist/Multi-Orchestrator-Bot.git
cd Multi-Orchestrator-Bot

# Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Synchroniser les dépendances
uv sync

# Activer l'environnement
source .venv/bin/activate
```

## Utilisation

### Backtest

```bash
uv run python examples/run_backtest_example.py
```

### Paper Trading

```bash
uv run python -m orchestrator.cli papertrade
```

### Mode Live (Risque réel)

```bash
LIVE=true uv run python -m orchestrator.cli papertrade
```

## Développement

```bash
# Tests
uv run pytest

# Formatage
uv run black .
uv run isort .
```

## Sécurité

- **Dry-run par défaut** : Aucun trade réel sans activation explicite
- **Mock Exchange** : Simulation complète pour les tests
- **Validation stricte** : Toutes les opérations sont vérifiées

## Licence

MIT
