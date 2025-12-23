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

Téléchargement des données de marché réelles (BTC-USD)...
Données chargées: 100 points de données
Prix initial: $45000.00
Prix final: $52000.00
Rendement total du marché: 15.56%

Évaluation individuelle des stratégies:
--------------------------------------------------
Stratégie: SMA_10_50
  Rendement total: 8.45%
  Ratio Sharpe: 1.23
  Max Drawdown: -8.12%
  Nombre de trades: 15

[... autres stratégies ...]

Selection de la meilleure strategie:
--------------------------------------------------
Strategie selectionnee: EMA_12_26
  Rendement total: 12.34%
  Ratio Sharpe: 1.45
  Max Drawdown: -6.78%
  Nombre de trades: 22

=== Resume ===
Backtest termine avec succes
3 strategies evaluees
Selection deterministe basee sur Sharpe > Return > Drawdown
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
2025-12-23 10:15:44 - orchestrator.orchestrator - INFO - Évaluation de 3 stratégies sur 31 points de données
2025-12-23 10:15:44 - orchestrator.orchestrator - INFO - Stratégie sélectionnée: MeanRevBear_15_2.2
2025-12-23 10:15:44 - orchestrator.papertrader - INFO - Démarrage de la simulation sur 10 jours
[... logs de trading détaillés ...]
2025-12-23 10:15:46 - orchestrator.papertrader - INFO - === RAPPORT FINAL ===

📊 RAPPORT DE PERFORMANCE - PAPER TRADING
💰 Balance initiale: $10,000.00
💰 Balance finale: $10,286.30
📈 PnL total: $3,810.06
📊 Rendement total: +2.86%

📋 Stratégie utilisée: MeanRevBear_15_2.2
🔄 Nombre d'ordres: 8
📊 Nombre de trades: 4

🎯 Trades gagnants: 4
❌ Trades perdants: 0
🏆 Taux de réussite: 100.0%
📊 PnL moyen par trade: $71.58
```

### Mode Live (ATTENTION)

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

- [Documentation complete](api.md)
- [Architecture detaillee](architecture.md)
- Signaler un bug : [Issues GitHub](https://github.com/yourusername/multi-orchestrator-bot/issues)
