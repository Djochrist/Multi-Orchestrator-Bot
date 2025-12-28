# 📝 Référence des Modèles

Documentation complète des modèles de données utilisés dans Multi-Orchestrator-Bot.

## Vue d'ensemble

L'application utilise des dataclasses Python pour représenter les entités métier. Tous les modèles héritent de `BaseModel` qui fournit les champs communs.

### Architecture

```
BaseModel (champs communs)
├── Strategy (stratégies de trading)
└── Trade (transactions)
```

## BaseModel

Classe de base pour tous les modèles, fournissant les champs standards.

### Attributs

| Attribut | Type | Description | Défaut |
|----------|------|-------------|---------|
| `id` | `int` | Identifiant unique | Timestamp-based |
| `created_at` | `datetime` | Date de création | `datetime.now()` |
| `updated_at` | `datetime` | Date de modification | `datetime.now()` |

### Méthodes

#### `to_dict() -> Dict[str, Any]`

Convertit l'instance en dictionnaire pour la sérialisation JSON.

```python
strategy = Strategy(name="Test", type="rsi")
data = strategy.to_dict()
# {
#   "id": 123456,
#   "name": "Test",
#   "type": "rsi",
#   "created_at": "2024-01-01T10:00:00Z",
#   "updated_at": "2024-01-01T10:00:00Z"
# }
```

#### `update(**kwargs) -> None`

Met à jour les attributs de l'instance et actualise `updated_at`.

```python
strategy.update(name="Nouvelle Stratégie", status="active")
# updated_at automatiquement mis à jour
```

## Strategy

Modèle représentant une stratégie de trading algorithmique.

### Attributs

| Attribut | Type | Description | Défaut |
|----------|------|-------------|---------|
| `name` | `str` | Nom de la stratégie | `""` |
| `description` | `str` | Description détaillée | `""` |
| `type` | `str` | Type de stratégie | `"manual"` |
| `status` | `str` | État de la stratégie | `"inactive"` |
| `config` | `Dict[str, Any]` | Configuration spécifique | `{}` |
| `performance` | `Dict[str, Any]` | Métriques de performance | `{}` |

### Types de stratégies

#### Manual (`"manual"`)
Stratégie contrôlée manuellement par l'utilisateur.

#### RSI (`"rsi"`)
Stratégie basée sur l'indicateur Relative Strength Index.

**Configuration** :
```python
{
    "period": 14,           # Période de calcul RSI
    "overbought": 70,       # Seuil de surachat
    "oversold": 30,         # Seuil de survente
    "min_volume": 1000      # Volume minimum requis
}
```

#### MACD (`"macd"`)
Stratégie basée sur le croisement des moyennes mobiles.

**Configuration** :
```python
{
    "fast_period": 12,      # Période EMA rapide
    "slow_period": 26,      # Période EMA lente
    "signal_period": 9,     # Période de signal
    "threshold": 0.001      # Seuil de croisement
}
```

#### ML (`"ml"`)
Stratégie basée sur l'apprentissage automatique (future).

### Statuts

- `"active"` : Stratégie en cours d'exécution
- `"inactive"` : Stratégie arrêtée

### Méthodes

#### `is_active() -> bool`

Vérifie si la stratégie est active.

```python
if strategy.is_active():
    print("Stratégie en cours d'exécution")
```

#### `activate() -> None`

Active la stratégie.

```python
strategy.activate()
assert strategy.status == "active"
```

#### `deactivate() -> None`

Désactive la stratégie.

```python
strategy.deactivate()
assert strategy.status == "inactive"
```

#### `update_performance(pnl: float, win_rate: float, **metrics) -> None`

Met à jour les métriques de performance.

```python
strategy.update_performance(
    pnl=1250.50,
    win_rate=0.65,
    total_trades=100,
    avg_trade_duration=2.5
)
```

#### Propriétés

##### `total_pnl -> float`

Retourne le PnL total depuis les performances.

##### `win_rate -> float`

Retourne le taux de réussite depuis les performances.

## Trade

Modèle représentant une transaction de trading.

### Attributs

| Attribut | Type | Description | Défaut |
|----------|------|-------------|---------|
| `strategy_id` | `Optional[int]` | ID de la stratégie associée | `None` |
| `symbol` | `str` | Symbole de l'actif | `""` |
| `side` | `str` | Côté de la transaction | `"buy"` |
| `quantity` | `float` | Quantité échangée | `0.0` |
| `entry_price` | `float` | Prix d'entrée | `0.0` |
| `exit_price` | `Optional[float]` | Prix de sortie | `None` |
| `entry_time` | `datetime` | Heure d'entrée | `datetime.now()` |
| `exit_time` | `Optional[datetime]` | Heure de sortie | `None` |
| `status` | `str` | Statut du trade | `"open"` |
| `pnl` | `Optional[float]` | Profit/Perte | `None` |
| `fees` | `float` | Frais de transaction | `0.0` |
| `notes` | `str` | Notes additionnelles | `""` |

### Côtés de transaction

- `"buy"` : Achat (long position)
- `"sell"` : Vente (short position)

### Statuts

- `"open"` : Trade en cours
- `"closed"` : Trade terminé avec succès
- `"cancelled"` : Trade annulé

### Propriétés

#### `is_open -> bool`

Vérifie si le trade est ouvert.

```python
if trade.is_open:
    print("Position ouverte")
```

#### `is_closed -> bool`

Vérifie si le trade est fermé.

```python
if trade.is_closed:
    print(f"PnL: {trade.pnl}")
```

### Méthodes

#### `close_trade(exit_price: float, exit_time: Optional[datetime] = None) -> None`

Ferme le trade et calcule le PnL.

```python
# Trade d'achat fermé à profit
trade = Trade(symbol="BTC", side="buy", quantity=1.0, entry_price=50000)
trade.close_trade(exit_price=55000)
print(f"PnL: {trade.pnl}")  # 5000.0

# Trade de vente fermé à profit
trade = Trade(symbol="BTC", side="sell", quantity=1.0, entry_price=55000)
trade.close_trade(exit_price=50000)
print(f"PnL: {trade.pnl}")  # 5000.0
```

**Calcul du PnL** :
- **Achat** : `(exit_price - entry_price) * quantity`
- **Vente** : `(entry_price - exit_price) * quantity`

#### `cancel_trade() -> None`

Annule le trade sans calculer de PnL.

```python
trade.cancel_trade()
assert trade.status == "cancelled"
assert trade.exit_time is not None
```

## Exemples d'utilisation

### Création d'une stratégie

```python
from src.models import Strategy

# Stratégie RSI
rsi_strategy = Strategy(
    name="RSI Momentum Trader",
    description="Stratégie basée sur RSI avec confirmation volume",
    type="rsi",
    config={
        "period": 14,
        "overbought": 70,
        "oversold": 30,
        "min_volume": 10000
    }
)

# Activation
rsi_strategy.activate()
print(f"Stratégie {rsi_strategy.name} activée")
```

### Création et fermeture d'un trade

```python
from src.models import Trade

# Trade d'achat
trade = Trade(
    strategy_id=rsi_strategy.id,
    symbol="BTC",
    side="buy",
    quantity=0.5,
    entry_price=45000.0,
    notes="Signal RSI survente"
)

print(f"Trade ouvert: {trade.symbol} {trade.side} {trade.quantity} @ {trade.entry_price}")

# Fermeture profitable
trade.close_trade(exit_price=47000.0)

print(f"Trade fermé - PnL: ${trade.pnl}")
print(f"Status: {trade.status}")
```

### Sérialisation

```python
# Conversion en dict pour l'API
strategy_dict = strategy.to_dict()
trade_dict = trade.to_dict()

# Structure JSON
{
  "id": 123456,
  "name": "RSI Momentum Trader",
  "type": "rsi",
  "status": "active",
  "config": {...},
  "performance": {...},
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

## Validation et contraintes

### Contraintes de validation

- **ID** : Généré automatiquement, unique
- **Noms** : Chaînes non vides pour les stratégies
- **Prix** : Valeurs positives pour entry_price, exit_price
- **Quantité** : Valeur positive
- **Types** : Valeurs énumérées (strategy types, trade sides, statuses)

### Types supportés

- **Symboles** : BTC, ETH, SOL, AAPL, TSLA, etc.
- **Devises** : USD (principalement)
- **Quantités** : Décimales pour crypto, entiers pour actions

## Évolutions futures

### Nouveaux modèles

#### `Portfolio`
Gestion de portefeuille multi-actifs.

#### `Order`
Ordres limit/stop avancés.

#### `Alert`
Système d'alertes et notifications.

### Extensions

#### Historique des modifications
```python
@dataclass
class AuditableModel(BaseModel):
    created_by: str = ""
    updated_by: str = ""
    version: int = 1
```

#### Relations
```python
@dataclass
class Trade(BaseModel):
    strategy: Strategy = None  # Relation directe
```

#### Validation avancée
```python
from pydantic import validator

class ValidatedStrategy(Strategy):
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Le nom ne peut pas être vide')
        return v
```

---

**Modèles compris ?** Découvrez l'[architecture de l'API](../architecture/api.md) ou les [tests](../architecture/testing.md).
