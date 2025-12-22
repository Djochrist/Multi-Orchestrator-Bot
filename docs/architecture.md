# Architecture du Projet

## Vue d'ensemble

Le projet **Multi-Orchestrator-Bot** suit une architecture modulaire et orientée objet, conçue pour la séparation claire des responsabilités et la facilité de maintenance.

## Diagramme ASCII

```
┌─────────────────────────────────────────────────────────────┐
│                    MULTI-ORCHESTRATOR-BOT                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
           ┌──────────▼──────────┐
           │   ORCHESTRATEUR     │
           │                     │
           │ • Sélection de la    │
           │   meilleure stratégie│
           │ • Backtest automatique│
           │ • Critères: Sharpe > │
           │   Return > Drawdown │
           └──────────┬──────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
   ┌──────▼────┐ ┌────▼────┐ ┌────▼────┐
   │ STRATÉGIES │ │DONNÉES  │ │  TRADER  │
   │ SIMPLES    │ │         │ │  PAPIER  │
   │            │ │• Charg. │ │          │
   │• SMA Cross │ │  données│ │• Simulation│
   │• EMA Cross │ │• Synth. │ │  trades   │
   │• Mean Rev. │ │  ou API │ │• Mock      │
   └────────────┘ └─────────┘ │  Exchange │
                              └──────────┘
```

## Flux de Données

### 1. Phase d'Initialisation

```
Données Récentes (30j) → Orchestrateur → Évaluation Stratégies → Sélection Meilleure
```

### 2. Phase de Trading

```
Stratégie Sélectionnée → Paper Trader → Génération Signaux → Mock Exchange → Simulation PnL
```

### 3. Métriques de Performance

```
Trades + Prix → Calcul Rendements → Sharpe, Drawdown, Retour Total → Classement
```

## Composants Principaux

### Orchestrateur (`orchestrator.py`)

**Responsabilités :**
- Gestion du cycle de vie des stratégies
- Exécution des backtests
- Sélection déterministe de la meilleure stratégie
- Coordination entre composants

**Interfaces :**
- `select_best_strategy() → StrategyAdapter`
- `get_all_strategies() → List[StrategyAdapter]`

### Stratégies (`adapters/simple_strategies.py`)

**Interface commune :**
```python
class StrategyAdapter(Protocol):
    @property
    def name(self) -> str: ...
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame: ...
```

**Stratégies implémentées :**
- **SMACrossover** : Croisement moyennes mobiles simples
- **EMACrossover** : Croisement moyennes mobiles exponentielles
- **MeanReversion** : Retour à la moyenne (Z-Score)

### Backtest Runner (`backtest_runner.py`)

**Métriques calculées :**
- **Rendement total** : `(prix_final / prix_initial) - 1`
- **Ratio Sharpe** : `moyenne_rendements / écart_type_rendements * √252`
- **Drawdown maximum** : `min(cumulative_returns - rolling_max)`
- **Nombre de trades** : Comptage des changements de signal

### Paper Trader (`papertrader.py`)

**Fonctionnement :**
- Simulation temporelle (barre par barre)
- Génération de signaux en continu
- Exécution d'ordres sur Mock Exchange
- Suivi PnL en temps réel

### Mock Exchange (`adapters/mock_exchange.py`)

**Fonctionnalités :**
- Simulation d'ordres market/limit
- Gestion de positions et balance
- Calcul PnL réalisé/non réalisé
- Historique des transactions

## Principes de Conception

### 1. Séparation des Responsabilités

Chaque module a une responsabilité unique :
- **Data** : Chargement et préparation des données
- **Strategy** : Logique de génération de signaux
- **Backtest** : Évaluation des performances
- **Orchestrator** : Coordination et décision
- **Exchange** : Interface de trading

### 2. Inversion de Dépendances

Les stratégies dépendent d'interfaces, pas d'implémentations concrètes :
- `StrategyAdapter` définit le contrat
- Orchestrateur travaille avec l'interface
- Facilite l'ajout de nouvelles stratégies

### 3. Configuration Centralisée

- `config.py` : Paramètres par défaut
- Possibilité d'override via variables d'environnement
- Séparation configuration/code

### 4. Testabilité

- Données synthétiques pour tests déterministes
- Mock Exchange pour isolation
- Tests unitaires complets

## Sécurité

### Dry-Run par Défaut

- **JAMAIS** de trading réel sans activation explicite
- Variable d'environnement `LIVE=true` requise
- Mock Exchange utilisé par défaut

### Validation

- Vérification des paramètres d'entrée
- Contrôle des limites de risque
- Logging complet des opérations

## Extensibilité

### Ajout de Stratégies

```python
class NewStrategy(StrategyAdapter):
    @property
    def name(self) -> str:
        return "NouvelleStratégie"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        # Implémentation
        pass
```

### Intégration Échange Réel

- `CCXTExecutor` pour échanges supportés par CCXT
- Interface commune avec MockExchange
- Configuration API externe sécurisée

## Performance

### Optimisations

- Calculs vectoriels avec pandas/numpy
- Évaluation paresseuse des stratégies
- Cache des données récurrentes

### Limites

- Données en mémoire (pas de streaming)
- Calculs synchrones (pas d'async)
- Métriques simples (pas de risk-adjusted avancées)
