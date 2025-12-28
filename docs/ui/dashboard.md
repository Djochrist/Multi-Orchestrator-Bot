# 📊 Interface Dashboard

Découvrez l'interface du dashboard principal de Multi-Orchestrator-Bot.

## Vue d'ensemble

Le dashboard est la page d'accueil de l'application, offrant une vue d'ensemble complète des performances et de l'état du système de trading.

### Fonctionnalités principales

- **Métriques clés** : PnL total, positions ouvertes, stratégies actives
- **État du système** : Santé de l'API en temps réel
- **Actualisation automatique** : Données mises à jour régulièrement
- **Navigation rapide** : Accès direct aux autres sections

## Métriques affichées

### PnL Total

**Description** : Profit/Perte cumulé de toutes les stratégies actives et fermées.

```javascript
// Calcul du PnL total
const totalPnL = closedTrades.reduce((sum, trade) => sum + trade.pnl, 0);
document.getElementById('total-pnl').textContent = `$${totalPnL.toFixed(2)}`;
```

**Format** : `$X,XXX.XX` (positif = vert, négatif = rouge)

**Source** : Calculé à partir de tous les trades fermés dans le stockage

### Positions Ouvertes

**Description** : Nombre de trades actuellement ouverts (non fermés).

```javascript
const openPositions = trades.filter(trade => trade.status === 'open').length;
```

**Format** : Nombre entier

**Source** : Comptage des trades avec `status = 'open'`

### Stratégies Actives

**Description** : Nombre de stratégies actuellement en cours d'exécution.

```javascript
const activeStrategies = strategies.filter(strategy => strategy.status === 'active').length;
```

**Format** : Nombre entier

**Source** : Comptage des stratégies avec `status = 'active'`

### Status API

**Description** : État de santé de l'API backend.

**États possibles** :
- `✓ API OK` (vert) : API fonctionnelle
- `✗ API HS` (rouge) : API hors service
- `Vérification...` (gris) : Test en cours

**Vérification** :
```javascript
async checkAPIHealth() {
    try {
        await fetch('/api/health');
        // Status: OK
    } catch (error) {
        // Status: Error
    }
}
```

## Actualisation des données

### Actualisation manuelle

**Bouton "Actualiser"** : Force la mise à jour de toutes les métriques.

```javascript
document.getElementById('refresh-btn').addEventListener('click', () => {
    loadDashboard();
    checkAPIHealth();
});
```

### Actualisation automatique

**Fréquence** : Toutes les 30 secondes

```javascript
setInterval(() => {
    if (currentPage === 'dashboard') {
        loadDashboard();
    }
}, 30000);
```

### Actualisation en temps réel

**Événements déclencheurs** :
- Création/modification de stratégie
- Création de trade
- Changement de page vers le dashboard

## Structure visuelle

### Layout responsive

```css
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
}
```

### Cartes de métriques

Chaque métrique est présentée dans une carte avec :

- **Titre** : Nom de la métrique
- **Valeur** : Donnée formatée
- **Couleur** : Indicateur visuel (vert/rouge/gris)

### États visuels

```css
.stat-value {
    font-size: 2rem;
    font-weight: bold;
    color: #2563eb; /* Bleu par défaut */
}

.stat-value.positive {
    color: #16a34a; /* Vert pour positif */
}

.stat-value.negative {
    color: #dc2626; /* Rouge pour négatif */
}

.stat-value.status-healthy {
    color: #16a34a; /* Vert pour API OK */
}
```

## Interactions utilisateur

### Navigation

**Cliques sur les boutons de navigation** :
- Dashboard → Actualisation des métriques
- Stratégies → Chargement de la liste des stratégies
- Trades → Chargement de l'historique des trades
- Marché → Chargement des données de marché

### Actions disponibles

- **Actualiser** : Rafraîchir manuellement les données
- **Navigation** : Changer de section

## Données techniques

### Endpoint utilisé

```http
GET /api/dashboard/summary
```

**Réponse** :
```json
{
  "total_pnl": 1250.50,
  "open_positions": 3,
  "active_strategies": 2,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Calculs côté serveur

```python
@app.get("/dashboard/summary")
def get_dashboard_summary():
    trades = trades_storage.get_all()
    closed_trades = [t for t in trades if t.is_closed]

    total_pnl = sum(t.pnl or 0 for t in closed_trades)
    open_positions = len([t for t in trades if t.is_open])
    active_strategies = len(strategies_storage.find_by(status="active"))

    return {
        "total_pnl": total_pnl,
        "open_positions": open_positions,
        "active_strategies": active_strategies,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
```

## Optimisations

### Mise en cache

**Cache côté client** : Évite les requêtes inutiles pendant 5 secondes

```javascript
let lastDashboardUpdate = 0;
const CACHE_DURATION = 5000; // 5 secondes

async function loadDashboard() {
    const now = Date.now();
    if (now - lastDashboardUpdate < CACHE_DURATION) {
        return; // Utilise le cache
    }

    // Charge les données
    const data = await apiRequest('/dashboard/summary');
    lastDashboardUpdate = now;

    // Met à jour l'interface
    updateDashboard(data);
}
```

### Lazy loading

**Chargement différé** : Les données ne sont chargées que quand nécessaire

```javascript
// Ne charge le dashboard que si on est sur cette page
if (currentPage === 'dashboard') {
    loadDashboard();
}
```

## Gestion d'erreurs

### Erreurs de réseau

```javascript
async loadDashboard() {
    try {
        const data = await apiRequest('/dashboard/summary');
        updateDashboard(data);
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        showError('Impossible de charger le dashboard');
        // Affiche les dernières données connues ou un état d'erreur
    }
}
```

### Données manquantes

- **PnL** : Affiche `$0.00` si non calculable
- **Positions** : Affiche `0` si données indisponibles
- **API Status** : Affiche `Vérification...` pendant le test

## Évolutions futures

### Nouvelles métriques

- **Taux de réussite** : Pourcentage de trades gagnants
- **Volume total** : Volume échangé sur la période
- **Performance par stratégie** : PnL détaillé par stratégie
- **Temps réel** : Graphiques en temps réel

### Graphiques et visualisations

```javascript
// Intégration Chart.js future
const pnlChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: dates,
        datasets: [{
            label: 'PnL Cumulé',
            data: pnlValues,
            borderColor: 'rgb(75, 192, 192)',
        }]
    }
});
```

### Alertes et notifications

- **Seuils d'alerte** : Notifications quand le PnL dépasse des seuils
- **Alertes système** : Notifications d'indisponibilité API
- **Rappels** : Rappels pour rééquilibrer les positions

## Accessibilité

### Support clavier

- **Tab** : Navigation entre les éléments
- **Enter/Espace** : Activation des boutons
- **Échap** : Fermeture des modals

### Lecteurs d'écran

- **Labels explicites** : Descriptions textuelles des métriques
- **Structure sémantique** : Utilisation correcte des headings
- **États dynamiques** : Annonces des changements de valeurs

### Contraste et couleurs

- **Couleurs différenciées** : Vert/rouge pour les valeurs positives/négatives
- **Texte lisible** : Contraste suffisant pour tous les textes
- **Indicateurs visuels** : Icônes et couleurs pour les statuts

---

**Dashboard maîtrisé ?** Découvrez la gestion des [stratégies](../ui/strategies.md) ou des [trades](../ui/trades.md).
