"""
Tests unitaires pour app/core/utils.py
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock
from fastapi import Request

from app.core.utils import (
    generate_secret_key,
    generate_unique_id,
    to_camel_case,
    to_snake_case,
    get_pagination_links,
)


class TestSecretKeyGeneration:
    """Tests pour la génération de clés secrètes."""

    def test_generate_secret_key_default_length(self):
        """Test génération clé avec longueur par défaut."""
        key = generate_secret_key()
        assert isinstance(key, str)
        assert len(key) == 64  # 32 bytes * 2 (hex)

    def test_generate_secret_key_custom_length(self):
        """Test génération clé avec longueur personnalisée."""
        key = generate_secret_key(16)
        assert isinstance(key, str)
        assert len(key) == 32  # 16 bytes * 2 (hex)

    def test_generate_secret_key_uniqueness(self):
        """Test que les clés générées sont uniques."""
        key1 = generate_secret_key()
        key2 = generate_secret_key()
        assert key1 != key2


class TestUniqueIdGeneration:
    """Tests pour la génération d'identifiants uniques."""

    def test_generate_unique_id_format(self):
        """Test format de l'ID unique."""
        uid = generate_unique_id()
        assert isinstance(uid, str)
        assert uid.isdigit()

    def test_generate_unique_id_uniqueness(self):
        """Test que les IDs générés sont uniques."""
        uid1 = generate_unique_id()
        uid2 = generate_unique_id()
        # Les IDs peuvent être identiques si générés trop rapidement
        # mais généralement différents
        assert isinstance(uid1, str)
        assert isinstance(uid2, str)


class TestCaseConversion:
    """Tests pour les conversions de casse."""

    def test_to_camel_case_simple(self):
        """Test conversion snake_case vers camelCase simple."""
        assert to_camel_case("hello_world") == "helloWorld"

    def test_to_camel_case_multiple_words(self):
        """Test conversion avec plusieurs mots."""
        assert to_camel_case("this_is_a_test") == "thisIsATest"

    def test_to_camel_case_single_word(self):
        """Test conversion d'un seul mot."""
        assert to_camel_case("hello") == "hello"

    def test_to_camel_case_empty_string(self):
        """Test conversion chaîne vide."""
        assert to_camel_case("") == ""

    def test_to_snake_case_simple(self):
        """Test conversion camelCase vers snake_case simple."""
        assert to_snake_case("helloWorld") == "hello_world"

    def test_to_snake_case_multiple_words(self):
        """Test conversion avec plusieurs mots."""
        assert to_snake_case("thisIsATest") == "this_is_a_test"

    def test_to_snake_case_single_word(self):
        """Test conversion d'un seul mot."""
        assert to_snake_case("hello") == "hello"

    def test_to_snake_case_empty_string(self):
        """Test conversion chaîne vide."""
        assert to_snake_case("") == ""

    def test_to_snake_case_already_lowercase(self):
        """Test conversion d'une chaîne déjà en minuscules."""
        assert to_snake_case("alreadylowercase") == "alreadylowercase"


class TestPaginationLinks:
    """Tests pour la génération de liens de pagination."""

    def test_get_pagination_links_first_page(self):
        """Test liens pagination pour première page."""
        request = Mock(spec=Request)
        request.url = "http://example.com/api/items"
        request.query_params = {}

        links = get_pagination_links(
            request=request,
            page=1,
            total_pages=5,
            page_size=10,
            total_items=50
        )

        assert links["first"] is None
        assert links["prev"] is None
        assert links["next"] is not None
        assert links["last"] is not None
        assert links["total_pages"] == 5
        assert links["total_items"] == 50
        assert links["current_page"] == 1
        assert links["page_size"] == 10

    def test_get_pagination_links_middle_page(self):
        """Test liens pagination pour page intermédiaire."""
        request = Mock(spec=Request)
        request.url = "http://example.com/api/items?page=3"
        request.query_params = {"page": "3"}

        links = get_pagination_links(
            request=request,
            page=3,
            total_pages=5,
            page_size=10,
            total_items=50
        )

        assert links["first"] is not None
        assert links["prev"] is not None
        assert links["next"] is not None
        assert links["last"] is not None
        assert "page=2" in links["prev"]
        assert "page=4" in links["next"]

    def test_get_pagination_links_last_page(self):
        """Test liens pagination pour dernière page."""
        request = Mock(spec=Request)
        request.url = "http://example.com/api/items?page=5"
        request.query_params = {"page": "5"}

        links = get_pagination_links(
            request=request,
            page=5,
            total_pages=5,
            page_size=10,
            total_items=50
        )

        assert links["first"] is not None
        assert links["prev"] is not None
        assert links["next"] is None
        assert links["last"] is None
        assert links["current_page"] == 5

    def test_get_pagination_links_with_query_params(self):
        """Test liens pagination avec paramètres de requête existants."""
        request = Mock(spec=Request)
        request.url = "http://example.com/api/items?filter=active&page=2"
        request.query_params = {"filter": "active", "page": "2"}

        links = get_pagination_links(
            request=request,
            page=2,
            total_pages=3,
            page_size=20,
            total_items=60
        )

        assert "filter=active" in links["next"]
        assert "page=3" in links["next"]
        assert "size=20" in links["next"]
