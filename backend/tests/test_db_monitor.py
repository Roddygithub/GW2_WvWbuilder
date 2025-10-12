"""
Tests pour le module de surveillance de la base de données.
"""

import asyncio
from datetime import datetime
import pytest
import pytest_asyncio
from unittest.mock import patch

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.db_monitor import DatabaseMonitor, DatabaseMetrics
from app.core.config import settings


@pytest_asyncio.fixture
async def test_engine():
    """Crée un moteur de base de données de test."""
    engine = create_async_engine(settings.TEST_SQLALCHEMY_DATABASE_URI)
    yield engine
    await engine.dispose()


@pytest.fixture
def db_monitor(test_engine):
    """Crée une instance de DatabaseMonitor pour les tests."""
    return DatabaseMonitor(test_engine)


@pytest.mark.asyncio
async def test_collect_metrics_sqlite(db_monitor):
    """Teste la collecte des métriques pour SQLite."""
    metrics = await db_monitor.collect_metrics()

    # Vérifie que les métriques de base sont présentes
    assert isinstance(metrics, DatabaseMetrics)
    assert isinstance(metrics.timestamp, datetime)
    assert metrics.db_size_mb >= 0  # La taille doit être un nombre positif


@pytest.mark.asyncio
async def test_check_for_issues_no_issues(db_monitor):
    """Teste la détection des problèmes quand tout va bien."""
    # Crée des métriques avec des valeurs saines
    metrics = DatabaseMetrics(
        timestamp=datetime.utcnow(),
        active_connections=5,
        idle_connections=10,
        cache_hit_ratio=99.5,
        index_hit_ratio=95.0,
        total_queries=1000,
        slow_queries=0,
        deadlocks=0,
        locks_waiting=0,
        transaction_idle_time=30.0,  # 30 secondes
        db_size_mb=100.0,  # 100 Mo
    )

    # Remplace la méthode collect_metrics pour retourner nos métriques de test
    with patch.object(db_monitor, "collect_metrics", return_value=metrics):
        issues = await db_monitor.check_for_issues()

    # Aucun problème ne devrait être détecté
    assert len(issues) == 0


@pytest.mark.asyncio
async def test_check_for_issues_with_warnings(db_monitor):
    """Teste la détection des avertissements."""
    # Crée des métriques avec des valeurs problématiques
    metrics = DatabaseMetrics(
        timestamp=datetime.utcnow(),
        active_connections=5,
        idle_connections=10,
        cache_hit_ratio=85.0,  # Taux de cache bas
        index_hit_ratio=80.0,  # Taux d'index bas
        total_queries=1000,
        slow_queries=0,
        deadlocks=0,
        locks_waiting=0,
        transaction_idle_time=30.0,
        db_size_mb=2000.0,  # Base de données volumineuse
    )

    with patch.object(db_monitor, "collect_metrics", return_value=metrics):
        issues = await db_monitor.check_for_issues()

    # On s'attend à des avertissements pour le cache, les index et la taille de la base
    assert len(issues) >= 2  # Au moins 2 avertissements
    assert any(issue["code"] == "LOW_CACHE_HIT_RATIO" for issue in issues)
    assert any(issue["code"] == "LOW_INDEX_USAGE" for issue in issues)
    assert any(issue["code"] == "LARGE_DATABASE" for issue in issues)


@pytest.mark.asyncio
async def test_check_for_issues_with_errors(db_monitor):
    """Teste la détection des erreurs critiques."""
    # Crée des métriques avec des valeurs critiques
    metrics = DatabaseMetrics(
        timestamp=datetime.utcnow(),
        active_connections=5,
        idle_connections=10,
        cache_hit_ratio=99.5,
        index_hit_ratio=95.0,
        total_queries=1000,
        slow_queries=5,
        deadlocks=2,  # Deadlocks détectés
        locks_waiting=3,  # Verrous en attente
        transaction_idle_time=360.0,  # Transaction inactive depuis 6 minutes
        db_size_mb=100.0,
    )

    with patch.object(db_monitor, "collect_metrics", return_value=metrics):
        issues = await db_monitor.check_for_issues()

    # On s'attend à des erreurs pour les deadlocks et les verrous
    assert len(issues) >= 2
    assert any(issue["code"] == "LOCKS_WAITING" for issue in issues)
    assert any(issue["severity"] == "error" for issue in issues)


@pytest.mark.asyncio
async def test_start_monitoring_stop(db_monitor):
    """Teste le démarrage et l'arrêt de la surveillance."""

    # Crée un mock pour collect_metrics
    async def mock_collect_metrics():
        return DatabaseMetrics(
            timestamp=datetime.utcnow(),
            active_connections=0,
            idle_connections=0,
            cache_hit_ratio=99.9,
            index_hit_ratio=99.9,
            total_queries=0,
            slow_queries=0,
            deadlocks=0,
            locks_waiting=0,
            transaction_idle_time=0.0,
            db_size_mb=0.0,
        )

    # Remplace la méthode collect_metrics
    db_monitor.collect_metrics = mock_collect_metrics

    # Crée une tâche de surveillance avec un intervalle court
    monitor_task = asyncio.create_task(db_monitor.start_monitoring(interval=1))

    # Attend un peu pour que la tâche ait le temps de s'exécuter au moins une fois
    await asyncio.sleep(1.5)

    # Arrête la tâche
    monitor_task.cancel()

    try:
        await monitor_task
    except asyncio.CancelledError:
        pass  # C'est normal, on a annulé la tâche

    # Vérifie que des métriques ont été collectées
    assert len(db_monitor.metrics_history) > 0
