import pytest
import time
import os
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models import Build, Profession, User # Importez les modèles nécessaires pour le nettoyage

@pytest.fixture(scope="session")
def performance_limits() -> Dict[str, Any]:
    """
    Définit les seuils de performance pour les tests.
    Ces valeurs peuvent être ajustées en fonction de l'environnement de test.
    """
    env = os.getenv("TEST_ENV", "local")

    if env == "ci":
        # Seuils plus tolérants pour les environnements CI
        return {
            "create_build": 0.5,
            "get_build": 0.3,
            "list_builds": 1.5,  # Seuil pour lister 100 builds
            "create_10_builds": 4.0,
            "large_payload": 0.6,
            "memory_increase_mb": 100,
            "load_test_success_rate": 0.9,
            "load_test_duration": 20.0,
            "update_build": 0.5,
            "max_memory_increase_mb": 150,
            "max_cpu_percent": 95.0,
            "timeouts": {
                "short": 10.0,  # secondes
                "medium": 20.0,
                "long": 60.0,
            },
        }
    else:
        # Seuils plus stricts pour l'environnement local
        return {
            "create_build": 0.2,
            "get_build": 0.1,
            "list_builds": 0.8,  # Seuil pour lister 100 builds
            "create_10_builds": 2.0,
            "large_payload": 0.3,
            "memory_increase_mb": 50,
            "load_test_success_rate": 0.95,
            "load_test_duration": 10.0,
            "update_build": 0.2,
            "max_memory_increase_mb": 75,
            "max_cpu_percent": 92.0, # Légère augmentation pour tolérer les pics locaux
            "timeouts": {
                "short": 5.0,   # secondes
                "medium": 10.0,
                "long": 30.0,
            },
        }

@pytest.fixture(autouse=True)
async def cleanup_performance_test_data(async_session: AsyncSession):
    """
    Nettoie les données de test spécifiques aux tests de performance après chaque test.
    Ceci est important pour l'isolation des tests et pour éviter l'accumulation de données.
    """
    yield
    # Supprimer tous les builds créés par les tests de performance
    # Utilise un filtre sur le nom pour ne pas affecter d'autres builds
    await async_session.execute(
        Build.__table__.delete().where(
            Build.name.like("Performance Test Build%") |
            Build.name.like("Load Test Build%") |
            Build.name.like("Large Payload Build%")
        )
    )
    await async_session.execute(Profession.__table__.delete().where(Profession.name.like("PerfProf%")))
    await async_session.execute(User.__table__.delete().where(User.username.like("mem_test_user%")))
    await async_session.commit()

# La fixture `record_metrics` sera gérée par `pytest-html` ou `pytest-xdist` si installés.
# Pour l'instant, nous nous appuyons sur `record_property` fourni par pytest lui-même pour les rapports JUnit.

@pytest.fixture(scope="function")
async def redis_client():
    """
    Fournit un client Redis pour les tests et vide la base de données Redis après chaque test.
    """
    if not settings.CACHE_ENABLED:
        pytest.skip("Cache is not enabled in settings")

    client = settings.redis_client
    yield client
    # Nettoyer la base de données Redis après le test pour garantir l'isolation
    await client.flushdb()
    await client.close()