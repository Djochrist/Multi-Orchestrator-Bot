# 🧪 Architecture des Tests

Découvrez la stratégie de tests de Multi-Orchestrator-Bot et les bonnes pratiques de test.

## Vue d'ensemble

La stratégie de tests suit une approche pyramidale avec trois niveaux de tests :

- **Tests unitaires** : Logique métier isolée
- **Tests d'intégration** : API et interactions
- **Tests end-to-end** : Parcours utilisateur complet

### Métriques de couverture

- **Couverture cible** : 80% minimum
- **Tests critiques** : 100% pour la logique de trading
- **Performance** : Tests en < 30 secondes

## Tests unitaires

### Structure des tests

```
tests/
├── __init__.py
├── test_models.py     # Tests des modèles de données
├── test_storage.py    # Tests du système de stockage
├── test_api.py        # Tests d'intégration API
└── test_e2e.py        # Tests end-to-end (futur)
```

### Tests de modèles

#### TestStrategyModel

```python
class TestStrategyModel:
    def test_strategy_creation(self):
        """Test création d'une stratégie"""
        strategy = Strategy(
            name="Test Strategy",
            description="Description test",
            type="rsi",
            config={"period": 14}
        )

        assert strategy.name == "Test Strategy"
        assert strategy.type == "rsi"
        assert strategy.status == "inactive"
        assert not strategy.is_active()

    def test_strategy_activation(self):
        """Test activation/désactivation"""
        strategy = Strategy(name="Test", type="rsi")

        assert not strategy.is_active()
        strategy.activate()
        assert strategy.is_active()
        assert strategy.status == "active"

        strategy.deactivate()
        assert not strategy.is_active()
        assert strategy.status == "inactive"
```

#### TestTradeModel

```python
class TestTradeModel:
    def test_trade_creation(self):
        """Test création d'un trade"""
        trade = Trade(
            symbol="BTC",
            side="buy",
            quantity=0.5,
            entry_price=50000.0
        )

        assert trade.symbol == "BTC"
        assert trade.side == "buy"
        assert trade.quantity == 0.5
        assert trade.entry_price == 50000.0
        assert trade.status == "open"
        assert trade.is_open

    def test_trade_close(self):
        """Test fermeture d'un trade"""
        trade = Trade(
            symbol="BTC",
            side="buy",
            quantity=1.0,
            entry_price=50000.0
        )

        trade.close_trade(exit_price=55000.0)

        assert trade.exit_price == 55000.0
        assert trade.status == "closed"
        assert trade.pnl == 5000.0  # (55000 - 50000) * 1.0
        assert trade.is_closed
```

### Tests de stockage

#### TestInMemoryStorage

```python
class TestInMemoryStorage:
    def test_create_and_retrieve(self):
        """Test création et récupération"""
        storage = InMemoryStorage[Strategy]()

        strategy = Strategy(name="Test", type="manual")
        created = storage.create(strategy)

        assert created.id == 1
        retrieved = storage.get(1)
        assert retrieved.name == "Test"

    def test_update_strategy(self):
        """Test mise à jour"""
        storage = InMemoryStorage[Strategy]()

        strategy = Strategy(name="Original", type="manual")
        created = storage.create(strategy)

        strategy.name = "Updated"
        updated = storage.update(created.id, strategy)

        assert updated.name == "Updated"

    def test_delete_strategy(self):
        """Test suppression"""
        storage = InMemoryStorage[Strategy]()

        strategy = Strategy(name="Test", type="manual")
        created = storage.create(strategy)

        assert storage.delete(created.id) == True
        assert storage.get(created.id) is None

    def test_find_by_attribute(self):
        """Test recherche par attribut"""
        storage = InMemoryStorage[Strategy]()

        rsi_strategy = Strategy(name="RSI", type="rsi")
        macd_strategy = Strategy(name="MACD", type="macd")

        storage.create(rsi_strategy)
        storage.create(macd_strategy)

        rsi_strategies = storage.find_by(type="rsi")
        assert len(rsi_strategies) == 1
        assert rsi_strategies[0].type == "rsi"
```

## Tests d'intégration

### Configuration des tests

#### TestClient FastAPI

```python
import pytest
from fastapi.testclient import TestClient

from src.main import create_application
from src.storage import strategies_storage, trades_storage

@pytest.fixture
def client():
    """Client de test FastAPI"""
    app = create_application()
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_storage():
    """Vide le stockage avant chaque test"""
    strategies_storage.clear()
    trades_storage.clear()
```

### Tests API

#### TestStrategiesAPI

```python
class TestStrategiesAPI:
    def test_get_strategies_empty(self, client):
        """Test récupération stratégies vides"""
        response = client.get("/strategies")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_strategy(self, client):
        """Test création stratégie"""
        data = {
            "name": "Test RSI",
            "description": "Stratégie de test",
            "type": "rsi",
            "config": {"period": 14}
        }

        response = client.post("/strategies", json=data)
        assert response.status_code == 201

        result = response.json()
        assert result["name"] == "Test RSI"
        assert result["type"] == "rsi"
        assert result["status"] == "inactive"

    def test_toggle_strategy(self, client):
        """Test activation/désactivation stratégie"""
        # Créer
        data = {"name": "Test", "type": "rsi"}
        create_response = client.post("/strategies", json=data)
        strategy_id = create_response.json()["id"]

        # Activer
        response = client.patch(f"/strategies/{strategy_id}/toggle")
        assert response.status_code == 200
        assert response.json()["status"] == "active"

        # Désactiver
        response = client.patch(f"/strategies/{strategy_id}/toggle")
        assert response.status_code == 200
        assert response.json()["status"] == "inactive"
```

#### TestTradesAPI

```python
class TestTradesAPI:
    def test_create_trade(self, client):
        """Test création trade"""
        data = {
            "symbol": "BTC",
            "side": "buy",
            "quantity": 0.5,
            "price": 50000.0
        }

        response = client.post("/trades", json=data)
        assert response.status_code == 201

        result = response.json()
        assert result["symbol"] == "BTC"
        assert result["side"] == "buy"
        assert result["quantity"] == 0.5
        assert result["status"] == "open"

    def test_create_trade_without_price(self, client):
        """Test création trade sans prix"""
        data = {
            "symbol": "BTC",
            "side": "buy",
            "quantity": 0.5
        }

        response = client.post("/trades", json=data)
        assert response.status_code == 201

        result = response.json()
        assert result["entry_price"] == 100.0  # Prix par défaut
```

### Tests de données de marché

```python
class TestMarketDataAPI:
    def test_get_market_prices(self, client):
        """Test récupération prix marché"""
        response = client.get("/market/prices")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Vérifier structure
        item = data[0]
        assert "symbol" in item
        assert "price" in item
        assert "volume" in item
        assert "timestamp" in item
```

## Tests end-to-end

### Tests avec Selenium/Playwright (futur)

```python
class TestE2E:
    def test_create_strategy_ui(self, browser):
        """Test création stratégie via interface"""
        browser.visit("http://localhost:8000")

        # Cliquer sur "Stratégies"
        browser.click_link("Stratégies")

        # Remplir formulaire
        browser.fill("name", "Nouvelle Stratégie")
        browser.select("type", "rsi")
        browser.click_button("Créer")

        # Vérifier création
        assert browser.has_text("Nouvelle Stratégie")

    def test_execute_trade_workflow(self, browser):
        """Test workflow complet de trade"""
        # Créer stratégie
        # Activer stratégie
        # Vérifier exécution automatique
        # Contrôler résultat
        pass
```

## Configuration des tests

### pyproject.toml

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/venv/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError"
]
```

### Fixtures personnalisées

```python
@pytest.fixture
def sample_strategy():
    """Fixture pour stratégie d'exemple"""
    return Strategy(
        name="Sample RSI",
        type="rsi",
        config={"period": 14, "overbought": 70, "oversold": 30}
    )

@pytest.fixture
def sample_trade():
    """Fixture pour trade d'exemple"""
    return Trade(
        symbol="BTC",
        side="buy",
        quantity=1.0,
        entry_price=50000.0
    )
```

## Mocking et données de test

### Mock des données de marché

```python
@pytest.fixture
def mock_market_data():
    """Mock pour données de marché"""
    return [
        {"symbol": "BTC", "price": 50000.0, "volume": 1000000.0},
        {"symbol": "ETH", "price": 3000.0, "volume": 500000.0},
    ]

def test_strategy_with_market_data(client, mock_market_data, mocker):
    """Test stratégie avec données marché mockées"""
    mocker.patch('src.api.get_market_prices', return_value=mock_market_data)

    response = client.get("/market/prices")
    assert response.json() == mock_market_data
```

### Mock du stockage

```python
@pytest.fixture
def mock_storage():
    """Mock du stockage pour tests isolés"""
    storage = MagicMock()
    storage.get_all.return_value = []
    storage.create.return_value = Strategy(name="Mock", type="manual")
    return storage
```

## Tests de performance

### Benchmark des opérations

```python
import time

def test_storage_performance():
    """Test performance du stockage"""
    storage = InMemoryStorage[Strategy]()

    # Test création en masse
    start_time = time.time()
    for i in range(1000):
        strategy = Strategy(name=f"Strategy {i}", type="manual")
        storage.create(strategy)
    end_time = time.time()

    assert end_time - start_time < 1.0  # < 1 seconde pour 1000 éléments

def test_api_response_time(client):
    """Test temps de réponse API"""
    import time

    start_time = time.time()
    response = client.get("/strategies")
    end_time = time.time()

    assert response.status_code == 200
    assert end_time - start_time < 0.1  # < 100ms
```

### Tests de charge

```python
def test_concurrent_requests(client):
    """Test requêtes concurrentes"""
    import threading
    import queue

    results = queue.Queue()

    def make_request():
        response = client.get("/health")
        results.put(response.status_code)

    threads = []
    for _ in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Toutes les requêtes doivent réussir
    while not results.empty():
        assert results.get() == 200
```

## Tests de sécurité

### Validation des entrées

```python
def test_sql_injection_protection(client):
    """Test protection contre injection SQL"""
    # Essayer des payloads malicieux
    malicious_data = {
        "name": "'; DROP TABLE strategies; --",
        "type": "manual"
    }

    response = client.post("/strategies", json=malicious_data)
    # Devrait échouer à cause de la validation
    assert response.status_code == 422

def test_xss_protection(client):
    """Test protection contre XSS"""
    xss_payload = {
        "name": "<script>alert('xss')</script>",
        "type": "manual"
    }

    response = client.post("/strategies", json=xss_payload)
    assert response.status_code == 422  # Validation échoue
```

## Intégration CI/CD

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install uv
        uv sync
    - name: Run tests
      run: uv run pytest --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Tests parallèles

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        test-type: ["unit", "integration"]

    steps:
    - name: Run tests
      run: uv run pytest tests/${{ matrix.test-type }}/ -v
```

## Métriques de qualité

### Couverture de code

```bash
# Rapport de couverture
uv run pytest --cov=src --cov-report=html

# Vérification seuil minimum
uv run pytest --cov=src --cov-fail-under=80
```

### Complexité cyclomatique

```bash
# Installation radon
uv add radon

# Analyse de complexité
uv run radon cc src/ -a

# Maintenir sous 10 pour les fonctions critiques
```

### Linting et formatage

```bash
# Black pour le formatage
uv run black src/ tests/

# Flake8 pour le linting
uv run flake8 src/ tests/

# MyPy pour le typage
uv run mypy src/
```

## Bonnes pratiques

### Règles générales

1. **Un test par comportement** : Chaque test vérifie un aspect spécifique
2. **Tests indépendants** : Pas de dépendance entre tests
3. **Données de test réalistes** : Utiliser des valeurs représentatives
4. **Noms descriptifs** : Expliquer ce qui est testé
5. **Assert explicites** : Vérifier les résultats attendus précisément

### Tests de régression

```python
def test_regression_issue_123(client):
    """Test pour régression #123: Problème de calcul PnL"""
    # Scénario qui causait le bug
    trade = Trade(symbol="BTC", side="buy", quantity=1.0, entry_price=50000.0)
    trade.close_trade(exit_price=55000.0)

    # Vérifier le calcul correct
    assert trade.pnl == 5000.0
```

### Tests de performance

```python
@pytest.mark.slow
def test_large_dataset_performance():
    """Test performance avec gros volume de données"""
    storage = InMemoryStorage[Trade]()

    # Créer 10,000 trades
    for i in range(10000):
        trade = Trade(
            symbol="BTC",
            side="buy" if i % 2 == 0 else "sell",
            quantity=1.0,
            entry_price=50000.0 + i
        )
        storage.create(trade)

    # Vérifier performance des requêtes
    start_time = time.time()
    results = storage.find_by(side="buy")
    end_time = time.time()

    assert len(results) == 5000
    assert end_time - start_time < 0.1  # < 100ms
```

---

**Tests maîtrisés ?** Découvrez les [modèles de données](../reference/models.md) ou commencez le [développement](../development/contributing.md).
