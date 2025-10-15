"""
Tests pour le module de rotation des clés.

Ces tests vérifient le bon fonctionnement de la rotation des clés JWT.
"""

import pytest
from datetime import datetime, timedelta

from app.core.key_rotation import KeyRotationConfig, KeyRotationManager


def test_key_rotation_initialization():
    """Teste l'initialisation du gestionnaire de rotation des clés."""
    # Test avec une clé personnalisée
    custom_key = "ma_cle_secrete_tres_longue_et_securisee"
    manager = KeyRotationManager(initial_key=custom_key)

    # Vérifier que la clé actuelle est bien celle fournie
    assert manager.get_current_key() == custom_key
    assert manager.get_previous_key() is None

    # Test avec génération aléatoire
    manager = KeyRotationManager()
    key = manager.get_current_key()
    assert isinstance(key, str)
    assert len(key) >= 64  # La clé doit être suffisamment longue


def test_key_rotation():
    """Teste la rotation des clés."""
    # Initialiser avec une clé connue
    initial_key = "cle_initiale"
    manager = KeyRotationManager(initial_key=initial_key)

    # Vérifier l'état initial
    assert manager.get_current_key() == initial_key
    assert manager.get_previous_key() is None

    # Effectuer une rotation
    new_key = manager.rotate_key()

    # Vérifier que la rotation a fonctionné
    assert manager.get_current_key() == new_key
    assert manager.get_previous_key() == initial_key
    assert new_key != initial_key


def test_automatic_rotation():
    """Teste la rotation automatique des clés."""
    # Créer une configuration avec un intervalle de rotation très court
    initial_key = "cle_initiale"
    rotation_interval = timedelta(
        seconds=1
    )  # Rotation toutes les secondes pour le test

    # Créer une configuration personnalisée
    config = KeyRotationConfig(
        current_key=initial_key,
        next_rotation=datetime.utcnow() - timedelta(seconds=1),  # Déjà expiré
        rotation_interval=rotation_interval,
    )

    # Créer un gestionnaire avec la configuration personnalisée
    class TestManager(KeyRotationManager):
        def _load_or_initialize(self, initial_key=None):
            return config

    manager = TestManager(initial_key=initial_key)

    # La première récupération devrait déclencher une rotation
    key1 = manager.get_current_key()
    assert key1 != initial_key

    # La deuxième récupération ne devrait pas déclencher de rotation
    key2 = manager.get_current_key()
    assert key1 == key2

    # Forcer une nouvelle rotation en modifiant la date de prochaine rotation
    config.next_rotation = datetime.utcnow() - timedelta(seconds=1)

    # La prochaine récupération devrait déclencher une nouvelle rotation
    key3 = manager.get_current_key()
    assert key3 != key1


def test_token_validation_with_key_rotation():
    """Teste la validation des tokens avec rotation des clés."""
    from jose import jwt

    # Initialiser avec une clé connue
    initial_key = "cle_pour_les_tokens"
    manager = KeyRotationManager(initial_key=initial_key)

    # Créer un token avec la clé actuelle
    payload = {"sub": "user123", "exp": datetime.utcnow() + timedelta(hours=1)}
    token = jwt.encode(payload, initial_key, algorithm="HS256")

    # Le token devrait être valide
    decoded = manager.decode_token(token)
    assert decoded["sub"] == "user123"

    # Effectuer une rotation de clé
    new_key = manager.rotate_key()

    # Le token devrait toujours être valide avec l'ancienne clé
    decoded_after_rotation = manager.decode_token(token)
    assert decoded_after_rotation["sub"] == "user123"

    # Créer un nouveau token avec la nouvelle clé
    new_token = jwt.encode(payload, new_key, algorithm="HS256")

    # Le nouveau token devrait être valide
    decoded_new_token = manager.decode_token(new_token)
    assert decoded_new_token["sub"] == "user123"


def test_invalid_token():
    """Teste la gestion des tokens invalides."""
    from jose import JWTError

    manager = KeyRotationManager()

    # Token invalide
    with pytest.raises(JWTError):
        manager.decode_token("token.invalide")

    # Token signé avec une clé inconnue
    invalid_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIn0.invalid_signature"
    )

    with pytest.raises(JWTError):
        manager.decode_token(invalid_token)


@pytest.mark.asyncio
async def test_key_rotation_integration():
    """Test d'intégration de la rotation des clés avec JWT."""
    from jose import jwt
    from app.core.key_rotation import key_manager

    # Sauvegarder l'état initial
    original_key = key_manager.get_current_key()

    try:
        # Créer un token avec la clé actuelle
        payload = {"sub": "test_user", "exp": datetime.utcnow() + timedelta(hours=1)}
        token = jwt.encode(payload, original_key, algorithm="HS256")

        # Le token devrait être valide
        decoded = key_manager.decode_token(token)
        assert decoded["sub"] == "test_user"

        # Effectuer une rotation de clé
        new_key = key_manager.rotate_key()

        # Le token original devrait toujours être valide (vérification avec l'ancienne clé)
        decoded_after_rotation = key_manager.decode_token(token)
        assert decoded_after_rotation["sub"] == "test_user"

        # Créer un nouveau token avec la nouvelle clé
        new_token = jwt.encode(payload, new_key, algorithm="HS256")

        # Le nouveau token devrait être valide
        decoded_new_token = key_manager.decode_token(new_token)
        assert decoded_new_token["sub"] == "test_user"

    finally:
        # Restaurer la clé d'origine pour les autres tests
        key_manager.rotate_key()  # Pour effacer la clé précédente
        key_manager.rotate_key()  # Pour restaurer la clé d'origine comme précédente
        key_manager.rotate_key()  # Pour restaurer la clé d'origine comme actuelle
