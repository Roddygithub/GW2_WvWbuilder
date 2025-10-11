"""
Module de gestion de la rotation des clés de sécurité.

Ce module fournit des fonctions pour gérer la rotation des clés JWT
de manière sécurisée et efficace.
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from jose import jwt
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)


class KeyRotationConfig(BaseModel):
    """Configuration de la rotation des clés."""

    current_key: str
    previous_key: Optional[str] = None
    next_rotation: datetime
    rotation_interval: timedelta = timedelta(days=1)  # Rotation quotidienne par défaut


class KeyRotationManager:
    """Gestionnaire de rotation des clés de sécurité."""

    def __init__(self, initial_key: Optional[str] = None):
        """Initialise le gestionnaire de rotation des clés.

        Args:
            initial_key: Clé initiale à utiliser (générée aléatoirement si None)
        """
        self._config = self._load_or_initialize(initial_key)

    def _load_or_initialize(self, initial_key: Optional[str] = None) -> KeyRotationConfig:
        """Charge la configuration existante ou initialise une nouvelle configuration."""
        # Dans une implémentation réelle, cela pourrait charger depuis une base de données
        # ou un service de configuration sécurisé comme AWS Secrets Manager ou HashiCorp Vault

        # Pour cette implémentation, nous utilisons une configuration en mémoire
        # qui sera perdue au redémarrage du serveur
        key = initial_key or secrets.token_urlsafe(64)
        return KeyRotationConfig(current_key=key, next_rotation=datetime.utcnow() + timedelta(days=1))

    def get_current_key(self) -> str:
        """Retourne la clé actuelle et effectue une rotation si nécessaire."""
        self._rotate_if_needed()
        return self._config.current_key

    def get_previous_key(self) -> Optional[str]:
        """Retourne la clé précédente (pour la validation des tokens expirés)."""
        return self._config.previous_key

    def get_keys(self) -> Tuple[str, Optional[str]]:
        """Retourne le tuple (clé_actuelle, clé_précédente)."""
        return self._config.current_key, self._config.previous_key

    def _rotate_if_needed(self) -> None:
        """Effectue une rotation de clé si nécessaire."""
        if datetime.utcnow() >= self._config.next_rotation:
            self.rotate_key()

    def rotate_key(self) -> str:
        """Effectue une rotation de clé manuelle.

        Returns:
            str: La nouvelle clé générée
        """
        logger.info("Rotation de la clé de sécurité...")

        # Sauvegarder l'ancienne clé
        self._config.previous_key = self._config.current_key

        # Générer une nouvelle clé
        self._config.current_key = secrets.token_urlsafe(64)

        # Planifier la prochaine rotation
        self._config.next_rotation = datetime.utcnow() + self._config.rotation_interval

        logger.info("Nouvelle clé de sécurité générée")

        # Dans une implémentation réelle, il faudrait sauvegarder la configuration
        # pour la persistance entre les redémarrages

        return self._config.current_key

    def decode_token(self, token: str) -> Dict:
        """Décode un token JWT en utilisant la clé actuelle ou précédente.

        Args:
            token: Le token JWT à décoder

        Returns:
            Dict: Les données décodées du token

        Raises:
            jwt.JWTError: Si le token est invalide ou expiré
        """
        # Essayer d'abord avec la clé actuelle
        try:
            return jwt.decode(
                token, self._config.current_key, algorithms=[settings.JWT_ALGORITHM], options={"verify_aud": False}
            )
        except jwt.JWTError as e:
            # Si échec et qu'il y a une clé précédente, essayer avec
            if self._config.previous_key:
                try:
                    return jwt.decode(
                        token,
                        self._config.previous_key,
                        algorithms=[settings.JWT_ALGORITHM],
                        options={"verify_aud": False},
                    )
                except jwt.JWTError:
                    # Si les deux échouent, relancer l'erreur originale
                    raise e
            else:
                raise


# Instance globale du gestionnaire de rotation des clés
key_manager = KeyRotationManager(initial_key=settings.SECRET_KEY)


def get_key_manager() -> KeyRotationManager:
    """Retourne l'instance du gestionnaire de rotation des clés."""
    return key_manager
