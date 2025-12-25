"""Configuration du système de trading avec support fichier et variables d'environnement."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Exception pour erreurs de configuration."""
    pass


class Config:
    """Configuration centralisée avec support fichier et variables d'environnement."""

    # Paramètres par défaut
    DEFAULTS = {
        "trading": {
            "symbol": "BTC/USD",
            "default_quantity": 0.01,
            "max_position_size": 0.1,
        },
        "backtest": {
            "recent_days": 30,
            "min_data_points": 50,
        },
        "risk": {
            "max_drawdown": 0.1,  # 10%
            "max_trades_per_day": 5,
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "security": {
            "api_key_rotation_days": 30,
            "max_request_rate": 10,  # requests per minute
            "allowed_symbols": ["BTC/USD", "ETH/USD", "BNB/USD"],
        },
        "data": {
            "cache_enabled": True,
            "cache_ttl_hours": 24,
            "max_retries": 3,
            "timeout_seconds": 30,
        },
    }

    _config_cache: Optional[Dict[str, Any]] = None
    _config_file_path: Optional[Path] = None

    @classmethod
    def load_from_file(cls, config_path: Optional[str] = None) -> None:
        """Charge la configuration depuis un fichier YAML.

        Args:
            config_path: Chemin vers le fichier de configuration.
                        Si None, cherche dans l'ordre:
                        - Variable d'environnement TRADING_CONFIG_PATH
                        - config.yml dans le répertoire courant
                        - config.yaml dans le répertoire courant
                        - examples/config.example.yml

        Raises:
            ConfigError: Si le fichier n'existe pas ou est invalide
        """
        if config_path:
            file_path = Path(config_path)
        else:
            # Recherche automatique du fichier de configuration
            search_paths = [
                os.getenv("TRADING_CONFIG_PATH"),
                "config.yml",
                "config.yaml",
                "examples/config.example.yml",
            ]

            file_path = None
            for path_str in search_paths:
                if path_str:
                    path = Path(path_str)
                    if path.exists():
                        file_path = path
                        break

        if not file_path or not file_path.exists():
            logger.warning("Aucun fichier de configuration trouvé, utilisation des valeurs par défaut")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)

            if not isinstance(file_config, dict):
                raise ConfigError(f"Configuration invalide dans {file_path}: doit être un dictionnaire")

            cls._config_cache = cls._merge_configs(cls.DEFAULTS, file_config)
            cls._config_file_path = file_path
            logger.info(f"Configuration chargée depuis {file_path}")

        except yaml.YAMLError as e:
            raise ConfigError(f"Erreur de syntaxe YAML dans {file_path}: {e}") from e
        except Exception as e:
            raise ConfigError(f"Erreur lors du chargement de {file_path}: {e}") from e

    @classmethod
    def _merge_configs(cls, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Fusionne récursivement deux configurations.

        Args:
            base: Configuration de base
            override: Configuration qui écrase la base

        Returns:
            Configuration fusionnée
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = cls._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration avec priorité: env > fichier > défaut.

        Args:
            key: Clé de configuration (peut être dotted, ex: "trading.symbol")
            default: Valeur par défaut si non trouvée

        Returns:
            Valeur de configuration
        """
        # Vérifier d'abord les variables d'environnement
        env_key = f"TRADING_{key.upper().replace('.', '_')}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            # Conversion de type basique
            if env_value.lower() in ('true', 'false'):
                return env_value.lower() == 'true'
            try:
                # Essayer de convertir en nombre
                if '.' in env_value:
                    return float(env_value)
                return int(env_value)
            except ValueError:
                return env_value

        # Puis vérifier le cache de configuration fichier
        if cls._config_cache is not None:
            keys = key.split(".")
            value = cls._config_cache
            try:
                for k in keys:
                    value = value[k]
                return value
            except KeyError:
                pass

        # Enfin utiliser les valeurs par défaut
        keys = key.split(".")
        value = cls.DEFAULTS
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default

    @classmethod
    def is_live_mode(cls) -> bool:
        """Vérifie si le mode live est activé."""
        return cls.get("live_mode", False) or os.getenv("LIVE", "false").lower() == "true"

    @classmethod
    def validate_config(cls) -> None:
        """Valide la configuration chargée.

        Raises:
            ConfigError: Si la configuration est invalide
        """
        # Validation des valeurs critiques
        if cls.get("trading.default_quantity", 0) <= 0:
            raise ConfigError("trading.default_quantity doit être positif")

        if not (0 < cls.get("risk.max_drawdown", 0) <= 1):
            raise ConfigError("risk.max_drawdown doit être entre 0 et 1")

        max_trades = cls.get("risk.max_trades_per_day", 0)
        if max_trades < 0:
            raise ConfigError("risk.max_trades_per_day doit être positif ou nul")

        # Validation de sécurité
        if cls.get("security.max_request_rate", 0) <= 0:
            raise ConfigError("security.max_request_rate doit être positif")

        allowed_symbols = cls.get("security.allowed_symbols", [])
        if not isinstance(allowed_symbols, list) or not allowed_symbols:
            raise ConfigError("security.allowed_symbols doit être une liste non vide")

        logger.info("Configuration validée avec succès")

    @classmethod
    def get_config_path(cls) -> Optional[Path]:
        """Retourne le chemin du fichier de configuration chargé."""
        return cls._config_file_path

    @classmethod
    def reload_config(cls) -> None:
        """Recharge la configuration depuis le fichier."""
        if cls._config_file_path:
            cls.load_from_file(str(cls._config_file_path))
        else:
            cls._config_cache = None
            logger.info("Configuration rechargée avec valeurs par défaut")
