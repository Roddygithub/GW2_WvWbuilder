"""
Tests unitaires pour app/core/security/password_utils.py
"""

import pytest
from unittest.mock import patch, MagicMock

from app.core.security.password_utils import (
    get_password_hash,
    verify_password,
    get_password_hash_sha256,
    is_password_strong,
)


class TestPasswordHashing:
    """Tests pour le hachage de mots de passe."""

    def test_get_password_hash_short_password(self):
        """Test hachage mot de passe court."""
        password = "MyPassword123!"
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Hash différent du mot de passe

    def test_get_password_hash_long_password(self):
        """Test hachage mot de passe >72 bytes (pre-hash SHA-256)."""
        # Créer un mot de passe >72 bytes
        password = "A" * 80
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_different_passwords(self):
        """Test que des mots de passe différents donnent des hash différents."""
        password1 = "Password123!"
        password2 = "DifferentPass456!"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        assert hash1 != hash2

    def test_get_password_hash_same_password_different_salt(self):
        """Test que le même mot de passe donne des hash différents (salt)."""
        password = "SamePassword123!"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Les hash devraient être différents à cause du salt
        assert hash1 != hash2


class TestPasswordVerification:
    """Tests pour la vérification de mots de passe."""

    def test_verify_password_correct(self):
        """Test vérification mot de passe correct."""
        password = "MyPassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test vérification mot de passe incorrect."""
        password = "MyPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_long_password(self):
        """Test vérification mot de passe >72 bytes."""
        password = "A" * 80
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_invalid_hash(self):
        """Test vérification avec hash invalide."""
        password = "MyPassword123!"
        invalid_hash = "invalid_hash_string"

        assert verify_password(password, invalid_hash) is False


class TestSHA256Hashing:
    """Tests pour le hachage SHA-256 (legacy)."""

    def test_get_password_hash_sha256(self):
        """Test hachage SHA-256."""
        password = "MyPassword123!"
        hashed = get_password_hash_sha256(password)

        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA-256 produit 64 caractères hex

    def test_get_password_hash_sha256_deterministic(self):
        """Test que SHA-256 est déterministe (même input = même output)."""
        password = "MyPassword123!"

        hash1 = get_password_hash_sha256(password)
        hash2 = get_password_hash_sha256(password)

        assert hash1 == hash2

    def test_get_password_hash_sha256_different_passwords(self):
        """Test que des mots de passe différents donnent des hash différents."""
        password1 = "Password123!"
        password2 = "DifferentPass456!"

        hash1 = get_password_hash_sha256(password1)
        hash2 = get_password_hash_sha256(password2)

        assert hash1 != hash2


class TestPasswordStrength:
    """Tests pour la validation de la force des mots de passe."""

    def test_is_password_strong_valid(self):
        """Test mot de passe fort valide."""
        password = "MyStrongP@ss1"
        assert is_password_strong(password) is True

    def test_is_password_strong_too_short(self):
        """Test mot de passe trop court (<8 caractères)."""
        password = "Short1!"
        assert is_password_strong(password) is False

    def test_is_password_strong_no_digit(self):
        """Test mot de passe sans chiffre."""
        password = "NoDigitPass!"
        assert is_password_strong(password) is False

    def test_is_password_strong_no_uppercase(self):
        """Test mot de passe sans majuscule."""
        password = "nouppercase1!"
        assert is_password_strong(password) is False

    def test_is_password_strong_no_lowercase(self):
        """Test mot de passe sans minuscule."""
        password = "NOLOWERCASE1!"
        assert is_password_strong(password) is False

    def test_is_password_strong_no_special_char(self):
        """Test mot de passe sans caractère spécial."""
        password = "NoSpecialChar1"
        assert is_password_strong(password) is False

    def test_is_password_strong_all_requirements(self):
        """Test mot de passe avec tous les critères."""
        # 8+ caractères, majuscule, minuscule, chiffre, spécial
        password = "ValidP@ss1"
        assert is_password_strong(password) is True

    def test_is_password_strong_various_special_chars(self):
        """Test mot de passe avec différents caractères spéciaux."""
        passwords = [
            "ValidP@ss1",
            "ValidP#ss1",
            "ValidP$ss1",
            "ValidP%ss1",
            "ValidP&ss1",
            "ValidP*ss1",
        ]
        for password in passwords:
            assert is_password_strong(password) is True

    def test_is_password_strong_edge_cases(self):
        """Test cas limites de force de mot de passe."""
        # Exactement 8 caractères avec tous les critères
        assert is_password_strong("Pass123!") is True

        # 7 caractères (trop court)
        assert is_password_strong("Pas123!") is False
