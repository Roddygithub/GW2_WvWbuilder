"""
Utilitaires pour les tests d'API.

Ce module fournit des fonctions utilitaires pour faciliter l'écriture des tests d'API.
"""

import json
from typing import Any, Dict, Optional

from fastapi import status
from httpx import AsyncClient, Response


class APIResponse:
    """Classe utilitaire pour faciliter les assertions sur les réponses d'API."""

    def __init__(self, response: Response):
        """Initialise avec une réponse HTTPX."""
        self.response = response
        self._json = None

    @property
    def status_code(self) -> int:
        """Retourne le code de statut HTTP."""
        return self.response.status_code

    @property
    def json(self) -> dict:
        """Retourne le corps de la réponse au format JSON."""
        if self._json is None:
            try:
                self._json = self.response.json()
            except json.JSONDecodeError:
                self._json = {}
        return self._json

    def assert_status_code(self, expected_code: int) -> "APIResponse":
        """Vérifie que le code de statut correspond à celui attendu."""
        assert self.status_code == expected_code, (
            f"Expected status code {expected_code}, got {self.status_code}. "
            f"Response: {self.response.text}"
        )
        return self

    def assert_json(self, expected_json: dict) -> "APIResponse":
        """Vérifie que la réponse JSON correspond à celle attendue."""
        assert (
            self.json == expected_json
        ), f"Expected JSON {expected_json}, got {self.json}"
        return self

    def assert_json_contains(self, expected_data: dict) -> "APIResponse":
        """Vérifie que la réponse JSON contient les données attendues."""
        for key, value in expected_data.items():
            assert key in self.json, f"Key '{key}' not found in response: {self.json}"
            assert (
                self.json[key] == value
            ), f"Expected {key}={value}, got {key}={self.json[key]}"
        return self

    def assert_error(
        self, error_message: str, status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> "APIResponse":
        """Vérifie que la réponse contient un message d'erreur spécifique."""
        self.assert_status_code(status_code)
        assert "detail" in self.json, f"No 'detail' in error response: {self.json}"
        assert (
            error_message in self.json["detail"]
        ), f"Expected error message containing '{error_message}', got '{self.json['detail']}'"
        return self


async def make_request(
    client: AsyncClient,
    method: str,
    url: str,
    *,
    json: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    auth_token: Optional[str] = None,
    expected_status: int = status.HTTP_200_OK,
) -> APIResponse:
    """
    Effectue une requête HTTP et retourne une réponse API.

    Args:
        client: Client HTTP asynchrone
        method: Méthode HTTP (GET, POST, PUT, DELETE, etc.)
        url: URL de la requête
        json: Données à envoyer au format JSON
        params: Paramètres de requête
        headers: En-têtes HTTP
        auth_token: Token d'authentification (optionnel)
        expected_status: Code de statut HTTP attendu (par défaut: 200)

    Returns:
        APIResponse: Réponse de l'API
    """
    # Ajouter le token d'authentification si fourni
    headers = headers or {}
    if auth_token and "Authorization" not in headers:
        headers["Authorization"] = f"Bearer {auth_token}"

    # Effectuer la requête
    http_method = getattr(client, method.lower())
    response = await http_method(url, json=json, params=params, headers=headers)

    # Vérifier le code de statut si spécifié
    api_response = APIResponse(response)
    if expected_status is not None:
        api_response.assert_status_code(expected_status)

    return api_response


# Alias pour les méthodes HTTP courantes
async def get(client: AsyncClient, url: str, **kwargs) -> APIResponse:
    """Effectue une requête GET."""
    return await make_request(client, "GET", url, **kwargs)


async def post(client: AsyncClient, url: str, **kwargs) -> APIResponse:
    """Effectue une requête POST."""
    return await make_request(client, "POST", url, **kwargs)


async def put(client: AsyncClient, url: str, **kwargs) -> APIResponse:
    """Effectue une requête PUT."""
    return await make_request(client, "PUT", url, **kwargs)


async def delete(client: AsyncClient, url: str, **kwargs) -> APIResponse:
    """Effectue une requête DELETE."""
    return await make_request(client, "DELETE", url, **kwargs)


async def patch(client: AsyncClient, url: str, **kwargs) -> APIResponse:
    """Effectue une requête PATCH."""
    return await make_request(client, "PATCH", url, **kwargs)
