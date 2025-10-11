"""
Module de surveillance de la base de données.

Fournit des fonctionnalités de monitoring des performances et de détection
des problèmes potentiels dans la base de données.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union

from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import settings

# Configuration du logger
logger = logging.getLogger(__name__)


@dataclass
class DatabaseMetrics:
    """Classe pour stocker les métriques de la base de données."""

    timestamp: datetime
    active_connections: int
    idle_connections: int
    cache_hit_ratio: float
    index_hit_ratio: float
    total_queries: int
    slow_queries: int
    deadlocks: int
    locks_waiting: int
    transaction_idle_time: float
    db_size_mb: float

    def to_dict(self) -> dict:
        """Convertit les métriques en dictionnaire."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "active_connections": self.active_connections,
            "idle_connections": self.idle_connections,
            "cache_hit_ratio": round(self.cache_hit_ratio, 2),
            "index_hit_ratio": round(self.index_hit_ratio, 2),
            "total_queries": self.total_queries,
            "slow_queries": self.slow_queries,
            "deadlocks": self.deadlocks,
            "locks_waiting": self.locks_waiting,
            "transaction_idle_time": round(self.transaction_idle_time, 2),
            "db_size_mb": round(self.db_size_mb, 2),
        }


class DatabaseMonitor:
    """Classe pour surveiller les performances de la base de données."""

    def __init__(self, engine_or_url: Union[AsyncEngine, str]):
        """Initialise le moniteur de base de données.

        Args:
            engine_or_url: Soit un moteur SQLAlchemy AsyncEngine, soit une URL de base de données sous forme de chaîne.
        """
        from sqlalchemy.ext.asyncio import create_async_engine

        if isinstance(engine_or_url, str):
            # Si on reçoit une URL, on crée un moteur temporaire
            self.engine = create_async_engine(engine_or_url)
            self._is_engine_temporary = True
        else:
            self.engine = engine_or_url
            self._is_engine_temporary = False

        self.is_postgres = "postgresql" in str(engine_or_url)
        self.is_sqlite = "sqlite" in str(engine_or_url)
        self.metrics_history: List[DatabaseMetrics] = []
        self._last_check: Optional[datetime] = None
        self._last_metrics: Dict = {}

    async def close(self):
        """Ferme le moteur de base de données s'il a été créé par cette instance."""
        if hasattr(self, "_is_engine_temporary") and self._is_engine_temporary and self.engine:
            await self.engine.dispose()

    async def collect_metrics(self) -> DatabaseMetrics:
        """Collecte les métriques de la base de données."""
        now = datetime.utcnow()

        if self.is_postgres:
            return await self._collect_postgres_metrics(now)
        elif self.is_sqlite:
            return await self._collect_sqlite_metrics(now)
        else:
            # Fallback pour les autres bases de données
            return DatabaseMetrics(
                timestamp=now,
                active_connections=0,
                idle_connections=0,
                cache_hit_ratio=0.0,
                index_hit_ratio=0.0,
                total_queries=0,
                slow_queries=0,
                deadlocks=0,
                locks_waiting=0,
                transaction_idle_time=0.0,
                db_size_mb=0.0,
            )

    async def _collect_postgres_metrics(self, timestamp: datetime) -> DatabaseMetrics:
        """Collecte les métriques spécifiques à PostgreSQL."""
        async with self.engine.connect() as conn:
            # Connexions actives/inactives
            result = await conn.execute(
                text(
                    """
                SELECT 
                    SUM(CASE WHEN state = 'active' THEN 1 ELSE 0 END) as active_connections,
                    SUM(CASE WHEN state = 'idle' THEN 1 ELSE 0 END) as idle_connections
                FROM pg_stat_activity
                WHERE pid <> pg_backend_pid()
                """
                )
            )
            active_connections, idle_connections = result.fetchone()

            # Taux de succès du cache
            result = await conn.execute(
                text(
                    """
                SELECT 
                    ROUND(blks_hit::numeric / NULLIF(blks_hit + blks_read, 0) * 100, 2) 
                FROM pg_stat_database 
                WHERE datname = current_database()
                """
                )
            )
            cache_hit_ratio = result.scalar() or 100.0

            # Taux d'utilisation des index
            result = await conn.execute(
                text(
                    """
                SELECT 
                    ROUND(
                        SUM(idx_scan) / NULLIF(SUM(seq_scan + idx_scan), 0) * 100, 
                        2
                    ) as index_usage_ratio
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                """
                )
            )
            index_hit_ratio = result.scalar() or 0.0

            # Requêtes lentes
            result = await conn.execute(
                text(
                    """
                SELECT COUNT(*)
                FROM pg_stat_activity
                WHERE state = 'active' 
                AND now() - query_start > interval '1 second'
                AND pid <> pg_backend_pid()
                """
                )
            )
            slow_queries = result.scalar()

            # Verrous en attente
            result = await conn.execute(
                text(
                    """
                SELECT COUNT(*) 
                FROM pg_stat_activity 
                WHERE wait_event_type = 'Lock' 
                AND pid <> pg_backend_pid()
                """
                )
            )
            locks_waiting = result.scalar()

            # Temps d'inactivité des transactions
            result = await conn.execute(
                text(
                    """
                SELECT COALESCE(EXTRACT(EPOCH FROM (now() - xact_start)))
                FROM pg_stat_activity
                WHERE xact_start IS NOT NULL
                AND pid <> pg_backend_pid()
                ORDER BY xact_start
                LIMIT 1
                """
                )
            )
            transaction_idle_time = result.scalar() or 0.0

            # Taille de la base de données
            result = await conn.execute(text("SELECT pg_database_size(current_database()) / (1024 * 1024.0)"))
            db_size_mb = result.scalar() or 0.0

            # Total des requêtes (estimation)
            result = await conn.execute(text("SELECT sum(calls) FROM pg_stat_statements"))
            total_queries = result.scalar() or 0

            # Deadlocks (depuis le dernier démarrage)
            result = await conn.execute(
                text("SELECT deadlocks FROM pg_stat_database WHERE datname = current_database()")
            )
            deadlocks = result.scalar() or 0

            return DatabaseMetrics(
                timestamp=timestamp,
                active_connections=active_connections or 0,
                idle_connections=idle_connections or 0,
                cache_hit_ratio=cache_hit_ratio,
                index_hit_ratio=index_hit_ratio,
                total_queries=total_queries,
                slow_queries=slow_queries,
                deadlocks=deadlocks,
                locks_waiting=locks_waiting,
                transaction_idle_time=transaction_idle_time,
                db_size_mb=db_size_mb,
            )

    async def _collect_sqlite_metrics(self, timestamp: datetime) -> DatabaseMetrics:
        """Collecte les métriques spécifiques à SQLite."""
        async with self.engine.connect() as conn:
            # Pour SQLite, les métriques sont plus limitées

            # Taille de la base de données
            result = await conn.execute(
                text("SELECT page_count * page_size / (1024 * 1024.0) FROM pragma_page_count(), pragma_page_size()")
            )
            db_size_mb = result.scalar() or 0.0

            # Nombre de tables
            result = await conn.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'"))
            result.scalar() or 0

            # Taille du cache
            result = await conn.execute(text("PRAGMA cache_size"))
            result.scalar() or 0

            # Journal WAL
            result = await conn.execute(text("PRAGMA journal_mode"))
            result.scalar()

            # Pour SQLite, on retourne des valeurs par défaut pour les métriques non disponibles
            return DatabaseMetrics(
                timestamp=timestamp,
                active_connections=0,  # Non disponible en SQLite standard
                idle_connections=0,  # Non disponible en SQLite standard
                cache_hit_ratio=0.0,  # Non disponible en SQLite standard
                index_hit_ratio=0.0,  # Non disponible en SQLite standard
                total_queries=0,  # Non disponible en SQLite standard
                slow_queries=0,  # Non disponible en SQLite standard
                deadlocks=0,  # Non disponible en SQLite standard
                locks_waiting=0,  # Non disponible en SQLite standard
                transaction_idle_time=0.0,  # Non disponible en SQLite standard
                db_size_mb=db_size_mb,
            )

    async def check_for_issues(self) -> List[Dict]:
        """Vérifie les problèmes potentiels dans la base de données."""
        issues = []
        metrics = await self.collect_metrics()

        # Vérifier le taux d'utilisation du cache
        if metrics.cache_hit_ratio < 95.0:
            issues.append(
                {
                    "severity": "warning",
                    "code": "LOW_CACHE_HIT_RATIO",
                    "message": f"Le taux de succès du cache est bas: {metrics.cache_hit_ratio:.2f}%",
                    "recommendation": "Augmentez la valeur de shared_buffers dans la configuration PostgreSQL.",
                }
            )

        # Vérifier le taux d'utilisation des index
        if metrics.index_hit_ratio < 90.0:
            issues.append(
                {
                    "severity": "warning",
                    "code": "LOW_INDEX_USAGE",
                    "message": f"Le taux d'utilisation des index est bas: {metrics.index_hit_ratio:.2f}%",
                    "recommendation": "Vérifiez si des index manquent ou sont inutilisés.",
                }
            )

        # Vérifier les verrous en attente
        if metrics.locks_waiting > 0:
            issues.append(
                {
                    "severity": "error",
                    "code": "LOCKS_WAITING",
                    "message": f"{metrics.locks_waiting} verrou(s) en attente détecté(s)",
                    "recommendation": "Vérifiez les transactions longues ou les deadlocks potentiels.",
                }
            )

        # Vérifier les transactions inactives
        if metrics.transaction_idle_time > 300:  # 5 minutes
            issues.append(
                {
                    "severity": "warning",
                    "code": "IDLE_TRANSACTION",
                    "message": f"Transaction inattentive détectée (inactive depuis {metrics.transaction_idle_time/60:.1f} minutes)",
                    "recommendation": "Vérifiez les connexions inactives ou les transactions non terminées.",
                }
            )

        # Vérifier la taille de la base de données
        if metrics.db_size_mb > 1024:  # 1 Go
            issues.append(
                {
                    "severity": "info",
                    "code": "LARGE_DATABASE",
                    "message": f"La base de données est volumineuse: {metrics.db_size_mb:.2f} MB",
                    "recommendation": "Envisagez d'archiver les anciennes données ou de partitionner les tables.",
                }
            )

        return issues

    async def start_monitoring(self, interval: int = 300):
        """Démarre la surveillance continue de la base de données."""
        logger.info(f"Démarrage de la surveillance de la base de données (intervalle: {interval}s)")

        while True:
            try:
                # Collecter les métriques
                metrics = await self.collect_issues()
                self.metrics_history.append(metrics)

                # Conserver uniquement les 100 dernières entrées
                if len(self.metrics_history) > 100:
                    self.metrics_history = self.metrics_history[-100:]

                # Vérifier les problèmes
                issues = await self.check_for_issues()
                for issue in issues:
                    if issue["severity"] == "error":
                        logger.error(f"[DB] {issue['message']} (Code: {issue['code']})")
                    elif issue["severity"] == "warning":
                        logger.warning(f"[DB] {issue['message']} (Code: {issue['code']})")
                    else:
                        logger.info(f"[DB] {issue['message']} (Code: {issue['code']})")

                # Attendre l'intervalle spécifié
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                logger.info("Arrêt de la surveillance de la base de données")
                break
            except Exception as e:
                logger.error(f"Erreur lors de la surveillance de la base de données: {str(e)}")
                await asyncio.sleep(60)  # Attendre 1 minute avant de réessayer


# Instance globale pour une utilisation facile
db_monitor = DatabaseMonitor(settings.get_async_database_url())
