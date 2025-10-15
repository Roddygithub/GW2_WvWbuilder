"""
Gestion du cycle de vie de l'application.

Ce module gère le démarrage et l'arrêt des composants de l'application,
y compris la surveillance de la base de données.
"""

import asyncio
import contextlib
import logging
from typing import AsyncIterator, Optional

from fastapi import FastAPI

from app.core import db_monitor, close_db

logger = logging.getLogger(__name__)


class AppLifespan:
    """Gère le cycle de vie de l'application."""

    def __init__(self, app: FastAPI):
        """Initialise le gestionnaire de cycle de vie."""
        self.app = app
        self.monitor_task: Optional[asyncio.Task] = None

    async def startup(self) -> None:
        """Démarre les composants de l'application."""
        logger.info("Démarrage des composants de l'application")

        # Démarrer la surveillance de la base de données
        self.monitor_task = asyncio.create_task(
            db_monitor.start_monitoring(interval=300)
        )  # Toutes les 5 minutes
        logger.info("Surveillance de la base de données démarrée")

        # Enregistrer les gestionnaires d'arrêt
        @self.app.on_event("shutdown")
        async def shutdown_event():
            await self.shutdown()

    async def shutdown(self) -> None:
        """Arrête les composants de l'application."""
        logger.info("Arrêt des composants de l'application")

        # Arrêter la surveillance de la base de données
        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
            logger.info("Surveillance de la base de données arrêtée")

        # Fermer les connexions à la base de données
        await close_db()
        logger.info("Connexions à la base de données fermées")


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Gère le cycle de vie de l'application.

    Args:
        app: L'application FastAPI

    Yields:
        None
    """
    lifespan_manager = AppLifespan(app)
    await lifespan_manager.startup()

    try:
        yield
    finally:
        await lifespan_manager.shutdown()
