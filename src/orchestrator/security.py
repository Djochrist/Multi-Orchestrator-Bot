"""Mesures de sécurité pour le système de trading."""

import hashlib
import logging
import re
import time
from collections import defaultdict
from typing import Dict, List, Optional, Set

from .config import Config

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Exception pour violations de sécurité."""
    pass


class RateLimiter:
    """Limiteur de taux pour les requêtes."""

    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """Initialise le limiteur de taux.

        Args:
            max_requests: Nombre maximum de requêtes par fenêtre
            time_window: Fenêtre de temps en secondes
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, identifier: str) -> bool:
        """Vérifie si une requête est autorisée.

        Args:
            identifier: Identifiant unique (ex: IP, user_id)

        Returns:
            True si la requête est autorisée
        """
        now = time.time()

        # Nettoyer les anciennes requêtes
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.time_window
        ]

        # Vérifier le taux
        if len(self.requests[identifier]) >= self.max_requests:
            logger.warning(f"Taux de requêtes dépassé pour {identifier}")
            return False

        # Enregistrer la requête
        self.requests[identifier].append(now)
        return True

    def get_remaining_requests(self, identifier: str) -> int:
        """Retourne le nombre de requêtes restantes.

        Args:
            identifier: Identifiant unique

        Returns:
            Nombre de requêtes restantes
        """
        now = time.time()
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.time_window
        ]

        return max(0, self.max_requests - len(self.requests[identifier]))


class InputValidator:
    """Validateur d'entrée pour les données utilisateur."""

    # Patterns de validation
    SYMBOL_PATTERN = re.compile(r'^[A-Z]{2,10}/[A-Z]{2,10}$')
    API_KEY_PATTERN = re.compile(r'^[a-zA-Z0-9]{32,128}$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @staticmethod
    def validate_symbol(symbol: str) -> str:
        """Valide un symbole de trading.

        Args:
            symbol: Symbole à valider (ex: "BTC/USD")

        Returns:
            Symbole validé

        Raises:
            SecurityError: Si le symbole est invalide
        """
        if not symbol or not isinstance(symbol, str):
            raise SecurityError("Le symbole doit être une chaîne non vide")

        symbol = symbol.strip().upper()

        if not InputValidator.SYMBOL_PATTERN.match(symbol):
            raise SecurityError(f"Format de symbole invalide: {symbol}")

        # Vérifier contre la liste des symboles autorisés
        allowed_symbols = Config.get("security.allowed_symbols", [])
        if symbol not in allowed_symbols:
            raise SecurityError(f"Symbole non autorisé: {symbol}")

        return symbol

    @staticmethod
    def validate_quantity(quantity: float) -> float:
        """Valide une quantité de trading.

        Args:
            quantity: Quantité à valider

        Returns:
            Quantité validée

        Raises:
            SecurityError: Si la quantité est invalide
        """
        if not isinstance(quantity, (int, float)):
            raise SecurityError("La quantité doit être un nombre")

        if quantity <= 0:
            raise SecurityError("La quantité doit être positive")

        max_position = Config.get("trading.max_position_size", 1.0)
        if quantity > max_position:
            raise SecurityError(f"Quantité trop élevée: {quantity} > {max_position}")

        return float(quantity)

    @staticmethod
    def validate_api_key(api_key: str) -> str:
        """Valide une clé API.

        Args:
            api_key: Clé API à valider

        Returns:
            Clé API validée (hashée pour la sécurité)

        Raises:
            SecurityError: Si la clé API est invalide
        """
        if not api_key or not isinstance(api_key, str):
            raise SecurityError("La clé API doit être une chaîne non vide")

        if not InputValidator.API_KEY_PATTERN.match(api_key):
            raise SecurityError("Format de clé API invalide")

        # Hasher la clé pour éviter de la stocker en clair
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def validate_email(email: str) -> str:
        """Valide une adresse email.

        Args:
            email: Email à valider

        Returns:
            Email validé

        Raises:
            SecurityError: Si l'email est invalide
        """
        if not email or not isinstance(email, str):
            raise SecurityError("L'email doit être une chaîne non vide")

        email = email.strip().lower()

        if not InputValidator.EMAIL_PATTERN.match(email):
            raise SecurityError(f"Format d'email invalide: {email}")

        return email

    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 1000) -> str:
        """Nettoie une chaîne de caractères.

        Args:
            input_str: Chaîne à nettoyer
            max_length: Longueur maximum autorisée

        Returns:
            Chaîne nettoyée

        Raises:
            SecurityError: Si la chaîne est dangereuse
        """
        if not isinstance(input_str, str):
            raise SecurityError("L'entrée doit être une chaîne")

        # Vérifier la longueur
        if len(input_str) > max_length:
            raise SecurityError(f"Chaîne trop longue: {len(input_str)} > {max_length}")

        # Supprimer les caractères de contrôle
        cleaned = ''.join(c for c in input_str if ord(c) >= 32 or c in '\n\r\t')

        # Vérifier les patterns dangereux
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # JavaScript
            r'<[^>]+>',  # HTML tags
            r';\s*(DROP|DELETE|UPDATE|INSERT)\s+',  # SQL injection
            r'union\s+select',  # SQL injection
            r'--',  # SQL comments
            r'#',  # SQL comments
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, cleaned, re.IGNORECASE):
                raise SecurityError("Contenu potentiellement dangereux détecté")

        return cleaned.strip()


class APIKeyManager:
    """Gestionnaire de clés API avec rotation automatique."""

    def __init__(self):
        self.keys: Dict[str, Dict] = {}
        self.rotation_days = Config.get("security.api_key_rotation_days", 30)

    def add_key(self, service: str, api_key: str, secret_key: Optional[str] = None) -> None:
        """Ajoute une clé API.

        Args:
            service: Nom du service (ex: 'binance', 'coinbase')
            api_key: Clé API
            secret_key: Clé secrète (optionnel)
        """
        hashed_key = InputValidator.validate_api_key(api_key)

        self.keys[service] = {
            'key_hash': hashed_key,
            'secret': secret_key,
            'created_at': time.time(),
            'service': service
        }

        logger.info(f"Clé API ajoutée pour le service: {service}")

    def get_key(self, service: str) -> Optional[Dict]:
        """Récupère une clé API pour un service.

        Args:
            service: Nom du service

        Returns:
            Dictionnaire avec les informations de clé ou None
        """
        if service not in self.keys:
            return None

        key_info = self.keys[service]

        # Vérifier si la clé doit être renouvelée
        age_days = (time.time() - key_info['created_at']) / (24 * 3600)
        if age_days > self.rotation_days:
            logger.warning(f"Clé API expirée pour {service}, renouvellement requis")
            return None

        return key_info

    def remove_key(self, service: str) -> bool:
        """Supprime une clé API.

        Args:
            service: Nom du service

        Returns:
            True si supprimée, False sinon
        """
        if service in self.keys:
            del self.keys[service]
            logger.info(f"Clé API supprimée pour le service: {service}")
            return True
        return False

    def list_services(self) -> List[str]:
        """Liste les services avec des clés API.

        Returns:
            Liste des noms de services
        """
        return list(self.keys.keys())


class SecurityManager:
    """Gestionnaire central de sécurité."""

    def __init__(self):
        self.rate_limiter = RateLimiter(
            max_requests=Config.get("security.max_request_rate", 10)
        )
        self.api_keys = APIKeyManager()
        self.blocked_entities: Set[str] = set()

    def check_request_allowed(self, identifier: str) -> bool:
        """Vérifie si une requête est autorisée.

        Args:
            identifier: Identifiant de la requête (IP, user, etc.)

        Returns:
            True si autorisée

        Raises:
            SecurityError: Si bloquée ou taux dépassé
        """
        if identifier in self.blocked_entities:
            raise SecurityError(f"Entité bloquée: {identifier}")

        if not self.rate_limiter.is_allowed(identifier):
            raise SecurityError(f"Taux de requêtes dépassé pour: {identifier}")

        return True

    def block_entity(self, identifier: str) -> None:
        """Bloque une entité.

        Args:
            identifier: Identifiant à bloquer
        """
        self.blocked_entities.add(identifier)
        logger.warning(f"Entité bloquée: {identifier}")

    def unblock_entity(self, identifier: str) -> None:
        """Débloque une entité.

        Args:
            identifier: Identifiant à débloquer
        """
        self.blocked_entities.discard(identifier)
        logger.info(f"Entité débloquée: {identifier}")

    def is_entity_blocked(self, identifier: str) -> bool:
        """Vérifie si une entité est bloquée.

        Args:
            identifier: Identifiant à vérifier

        Returns:
            True si bloquée
        """
        return identifier in self.blocked_entities


# Instance globale du gestionnaire de sécurité
security_manager = SecurityManager()
