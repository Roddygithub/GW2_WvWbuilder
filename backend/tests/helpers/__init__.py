"""
Package d'aide aux tests pour GW2 WvW Builder.

Ce package contient des utilitaires et des factories pour faciliter l'écriture des tests.

Modules:
    test_utils: Utilitaires pour les tests d'API
    factories: Factories pour générer des données de test
"""

from .test_utils import APIResponse, make_request, get, post, put, delete, patch

from .factories import (
    random_string,
    random_email,
    random_password,
    create_user,
    create_role,
    create_permission,
    create_profession,
    create_build,
    create_composition,
    create_user_factory,
    create_role_factory,
    create_permission_factory,
    create_profession_factory,
    create_build_factory,
    create_composition_factory,
)

__all__ = [
    # test_utils
    "APIResponse",
    "make_request",
    "get",
    "post",
    "put",
    "delete",
    "patch",
    # factories
    "random_string",
    "random_email",
    "random_password",
    "create_user",
    "create_role",
    "create_permission",
    "create_profession",
    "create_build",
    "create_composition",
    "create_user_factory",
    "create_role_factory",
    "create_permission_factory",
    "create_profession_factory",
    "create_build_factory",
    "create_composition_factory",
]
