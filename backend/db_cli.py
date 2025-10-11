#!/usr/bin/env python3
"""
Interface en ligne de commande pour gérer la base de données.

Ce script fournit des commandes pour :
- Créer des sauvegardes
- Restaurer des sauvegardes
- Optimiser la base de données
- Afficher des statistiques
"""
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Optional

from app.core import db_manager, test_db_manager, init_db, close_db

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def backup_database(backup_dir: str = "backups", test_db: bool = False) -> None:
    """Crée une sauvegarde de la base de données."""
    manager = test_db_manager if test_db else db_manager
    backup_path = await manager.backup_database(backup_dir)
    
    if backup_path:
        print(f"✅ Sauvegarde créée : {backup_path}")
    else:
        print("❌ Échec de la création de la sauvegarde")

async def optimize_database(test_db: bool = False) -> None:
    """Optimise la base de données."""
    manager = test_db_manager if test_db else db_manager
    print("⏳ Optimisation de la base de données en cours...")
    
    try:
        result = await manager.optimize_database()
        if result["status"] == "success":
            print("✅ Base de données optimisée avec succès")
            print("Opérations effectuées :")
            for op in result["operations"]:
                print(f"  - {op}")
        else:
            print(f"❌ Erreur lors de l'optimisation : {result['status']}")
    except Exception as e:
        print(f"❌ Erreur lors de l'optimisation : {str(e)}")

async def show_stats(test_db: bool = False) -> None:
    """Affiche des statistiques sur la base de données."""
    manager = test_db_manager if test_db else db_manager
    
    print("📊 Statistiques de la base de données :")
    print("=" * 50)
    
    # Taille de la base de données
    db_size = await manager.get_database_size()
    print(f"Taille de la base de données : {db_size / (1024 * 1024):.2f} MB")
    
    # Tailles des tables
    print("\nTaille des tables :")
    table_sizes = await manager.get_table_sizes()
    for table, size in table_sizes.items():
        print(f"  - {table}: {size / (1024 * 1024):.2f} MB")
    
    print("=" * 50)

async def init_database() -> None:
    """Initialise la base de données."""
    print("⏳ Initialisation de la base de données...")
    try:
        await init_db()
        print("✅ Base de données initialisée avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {str(e)}")
    finally:
        await close_db()

def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(description="Gestion de la base de données")
    subparsers = parser.add_subparsers(dest='command', help='Commande à exécuter')
    
    # Commande de sauvegarde
    backup_parser = subparsers.add_parser('backup', help='Créer une sauvegarde')
    backup_parser.add_argument('--dir', default='backups', help='Répertoire de destination')
    backup_parser.add_argument('--test', action='store_true', help='Utiliser la base de test')
    
    # Commande d'optimisation
    optimize_parser = subparsers.add_parser('optimize', help='Optimiser la base de données')
    optimize_parser.add_argument('--test', action='store_true', help='Utiliser la base de test')
    
    # Commande de statistiques
    stats_parser = subparsers.add_parser('stats', help='Afficher les statistiques')
    stats_parser.add_argument('--test', action='store_true', help='Utiliser la base de test')
    
    # Commande d'initialisation
    subparsers.add_parser('init', help='Initialiser la base de données')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Exécution de la commande demandée
    if args.command == 'backup':
        asyncio.run(backup_database(args.dir, args.test))
    elif args.command == 'optimize':
        asyncio.run(optimize_database(args.test))
    elif args.command == 'stats':
        asyncio.run(show_stats(args.test))
    elif args.command == 'init':
        asyncio.run(init_database())
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
