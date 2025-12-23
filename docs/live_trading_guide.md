# Guide du Trading Réel - Multi-Orchestrator-Bot

Ce guide explique comment utiliser le Multi-Orchestrator-Bot pour effectuer du trading réel sur les marchés financiers.

## ⚠️ AVERTISSEMENT IMPORTANT

**LE TRADING RÉEL IMPLIQUE DES RISQUES FINANCIERS SUBSTANTIELS**

- Vous pouvez perdre tout votre capital investi
- Les performances passées ne garantissent pas les résultats futurs
- Ce bot est fourni "tel quel" sans garantie de performance
- Consultez un conseiller financier avant d'investir

## Prérequis pour le Trading Réel

### 1. Configuration Matérielle
- **Ordinateur fiable** : Serveur dédié ou VPS recommandé
- **Connexion internet stable** : Éviter les coupures
- **Alimentation électrique** : UPS recommandé
- **Sauvegarde automatique** : Système de sauvegarde des données

### 2. Configuration Logicielle
```bash
# Installation des dépendances
pip install -r requirements.txt

# Configuration du timezone
export TZ="Europe/Paris"  # ou votre timezone

# Test de connectivité
python -c "import yfinance; print('Yahoo Finance OK')"
python -c "import ccxt; print('CCXT OK')"
```

### 3. Comptes de Trading
#### Brokers Recommandés
- **Binance** : Support complet via CCXT
- **Kraken** : Bon support crypto
- **Interactive Brokers** : Actions, futures, forex
- **OANDA** : Forex spécialisé

#### Création d'un Compte Demo
```bash
# Testez d'abord avec un compte demo
# Binance offre des comptes de test
# Utilisez toujours le mode sandbox en premier
```

## Configuration du Bot

### 1. Fichier de Configuration
Créez `config/live_config.yml` :

```yaml
# Configuration pour trading réel
trading:
  symbol: "BTC/USDT"  # Paire à trader
  initial_balance: 1000  # Balance initiale en quote currency
  position_size_pct: 0.05  # 5% du capital par trade
  max_positions: 3  # Nombre maximum de positions simultanées

  # Gestion du risque
  risk_management:
    max_drawdown_pct: 0.10  # Stop à 10% de perte
    daily_loss_limit_pct: 0.05  # Limite de perte journalière
    max_position_size_pct: 0.10  # Taille max par position

  # Paramètres de stratégie
  strategy_params:
    OrderFlowImbalance:
      volume_window: 15
      imbalance_threshold: 1.2
      momentum_period: 5
      stop_loss_pct: 0.025
      take_profit_pct: 0.05

# Configuration des échanges
exchanges:
  binance:
    api_key: "votre_api_key_ici"
    api_secret: "votre_api_secret_ici"
    sandbox: true  # METTEZ false POUR TRADING RÉEL

# Logging et monitoring
logging:
  level: "INFO"
  file: "logs/live_trading.log"
  max_file_size: 10485760  # 10MB
  backup_count: 5

# Alertes (optionnel)
alerts:
  telegram:
    enabled: true
    bot_token: "votre_bot_token"
    chat_id: "votre_chat_id"
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "votre@email.com"
    password: "votre_mot_de_passe"
```

### 2. Variables d'Environnement
```bash
# Variables sensibles (NE PAS les mettre dans le code)
export BINANCE_API_KEY="votre_clé_api"
export BINANCE_API_SECRET="votre_secret_api"
export TELEGRAM_BOT_TOKEN="token_bot"
export LIVE_TRADING="true"  # Active le mode réel
```

## Démarrage du Trading Réel

### Phase 1 : Tests en Mode Sandbox
```bash
# 1. Test avec données historiques
python examples/advanced_backtest_example.py

# 2. Test en mode paper trading
python -m orchestrator.cli papertrade --days 7

# 3. Test avec compte sandbox (simulé)
LIVE=true python -m orchestrator.cli papertrade --live
```

### Phase 2 : Trading Réel Progressif
```bash
# Petit capital initial (ex: 100$)
python live_trading_bot.py --config config/live_config.yml --capital 100

# Augmenter progressivement
python live_trading_bot.py --config config/live_config.yml --capital 500
python live_trading_bot.py --config config/live_config.yml --capital 1000
```

## Scripts de Trading Automatisé

### 1. Bot de Trading Continu
Créez `live_trading_bot.py` :

```python
#!/usr/bin/env python3
"""
Bot de trading réel pour Multi-Orchestrator-Bot
"""

import os
import sys
import time
import logging
import signal
import yaml
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Ajouter src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from orchestrator.orchestrator import TradingOrchestrator
from orchestrator.adapters.live_exchange import LiveExchange
from orchestrator.adapters.alert_system import AlertSystem

class LiveTradingBot:
    """Bot de trading en temps réel."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.load_config()
        self.orchestrator = TradingOrchestrator()
        self.exchange = LiveExchange(self.config['exchanges'])
        self.alerts = AlertSystem(self.config.get('alerts', {}))
        self.is_running = False

        # Métriques de performance
        self.daily_pnl = 0
        self.total_pnl = 0
        self.start_balance = self.config['trading']['initial_balance']

        # Gestion des signaux système
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def load_config(self) -> Dict[str, Any]:
        """Charge la configuration."""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def initialize(self):
        """Initialisation du bot."""
        logger.info("🤖 Initialisation du bot de trading réel")

        # Vérification de la configuration
        self.validate_config()

        # Connexion à l'échange
        if not self.exchange.connect():
            raise Exception("❌ Impossible de se connecter à l'échange")

        # Vérification du solde
        balance = self.exchange.get_balance()
        logger.info(f"💰 Solde disponible: {balance}")

        # Sélection de la stratégie optimale
        best_strategy = self.orchestrator.select_best_strategy()
        logger.info(f"🎯 Stratégie sélectionnée: {best_strategy.name}")

        self.alerts.send_message("🤖 Bot de trading initialisé avec succès")

    def validate_config(self):
        """Validation de la configuration."""
        required_keys = ['trading', 'exchanges']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"❌ Clé requise manquante: {key}")

        # Validation des paramètres de risque
        risk_config = self.config['trading'].get('risk_management', {})
        if risk_config.get('max_drawdown_pct', 0) > 0.20:
            logger.warning("⚠️ Drawdown maximum élevé détecté")

    def check_risk_limits(self) -> bool:
        """Vérifie les limites de risque."""
        # Vérification du drawdown journalier
        daily_loss_limit = self.config['trading']['risk_management']['daily_loss_limit_pct']

        if self.daily_pnl < -self.start_balance * daily_loss_limit:
            logger.error("🚨 Limite de perte journalière atteinte")
            self.alerts.send_message("🚨 Arrêt d'urgence: Limite de perte journalière atteinte")
            return False

        # Vérification du drawdown maximum
        max_drawdown = self.config['trading']['risk_management']['max_drawdown_pct']
        current_drawdown = (self.start_balance + self.total_pnl) / self.start_balance - 1

        if current_drawdown < -max_drawdown:
            logger.error("🚨 Drawdown maximum atteint")
            self.alerts.send_message("🚨 Arrêt d'urgence: Drawdown maximum atteint")
            return False

        return True

    def execute_trading_logic(self):
        """Logique principale de trading."""
        try:
            # Récupération des données récentes
            df = self.exchange.get_recent_data(hours=24)  # Dernières 24h

            # Génération des signaux
            signals = self.orchestrator.generate_signals(df)

            # Vérification des conditions d'entrée
            for signal in signals:
                if self.should_enter_position(signal):
                    self.enter_position(signal)

            # Gestion des positions existantes
            self.manage_positions()

        except Exception as e:
            logger.error(f"❌ Erreur dans la logique de trading: {e}")
            self.alerts.send_message(f"❌ Erreur: {e}")

    def should_enter_position(self, signal) -> bool:
        """Détermine si on doit entrer en position."""
        # Vérifications de risque
        if not self.check_risk_limits():
            return False

        # Vérification de la volatilité
        volatility = self.exchange.get_current_volatility()
        if volatility > 0.05:  # 5% de volatilité
            logger.info("⚠️ Volatilité élevée détectée, attente")
            return False

        # Vérification du timing (éviter les heures de faible liquidité)
        current_hour = datetime.now().hour
        if current_hour < 8 or current_hour > 20:  # Trading 8h-20h UTC
            return False

        return True

    def enter_position(self, signal):
        """Entre en position."""
        position_size = self.calculate_position_size(signal)

        try:
            order = self.exchange.place_order(
                symbol=signal['symbol'],
                side=signal['side'],
                quantity=position_size,
                order_type='market'
            )

            logger.info(f"📈 Position ouverte: {order}")
            self.alerts.send_message(f"📈 Position: {signal['symbol']} {signal['side']} {position_size}")

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ouverture de position: {e}")

    def calculate_position_size(self, signal) -> float:
        """Calcule la taille de position basée sur le risque."""
        risk_pct = self.config['trading']['position_size_pct']
        account_balance = self.exchange.get_balance()

        # Calcul basé sur le stop loss
        stop_loss_pct = self.config['trading']['strategy_params']['OrderFlowImbalance']['stop_loss_pct']
        risk_amount = account_balance * risk_pct
        position_size = risk_amount / (signal['entry_price'] * stop_loss_pct)

        # Limite de taille maximale
        max_size_pct = self.config['trading']['risk_management']['max_position_size_pct']
        max_size = account_balance * max_size_pct / signal['entry_price']
        position_size = min(position_size, max_size)

        return position_size

    def manage_positions(self):
        """Gère les positions existantes."""
        positions = self.exchange.get_positions()

        for position in positions:
            if self.should_close_position(position):
                self.close_position(position)

    def should_close_position(self, position) -> bool:
        """Détermine si une position doit être fermée."""
        # Vérification des stops/targets
        current_price = self.exchange.get_current_price(position['symbol'])

        if position['side'] == 'long':
            stop_loss = position['entry_price'] * (1 - position['stop_loss_pct'])
            take_profit = position['entry_price'] * (1 + position['take_profit_pct'])

            if current_price <= stop_loss or current_price >= take_profit:
                return True
        else:  # short
            stop_loss = position['entry_price'] * (1 + position['stop_loss_pct'])
            take_profit = position['entry_price'] * (1 - position['take_profit_pct'])

            if current_price >= stop_loss or current_price <= take_profit:
                return True

        return False

    def close_position(self, position):
        """Ferme une position."""
        try:
            order = self.exchange.close_position(position['symbol'])
            pnl = self.calculate_pnl(position)

            logger.info(f"🔒 Position fermée: {position['symbol']} | PnL: {pnl}")
            self.alerts.send_message(f"🔒 Fermeture: {position['symbol']} | PnL: {pnl}")

            # Mise à jour des métriques
            self.total_pnl += pnl

        except Exception as e:
            logger.error(f"❌ Erreur lors de la fermeture: {e}")

    def calculate_pnl(self, position) -> float:
        """Calcule le PnL d'une position."""
        current_price = self.exchange.get_current_price(position['symbol'])
        entry_price = position['entry_price']
        quantity = position['quantity']

        if position['side'] == 'long':
            return (current_price - entry_price) * quantity
        else:
            return (entry_price - current_price) * quantity

    def signal_handler(self, signum, frame):
        """Gestionnaire de signaux système."""
        logger.info("🛑 Signal d'arrêt reçu, fermeture des positions...")
        self.emergency_stop()

    def emergency_stop(self):
        """Arrêt d'urgence."""
        try:
            # Fermeture de toutes les positions
            positions = self.exchange.get_positions()
            for position in positions:
                self.close_position(position)

            logger.info("🔴 Arrêt d'urgence terminé")
            self.alerts.send_message("🔴 Arrêt d'urgence du bot")

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'arrêt d'urgence: {e}")

        finally:
            self.is_running = False

    def run(self):
        """Boucle principale du bot."""
        logger.info("🚀 Démarrage du bot de trading réel")

        try:
            self.initialize()
            self.is_running = True

            while self.is_running:
                self.execute_trading_logic()

                # Pause entre les cycles (ex: 5 minutes)
                time.sleep(300)

                # Réinitialisation du PnL journalier à minuit
                if datetime.now().hour == 0 and datetime.now().minute < 5:
                    self.daily_pnl = 0
                    logger.info("🌅 Nouveau jour de trading")

        except Exception as e:
            logger.error(f"❌ Erreur critique: {e}")
            self.alerts.send_message(f"❌ Erreur critique: {e}")

        finally:
            self.emergency_stop()


def main():
    """Fonction principale."""
    import argparse

    parser = argparse.ArgumentParser(description='Bot de Trading Réel')
    parser.add_argument('--config', required=True, help='Chemin vers le fichier de config')
    parser.add_argument('--capital', type=float, help='Capital initial')

    args = parser.parse_args()

    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/live_trading.log'),
            logging.StreamHandler()
        ]
    )

    # Vérification des variables d'environnement
    if not os.getenv('LIVE_TRADING'):
        logger.warning("⚠️ Mode LIVE_TRADING non activé, fonctionnement en mode test")

    # Démarrage du bot
    bot = LiveTradingBot(args.config)
    bot.run()


if __name__ == "__main__":
    main()
```

### 2. Système d'Alertes
Créez `src/orchestrator/adapters/alert_system.py` :

```python
"""Système d'alertes pour le trading réel."""

import requests
import smtplib
from email.mime.text import MIMEText
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AlertSystem:
    """Système d'alertes multi-canaux."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def send_message(self, message: str, level: str = "info"):
        """Envoie un message via tous les canaux configurés."""

        # Telegram
        if self.config.get('telegram', {}).get('enabled'):
            self.send_telegram(message, level)

        # Email
        if self.config.get('email', {}).get('enabled'):
            self.send_email(message, level)

        # Log
        logger.info(f"📢 Alerte {level}: {message}")

    def send_telegram(self, message: str, level: str):
        """Envoie un message Telegram."""
        try:
            config = self.config['telegram']
            token = config['bot_token']
            chat_id = config['chat_id']

            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': f"🤖 Trading Bot Alert\n\n{message}",
                'parse_mode': 'HTML'
            }

            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()

        except Exception as e:
            logger.error(f"Erreur Telegram: {e}")

    def send_email(self, message: str, level: str):
        """Envoie un email."""
        try:
            config = self.config['email']

            msg = MIMEText(message)
            msg['Subject'] = f'Trading Bot Alert - {level.upper()}'
            msg['From'] = config['username']
            msg['To'] = config['username']  # ou liste d'emails

            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.sendmail(config['username'], [msg['To']], msg.as_string())
            server.quit()

        except Exception as e:
            logger.error(f"Erreur Email: {e}")
```

### 3. Échange Live
Créez `src/orchestrator/adapters/live_exchange.py` :

```python
"""Adaptateur pour échanges réels."""

import ccxt
import pandas as pd
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class LiveExchange:
    """Interface pour échanges réels via CCXT."""

    def __init__(self, exchange_config: Dict[str, Any]):
        self.config = exchange_config
        self.exchange = None
        self.symbol = "BTC/USDT"  # Configurable

    def connect(self) -> bool:
        """Connexion à l'échange."""
        try:
            exchange_name = list(self.config.keys())[0]
            config = self.config[exchange_name]

            exchange_class = getattr(ccxt, exchange_name)
            self.exchange = exchange_class({
                'apiKey': config['api_key'],
                'secret': config['api_secret'],
                'sandbox': config.get('sandbox', True),
                'enableRateLimit': True,
            })

            # Test de connexion
            self.exchange.loadMarkets()
            logger.info(f"✅ Connecté à {exchange_name} (sandbox: {config.get('sandbox', True)})")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur de connexion: {e}")
            return False

    def get_balance(self) -> float:
        """Récupère le solde disponible."""
        try:
            balance = self.exchange.fetch_balance()
            return balance['total'].get('USDT', 0)
        except Exception as e:
            logger.error(f"Erreur récupération solde: {e}")
            return 0

    def get_recent_data(self, hours: int = 24) -> pd.DataFrame:
        """Récupère les données récentes."""
        try:
            since = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, '1h', since=since)

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            return df

        except Exception as e:
            logger.error(f"Erreur récupération données: {e}")
            return pd.DataFrame()

    def place_order(self, symbol: str, side: str, quantity: float, order_type: str = 'market', price: Optional[float] = None) -> Dict[str, Any]:
        """Place un ordre."""
        try:
            if order_type == 'market':
                order = self.exchange.create_market_order(symbol, side, quantity)
            elif order_type == 'limit' and price:
                order = self.exchange.create_limit_order(symbol, side, quantity, price)
            else:
                raise ValueError("Type d'ordre non supporté")

            logger.info(f"📋 Ordre {side} {quantity} {symbol} placé: {order['id']}")
            return order

        except Exception as e:
            logger.error(f"Erreur placement ordre: {e}")
            raise

    def get_positions(self) -> List[Dict[str, Any]]:
        """Récupère les positions ouvertes."""
        # Pour les exchanges spot, simuler avec les ordres ouverts
        try:
            orders = self.exchange.fetch_open_orders(self.symbol)
            positions = []

            for order in orders:
                positions.append({
                    'symbol': order['symbol'],
                    'side': order['side'],
                    'quantity': order['amount'],
                    'entry_price': order['price'],
                    'stop_loss_pct': 0.02,  # Configurable
                    'take_profit_pct': 0.04,  # Configurable
                })

            return positions

        except Exception as e:
            logger.error(f"Erreur récupération positions: {e}")
            return []

    def close_position(self, symbol: str) -> Dict[str, Any]:
        """Ferme une position."""
        try:
            # Pour spot, créer un ordre opposé
            positions = self.get_positions()
            for position in positions:
                if position['symbol'] == symbol:
                    side = 'sell' if position['side'] == 'buy' else 'buy'
                    order = self.exchange.create_market_order(symbol, side, position['quantity'])
                    logger.info(f"🔒 Position {symbol} fermée")
                    return order

        except Exception as e:
            logger.error(f"Erreur fermeture position: {e}")
            raise

    def get_current_price(self, symbol: str) -> float:
        """Récupère le prix actuel."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Erreur récupération prix: {e}")
            return 0

    def get_current_volatility(self) -> float:
        """Calcule la volatilité actuelle."""
        try:
            df = self.get_recent_data(hours=24)
            if len(df) > 0:
                returns = df['close'].pct_change().dropna()
                return returns.std() * (252 ** 0.5)  # Annualisée
            return 0
        except Exception as e:
            logger.error(f"Erreur calcul volatilité: {e}")
            return 0
```

## Monitoring et Maintenance

### 1. Dashboard de Surveillance
```bash
# Installation de Grafana + Prometheus pour monitoring
pip install grafana-client prometheus-client

# Ou utilisation simple avec script Python
python monitoring_dashboard.py
```

### 2. Logs et Alertes
```bash
# Surveillance des logs en temps réel
tail -f logs/live_trading.log

# Recherche d'erreurs
grep "ERROR" logs/live_trading.log

# Alertes sur seuils
python alert_monitor.py
```

### 3. Sauvegarde Automatique
```bash
# Script de sauvegarde
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz logs/ config/
echo "Sauvegarde créée: backup_$DATE.tar.gz"
```

## Optimisation et Amélioration

### 1. Walk-Forward Analysis
```python
# Optimisation progressive
def walk_forward_optimization(data, window_size=252):  # 1 an
    results = []

    for i in range(window_size, len(data), 21):  # Toutes les 3 semaines
        train_data = data[i-window_size:i]
        test_data = data[i:i+21]

        # Optimisation sur train_data
        best_params = optimize_parameters(train_data)

        # Validation sur test_data
        performance = evaluate_parameters(test_data, best_params)

        results.append(performance)

    return results
```

### 2. Risk Parity et Diversification
```python
# Allocation basée sur le risque
def risk_parity_allocation(returns, target_volatility=0.10):
    # Calcul de la matrice de covariance
    cov_matrix = returns.cov()

    # Optimisation pour allocation équipondérée en risque
    # (Implémentation avec scipy.optimize)
    pass
```

## Checklist Pré-Lancement

### ✅ Avant de Trader Réel
- [ ] **Backtests sur 2+ ans** de données historiques
- [ ] **Tests sur compte demo** pendant au moins 1 mois
- [ ] **Vérification des frais** de trading (commission, spread)
- [ ] **Test de connectivité** réseau stable 24/7
- [ ] **Plan de contingence** en cas de panne
- [ ] **Limites de risque** définies et testées
- [ ] **Système d'alertes** configuré et testé

### ✅ Pendant le Trading
- [ ] **Monitoring continu** des positions
- [ ] **Logs analysés** quotidiennement
- [ ] **Rééquilibrage** des paramètres si nécessaire
- [ ] **Sauvegarde** régulière des données
- [ ] **Révision mensuelle** des performances

### ⚠️ Points Critiques
- **N'investissez que ce que vous pouvez perdre**
- **Commencez petit** et augmentez progressivement
- **Ayez toujours un plan d'arrêt d'urgence**
- **Ne tradez pas sur émotions**
- **Gardez des liquidités** pour les urgences

---

**Rappel : Ce guide est fourni à titre éducatif. Le trading comporte des risques importants et peut entraîner des pertes financières.**
