# Comment Exécuter le Projet

## Prérequis

- **Python 3.10+**
- **uv** pour la gestion des dépendances ([Installation](https://github.com/astral-sh/uv))

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/Djochrist/Multi-Orchestrator-Bot.git
cd Multi-Orchestrator-Bot
```

### 2. Installer uv (si pas déjà fait)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Synchroniser les dépendances

```bash
uv sync
```

### 4. Activer l'environnement virtuel

```bash
source .venv/bin/activate
```

## Utilisation

### Backtest Simple

Exécutez l'exemple de backtest pour voir les performances des stratégies :

```bash
uv run python examples/run_backtest_example.py
```

**Sortie attendue :**
```
=== Exemple de Backtest Multi-Stratégies ===

Génération des données de test...
Données générées: 100 points de données
Prix initial: $50000.00
Prix final: $51234.56
Rendement total du marché: 2.47%

Évaluation individuelle des stratégies:
--------------------------------------------------
Stratégie: SMA_10_50
  Rendement total: 1.23%
  Ratio Sharpe: 0.85
  Max Drawdown: -3.45%
  Nombre de trades: 12

[... autres stratégies ...]

Sélection de la meilleure stratégie:
--------------------------------------------------
🏆 Stratégie sélectionnée: EMA_12_26
  Rendement total: 2.10%
  Ratio Sharpe: 1.15
  Max Drawdown: -2.30%
  Nombre de trades: 8

=== Résumé ===
✅ Backtest terminé avec succès
📊 3 stratégies évaluées
🎯 Sélection déterministe basée sur Sharpe > Return > Drawdown
```

### Paper Trading

Simulez du trading en temps réel avec la stratégie sélectionnée :

```bash
uv run python -m orchestrator.cli papertrade --days 10 --quantity 0.01
```

**Paramètres :**
- `--days` : Nombre de jours à simuler (défaut: 10)
- `--quantity` : Quantité à trader par ordre (défaut: 0.01)

**Sortie attendue :**
```
2025-12-22 15:30:27 - orchestrator.orchestrator - INFO - Évaluation de 3 stratégies sur 30 points de données
2025-12-22 15:30:27 - orchestrator.orchestrator - INFO - Stratégie sélectionnée: MeanRev_20_1.5
2025-12-22 15:30:27 - orchestrator.papertrader - INFO - Démarrage de la simulation sur 10 jours
2025-12-22 15:30:27 - orchestrator.mock_exchange - INFO - Ordre exécuté: buy 0.01 BTC/USD @ 51234.56
[... logs de trading ...]
2025-12-22 15:30:27 - orchestrator.papertrader - INFO - === RAPPORT FINAL ===
2025-12-22 15:30:27 - orchestrator.papertrader - INFO - Balance finale: 10015.67
2025-12-22 15:30:27 - orchestrator.papertrader - INFO - PnL total: 15.67
2025-12-22 15:30:27 - orchestrator.papertrader - INFO - Stratégie utilisée: MeanRev_20_1.5
2025-12-22 15:30:27 - orchestrator.papertrader - INFO - Nombre d'ordres: 4
```

### Mode Live (⚠️ ATTENTION)

**DANGER :** Le mode live exécute des ordres réels sur un échange !

```bash
# DÉFINIR LA VARIABLE D'ENVIRONNEMENT
export LIVE=true

# Configurer les clés API (dans un fichier séparé, JAMAIS dans le code)
# Créer config.yml avec vos clés API

# Exécuter en mode live
uv run python -m orchestrator.cli papertrade --live
```

**Prérequis pour le mode live :**
1. Compte sur un échange supporté par CCXT (Binance, etc.)
2. Clés API configurées
3. Fonds suffisants sur le compte
4. **TESTER D'ABORD EN SANDBOX**

## Tests

### Exécuter tous les tests

```bash
uv run pytest
```

### Tests avec couverture

```bash
uv run pytest --cov=orchestrator --cov-report=html
```

### Tests spécifiques

```bash
# Tests des stratégies
uv run pytest tests/test_strategies.py -v

# Tests du backtest
uv run pytest tests/test_backtest.py -v

# Tests de l'orchestrateur
uv run pytest tests/test_orchestrator.py -v

# Tests du paper trader
uv run pytest tests/test_papertrader.py -v
```

## Développement

### Formatage du code

```bash
# Formatter
uv run black .

# Organiser les imports
uv run isort .
```

### Vérification du type (si mypy ajouté)

```bash
uv run mypy src/
```

### Pré-commit (si configuré)

```bash
uv run pre-commit run --all-files
```

## Configuration

### Variables d'environnement

- `LIVE=true` : Active le mode trading réel
- `LOG_LEVEL=DEBUG` : Niveau de logging détaillé

### Fichier de configuration

Copiez `examples/config.example.yml` vers `config.yml` et ajustez :

```yaml
general:
  log_level: INFO
  dry_run: true

trading:
  symbol: BTC/USD
  default_quantity: 0.01

exchanges:
  binance:
    api_key: your_api_key
    api_secret: your_api_secret
    sandbox: true
```

## Dépannage

### Erreur "Module not found"

Assurez-vous d'avoir activé l'environnement virtuel :

```bash
source .venv/bin/activate
```

### Erreur "uv command not found"

Réinstallez uv :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Tests qui échouent

Vérifiez que toutes les dépendances sont installées :

```bash
uv sync
```

### Performance lente

- Réduisez le nombre de jours dans les simulations
- Vérifiez que numpy/pandas utilisent les optimisations

## Structure du Projet

```
multi-orchestrator-bot/
├── src/orchestrator/          # Code source
│   ├── adapters/              # Adaptateurs stratégies/échanges
│   ├── *.py                   # Modules principaux
├── tests/                     # Tests unitaires
├── examples/                  # Exemples d'utilisation
├── docs/                      # Documentation
├── pyproject.toml             # Configuration uv
└── README.md                  # Documentation principale
```

## Support

- 📖 [Documentation complète](api.md)
- 🏗️ [Architecture détaillée](architecture.md)
- 🐛 Signaler un bug : [Issues GitHub](https://github.com/yourusername/multi-orchestrator-bot/issues)
