"""
Service de rotation des clés pour la sécurité de l'application.

Ce module fournit des fonctionnalités pour gérer la rotation sécurisée des clés cryptographiques
utilisées dans l'application, notamment pour les tokens JWT et le chiffrement.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import jwt
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class KeyRotationService:
    """
    Service de gestion de la rotation des clés de sécurité.

    Ce service permet de gérer plusieurs clés de signature JWT et de chiffrement,
    facilitant ainsi la rotation sécurisée des clés sans interruption de service.
    """

    def __init__(self):
        """Initialise le service avec les clés actuelles et historiques."""
        self.current_key_id = "key_1"
        self.keys: Dict[str, str] = {}
        self.key_rotation_interval = timedelta(days=30)
        self.last_rotation_date = datetime.utcnow()
        self._initialize_keys()

    def _initialize_keys(self):
        """Initialise les clés à partir des variables d'environnement."""
        # Clé principale (obligatoire)
        main_key = settings.SECRET_KEY
        if not main_key or main_key == "your-secret-key-here":
            raise ValueError(
                "La clé secrète principale n'est pas configurée correctement"
            )

        # Ajout de la clé principale avec l'ID actuel
        self.keys[self.current_key_id] = main_key

        # Clés historiques (optionnelles)
        for i in range(1, 4):  # Jusqu'à 3 clés historiques
            key = os.getenv(f"SECRET_KEY_{i}")
            if key:
                self.keys[f"key_{i}"] = key

    def get_current_key(self) -> Tuple[str, str]:
        """
        Retourne l'ID et la valeur de la clé actuelle.

        Returns:
            Tuple[str, str]: Un tuple contenant (key_id, key_value)
        """
        return self.current_key_id, self.keys[self.current_key_id]

    def rotate_keys(self, new_key: str) -> bool:
        """
        Effectue une rotation des clés.

        Args:
            new_key: La nouvelle clé à utiliser

        Returns:
            bool: True si la rotation a réussi, False sinon
        """
        if not new_key:
            logger.error("Tentative de rotation avec une clé vide")
            return False

        # Vérifier que la nouvelle clé est différente de l'actuelle
        if new_key == self.keys[self.current_key_id]:
            logger.warning("La nouvelle clé est identique à l'actuelle")
            return False

        try:
            # Générer un nouvel ID de clé (incrémenter le numéro)
            current_num = int(self.current_key_id.split("_")[1])
            new_key_id = f"key_{current_num + 1}"

            # Ajouter la nouvelle clé
            self.keys[new_key_id] = new_key

            # Mettre à jour la clé actuelle
            old_key_id = self.current_key_id
            self.current_key_id = new_key_id
            self.last_rotation_date = datetime.utcnow()

            logger.info(f"Rotation des clés effectuée: {old_key_id} -> {new_key_id}")

            # Supprimer les anciennes clés (conserver uniquement les 3 dernières)
            self._cleanup_old_keys()

            return True

        except Exception as e:
            logger.error(f"Échec de la rotation des clés: {str(e)}", exc_info=True)
            return False

    def _cleanup_old_keys(self):
        """Nettoie les anciennes clés, ne garde que les 3 plus récentes."""
        # Trier les clés par numéro (du plus ancien au plus récent)
        sorted_keys = sorted(
            [k for k in self.keys.keys() if k.startswith("key_")],
            key=lambda x: int(x.split("_")[1]),
        )

        # Supprimer les clés les plus anciennes (sauf les 3 plus récentes)
        for key_id in sorted_keys[:-3]:
            if key_id != self.current_key_id:  # Ne pas supprimer la clé actuelle
                self.keys.pop(key_id, None)

    def should_rotate(self) -> bool:
        """
        Vérifie si une rotation des clés est nécessaire.

        Returns:
            bool: True si une rotation est nécessaire, False sinon
        """
        time_since_rotation = datetime.utcnow() - self.last_rotation_date
        return time_since_rotation >= self.key_rotation_interval

    def decode_token(self, token: str) -> dict:
        """
        Décode un token JWT en essayant toutes les clés disponibles.

        Args:
            token: Le token JWT à décoder

        Returns:
            dict: Le payload décodé

        Raises:
            HTTPException: Si le token est invalide ou expiré
        """
        for key_id, key in self.keys.items():
            try:
                payload = jwt.decode(
                    token,
                    key,
                    algorithms=[settings.JWT_ALGORITHM],
                    options={"verify_signature": True, "verify_aud": False},
                )
                return payload
            except jwt.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expiré",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except jwt.JWTError:
                # Essayer avec la clé suivante
                continue

        # Si aucune clé ne fonctionne
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossible de valider les informations d'identification",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def encode_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crée un nouveau token JWT signé avec la clé actuelle.

        Args:
            data: Les données à encoder dans le token
            expires_delta: Durée de validité du token

        Returns:
            str: Le token JWT encodé
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire, "kid": self.current_key_id})

        return jwt.encode(
            to_encode, self.keys[self.current_key_id], algorithm=settings.JWT_ALGORITHM
        )


# Instance singleton du service
key_rotation_service = KeyRotationService()
