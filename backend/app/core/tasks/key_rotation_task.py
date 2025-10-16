"""
Tâche de rotation des clés de sécurité.

Ce module fournit une fonction pour effectuer la rotation des clés de manière sécurisée.
"""

import logging
import os
import secrets


from app.core.config import settings
from app.core.key_rotation_service import key_rotation_service

logger = logging.getLogger(__name__)


def rotate_keys() -> bool:
    """
    Effectue une rotation des clés de sécurité si nécessaire.

    Returns:
        bool: True si une rotation a été effectuée, False sinon
    """
    logger.info("Vérification de la nécessité d'une rotation des clés...")

    # Vérifier si une rotation est nécessaire
    if not key_rotation_service.should_rotate():
        next_rotation = (
            key_rotation_service.last_rotation_date
            + key_rotation_service.key_rotation_interval
        )
        logger.info(
            f"Aucune rotation nécessaire. Prochaine rotation prévue le {next_rotation.isoformat()}"
        )
        return False

    try:
        # Générer une nouvelle clé sécurisée
        new_key = secrets.token_urlsafe(64)

        # Effectuer la rotation
        logger.info("Début de la rotation des clés...")
        if key_rotation_service.rotate_keys(new_key):
            # Mettre à jour les variables d'environnement (pour les redémarrages)
            update_environment_keys()

            logger.info(
                f"Rotation des clés effectuée avec succès. Nouvelle clé ID: {key_rotation_service.current_key_id}"
            )

            # Planifier la prochaine rotation
            next_rotation = (
                key_rotation_service.last_rotation_date
                + key_rotation_service.key_rotation_interval
            )
            logger.info(f"Prochaine rotation prévue le {next_rotation.isoformat()}")

            return True
        else:
            logger.warning("La rotation des clés n'a pas été effectuée")
            return False

    except Exception as e:
        logger.error(f"Erreur lors de la rotation des clés: {str(e)}", exc_info=True)
        return False


def update_environment_keys() -> None:
    """Met à jour les variables d'environnement avec les clés actuelles."""
    try:
        # Mettre à jour le fichier .env si nécessaire
        env_file = os.path.join(settings.BASE_DIR, ".env")
        if not os.path.exists(env_file):
            return

        # Lire le contenu actuel du fichier .env
        with open(env_file, "r") as f:
            lines = f.readlines()

        # Mettre à jour les clés
        updated_lines = []
        key_updated = False

        for line in lines:
            # Mettre à jour la clé principale
            if line.startswith("SECRET_KEY="):
                current_key_id, current_key = key_rotation_service.get_current_key()
                updated_lines.append(f"SECRET_KEY={current_key}\n")
                key_updated = True
            # Mettre à jour les clés historiques
            elif (
                line.startswith("SECRET_KEY_1=")
                or line.startswith("SECRET_KEY_2=")
                or line.startswith("SECRET_KEY_3=")
            ):
                # On ne met à jour pas les clés historiques ici, elles sont gérées par le service
                updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Si la clé n'était pas dans le fichier, l'ajouter
        if not key_updated:
            current_key_id, current_key = key_rotation_service.get_current_key()
            updated_lines.append(
                f"\n# Clé de sécurité principale (générée automatiquement)\nSECRET_KEY={current_key}\n"
            )

        # Écrire les modifications dans le fichier .env
        with open(env_file, "w") as f:
            f.writelines(updated_lines)

        logger.info("Fichier .env mis à jour avec la nouvelle clé")

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du fichier .env: {str(e)}")
        # Ne pas échouer si la mise à jour du fichier échoue


def schedule_key_rotation() -> None:
    """Planifie la prochaine rotation des clés."""
    try:
        import schedule
        import time
        from threading import Thread

        def run_scheduler() -> None:
            # Planifier la rotation quotidienne
            schedule.every().day.at("03:00").do(rotate_keys)

            # Exécuter la vérification immédiatement au démarrage
            rotate_keys()

            # Boucle d'exécution du planificateur
            while True:
                schedule.run_pending()
                time.sleep(3600)  # Vérifier toutes les heures

        # Démarrer le planificateur dans un thread séparé
        scheduler_thread = Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

        logger.info("Planificateur de rotation des clés démarré")

    except ImportError:
        logger.warning(
            "Le module 'schedule' n'est pas installé. La rotation automatique des clés est désactivée."
        )
    except Exception as e:
        logger.error(
            f"Erreur lors du démarrage du planificateur de rotation des clés: {str(e)}"
        )


# Démarrer automatiquement le planificateur au chargement du module
schedule_key_rotation()
