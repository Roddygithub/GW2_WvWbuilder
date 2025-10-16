"""
Classe de base pour les modèles SQLAlchemy.
"""

import time
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer, event
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session

from app.core.config import settings


@as_declarative()
class Base:
    """Classe de base pour tous les modèles SQLAlchemy."""

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True
    )

    # Génère automatiquement le nom de la table à partir du nom de la classe
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}  # type: ignore

    def update(self, db: Session, **kwargs: Any) -> None:
        """Met à jour les champs du modèle."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.add(self)
        db.commit()
        db.refresh(self)


def setup_database_events() -> None:
    """Configure les événements de base de données."""
    from sqlalchemy.engine import Engine

    if settings.DEBUG:
        # Active le logging des requêtes SQL en mode debug
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(
            conn: Any,
            cursor: Any,
            statement: str,
            params: Any,
            context: Any,
            executemany: Any,
        ) -> None:
            conn.info.setdefault("query_start_time", []).append(time.time())

    # Configuration des contraintes de clé étrangère pour SQLite
    if settings.DATABASE_TYPE == "sqlite":
        from sqlalchemy.engine import Engine

        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()


# Appel de la configuration des événements au chargement du module
setup_database_events()
