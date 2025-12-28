# Contribuer à Multi-Orchestrator-Bot

Nous accueillons les contributions de la communauté. Ce guide décrit le processus de contribution au projet.

## Code de Conduite

Ce projet suit un code de conduite pour assurer un environnement professionnel pour tous les contributeurs. En participant, vous acceptez de :

- Être respectueux et inclusif
- Vous concentrer sur les retours constructifs
- Accepter la responsabilité des erreurs
- Montrer de l'empathie envers les autres contributeurs
- Aider à créer une communauté positive

## Processus de Contribution

### 1. Forker le Dépôt

Commencez par forker le dépôt sur GitHub et cloner votre fork :

```bash
git clone https://github.com/Djochrist/Multi-Orchestrator-Bot.git
cd multi-orchestrator-bot
```

### 2. Configurer l'Environnement de Développement

```bash
# Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Installer les dépendances
uv sync --dev

# Configurer les hooks pre-commit
uv run pre-commit install
```

### 3. Créer une Branche de Fonctionnalité

```bash
git checkout -b feature/votre-nom-fonctionnalite
# ou
git checkout -b fix/numero-issue
```

### 4. Faire Vos Modifications

- Suivre le style de code existant
- Écrire des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation si nécessaire
- S'assurer que tous les tests passent

### 5. Exécuter les Contrôles de Qualité

```bash
# Exécuter le linting
uv run flake8 src/ tests/
uv run mypy src/
uv run black --check src/ tests/
uv run isort --check-only src/ tests/

# Exécuter les tests
uv run pytest --cov=src

# Exécuter les vérifications de sécurité
uv run bandit -r src/
```

### 6. Commiter Vos Modifications

```bash
git add .
git commit -m "feat: ajouter votre description de fonctionnalité"
```

Suivre le format de commit conventionnel :
- `feat:` pour les nouvelles fonctionnalités
- `fix:` pour les corrections de bugs
- `docs:` pour la documentation
- `style:` pour le formatage
- `refactor:` pour la restructuration du code
- `test:` pour les tests
- `chore:` pour la maintenance

### 7. Push et Créer une Pull Request

```bash
git push origin feature/votre-nom-fonctionnalite
```

Puis créer une pull request sur GitHub.

## Directives de Développement

### Style de Code

- Utiliser `black` pour le formatage du code
- Utiliser `isort` pour le tri des imports
- Suivre les directives PEP 8
- Utiliser des indications de type pour tous les paramètres de fonction et valeurs de retour
- Écrire des docstrings pour toutes les fonctions et classes publiques

### Tests

- Écrire des tests unitaires pour toutes les nouvelles fonctionnalités
- Viser >90% de couverture de code
- Utiliser des noms de tests descriptifs
- Tester à la fois les cas de succès et d'échec
- Simuler les dépendances externes

### Documentation

- Mettre à jour la documentation pour toute nouvelle fonctionnalité
- Utiliser un langage clair et concis
- Inclure des exemples de code si utile
- Maintenir la documentation API à jour

## Structure du Projet

```
multi-orchestrator-bot/
├── src/                    # Code source
│   ├── api/               # Routes FastAPI
│   ├── core/              # Fonctionnalités core
│   ├── models/            # Modèles de base de données
│   ├── services/          # Services métier
│   ├── strategies/        # Implémentations de stratégies de trading
│   └── utils/            # Fonctions utilitaires
├── tests/                 # Suite de tests
├── docs/                  # Documentation
└── scripts/              # Scripts utilitaires
```

## Domaines de Contribution

### Priorité Élevée
- Implémentations de stratégies d'apprentissage automatique
- Indicateurs techniques supplémentaires
- Intégrations d'échanges
- Optimisations de performance
- Améliorations de la documentation

### Priorité Moyenne
- Améliorations du tableau de bord web
- Fonctionnalités de backtesting supplémentaires
- Modules de gestion des risques
- Systèmes de notifications
- Bibliothèques client API

### Priorité Faible
- Développement d'application mobile
- Application desktop
- Support de langues supplémentaires
- Modèles de déploiement cloud

## Signaler des Problèmes

Lors du signalement de bugs ou de demandes de fonctionnalités :

1. Vérifier les issues existantes d'abord
2. Utiliser les modèles d'issues si disponibles
3. Fournir des étapes de reproduction détaillées
4. Inclure les logs et messages d'erreur pertinents
5. Spécifier votre environnement (OS, version Python, etc.)

## Obtenir de l'Aide

- **Documentation** : [docs.multi-orchestrator-bot.com](https://Djochrist.github.io/Multi-Orchestrator-Bot/)
- **Issues** : [Issues GitHub](https://github.com/Djochrist/Multi-Orchestrator-Bot/issues)
- **Discussions** : [Discussions GitHub](https://github.com/Djochrist/Multi-Orchestrator-Bot/discussions)
- **Discord** : [Rejoignez notre communauté](https://discord.gg/multi-orchestrator-bot)

## Licence

En contribuant à ce projet, vous acceptez que vos contributions soient licenciées sous la même licence MIT qui couvre le projet.
