# ⚙️ Guide de Configuration

Apprenez à configurer Multi-Orchestrator-Bot pour différents environnements et cas d'usage.

## Variables d'environnement

### Configuration de base

Créez un fichier `.env` à la racine du projet :

```bash
# Configuration serveur
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO

# Sécurité
SECRET_KEY=votre-cle-secrete-très-longue-et-complexe
ALLOW_ORIGINS=http://localhost:3000,http://localhost:5173

# Base de données (future)
DATABASE_URL=sqlite:///./trading.db

# Trading
DEFAULT_CURRENCY=USD
MAX_POSITION_SIZE=1000
RISK_PER_TRADE=0.02
```

### Variables disponibles

| Variable | Description | Défaut | Exemple |
|----------|-------------|---------|---------|
| `HOST` | Adresse d'écoute | `0.0.0.0` | `127.0.0.1` |
| `PORT` | Port du serveur | `8000` | `8080` |
| `DEBUG` | Mode debug | `true` | `false` |
| `LOG_LEVEL` | Niveau de logs | `INFO` | `DEBUG` |
| `SECRET_KEY` | Clé de sécurité | Générée | `abc123...` |
| `ALLOW_ORIGINS` | Origines CORS | Localhost | `https://monapp.com` |

## Configuration des stratégies

### Paramètres par défaut

```json
{
  "rsi": {
    "period": 14,
    "overbought": 70,
    "oversold": 30,
    "min_volume": 1000
  },
  "macd": {
    "fast_period": 12,
    "slow_period": 26,
    "signal_period": 9,
    "threshold": 0.001
  }
}
```

### Configuration avancée

#### RSI Strategy
```json
{
  "name": "RSI Aggressive",
  "type": "rsi",
  "parameters": {
    "period": 21,
    "overbought": 75,
    "oversold": 25,
    "min_volume": 5000,
    "max_trades_per_day": 10
  },
  "risk_management": {
    "stop_loss": 0.05,
    "take_profit": 0.10,
    "max_position_size": 0.1
  }
}
```

#### MACD Strategy
```json
{
  "name": "MACD Trend Follower",
  "type": "macd",
  "parameters": {
    "fast_period": 8,
    "slow_period": 21,
    "signal_period": 5,
    "threshold": 0.002
  },
  "filters": {
    "min_price": 10.0,
    "max_price": 1000.0,
    "min_volume": 10000
  }
}
```

## Configuration du stockage

### Stockage en mémoire (par défaut)

```python
# Configuration automatique
from src.storage import strategies_storage, trades_storage

# Pas de configuration supplémentaire requise
```

### Migration vers base de données

#### SQLite
```python
DATABASE_URL = "sqlite:///./trading.db"
```

#### PostgreSQL
```python
DATABASE_URL = "postgresql://user:password@localhost/trading"
```

#### Configuration de connexion
```python
# Dans .env
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
```

## Configuration réseau

### Reverse proxy (nginx)

```nginx
server {
    listen 80;
    server_name trading.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        # Rate limiting
        limit_req zone=api burst=10 nodelay;
    }
}
```

### Load balancer

```nginx
upstream trading_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://trading_backend;
    }
}
```

## Configuration de sécurité

### HTTPS avec Let's Encrypt

```bash
# Installation certbot
sudo apt install certbot python3-certbot-nginx

# Obtention certificat
sudo certbot --nginx -d trading.example.com

# Renouvellement automatique
sudo crontab -e
# Ajouter: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Authentification API

```python
# Configuration JWT
JWT_SECRET_KEY = "votre-cle-jwt-très-longue"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Rate limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # secondes
```

## Configuration de monitoring

### Métriques Prometheus

```python
# Configuration
PROMETHEUS_ENABLED = true
PROMETHEUS_PORT = 9090

# Métriques exposées
# - http_requests_total
# - response_time_seconds
# - active_strategies
# - open_positions
```

### Logs structurés

```python
# Configuration logging
LOG_FORMAT = "json"
LOG_FILE = "/var/log/trading/app.log"
LOG_MAX_SIZE = "10MB"
LOG_BACKUP_COUNT = 5

# Niveaux par module
LOG_LEVELS = {
    "src.api": "INFO",
    "src.storage": "WARNING",
    "src.models": "DEBUG"
}
```

## Environnements de déploiement

### Développement

```bash
# .env.development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./dev.db
ALLOW_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Production

```bash
# .env.production
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://user:pass@prod-db/trading
ALLOW_ORIGINS=https://trading.example.com
SECRET_KEY=production-secret-key
```

### Staging

```bash
# .env.staging
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@staging-db/trading
ALLOW_ORIGINS=https://staging.trading.example.com
```

## Configuration des tests

### Tests unitaires

```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=src --cov-report=html
markers =
    unit: tests unitaires
    integration: tests d'intégration
    slow: tests lents
```

### Base de données de test

```python
# Configuration test
TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_FIXTURES_DIR = "tests/fixtures"
```

## Validation de configuration

### Script de validation

```bash
#!/bin/bash
# validate_config.sh

# Vérification des variables requises
required_vars=("SECRET_KEY" "DATABASE_URL")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Erreur: $var non défini"
        exit 1
    fi
done

# Test de connexion base de données
python -c "import src.storage; print('Configuration valide')"
```

### Health checks

```python
# Endpoint /health
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": check_database_connection(),
        "memory": get_memory_usage(),
        "disk": get_disk_usage()
    }
```

## Dépannage configuration

### Problèmes courants

#### Variables d'environnement non chargées
```bash
# Vérification
python -c "import os; print(os.environ.get('DEBUG'))"

# Forcer le rechargement
source .env
```

#### Erreur de connexion base de données
```bash
# Test de connexion
python -c "import sqlalchemy; engine = sqlalchemy.create_engine(DATABASE_URL); engine.connect()"
```

#### Problèmes de CORS
```bash
# Vérification des origines
curl -H "Origin: http://localhost:3000" -v http://localhost:8000/api/strategies
```

---

**Configuration terminée ?** Retournez au [guide d'installation](../getting-started/installation.md) ou consultez l'[architecture](../architecture/overview.md).
