import logging
import logging.config
import os
from pathlib import Path
from typing import Dict, Any
import json
import sys
from app.core.config import settings

def setup_logging() -> None:
    """Setup logging configuration.
    
    This sets up logging to both console and file, with different log levels
    for development and production environments.
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Default logging configuration
    log_to_file = getattr(settings, "LOG_TO_FILE", False)
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s %(message)s"
            },
            "json": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": """
                    asctime: %(asctime)s
                    name: %(name)s
                    levelname: %(levelname)s
                    message: %(message)s
                    pathname: %(pathname)s
                    funcName: %(funcName)s
                    lineno: %(lineno)s
                """
            }
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose" if settings.DEBUG else "simple"
            },
            "file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_dir / "app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "json" if not settings.DEBUG else "verbose",
                "encoding": "utf8"
            },
            "error_file": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_dir / "error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "json" if not settings.DEBUG else "verbose",
                "encoding": "utf8"
            }
        },
        "root": {
            "handlers": ["console", "file", "error_file"] if log_to_file else ["console"],
            "level": "DEBUG" if settings.DEBUG else "INFO"
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.error": {
                "level": "INFO"
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False
            },
            "app": {
                "handlers": ["console", "file", "error_file"] if log_to_file else ["console"],
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "propagate": False
            }
        }
    }
    
    # Apply the logging configuration
    logging.config.dictConfig(log_config)
    
    # Set log level for asyncio and other noisy loggers
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Log the current configuration
    logger = logging.getLogger(__name__)
    logger.info("Logging is configured")
    
    # Log unhandled exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Log unhandled exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Call the default excepthook when keyboard interrupt is raised
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception
