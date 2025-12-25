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

```

## Utilisation

### Point d'entrée principal

```bash
python main.py papertrade --days 10 --quantity 0.01
```

### Backtest

```bash
python main.py backtest --symbol BTC-USD --days 100
```

### Paper Trading

```bash
python main.py papertrade --days 10 --quantity 0.01
```

### Mode Live (Risque réel)

**ATTENTION: Le mode live n'est pas encore implémenté pour des raisons de sécurité.**

```bash
# Cette commande échouera actuellement
LIVE=true python main.py papertrade --days 10 --quantity 0.01
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
