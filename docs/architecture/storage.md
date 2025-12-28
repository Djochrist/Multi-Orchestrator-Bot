# 💾 Architecture du Stockage

Découvrez le système de stockage en mémoire de Multi-Orchestrator-Bot et ses possibilités d'extension.

## Vue d'ensemble

Le système de stockage utilise actuellement une implémentation en mémoire thread-safe, conçue pour être facilement extensible vers des bases de données persistantes.

### Caractéristiques principales

- **Thread-safe** : Accès concurrent sécurisé avec verrous
- **Générique** : Interface commune pour tous les types de données
- **Extensible** : Architecture permettant la migration facile
- **Performant** : Accès O(1) pour les opérations CRUD de base

### Architecture

```
Interface: InMemoryStorage[T]
├── Thread Safety (Lock)
├── Data Storage (Dict[int, T])
├── ID Generation (Auto-increment)
└── CRUD Operations
```

## Interface de stockage

### Classe générique `InMemoryStorage[T]`

```python
class InMemoryStorage(Generic[T]):
    def create(self, item: T) -> T
    def get(self, item_id: int) -> Optional[T]
    def get_all(self) -> List[T]
    def update(self, item_id: int, item: T) -> Optional[T]
    def delete(self, item_id: int) -> bool
    def find_by(self, **kwargs) -> List[T]
    def clear(self) -> None
```

### Méthodes principales

#### create(item: T) -> T

Crée un nouvel élément dans le stockage.

- **Génération automatique d'ID** : Incrémentation automatique
- **Thread-safe** : Verrouillage pendant l'opération
- **Validation** : Vérification de l'unicité de l'ID

```python
strategy = Strategy(name="Nouvelle Stratégie", type="manual")
created = strategies_storage.create(strategy)
print(f"ID généré: {created.id}")  # ID auto-généré
```

#### get(item_id: int) -> Optional[T]

Récupère un élément par son ID.

- **Accès O(1)** : Recherche directe par clé
- **Type-safe** : Retourne le type générique approprié
- **Null-safe** : Retourne None si non trouvé

#### get_all() -> List[T]

Récupère tous les éléments.

- **Copie défensive** : Retourne une nouvelle liste
- **Thread-safe** : Instantané cohérent des données
- **Ordre non garanti** : Utiliser le tri si nécessaire

#### update(item_id: int, item: T) -> Optional[T]

Met à jour un élément existant.

- **Mise à jour automatique des timestamps** : `updated_at`
- **Validation d'existence** : Vérifie que l'élément existe
- **Thread-safe** : Opération atomique

#### delete(item_id: int) -> bool

Supprime un élément.

- **Suppression logique possible** : Extension future
- **Cascade** : Gestion des relations (future)
- **Retour booléen** : Succès/échec de l'opération

#### find_by(**kwargs) -> List[T]

Recherche flexible par attributs.

- **Filtrage multiple** : Plusieurs critères AND
- **Performance** : Scan linéaire (O(n))
- **Flexible** : Supporte tous les attributs

```python
# Trouver toutes les stratégies actives
active_strategies = strategies_storage.find_by(status="active")

# Trouver les stratégies RSI
rsi_strategies = strategies_storage.find_by(type="rsi")
```

## Instances de stockage

### Stockage global

```python
# Instances singleton
strategies_storage: InMemoryStorage[Strategy]
trades_storage: InMemoryStorage[Trade]
```

### Initialisation

```python
from src.storage import strategies_storage, trades_storage

# Utilisation directe
strategies = strategies_storage.get_all()
trades = trades_storage.get_all()
```

## Données d'exemple

### Fonction d'initialisation

```python
def initialize_sample_data():
    """Initialise des données d'exemple pour développement"""

    # Stratégie RSI
    rsi_strategy = Strategy(
        name="RSI Momentum",
        description="Stratégie basée sur RSI",
        type="rsi",
        status="active",
        config={"rsi_period": 14, "overbought": 70, "oversold": 30},
        performance={"total_pnl": 1250.50, "win_rate": 65.0}
    )
    strategies_storage.create(rsi_strategy)

    # Trade associé
    trade = Trade(
        strategy_id=rsi_strategy.id,
        symbol="BTC",
        side="buy",
        quantity=0.5,
        entry_price=92000.0,
        status="closed",
        pnl=1250.0
    )
    trade.close_trade(94500.0)
    trades_storage.create(trade)
```

### Données mockées

- **2 stratégies** : RSI active, MACD inactive
- **1 trade** : Position fermée avec PnL positif
- **Performances** : Métriques réalistes pour les tests

## Thread Safety

### Mécanisme de verrouillage

```python
class InMemoryStorage(Generic[T]):
    def __init__(self):
        self._lock = Lock()  # Verrou réentrant

    def create(self, item: T) -> T:
        with self._lock:  # Section critique
            # Opération atomique
            pass
```

### Opérations atomiques

- **Création** : Génération ID + stockage
- **Mise à jour** : Validation + modification
- **Suppression** : Vérification + retrait
- **Lecture** : Accès cohérent aux données

### Performance

- **Verrous fins** : Pas de verrou global
- **Lectures concurrentes** : Plusieurs readers simultanés
- **Écritures séquentielles** : Un writer à la fois

## Extension vers base de données

### Interface commune

```python
class StorageInterface(Protocol[T]):
    def create(self, item: T) -> T: ...
    def get(self, item_id: int) -> Optional[T]: ...
    def get_all(self) -> List[T]: ...
    def update(self, item_id: int, item: T) -> Optional[T]: ...
    def delete(self, item_id: int) -> bool: ...
    def find_by(self, **kwargs) -> List[T]: ...
```

### Implémentation SQLAlchemy

```python
class SQLAlchemyStorage(StorageInterface[T]):
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
        self.session = get_session()

    def create(self, item: T) -> T:
        db_item = self.model_class(**item.dict())
        self.session.add(db_item)
        self.session.commit()
        return db_item

    def get(self, item_id: int) -> Optional[T]:
        return self.session.query(self.model_class).get(item_id)
```

### Migration transparente

```python
# Remplacement à chaud
from database_storage import DatabaseStorage

strategies_storage = DatabaseStorage[Strategy](StrategyModel)
trades_storage = DatabaseStorage[Trade](TradeModel)

# Code existant inchangé
strategies = strategies_storage.get_all()
```

## Persistance des données

### Sauvegarde périodique

```python
import json
from pathlib import Path

def save_to_file(storage: InMemoryStorage, filename: str):
    """Sauvegarde les données dans un fichier JSON"""
    data = [item.dict() for item in storage.get_all()]
    Path(filename).write_text(json.dumps(data, indent=2, default=str))

def load_from_file(storage: InMemoryStorage, filename: str, model_class):
    """Charge les données depuis un fichier JSON"""
    if Path(filename).exists():
        data = json.loads(Path(filename).read_text())
        for item_data in data:
            item = model_class(**item_data)
            storage.create(item)
```

### Points de sauvegarde

- **À l'arrêt** : Sauvegarde automatique
- **Périodique** : Toutes les 5 minutes
- **Sur modification** : Après chaque écriture
- **Manuel** : Endpoint API pour déclenchement

## Optimisations futures

### Cache

```python
from functools import lru_cache

class CachedStorage(InMemoryStorage[T]):
    @lru_cache(maxsize=1000)
    def get(self, item_id: int) -> Optional[T]:
        return super().get(item_id)
```

### Indexation

```python
class IndexedStorage(InMemoryStorage[T]):
    def __init__(self):
        super().__init__()
        self._indexes: Dict[str, Dict[Any, List[T]]] = {}

    def create_index(self, field: str):
        """Crée un index sur un champ"""
        self._indexes[field] = {}
        for item in self.get_all():
            value = getattr(item, field)
            if value not in self._indexes[field]:
                self._indexes[field][value] = []
            self._indexes[field][value].append(item)
```

### Partitionnement

```python
class PartitionedStorage(InMemoryStorage[T]):
    def __init__(self, partitions: int = 4):
        self._partitions = [InMemoryStorage[T]() for _ in range(partitions)]

    def _get_partition(self, item_id: int) -> InMemoryStorage[T]:
        return self._partitions[item_id % len(self._partitions)]
```

## Tests du stockage

### Tests unitaires

```python
def test_storage_operations():
    storage = InMemoryStorage[Strategy]()

    # Test création
    strategy = Strategy(name="Test", type="manual")
    created = storage.create(strategy)
    assert created.id == 1

    # Test récupération
    retrieved = storage.get(1)
    assert retrieved.name == "Test"

    # Test mise à jour
    strategy.name = "Updated"
    updated = storage.update(1, strategy)
    assert updated.name == "Updated"

    # Test suppression
    assert storage.delete(1) == True
    assert storage.get(1) is None
```

### Tests de performance

```python
def test_concurrent_access():
    storage = InMemoryStorage[Strategy]()
    import threading

    def worker():
        for i in range(100):
            strategy = Strategy(name=f"Strategy {i}", type="manual")
            storage.create(strategy)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(storage.get_all()) == 1000
```

## Métriques et monitoring

### Métriques exposées

```python
class MonitoredStorage(InMemoryStorage[T]):
    def __init__(self):
        super().__init__()
        self.operations_count = 0
        self.average_response_time = 0.0

    def get_metrics(self):
        return {
            "total_items": len(self._data),
            "operations_count": self.operations_count,
            "memory_usage": sys.getsizeof(self._data),
            "average_response_time": self.average_response_time
        }
```

### Alertes

- **Utilisation mémoire** : Seuil d'alerte à 80%
- **Temps de réponse** : Alertes sur dégradation
- **Taux d'erreur** : Monitoring des échecs d'opération

---

**Stockage maîtrisé ?** Découvrez les [modèles de données](../reference/models.md) ou les [tests](../architecture/testing.md).
