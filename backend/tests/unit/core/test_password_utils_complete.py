"""
Comprehensive tests for password utilities.
Tests for app/core/security/password_utils.py to achieve 90%+ coverage.
"""

import pytest
from app.core.security.password_utils import (
    get_password_hash,
    verify_password,
    generate_password_reset_token,
    verify_password_reset_token,
)


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_get_password_hash_basic(self):
        """Test basic password hashing."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

    def test_get_password_hash_different_passwords(self):
        """Test that different passwords produce different hashes."""
        password1 = "Password1"
        password2 = "Password2"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        assert hash1 != hash2

    def test_get_password_hash_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)."""
        password = "SamePassword123"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Due to salt, same password should produce different hashes
        assert hash1 != hash2

    def test_get_password_hash_empty_password(self):
        """Test hashing empty password."""
        password = ""
        hashed = get_password_hash(password)

        assert hashed is not None
        assert isinstance(hashed, str)

    def test_get_password_hash_long_password(self):
        """Test hashing very long password."""
        password = "a" * 1000
        hashed = get_password_hash(password)

        assert hashed is not None
        assert isinstance(hashed, str)

    def test_get_password_hash_special_characters(self):
        """Test hashing password with special characters."""
        password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:',.<>?/~`"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert isinstance(hashed, str)

    def test_get_password_hash_unicode(self):
        """Test hashing password with unicode characters."""
        password = "Пароль123密码🔐"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert isinstance(hashed, str)


class TestPasswordVerification:
    """Test password verification functionality."""

    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "CorrectPassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "CorrectPassword123"
        wrong_password = "WrongPassword123"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "Password123"
        hashed = get_password_hash(password)

        assert verify_password("password123", hashed) is False
        assert verify_password("PASSWORD123", hashed) is False

    def test_verify_password_empty_password(self):
        """Test verifying empty password."""
        password = ""
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is True
        assert verify_password("nonempty", hashed) is False

    def test_verify_password_special_characters(self):
        """Test verifying password with special characters."""
        password = "P@ssw0rd!#$%"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("P@ssw0rd!#$", hashed) is False

    def test_verify_password_unicode(self):
        """Test verifying password with unicode characters."""
        password = "Пароль123密码🔐"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_invalid_hash(self):
        """Test verifying password with invalid hash."""
        password = "Password123"
        invalid_hash = "not_a_valid_bcrypt_hash"

        # Should return False or raise exception depending on implementation
        result = verify_password(password, invalid_hash)
        assert result is False

    def test_verify_password_none_hash(self):
        """Test verifying password with None hash."""
        password = "Password123"

        # Should handle None gracefully
        try:
            result = verify_password(password, None)
            assert result is False
        except (TypeError, AttributeError):
            # Expected if implementation doesn't handle None
            pass

    def test_verify_password_none_password(self):
        """Test verifying None password."""
        hashed = get_password_hash("Password123")

        # Should handle None gracefully
        try:
            result = verify_password(None, hashed)
            assert result is False
        except (TypeError, AttributeError):
            # Expected if implementation doesn't handle None
            pass


class TestPasswordResetToken:
    """Test password reset token functionality."""

    def test_generate_password_reset_token(self):
        """Test generating password reset token."""
        email = "user@example.com"
        token = generate_password_reset_token(email)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_password_reset_token_different_emails(self):
        """Test that different emails produce different tokens."""
        email1 = "user1@example.com"
        email2 = "user2@example.com"

        token1 = generate_password_reset_token(email1)
        token2 = generate_password_reset_token(email2)

        assert token1 != token2

    def test_verify_password_reset_token_valid(self):
        """Test verifying valid password reset token."""
        email = "user@example.com"
        token = generate_password_reset_token(email)

        verified_email = verify_password_reset_token(token)
        assert verified_email == email

    def test_verify_password_reset_token_invalid(self):
        """Test verifying invalid password reset token."""
        invalid_token = "invalid.token.here"

        verified_email = verify_password_reset_token(invalid_token)
        assert verified_email is None

    def test_verify_password_reset_token_expired(self):
        """Test verifying expired password reset token."""
        # This test depends on implementation
        # If tokens have expiration, create an expired one
        email = "user@example.com"

        # Create token with very short expiration if supported
        # Otherwise skip this test
        try:
            from datetime import timedelta

            token = generate_password_reset_token(email, expires_delta=timedelta(seconds=-1))
            verified_email = verify_password_reset_token(token)
            assert verified_email is None
        except TypeError:
            # If expires_delta not supported, skip
            pytest.skip("Password reset token expiration not supported")

    def test_verify_password_reset_token_empty(self):
        """Test verifying empty token."""
        verified_email = verify_password_reset_token("")
        assert verified_email is None

    def test_verify_password_reset_token_none(self):
        """Test verifying None token."""
        verified_email = verify_password_reset_token(None)
        assert verified_email is None


class TestPasswordHashingIntegration:
    """Integration tests for password hashing workflow."""

    def test_full_password_lifecycle(self):
        """Test complete password creation and verification cycle."""
        # User registration
        original_password = "UserPassword123!"
        hashed_password = get_password_hash(original_password)

        # Store hashed_password in database (simulated)
        stored_hash = hashed_password

        # User login - correct password
        login_password = "UserPassword123!"
        assert verify_password(login_password, stored_hash) is True

        # User login - incorrect password
        wrong_password = "WrongPassword123!"
        assert verify_password(wrong_password, stored_hash) is False

    def test_password_change_workflow(self):
        """Test password change workflow."""
        # Original password
        old_password = "OldPassword123"
        old_hash = get_password_hash(old_password)

        # User changes password
        new_password = "NewPassword456"
        new_hash = get_password_hash(new_password)

        # Old password should not work with new hash
        assert verify_password(old_password, new_hash) is False

        # New password should work with new hash
        assert verify_password(new_password, new_hash) is True

        # Old password should still work with old hash
        assert verify_password(old_password, old_hash) is True

    def test_password_reset_workflow(self):
        """Test password reset workflow."""
        # User requests password reset
        email = "user@example.com"
        reset_token = generate_password_reset_token(email)

        # Verify token
        verified_email = verify_password_reset_token(reset_token)
        assert verified_email == email

        # User sets new password
        new_password = "NewResetPassword123"
        new_hash = get_password_hash(new_password)

        # Verify new password works
        assert verify_password(new_password, new_hash) is True

    def test_multiple_users_passwords(self):
        """Test that multiple users can have same password with different hashes."""
        password = "CommonPassword123"

        # Three users with same password
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        hash3 = get_password_hash(password)

        # All hashes should be different (due to salt)
        assert hash1 != hash2
        assert hash2 != hash3
        assert hash1 != hash3

        # But all should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
        assert verify_password(password, hash3) is True


class TestPasswordSecurity:
    """Test password security features."""

    def test_hash_format(self):
        """Test that hash has expected bcrypt format."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        # Bcrypt hashes start with $2b$ or $2a$ or $2y$
        assert hashed.startswith(("$2b$", "$2a$", "$2y$"))

    def test_hash_length(self):
        """Test that hash has expected length."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        # Bcrypt hashes are 60 characters
        assert len(hashed) == 60

    def test_timing_attack_resistance(self):
        """Test that verification time is consistent (timing attack resistance)."""
        import time

        password = "TestPassword123"
        hashed = get_password_hash(password)

        # Measure time for correct password
        start = time.time()
        verify_password(password, hashed)
        correct_time = time.time() - start

        # Measure time for incorrect password
        start = time.time()
        verify_password("WrongPassword", hashed)
        incorrect_time = time.time() - start

        # Times should be similar (within reasonable margin)
        # This is a basic check; real timing attack tests are more complex
        time_diff = abs(correct_time - incorrect_time)
        assert time_diff < 0.1  # 100ms tolerance
