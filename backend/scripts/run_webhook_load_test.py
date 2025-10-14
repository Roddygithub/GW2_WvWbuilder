#!/usr/bin/env python3
"""
Script pour exécuter des tests de charge sur les webhooks avec Locust.

Ce script permet de lancer des tests de charge automatisés sur les endpoints de webhooks
avec différentes configurations de charge utilisateur.
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import signal

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('reports/webhook_load_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Chemins des fichiers
BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / 'config' / 'webhook_load_test_config.json'
TEST_FILE = BASE_DIR / 'tests' / 'load_tests' / 'webhook_tests.py'
REPORT_DIR = BASE_DIR / 'reports'

class WebhookLoadTester:
    """Classe pour gérer les tests de charge des webhooks."""
    
    def __init__(self, config_path: Path = CONFIG_PATH):
        """Initialise le testeur avec la configuration."""
        self.config_path = config_path
        self.config = self._load_config()
        self.process: Optional[subprocess.Popen] = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier JSON."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            sys.exit(1)
    
    async def start_application(self):
        """Démarre l'application FastAPI en arrière-plan pour les tests."""
        logger.info("Démarrage de l'application FastAPI...")
        self.app_process = subprocess.Popen(
            ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Attendre que l'application démarre
        await asyncio.sleep(5)
        logger.info("Application démarrée avec succès")
    
    async def stop_application(self):
        """Arrête l'application FastAPI."""
        if self.app_process:
            logger.info("Arrêt de l'application FastAPI...")
            self.app_process.terminate()
            try:
                self.app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.app_process.kill()
            logger.info("Application arrêtée")
    
    def run_load_test(self):
        """Exécute le test de charge avec Locust."""
        # Créer le répertoire des rapports s'il n'existe pas
        os.makedirs(REPORT_DIR, exist_ok=True)
        
        # Construire la commande Locust
        cmd = [
            "locust",
            "-f", str(TEST_FILE),
            "--host", self.config["webhooks"]["host"],
            "--headless",
            "--run-time", self.config["webhooks"]["run_time"],
            "--loglevel", self.config["webhooks"].get("log_level", "INFO"),
            "--html", str(REPORT_DIR / "webhook_load_test.html"),
            "--csv", str(REPORT_DIR / "webhook_load_test"),
        ]
        
        # Ajouter les utilisateurs et le taux de création
        users = self.config["webhooks"]["users"]
        for user_type, config in users.items():
            if config["count"] > 0:
                cmd.extend([
                    "--users", str(config["count"]),
                    "--spawn-rate", str(config["spawn_rate"]),
                ])
                break  # Locust ne prend en compte que le premier --users/--spawn-rate
        
        # Ajouter les tags si spécifiés
        if "tags" in self.config["webhooks"] and self.config["webhooks"]["tags"]:
            cmd.extend(["--tags", ",".join(self.config["webhooks"]["tags"])])
        
        # Afficher la commande exécutée
        logger.info(f"Exécution de la commande: {' '.join(cmd)}")
        
        # Exécuter la commande
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Afficher la sortie en temps réel
        if self.process.stdout:
            for line in iter(self.process.stdout.readline, ''):
                logger.info(line.strip())
        
        # Attendre la fin du processus
        return_code = self.process.wait()
        
        if return_code != 0 and self.process.stderr:
            for line in iter(self.process.stderr.readline, ''):
                logger.error(line.strip())
        
        return return_code
    
    async def run(self):
        """Exécute le processus complet de test de charge."""
        try:
            # Démarrer l'application
            await self.start_application()
            
            # Exécuter le test de charge
            logger.info("Démarrage des tests de charge...")
            return_code = self.run_load_test()
            
            if return_code == 0:
                logger.info("Tests de charge terminés avec succès")
            else:
                logger.error(f"Échec des tests de charge avec le code: {return_code}")
            
            return return_code
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution des tests: {e}")
            return 1
            
        finally:
            # Toujours s'assurer d'arrêter l'application
            await self.stop_application()

def handle_signal(signum, frame):
    """Gère les signaux d'arrêt."""
    logger.info("\nRéception d'un signal d'arrêt, nettoyage en cours...")
    if 'tester' in globals() and tester.process:
        tester.process.terminate()
    sys.exit(0)

if __name__ == "__main__":
    # Enregistrer les gestionnaires de signaux
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Créer et exécuter le testeur
    tester = WebhookLoadTester()
    return_code = asyncio.run(tester.run())
    
    # Terminer avec le code de retour approprié
    sys.exit(return_code)
