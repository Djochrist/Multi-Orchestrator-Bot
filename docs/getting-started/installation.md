# 🚀 Guide d'Installation

Ce guide vous accompagne pas à pas dans l'installation et la configuration de Multi-Orchestrator-Bot.

##  Prérequis système

### Configuration minimale requise

| Composant | Version minimale | Recommandé |
|-----------|------------------|------------|
| **Python** | 3.10.0 | 3.11+ |
| **RAM** | 2 Go | 4 Go |
| **Disque** | 500 Mo | 1 Go |
| **OS** | Linux/macOS/Windows | Linux/macOS |

### Dépendances système

#### Linux (Ubuntu/Debian)
```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances de base
sudo apt install -y curl build-essential
```

#### macOS
```bash
# Installation via Homebrew (recommandé)
brew install curl

# Ou via Xcode Command Line Tools
xcode-select --install
```

#### Windows
```bash
# Windows Terminal ou PowerShell en mode administrateur
# Installation de Python via Microsoft Store ou python.org
```

## 🛠️ Installation étape par étape

### Étape 1 : Installation de uv

uv est le gestionnaire de paquets moderne pour Python.

```bash
# Installation automatique
curl -LsSf https://astral.sh/uv/install.sh | sh

# Recharger le shell
source ~/.bashrc  # ou ~/.zshrc selon votre shell

# Vérification
uv --version
```

### Étape 2 : Clonage du dépôt

```bash
# Clonage du projet
git clone https://github.com/username/Multi-Orchestrator-Bot.git
cd multi-orchestrator-bot

# Vérification des fichiers
ls -la
```

### Étape 3 : Installation des dépendances

```bash
# Installation de toutes les dépendances (runtime + dev)
uv sync

# Vérification de l'installation
uv run python --version
uv run python -c "import fastapi, uvicorn; print('✅ Dépendances installées')"
```

### Étape 4 : Premier lancement

```bash
# Lancement en mode développement
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Étape 5 : Vérification

Ouvrez votre navigateur et accédez à :

- **Interface Web** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Santé système** : http://localhost:8000/health

## ⚙️ Configuration avancée

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```bash
# Copie du fichier d'exemple
cp .env.example .env

# Édition des paramètres
nano .env
```

Contenu du fichier `.env` :

```bash
# Configuration de l'application
DEBUG=true
LOG_LEVEL=INFO

# Configuration du serveur
HOST=0.0.0.0
PORT=8000

# Configuration CORS (pour développement)
ALLOW_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Configuration de l'IDE

#### VS Code
Installez l'extension Python et configurez le workspace :

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.formatting.provider": "black"
}
```

#### PyCharm
1. Ouvrez le projet
2. Configurez l'interpréteur Python : `File > Settings > Project Interpreter`
3. Sélectionnez l'environnement virtuel créé par uv

## 🧪 Tests et validation

### Exécution des tests

```bash
# Tests unitaires uniquement
uv run pytest tests/unit/ -v

# Tests d'intégration
uv run pytest tests/integration/ -v

# Tous les tests avec couverture
uv run pytest --cov=src --cov-report=html
```

### Validation de l'installation

```bash
# Test de l'import des modules
uv run python -c "from src.main import app; print('Application importable')"

# Test du stockage
uv run python -c "from src.storage import strategies_storage; print('Stockage fonctionnel')"

# Test de l'API
uv run python -c "from src.api import router; print('API initialisée')"
```

## Déploiement en production

### Avec Docker (recommandé)

```bash
# Construction de l'image
docker build -t multi-orchestrator-bot .

# Lancement du conteneur
docker run -p 8000:8000 multi-orchestrator-bot
```

### Avec gunicorn

```bash
# Installation de gunicorn
uv add gunicorn

# Lancement en production
uv run gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🔧 Dépannage

### Problèmes courants

#### Erreur "uv command not found"
```bash
# Réinstallation de uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Vérification du PATH
echo $PATH
```

#### Erreur de permissions
```bash
# Problème avec les permissions d'installation
sudo chown -R $USER:$USER ~/.local
```

#### Port déjà utilisé
```bash
# Vérification des processus utilisant le port 8000
lsof -i :8000

# Changement de port
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

#### Erreur d'import Python
```bash
# Problème de PYTHONPATH
cd /path/to/multi-orchestrator-bot
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
uv run python -c "import src.main"
```

### Logs de diagnostic

```bash
# Logs détaillés de l'application
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

# Logs des tests
uv run pytest -v -s --tb=long
```

## 📞 Support

Si vous rencontrez des problèmes :

1. Consultez la [FAQ](../faq/installation.md)
2. Vérifiez les [Issues GitHub](https://github.com/username/Multi-Orchestrator-Bot/issues)
3. Créez une nouvelle issue avec :
   - Version de Python : `python --version`
   - Version de uv : `uv --version`
   - Système d'exploitation
   - Logs d'erreur complets

---

**Installation terminée ?** Passez au [guide d'utilisation](usage.md) !
