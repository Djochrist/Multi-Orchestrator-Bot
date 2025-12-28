# 🔌 Architecture de l'API

Découvrez l'architecture technique de l'API REST de Multi-Orchestrator-Bot.

## Vue d'ensemble

L'API REST suit les principes RESTful avec FastAPI, offrant une interface complète pour toutes les opérations de trading algorithmique.

### Technologies utilisées

- **FastAPI** : Framework web moderne et rapide
- **Pydantic** : Validation automatique des données
- **OpenAPI** : Documentation automatique des endpoints
- **JSON** : Format d'échange standard

### Principes de conception

- **RESTful** : Utilisation correcte des méthodes HTTP
- **Stateless** : Pas d'état côté serveur entre les requêtes
- **Versionnée** : Préfixe `/api` pour la version actuelle
- **Documentée** : OpenAPI/Swagger généré automatiquement

## Structure des endpoints

### Base URL

```
http://localhost:8000/api
```

### Organisation par domaine

```
/api/strategies/*     # Gestion des stratégies
/api/trades/*          # Gestion des trades
/api/market/*          # Données de marché
/api/dashboard/*       # Métriques du dashboard
/api/health            # Santé du système
```

## Modèles de données

### Strategy

```python
class StrategyCreate(BaseModel):
    name: str                    # Nom de la stratégie (1-255 caractères)
    description: str             # Description optionnelle
    type: str                    # Type: 'rsi', 'macd', 'ml', 'manual'
    config: dict                 # Configuration spécifique au type

class StrategyUpdate(BaseModel):
    name: Optional[str]          # Nom optionnel pour mise à jour
    description: Optional[str]   # Description optionnelle
    status: Optional[str]        # Status: 'active', 'inactive'
    config: Optional[dict]       # Configuration optionnelle
```

### Trade

```python
class TradeCreate(BaseModel):
    symbol: str                  # Symbole (ex: 'BTC', 'AAPL')
    side: str                    # Côté: 'buy' ou 'sell'
    quantity: float              # Quantité (> 0)
    price: Optional[float]       # Prix d'entrée optionnel
```

### MarketData

```python
class MarketDataResponse(BaseModel):
    symbol: str                  # Symbole du marché
    price: float                 # Prix actuel
    volume: float                # Volume échangé
    timestamp: str               # Timestamp ISO 8601
```

## Endpoints détaillés

### Stratégies

#### GET /api/strategies

Récupère la liste des stratégies avec pagination et filtrage.

**Paramètres de requête :**
- `skip` (int, optionnel): Nombre d'éléments à sauter (défaut: 0)
- `limit` (int, optionnel): Nombre maximum d'éléments (1-1000, défaut: 100)
- `status` (str, optionnel): Filtre par status ('active' ou 'inactive')

**Réponse :** `200 OK`
```json
[
  {
    "id": 1,
    "name": "RSI Strategy",
    "description": "Stratégie basée sur RSI",
    "type": "rsi",
    "status": "active",
    "config": {"period": 14, "overbought": 70},
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
]
```

#### POST /api/strategies

Crée une nouvelle stratégie.

**Corps de la requête :**
```json
{
  "name": "Nouvelle Stratégie",
  "description": "Description de la stratégie",
  "type": "rsi",
  "config": {
    "period": 14,
    "overbought": 70,
    "oversold": 30
  }
}
```

**Réponse :** `201 Created`
```json
{
  "id": 2,
  "name": "Nouvelle Stratégie",
  "status": "inactive",
  "created_at": "2024-01-01T10:30:00Z",
  "updated_at": "2024-01-01T10:30:00Z"
}
```

#### GET /api/strategies/{strategy_id}

Récupère une stratégie spécifique.

**Paramètres d'URL :**
- `strategy_id` (int): ID de la stratégie

**Réponse :** `200 OK` ou `404 Not Found`

#### PUT /api/strategies/{strategy_id}

Met à jour complètement une stratégie.

**Paramètres d'URL :**
- `strategy_id` (int): ID de la stratégie

**Corps de la requête :** StrategyUpdate partiel ou complet

#### PATCH /api/strategies/{strategy_id}/toggle

Active ou désactive une stratégie.

**Réponse :** `200 OK` avec la stratégie mise à jour

#### DELETE /api/strategies/{strategy_id}

Supprime une stratégie.

**Réponse :** `204 No Content` ou `404 Not Found`

### Trades

#### GET /api/trades

Récupère la liste des trades avec filtrage.

**Paramètres de requête :**
- `skip`, `limit`: Pagination
- `status`: Filtre par status ('open', 'closed', 'cancelled')
- `symbol`: Filtre par symbole

**Réponse :** Liste de trades triés par date décroissante

#### POST /api/trades

Crée un nouveau trade.

**Corps de la requête :** TradeCreate

**Note :** Si aucun prix n'est fourni, utilise 100.0 par défaut

### Marché

#### GET /api/market/prices

Récupère les données de marché mockées.

**Réponse :** Liste des prix pour BTC, ETH, SOL, AAPL, TSLA

### Dashboard

#### GET /api/dashboard/summary

Récupère le résumé des métriques du dashboard.

**Réponse :**
```json
{
  "total_pnl": 1250.50,
  "open_positions": 3,
  "active_strategies": 5,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Santé système

#### GET /api/health

Vérification de santé de l'application.

**Réponse :**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Gestion d'erreurs

### Codes d'erreur HTTP

- **400 Bad Request** : Données invalides
- **404 Not Found** : Ressource non trouvée
- **422 Unprocessable Entity** : Validation Pydantic
- **500 Internal Server Error** : Erreur serveur

### Format des erreurs

```json
{
  "detail": "Description de l'erreur",
  "errors": [
    {
      "field": "name",
      "message": "Le champ name est requis"
    }
  ]
}
```

## Authentification et sécurité

### CORS

Configuration CORS pour permettre les requêtes cross-origin :

```python
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://multi-orchestrator-bot.dev"
]
```

### Validation des données

- **Pydantic** : Validation automatique des types et contraintes
- **Sanitisation** : Nettoyage automatique des entrées
- **Limites** : Contraintes sur les longueurs et valeurs

### Rate Limiting

Implémentation future pour limiter les requêtes par IP/utilisateur.

## Performance

### Optimisations

- **Async/Await** : Support natif des opérations asynchrones
- **Pagination** : Limitation automatique des résultats
- **Cache** : Possibilité d'implémentation future
- **Compression** : Gzip automatique pour les réponses

### Métriques

Endpoints pour monitoring :
- Temps de réponse moyen
- Taux d'erreur par endpoint
- Utilisation mémoire
- Nombre de requêtes actives

## Tests API

### Tests unitaires

```python
def test_create_strategy(client):
    response = client.post("/api/strategies", json={
        "name": "Test Strategy",
        "type": "manual"
    })
    assert response.status_code == 201
```

### Tests d'intégration

```python
def test_strategy_workflow(client):
    # Créer
    response = client.post("/api/strategies", json=strategy_data)
    strategy_id = response.json()["id"]

    # Récupérer
    response = client.get(f"/api/strategies/{strategy_id}")
    assert response.json()["name"] == strategy_data["name"]

    # Mettre à jour
    client.put(f"/api/strategies/{strategy_id}", json=update_data)

    # Supprimer
    client.delete(f"/api/strategies/{strategy_id}")
```

## Évolution future

### Nouvelles fonctionnalités

- **Authentification JWT** : Sécurisation des endpoints
- **WebSocket** : Données temps réel
- **Pagination cursor-based** : Pour de gros volumes
- **Filtrage avancé** : Requêtes complexes
- **Rate limiting** : Protection contre les abus

### Versionnement

Stratégie de versionnement de l'API :
- `/api/v1/*` : Version actuelle
- `/api/v2/*` : Version future (breaking changes)
- Headers `Accept-Version` pour négociation

---

**API comprise ?** Consultez la [documentation interactive](http://localhost:8000/docs) ou les [modèles de données](../reference/models.md).
