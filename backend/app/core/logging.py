"""
Configuration de la journalisation pour l'application.

Ce module configure la journalisation de l'application en utilisant la bibliothèque standard
logging de Python, avec des formateurs personnalisés et des gestionnaires pour la sortie
console et fichier.
"""

import logging
import logging.config
import os
import sys
from typing import Any, Dict

from pydantic import Field
from pydantic_settings import BaseSettings


class LoggingSettings(BaseSettings):
    """Configuration de la journalisation."""

    # Niveau de journalisation par défaut
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # Format des logs
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Format des dates dans les logs
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # Dossier pour les fichiers de log
    LOG_DIR: str = "logs"

    # Fichier de log principal
    LOG_FILE: str = "app.log"

    # Taille maximale d'un fichier de log (en octets)
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10 Mo

    # Nombre de fichiers de sauvegarde à conserver
    LOG_BACKUP_COUNT: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_logging_config(settings: LoggingSettings) -> Dict[str, Any]:
    """
    Retourne la configuration de journalisation au format dict.

    Args:
        settings: Instance de LoggingSettings contenant la configuration

    Returns:
        Un dictionnaire de configuration pour logging.config.dictConfig
    """
    # Créer le dossier de logs s'il n'existe pas
    os.makedirs(settings.LOG_DIR, exist_ok=True)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": settings.LOG_FORMAT,
                "datefmt": settings.LOG_DATE_FORMAT,
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": """
                    asctime: %(asctime)s
                    name: %(name)s
                    levelname: %(levelname)s
                    message: %(message)s
                    pathname: %(pathname)s
                    funcName: %(funcName)s
                    lineno: %(lineno)d
                """,
                "datefmt": settings.LOG_DATE_FORMAT,
            },
        },
        "handlers": {
            "console": {
                "level": settings.LOG_LEVEL,
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": sys.stdout,
            },
            "file": {
                "level": settings.LOG_LEVEL,
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(settings.LOG_DIR, settings.LOG_FILE),
                "maxBytes": settings.LOG_MAX_BYTES,
                "backupCount": settings.LOG_BACKUP_COUNT,
                "formatter": "standard",
                "encoding": "utf8",
            },
            "json_file": {
                "level": settings.LOG_LEVEL,
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(settings.LOG_DIR, "app.json.log"),
                "maxBytes": settings.LOG_MAX_BYTES,
                "backupCount": settings.LOG_BACKUP_COUNT,
                "formatter": "json",
                "encoding": "utf8",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file", "json_file"],
                "level": settings.LOG_LEVEL,
                "propagate": True,
            },
            "app": {
                "handlers": ["console", "file", "json_file"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "sqlalchemy": {
                "handlers": ["console", "file"],
                "level": "WARNING",  # Réduit le bruit de SQLAlchemy
                "propagate": False,
            },
        },
    }


def setup_logging() -> None:
    """
    Configure la journalisation de l'application.

    Cette fonction doit être appelée au démarrage de l'application.
    """
    settings = LoggingSettings()
    logging_config = get_logging_config(settings)
    logging.config.dictConfig(logging_config)

    # Désactive le logging des requêtes HTTP pour les endpoints de santé
    logging.getLogger("uvicorn.access").addFilter(
        lambda record: not any(path in record.args[1] for path in ["/health", "/healthz", "/ready", "/metrics"])
    )

    # Affiche la configuration de journalisation au démarrage
    logger = logging.getLogger(__name__)
    logger.info("Configuration de la journalisation terminée")
    logger.debug("Niveau de journalisation: %s", settings.LOG_LEVEL)


# Créer un logger par défaut au chargement du module
logger = logging.getLogger(__name__)

# S'assurer que le logger a au moins un gestionnaire
if not logger.handlers:
    # Configuration minimale si setup_logging n'a pas encore été appelé
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.warning(
        "La configuration de la journalisation n'a pas été initialisée. "
        "Utilisation de la configuration par défaut. Appelez setup_logging()."
    )
