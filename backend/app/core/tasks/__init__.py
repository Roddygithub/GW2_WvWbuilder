"""
Package des tâches planifiées de l'application.

Ce package contient les tâches planifiées telles que la rotation des clés de sécurité,
les tâches de maintenance, etc.
"""

# Importer les tâches pour les rendre disponibles lors de l'import du package
from .key_rotation_task import rotate_keys, schedule_key_rotation

# Exporter les symboles publics
__all__ = [
    "rotate_keys",
    "schedule_key_rotation",
]
