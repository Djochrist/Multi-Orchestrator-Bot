"""
Tests d'intégration pour l'API
"""

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


class TestStrategiesAPI:
    """Tests pour l'API des stratégies"""

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

    def test_get_strategy_by_id(self, client):
        """Test récupération stratégie par ID"""
        # Créer d'abord
        data = {"name": "Test", "type": "rsi"}
        create_response = client.post("/strategies", json=data)
        strategy_id = create_response.json()["id"]

        # Récupérer
        response = client.get(f"/strategies/{strategy_id}")
        assert response.status_code == 200

        result = response.json()
        assert result["id"] == strategy_id
        assert result["name"] == "Test"

    def test_get_strategy_not_found(self, client):
        """Test stratégie non trouvée"""
        response = client.get("/strategies/999")
        assert response.status_code == 404

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

    def test_delete_strategy(self, client):
        """Test suppression stratégie"""
        # Créer
        data = {"name": "Test", "type": "rsi"}
        create_response = client.post("/strategies", json=data)
        strategy_id = create_response.json()["id"]

        # Supprimer
        response = client.delete(f"/strategies/{strategy_id}")
        assert response.status_code == 204

        # Vérifier suppression
        response = client.get(f"/strategies/{strategy_id}")
        assert response.status_code == 404


class TestTradesAPI:
    """Tests pour l'API des trades"""

    def test_get_trades_empty(self, client):
        """Test récupération trades vides"""
        response = client.get("/trades")
        assert response.status_code == 200
        assert response.json() == []

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


class TestMarketDataAPI:
    """Tests pour l'API des données de marché"""

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


class TestDashboardAPI:
    """Tests pour l'API du dashboard"""

    def test_get_dashboard_summary(self, client):
        """Test récupération résumé dashboard"""
        response = client.get("/dashboard/summary")
        assert response.status_code == 200

        data = response.json()
        assert "total_pnl" in data
        assert "open_positions" in data
        assert "active_strategies" in data
        assert "timestamp" in data


class TestHealthCheck:
    """Tests pour la vérification de santé"""

    def test_health_check(self, client):
        """Test endpoint de santé"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
