# Multi-Orchestrator-Bot (Work in Progress)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-green.svg)](https://fastapi.tiangolo.com/) [![Tests](https://img.shields.io/badge/tests-22%20passed-green.svg)](https://github.com/Djochrist/Multi-Orchestrator-Bot/actions) [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Repository](https://img.shields.io/badge/github-Djochrist/Multi--Orchestrator--Bot-lightgrey.svg)](https://github.com/Djochrist/Multi-Orchestrator-Bot)

Multi-Orchestrator-Bot est une plateforme de trading algorithmique moderne combinant
un moteur de stratégies, une API backend robuste et une interface web de pilotage.

Le projet est conçu pour être modulaire, testable et extensible, avec une séparation
claire entre la logique de trading, l’orchestration et l’interface utilisateur.

> **Note importante**
>
> La version utilisant des données réelles, avec un backtest complet et fiable,
> sans interface graphique (headless), est disponible dans la branche `dev`.
> La branche `main` se concentre actuellement sur l’interface web et la démonstration
> du système.


## Démonstration

```html
<video width="100%" controls>
  <source src="demo.webm" type="video/webm">
  Votre navigateur ne supporte pas la lecture vidéo.
</video>
```
---

## Architecture du projet

```
multi-orchestrator-bot/
├── src/
│   ├── core/            # Logique métier et orchestration
│   ├── strategies/      # Stratégies de trading
│   ├── backtesting/     # Outils de backtest (branche dev)
│   ├── api/             # API FastAPI
│   ├── web/             # Interface web
│   └── utils/           # Outils et helpers
├── tests/               # Tests unitaires et d’intégration
├── docs/                # Documentation
├── run.py               # Point d’entrée de l’application
└── pyproject.toml
```

---

## Installation

### Prérequis

* Python 3.10 ou supérieur
* `uv` (gestionnaire de dépendances utilisé dans le projet)
* Git

### Étapes

```bash
git clone https://github.com/Djochrist/Multi-Orchestrator-Bot.git
cd Multi-Orchestrator-Bot
uv sync
```

> Remarque : si vous souhaitez travailler sur la version de backtest (données réelles, exécution headless), basculez sur la branche `dev` :

```bash
git checkout dev
```

---

## Lancement

Pour lancer l’application (interface + API) depuis la branche `main` :

```bash
python run.py
```

**Accès** :

* Interface Web : `http://localhost:8000`
* API : `http://localhost:8000/api`
* Documentation OpenAPI : `http://localhost:8000/docs`

---

## Documentation

Consultez la documentation complète dans le dossier `docs/` :

* Guide d’installation : `docs/getting-started/installation.md`
* Guide d’utilisation : `docs/getting-started/usage.md`
* Architecture technique : `docs/architecture/overview.md`
* Documentation complète : `docs/README.md`

---

## Tests

Exécutez la suite de tests :

```bash
uv run pytest
```

Les tests couvrent les composants critiques : orchestration, stratégies, API et utils.

---

## Améliorations futures

* Connecter le frontend avec le backend stable sur la branche `dev`.
* Standardiser le pipeline de backtesting (import de données, vectorisation, reporting).
* Ajouter des métriques avancées (drawdown, Sharpe rolling, factor attribution).
* Automatiser les déploiements (CI/CD) pour staging et production.
* Documentation et guides pour l’intégration de nouvelles stratégies.

---

## Contribution

Merci pour ton intérêt. Pour contribuer :

1. Fork le projet
2. Crée une branche de fonctionnalité : `git checkout -b feature/AmazingFeature`
3. Fais des commits clairs : `git commit -m "Add AmazingFeature"`
4. Push ta branche : `git push origin feature/AmazingFeature`
5. Ouvre une Pull Request

Pour les contributions liées au backtesting (données réelles), cible la branche `dev`.

---

## Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour détails.

---

## Contact

Pour toute question ou demande, ouvre une issue sur le dépôt GitHub ou contacte le mainteneur du projet.
