"""
Tests supplémentaires pour les utilitaires de sécurité.

Ce module contient des tests pour les fonctionnalités de sécurité
qui ne sont pas couvertes par les autres fichiers de test.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from jose import JWTError, jwt

from app.core.security import decode_token
from app.core.config import settings

# Données de test
TEST_USER_ID = 1


def test_verify_token_valid():
    """Teste la vérification d'un token JWT valide."""
    # Créer un token valide
    token_data = {"sub": str(TEST_USER_ID), "exp": datetime.now(timezone.utc) + timedelta(minutes=30), "type": "access"}
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Tester la vérification
    with patch("app.core.security.jwt.jwt.decode") as mock_decode:
        mock_decode.return_value = token_data
        payload = decode_token(token, token_type="access")
        assert payload is not None
        assert payload["sub"] == str(TEST_USER_ID)
        mock_decode.assert_called_once_with(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": True, "require": ["exp", "sub", "type"]},
        )


def test_verify_token_expired():
    """Teste la vérification d'un token JWT expiré."""
    # Créer un token expiré
    token_data = {"sub": str(TEST_USER_ID), "exp": datetime.now(timezone.utc) - timedelta(minutes=30), "type": "access"}
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Tester que l'exception est levée
    with pytest.raises(JWTExpiredSignatureError):
        decode_token(token, token_type="access")


def test_verify_token_missing_sub():
    """Teste la vérification d'un token JWT sans champ 'sub'."""
    # Créer un token sans 'sub'
    token_data = {"exp": datetime.now(timezone.utc) + timedelta(minutes=30), "type": "access"}
    token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Tester que l'exception est levée
    with pytest.raises(JWTError):
        decode_token(token, token_type="access")


def test_verify_token_invalid_signature():
    """Teste la vérification d'un token avec une signature invalide."""
    # Créer un token avec une clé secrète différente
    token_data = {"sub": str(TEST_USER_ID), "exp": datetime.now(timezone.utc) + timedelta(minutes=30), "type": "access"}
    token = jwt.encode(token_data, "wrong-secret-key", algorithm=settings.ALGORITHM)

    # Tester que l'exception est levée
    with pytest.raises(JWTError):
        decode_token(token, token_type="access")
