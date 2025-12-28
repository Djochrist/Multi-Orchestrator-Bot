# 🎮 Guide d'Utilisation

Découvrez comment utiliser Multi-Orchestrator-Bot à travers son interface web moderne.

## 🚀 Démarrage rapide

### Lancement de l'application

```bash
# Depuis le dossier du projet
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Puis ouvrez : **http://localhost:8000**

### Interface principale

L'interface se compose de 4 sections principales :

1. **Dashboard** - Vue d'ensemble des performances
2. **Stratégies** - Gestion des stratégies de trading
3. **Trades** - Historique et création de trades
4. **Marché** - Données de marché en temps réel

## Dashboard

### Métriques principales

Le dashboard affiche les indicateurs clés :

- **PnL Total** : Profit/Perte cumulé de toutes les stratégies
- **Positions Ouvertes** : Nombre de trades actifs
- **Stratégies Actives** : Nombre de stratégies en cours d'exécution
- **Status API** : État de santé du système

### Actualisation automatique

- Cliquez sur **"Actualiser"** pour mettre à jour les données
- Les données se rafraîchissent automatiquement toutes les 30 secondes

## Gestion des Stratégies

### Création d'une stratégie

1. Cliquez sur **"Stratégies"** dans la navigation
2. Cliquez sur **"Ajouter Stratégie"**
3. Remplissez le formulaire :
   - **Nom** : Nom descriptif de la stratégie
   - **Description** : Détails optionnels
   - **Type** : RSI, MACD, ou Manuel

### Activation/Désactivation

- Utilisez le bouton **"Activer/Désactiver"** pour chaque stratégie
- Une stratégie active participe au trading algorithmique
- Une stratégie inactive est en pause

### Modification et suppression

- **Modifier** : Cliquez sur le bouton d'édition (icône crayon)
- **Supprimer** : Cliquez sur "Supprimer" (avec confirmation)

## Gestion des Trades

### Création d'un trade manuel

1. Cliquez sur **"Trades"** dans la navigation
2. Cliquez sur **"Nouveau Trade"**
3. Remplissez les détails :
   - **Symbole** : BTC, ETH, etc.
   - **Côté** : Achat ou Vente
   - **Quantité** : Volume du trade
   - **Prix** : Prix d'entrée (optionnel, auto si vide)

### Historique des trades

- **Liste chronologique** : Trades triés par date (plus récent en premier)
- **Statuts** : Ouvert, Fermé, Annulé
- **Détails** : Prix d'entrée, quantité, PnL calculé

### Fermeture automatique

Les trades se ferment automatiquement selon la logique de stratégie, ou peuvent être fermés manuellement via l'API.

## Données de Marché

### Vue d'ensemble

La section Marché affiche des données mockées en temps réel :

- **Symboles** : BTC, ETH, SOL, AAPL, TSLA
- **Prix** : Valeurs mises à jour automatiquement
- **Volume** : Volume de trading simulé

### Actualisation

- Cliquez sur **"Actualiser"** pour forcer la mise à jour
- Les prix évoluent automatiquement toutes les 2 secondes

## Workflows courants

### Configuration initiale

1. **Créer des stratégies** selon vos préférences
2. **Activer les stratégies** que vous souhaitez utiliser
3. **Surveiller le dashboard** pour les performances
4. **Ajuster les paramètres** selon les résultats

### Trading quotidien

1. **Consulter le dashboard** au démarrage
2. **Vérifier les positions ouvertes** dans Trades
3. **Surveiller les données marché** pour le contexte
4. **Ajuster les stratégies** si nécessaire

### Maintenance

1. **Désactiver les stratégies** sous-performantes
2. **Créer de nouvelles stratégies** pour tester
3. **Analyser l'historique** des trades fermés
4. **Optimiser les paramètres** basés sur les données

## ⚙️ Paramètres avancés

### Configuration des stratégies

Chaque type de stratégie a ses propres paramètres :

#### RSI (Relative Strength Index)
- **Période RSI** : Fenêtre de calcul (défaut: 14)
- **Surachat** : Seuil supérieur (défaut: 70)
- **Survente** : Seuil inférieur (défaut: 30)

#### MACD (Moving Average Convergence Divergence)
- **Rapide** : Période EMA rapide (défaut: 12)
- **Lente** : Période EMA lente (défaut: 26)
- **Signal** : Période de signal (défaut: 9)

### Gestion des risques

- **Limites de position** : Quantité maximale par trade
- **Stop-loss** : Niveaux d'arrêt automatique
- **Take-profit** : Objectifs de profit

## 🔧 Fonctionnalités API

### Accès programmatique

L'interface web utilise l'API REST. Vous pouvez également :

```bash
# Récupérer toutes les stratégies
curl http://localhost:8000/api/strategies

# Créer un trade
curl -X POST http://localhost:8000/api/trades \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC", "side": "buy", "quantity": 0.1}'
```

### Documentation API

Consultez la documentation complète : http://localhost:8000/docs

## 📱 Interface responsive

L'interface s'adapte automatiquement :

- **Desktop** : Layout complet avec toutes les colonnes
- **Tablette** : Colonnes réduites, navigation optimisée
- **Mobile** : Interface verticale, modals adaptés

##  Gestion des erreurs

### Messages d'erreur courants

- **"Stratégie non trouvée"** : ID incorrect ou stratégie supprimée
- **"Erreur API"** : Problème de connexion réseau
- **"Données invalides"** : Format incorrect dans les formulaires

### Diagnostic

1. **Vérifiez la console** du navigateur (F12)
2. **Consultez les logs** du serveur
3. **Testez l'API** directement via /docs
4. **Redémarrez** l'application si nécessaire

##  Prochaines étapes

Maintenant que vous maîtrisez l'interface :

1. [Explorez l'API](../architecture/api.md) pour l'intégration
2. [Configurez des stratégies avancées](../ui/strategies.md)
3. [Analysez les performances](../ui/dashboard.md)
4. [Contribuez au projet](../development/contributing.md)

---

**💡 Conseil** : Commencez par explorer avec les données d'exemple, puis créez vos propres stratégies !
