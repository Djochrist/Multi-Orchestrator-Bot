# API Reference

## Classes Publiques

### StrategyAdapter

Interface abstraite pour les stratégies de trading.

```python
class StrategyAdapter(Protocol):
    @property
    def name(self) -> str:
        """Nom unique de la stratégie."""
        ...

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génère les signaux de trading.

        Args:
            df: DataFrame OHLCV avec colonnes [open, high, low, close, volume]

        Returns:
            DataFrame avec colonne 'signal' ajoutée (-1, 0, 1)
        """
        ...
```

### TradingOrchestrator

Orchestrateur principal pour la gestion des stratégies.

```python
class TradingOrchestrator:
    def __init__(self):
        """Initialise avec les stratégies par défaut."""

    def select_best_strategy(self) -> StrategyAdapter:
        """Sélectionne la meilleure stratégie via backtest.

        Returns:
            Instance de la stratégie sélectionnée
        """

    def get_all_strategies(self) -> List[StrategyAdapter]:
        """Retourne toutes les stratégies disponibles.

        Returns:
            Liste des stratégies
        """
```

### SMACrossover

Stratégie de croisement de moyennes mobiles simples.

```python
class SMACrossover(StrategyAdapter):
    def __init__(self, short: int = 10, long: int = 50):
        """Initialise la stratégie SMA.

        Args:
            short: Période de la moyenne courte
            long: Période de la moyenne longue
        """
```

### EMACrossover

Stratégie de croisement de moyennes mobiles exponentielles.

```python
class EMACrossover(StrategyAdapter):
    def __init__(self, short: int = 12, long: int = 26):
        """Initialise la stratégie EMA.

        Args:
            short: Période de la moyenne courte
            long: Période de la moyenne longue
        """
```

### MeanReversion

Stratégie de retour à la moyenne.

```python
class MeanReversion(StrategyAdapter):
    def __init__(self, lookback: int = 20, z_thresh: float = 1.5):
        """Initialise la stratégie Mean Reversion.

        Args:
            lookback: Période de lookback pour la moyenne
            z_thresh: Seuil Z-Score pour les signaux
        """
```

### PaperTrader

Simulateur de trading en temps réel avec rapports détaillés.

```python
class PaperTrader:
    def __init__(self, orchestrator: Optional[TradingOrchestrator] = None,
                 exchange: Optional[MockExchange] = None):
        """Initialise le paper trader.

        Args:
            orchestrator: Orchestrateur personnalisé (optionnel)
            exchange: Exchange simulé (optionnel)
        """

    def initialize(self):
        """Sélectionne la meilleure stratégie via backtest."""

    def run_simulation(self, days: int = 10, trade_quantity: float = 0.01) -> Dict[str, Any]:
        """Exécute une simulation de trading avec analyse détaillée.

        Args:
            days: Nombre de jours à simuler
            trade_quantity: Quantité par trade

        Returns:
            Dictionnaire détaillé avec statistiques complètes:
            {
                "initial_balance": float,      # Balance de départ
                "final_balance": float,        # Balance finale
                "total_pnl": float,            # PnL total
                "total_return_pct": float,     # Rendement total en %
                "orders_count": int,           # Nombre total d'ordres
                "trades_count": int,           # Nombre de trades complets
                "winning_trades": int,         # Trades gagnants
                "losing_trades": int,          # Trades perdants
                "win_rate": float,             # Taux de réussite en %
                "avg_trade_pnl": float,        # PnL moyen par trade
                "strategy_name": str           # Nom de la stratégie utilisée
            }
        """
```

### MockExchange

Échange simulé pour les tests et paper trading.

```python
class MockExchange:
    def __init__(self, initial_balance: float = 10000.0):
        """Initialise l'échange simulé.

        Args:
            initial_balance: Balance initiale
        """

    def place_order(self, symbol: str, side: str, quantity: float, price: Optional[float] = None) -> str:
        """Place un ordre simulé.

        Args:
            symbol: Symbole (ex: 'BTC/USD')
            side: 'buy' ou 'sell'
            quantity: Quantité
            price: Prix (None = market order)

        Returns:
            ID de l'ordre
        """

    def get_balance(self) -> float:
        """Retourne la balance actuelle."""

    def get_positions(self) -> Dict[str, Position]:
        """Retourne les positions ouvertes."""

    def get_total_pnl(self) -> float:
        """Calcule le PnL total."""
```

## Fonctions Utiles

### run_backtest

Fonction principale pour exécuter un backtest.

```python
def run_backtest(strategy: StrategyAdapter, df: pd.DataFrame) -> Dict[str, float]:
    """Exécute un backtest complet.

    Args:
        strategy: Stratégie à tester
        df: Données OHLCV

    Returns:
        Dictionnaire avec métriques:
        {
            "total_return": float,    # Rendement total
            "sharpe": float,          # Ratio Sharpe annualisé
            "max_drawdown": float,    # Drawdown maximum
            "trades_count": int       # Nombre de trades
        }
    """
```

### generate_synthetic_data

Génère des données OHLCV synthétiques pour les tests.

```python
def generate_synthetic_data(days: int = 100, start_price: float = 100.0, volatility: float = 0.02) -> pd.DataFrame:
    """Génère des données synthétiques.

    Args:
        days: Nombre de jours
        start_price: Prix de départ
        volatility: Volatilité quotidienne

    Returns:
        DataFrame avec colonnes [timestamp, open, high, low, close, volume]
    """
```

### load_recent_data

Charge les données récentes pour l'orchestration.

```python
def load_recent_data(days: int = 30) -> pd.DataFrame:
    """Charge les données des 30 derniers jours.

    Args:
        days: Nombre de jours (défaut: 30)

    Returns:
        DataFrame OHLCV
    """
```

## Configuration

### Config

Classe de configuration centralisée.

```python
class Config:
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration.

        Args:
            key: Clé avec notation point (ex: 'trading.symbol')
            default: Valeur par défaut

        Returns:
            Valeur de configuration
        """

    @classmethod
    def is_live_mode(cls) -> bool:
        """Vérifie si le mode live est activé.

        Returns:
            True si LIVE=true dans l'environnement
        """
```

## Types de Données

### DataFrame OHLCV

Structure standard des données de marché :

```python
df = pd.DataFrame({
    'timestamp': pd.DatetimeIndex,  # Index temporel
    'open': pd.Series,               # Prix d'ouverture
    'high': pd.Series,               # Prix maximum
    'low': pd.Series,                # Prix minimum
    'close': pd.Series,              # Prix de clôture
    'volume': pd.Series              # Volume échangé
})
```

### Signaux de Trading

Les stratégies génèrent des signaux dans la colonne 'signal' :

- **1** : Signal d'achat (long)
- **0** : Neutre (pas de position)
- **-1** : Signal de vente (short)

### Métriques de Performance

Structure des résultats de backtest :

```python
metrics = {
    "total_return": 0.05,      # 5% de rendement total
    "sharpe": 1.2,             # Ratio Sharpe annualisé
    "max_drawdown": -0.03,     # -3% drawdown maximum
    "trades_count": 15         # 15 trades exécutés
}
```

## Gestion d'Erreurs

### Exceptions Courantes

- **ValueError** : Paramètres invalides
- **ConnectionError** : Problème de connexion API (mode live)
- **InsufficientFundsError** : Fonds insuffisants (mode live)

### Logging

Le système utilise le module `logging` standard :

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Message informatif")
logger.warning("Avertissement")
logger.error("Erreur")
```

## Exemples d'Utilisation

### Utilisation Basique

```python
from orchestrator import TradingOrchestrator

# Créer l'orchestrateur
orchestrator = TradingOrchestrator()

# Sélectionner la meilleure stratégie
strategy = orchestrator.select_best_strategy()
print(f"Stratégie sélectionnée: {strategy.name}")

# Évaluer toutes les stratégies
for strat in orchestrator.get_all_strategies():
    print(f"- {strat.name}")
```

### Backtest Manuel

```python
from orchestrator import run_backtest, generate_synthetic_data
from orchestrator.adapters.simple_strategies import SMACrossover

# Générer des données
df = generate_synthetic_data(days=100)

# Créer et tester une stratégie
strategy = SMACrossover(short=5, long=20)
results = run_backtest(strategy, df)

print(f"Rendement: {results['total_return']:.2%}")
print(f"Sharpe: {results['sharpe']:.2f}")
```

### Paper Trading

```python
from orchestrator import PaperTrader

# Créer et initialiser le trader
trader = PaperTrader()
trader.initialize()

# Lancer une simulation
results = trader.run_simulation(days=30, trade_quantity=0.01)

print(f"Balance initiale: ${results['initial_balance']:,.2f}")
print(f"Balance finale: ${results['final_balance']:,.2f}")
print(f"PnL total: ${results['total_pnl']:,.2f}")
print(f"Rendement: {results['total_return_pct']:+.2f}%")
print(f"Trades: {results['trades_count']} (Gagnants: {results['winning_trades']}, Perdants: {results['losing_trades']})")
print(f"Taux de réussite: {results['win_rate']:.1f}%")
print(f"PnL moyen par trade: ${results['avg_trade_pnl']:,.2f}")
