"""
Configuration et utilitaires pour les tests de performance avec Locust.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configuration du logger
logger = logging.getLogger(__name__)

class LocustConfig:
    """Configuration pour les tests de charge Locust."""
    
    def __init__(self):
        self.host = os.getenv("LOCUST_HOST", "http://localhost:8000")
        self.users = int(os.getenv("LOCUST_USERS", "100"))
        self.spawn_rate = int(os.getenv("LOCUST_SPAWN_RATE", "10"))
        self.run_time = os.getenv("LOCUST_RUN_TIME", "1m")
        self.headless = os.getenv("LOCUST_HEADLESS", "true").lower() == "true"
        self.web_host = os.getenv("LOCUST_WEB_HOST", "0.0.0.0")
        self.web_port = os.getenv("LOCUST_WEB_PORT", "8089")
        self.thresholds = self._load_thresholds()
        self.stages = self._load_stages()
        self.enable_prometheus = os.getenv("LOCUST_PROMETHEUS", "true").lower() == "true"
        self.prometheus_port = int(os.getenv("LOCUST_PROMETHEUS_PORT", "9090"))
        self.html_report = os.getenv("LOCUST_HTML_REPORT", "true").lower() == "true"
        self.csv_prefix = os.getenv("LOCUST_CSV_PREFIX", "performance_report")
        self.percentiles = self._parse_percentiles()
        self.enable_cache = os.getenv("LOCUST_ENABLE_CACHE", "true").lower() == "true"
        self.cache_ttl = int(os.getenv("LOCUST_CACHE_TTL", "300"))

    def _load_thresholds(self) -> Dict[str, int]:
        """Charge les seuils de performance."""
        thresholds = {
            "get_public_endpoints": 500,  # ms
            "get_specific_build": 800,    # ms
            "create_build": 1000,         # ms
        }
        
        for key in thresholds.keys():
            env_var = f"LOCUST_THRESHOLD_{key.upper()}"
            if env_var in os.environ:
                try:
                    thresholds[key] = int(os.environ[env_var])
                except ValueError:
                    logger.warning(f"Valeur invalide pour {env_var}, utilisation de la valeur par défaut")
                    
        return thresholds

    def _load_stages(self) -> List[Dict[str, Any]]:
        """Charge la configuration des étapes de test."""
        default_stages = [
            {"duration": "30s", "users": 10, "spawn_rate": 1},
            {"duration": "1m", "users": 50, "spawn_rate": 5},
            {"duration": "2m", "users": 100, "spawn_rate": 10},
            {"duration": "1m", "users": 10, "spawn_rate": 1}
        ]
        
        stages_env = os.getenv("LOCUST_STAGES")
        if not stages_env:
            return default_stages
            
        try:
            return json.loads(stages_env)
        except json.JSONDecodeError:
            logger.warning("Format de configuration des étapes invalide, utilisation des valeurs par défaut")
            return default_stages

    def _parse_percentiles(self) -> List[float]:
        """Parse la liste des percentiles."""
        percentiles_str = os.getenv("LOCUST_PERCENTILES", "50,95,99")
        try:
            return [float(p.strip()) for p in percentiles_str.split(",")]
        except ValueError:
            logger.warning("Format de percentiles invalide, utilisation des valeurs par défaut")
            return [50.0, 95.0, 99.0]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire."""
        return {
            "host": self.host,
            "users": self.users,
            "spawn_rate": self.spawn_rate,
            "run_time": self.run_time,
            "headless": self.headless,
            "web_host": self.web_host,
            "web_port": self.web_port,
            "thresholds": self.thresholds,
            "stages": self.stages,
            "enable_prometheus": self.enable_prometheus,
            "prometheus_port": self.prometheus_port,
            "html_report": self.html_report,
            "csv_prefix": self.csv_prefix,
            "percentiles": self.percentiles,
            "enable_cache": self.enable_cache,
            "cache_ttl": self.cache_ttl,
        }

    def save_to_file(self, filepath: str = "locust_config.json") -> None:
        """Sauvegarde la configuration dans un fichier."""
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        config_path = config_dir / filepath
        with open(config_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
            
        logger.info(f"Configuration Locust sauvegardée dans {config_path}")

# Instance globale de configuration
locust_config = LocustConfig()

def configure_locust() -> LocustConfig:
    """Configure et retourne la configuration Locust."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    locust_config.save_to_file()
    return locust_config
