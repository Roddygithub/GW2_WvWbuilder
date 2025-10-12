#!/usr/bin/env python3
"""
Script pour exécuter les tests de charge avec Locust.

Ce script permet d'exécuter des tests de charge avec différentes configurations
et de générer des rapports détaillés.
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(str(Path(__file__).parent))

try:
    from tests.load_tests.config import locust_config, configure_locust
except ImportError:
    print("Erreur: Impossible d'importer la configuration Locust")
    print("Assurez-vous d'exécuter ce script depuis le répertoire racine du projet")
    sys.exit(1)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('reports/load_test_runner.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse les arguments en ligne de commande."""
    # Charger la configuration
    config = configure_locust()
    
    parser = argparse.ArgumentParser(
        description="Exécute des tests de charge avec Locust",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Groupe pour les paramètres de test
    test_group = parser.add_argument_group('Paramètres de test')
    test_group.add_argument(
        "--users", 
        type=int, 
        default=config.users,
        help=f"Nombre d'utilisateurs simultanés"
    )
    test_group.add_argument(
        "--spawn-rate", 
        type=float, 
        default=config.spawn_rate,
        help="Taux de création d'utilisateurs par seconde"
    )
    test_group.add_argument(
        "--run-time", 
        default=config.run_time,
        help="Durée du test (ex: 10s, 1m, 1h)"
    )
    test_group.add_argument(
        "--host", 
        default=config.host,
        help="URL de l'application à tester"
    )
    
    # Groupe pour les options de sortie
    output_group = parser.add_argument_group('Options de sortie')
    output_group.add_argument(
        "--headless", 
        action="store_true",
        default=config.headless,
        help="Mode sans interface web"
    )
    output_group.add_argument(
        "--html", 
        metavar="FILE",
        default=getattr(config, 'html_report', 'reports/locust_report.html'),
        help="Générer un rapport HTML"
    )
    output_group.add_argument(
        "--csv", 
        metavar="PREFIX",
        default=getattr(config, 'csv_prefix', 'reports/locust'),
        help="Préfixe pour les fichiers CSV de sortie"
    )
    output_group.add_argument(
        "--log-level",
        default=getattr(config, 'log_level', 'INFO'),
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Niveau de journalisation"
    )
    
    # Groupe pour le filtrage des tests
    filter_group = parser.add_argument_group('Filtrage des tests')
    filter_group.add_argument(
        "--tags", 
        nargs="+",
        default=getattr(config, 'tags', []),
        help="Exécuter uniquement les tests avec ces tags"
    )
    filter_group.add_argument(
        "--exclude-tags", 
        nargs="+",
        default=getattr(config, 'exclude_tags', []),
        help="Exclure les tests avec ces tags"
    )
    filter_group.add_argument(
        "--test-file",
        default="tests/load_tests/load_test.py",
        help="Fichier de test à exécuter"
    )
    
    # Options avancées
    advanced_group = parser.add_argument_group('Options avancées')
    advanced_group.add_argument(
        "--config",
        default=None,
        help="Chemin vers un fichier de configuration JSON"
    )
    advanced_group.add_argument(
        "--save-config",
        metavar="FILE",
        help="Enregistrer la configuration actuelle dans un fichier"
    )
    
    args = parser.parse_args()
    
    # Charger la configuration depuis un fichier si spécifié
    if args.config:
        config.load_from_file(args.config)
        
        # Mettre à jour les arguments avec les valeurs du fichier
        for arg in vars(args):
            if hasattr(config, arg):
                setattr(args, arg, getattr(config, arg))
    
    # Enregistrer la configuration si demandé
    if args.save_config:
        config.save_to_file(args.save_config)
        logger.info(f"Configuration enregistrée dans {args.save_config}")
    
    return args

def run_locust(args: argparse.Namespace) -> int:
    """Exécute les tests de charge avec les arguments donnés.
    
    Args:
        args: Arguments de ligne de commande parsés
        
    Returns:
        Code de sortie (0 pour succès, autre pour échec)
    """
    # Créer le répertoire de rapports si nécessaire
    os.makedirs("reports", exist_ok=True)
    
    # Construire la commande de base
    cmd = [
        "locust",
        "-f", args.test_file,
        "--host", args.host,
        "--users", str(args.users),
        "--spawn-rate", str(args.spawn_rate),
        "--run-time", args.run_time,
        "--loglevel", args.log_level,
        "--logfile", getattr(args, 'logfile', 'reports/locust.log'),
    ]
    
    # Ajouter les options conditionnelles
    if args.headless:
        cmd.append("--headless")
    else:
        cmd.extend(["--web-host", getattr(args, 'web_host', '0.0.0.0')])
        cmd.extend(["--web-port", str(getattr(args, 'web_port', '8089'))])
    
    # Configurer la sortie HTML
    if args.html:
        os.makedirs(os.path.dirname(os.path.abspath(args.html)), exist_ok=True)
        cmd.extend(["--html", args.html])
    
    # Configurer la sortie CSV
    if args.csv:
        os.makedirs(os.path.dirname(os.path.abspath(args.csv)), exist_ok=True)
        cmd.extend(["--csv", args.csv])
    
    # Configurer les tags
    if args.tags and not (len(args.tags) == 1 and not args.tags[0]):
        cmd.extend(["--tags", ",".join(args.tags)])
    
    if args.exclude_tags and not (len(args.exclude_tags) == 1 and not args.exclude_tags[0]):
        cmd.extend(["--exclude-tags", ",".join(args.exclude_tags)])
    
    # Afficher la configuration
    logger.info("Configuration du test de charge :")
    logger.info(f"- Fichier de test: {args.test_file}")
    logger.info(f"- Hôte cible: {args.host}")
    logger.info(f"- Utilisateurs: {args.users}")
    logger.info(f"- Taux de création: {args.spawn_rate}/s")
    logger.info(f"- Durée: {args.run_time}")
    logger.info(f"- Mode: {'Sans interface' if args.headless else 'Avec interface web'}")
    
    if args.tags:
        logger.info(f"- Tags inclus: {', '.join(args.tags)}")
    if args.exclude_tags:
        logger.info(f"- Tags exclus: {', '.join(args.exclude_tags)}")
    
    logger.info("\nExécution de la commande :")
    logger.info(" ".join(cmd) + "\n")
    
    try:
        # Exécuter la commande
        start_time = time.time()
        result = subprocess.run(cmd, check=False)
        duration = time.time() - start_time
        
        if result.returncode == 0:
            logger.info(f"Test de charge terminé avec succès en {duration:.2f} secondes")
        else:
            logger.error(f"Échec du test de charge (code: {result.returncode}) après {duration:.2f} secondes")
        
        return result.returncode
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de l'exécution de Locust: {e}")
        return e.returncode
    except KeyboardInterrupt:
        logger.warning("\nTest de charge arrêté par l'utilisateur")
        return 0
    except Exception as e:
        logger.exception("Erreur inattendue lors de l'exécution du test de charge")
        return 1


def generate_report(args: argparse.Namespace) -> None:
    """Génère un rapport de test de charge.
    
    Args:
        args: Arguments de ligne de commande
    """
    # Cette fonction peut être étendue pour générer des rapports personnalisés
    logger.info("Génération du rapport...")
    
    # Exemple: Analyser les fichiers CSV générés
    if args.csv and os.path.exists(f"{args.csv}_stats.csv"):
        logger.info(f"Rapport CSV disponible dans : {args.csv}_*.csv")
    
    if args.html and os.path.exists(args.html):
        logger.info(f"Rapport HTML disponible : {os.path.abspath(args.html)}")


def main() -> int:
    """Fonction principale."""
    try:
        # Parser les arguments
        args = parse_args()
        
        # Configurer le niveau de journalisation
        logging.getLogger().setLevel(args.log_level)
        
        # Exécuter les tests
        return_code = run_locust(args)
        
        # Générer un rapport
        if return_code == 0:
            generate_report(args)
        
        return return_code
        
    except Exception as e:
        logger.exception("Erreur critique lors de l'exécution du script")
        return 1


if __name__ == "__main__":
    sys.exit(main())
