"""
Configuration pour les tests de charge avec Locust.
Permet de charger la configuration depuis un fichier JSON ou des variables d'environnement.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Chemin par défaut vers le fichier de configuration
DEFAULT_CONFIG_PATH = Path("config/locust_config.json")


class LocustConfig:
    """Classe de configuration pour les tests de charge Locust."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialise la configuration.

        Args:
            config_path: Chemin vers le fichier de configuration JSON.
        """
        self.host: str = os.getenv("LOCUST_HOST", "http://localhost:8000")
        self.users: int = int(os.getenv("LOCUST_USERS", "100"))
        self.spawn_rate: int = int(os.getenv("LOCUST_SPAWN_RATE", "10"))
        self.run_time: str = os.getenv("LOCUST_RUN_TIME", "1m")
        self.headless: bool = os.getenv("LOCUST_HEADLESS", "true").lower() == "true"
        self.web_host: str = os.getenv("LOCUST_WEB_HOST", "0.0.0.0")
        self.web_port: str = os.getenv("LOCUST_WEB_PORT", "8089")
        self.log_level: str = os.getenv("LOCUST_LOG_LEVEL", "INFO").upper()
        self.csv_prefix: str = os.getenv("LOCUST_CSV_PREFIX", "reports/locust")
        self.html_report: str = os.getenv("LOCUST_HTML", "reports/locust_report.html")
        self.only_summary: bool = os.getenv("LOCUST_ONLY_SUMMARY", "true").lower() == "true"
        self.logfile: str = os.getenv("LOCUST_LOGFILE", "reports/locust.log")

        # Configuration avancée
        self.tags: List[str] = os.getenv("LOCUST_TAGS", "").split(",") if os.getenv("LOCUST_TAGS") else []
        self.exclude_tags: List[str] = (
            os.getenv("LOCUST_EXCLUDE_TAGS", "").split(",") if os.getenv("LOCUST_EXCLUDE_TAGS") else []
        )
        self.percentiles: List[float] = [
            float(p) for p in os.getenv("LOCUST_PERCENTILES", "0.5,0.9,0.95,0.99,0.999").split(",")
        ]

        # Charger la configuration depuis le fichier si spécifié
        if config_path:
            self.load_from_file(config_path)
        elif DEFAULT_CONFIG_PATH.exists():
            self.load_from_file(DEFAULT_CONFIG_PATH)

    def load_from_file(self, config_path: Union[str, Path]) -> None:
        """Charge la configuration depuis un fichier JSON.

        Args:
            config_path: Chemin vers le fichier de configuration JSON.
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Mettre à jour les attributs avec les valeurs du fichier
            for key, value in config.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            # Gestion spéciale pour les seuils et les étapes
            if "thresholds" in config and isinstance(config["thresholds"], dict):
                self.thresholds = config["thresholds"]

            if "stages" in config and isinstance(config["stages"], list):
                self.stages = config["stages"]

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Avertissement: Impossible de charger le fichier de configuration {config_path}: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire.

        Returns:
            Un dictionnaire contenant la configuration.
        """
        return {
            "host": self.host,
            "users": self.users,
            "spawn_rate": self.spawn_rate,
            "run_time": self.run_time,
            "headless": self.headless,
            "web_host": self.web_host,
            "web_port": self.web_port,
            "log_level": self.log_level,
            "csv_prefix": self.csv_prefix,
            "html": self.html_report,
            "only_summary": self.only_summary,
            "logfile": self.logfile,
            "tags": self.tags,
            "exclude_tags": self.exclude_tags,
            "percentiles": self.percentiles,
            "thresholds": getattr(self, "thresholds", {}),
            "stages": getattr(self, "stages", []),
        }

    def save_to_file(self, filepath: Union[str, Path] = None) -> None:
        """Sauvegarde la configuration dans un fichier JSON.

        Args:
            filepath: Chemin vers le fichier de sortie. Si non spécifié, utilise le chemin par défaut.
        """
        if filepath is None:
            filepath = DEFAULT_CONFIG_PATH

        # Créer le répertoire parent si nécessaire
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Écrire la configuration dans le fichier
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# Instance par défaut de la configuration
locust_config = LocustConfig()


def configure_locust() -> LocustConfig:
    """Configure et retourne une instance de LocustConfig.

    Returns:
        Une instance de LocustConfig configurée.
    """
    return locust_config
