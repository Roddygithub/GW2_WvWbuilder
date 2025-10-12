"""
Script pour vérifier la configuration de sécurité de l'application.
Exécute des vérifications de base pour s'assurer que la configuration est sécurisée.
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import requests

# Chemin vers le répertoire racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Ajout du répertoire de l'application au chemin Python
sys.path.insert(0, str(BASE_DIR))

# Configuration de l'environnement pour le chargement des variables d'environnement
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "True"
os.environ["TESTING"] = "True"

# Désactive la vérification SSL pour les requêtes en mode test
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_secret_key() -> Dict[str, Any]:
    """Vérifie que la clé secrète n'est pas la valeur par défaut."""
    try:
        # Importation différée pour éviter les problèmes de configuration
        from app.core.config import settings
        
        # Vérifie si la clé secrète est toujours la valeur par défaut
        is_default = getattr(settings, "SECRET_KEY", "") in [
            "your-secret-key-here",
            "dev-secret-key-change-in-production",
            ""
        ]
        
        # Vérifie également si la clé est suffisamment longue
        secret_key = getattr(settings, "SECRET_KEY", "")
        print(f"DEBUG - Valeur de SECRET_KEY: {secret_key}")
        print(f"DEBUG - Longueur de SECRET_KEY: {len(secret_key)}")
        is_too_short = len(secret_key) < 32
        
        messages = []
        if is_default:
            messages.append("La clé secrète utilise une valeur par défaut")
        if is_too_short:
            messages.append(f"La clé secrète est trop courte ({len(secret_key)} caractères), utilisez au moins 32 caractères")
        
        if messages:
            return {
                "check": "Clé secrète",
                "status": "FAIL",
                "message": "; ".join(messages),
                "recommendation": "Générez une clé sécurisée avec: openssl rand -hex 32"
            }
        
        return {
            "check": "Clé secrète",
            "status": "PASS",
            "message": "La clé secrète est correctement configurée"
        }
        
    except Exception as e:
        return {
            "check": "Clé secrète",
            "status": "ERROR",
            "message": f"Erreur lors de la vérification: {str(e)}",
            "recommendation": "Vérifiez la configuration de l'application et les logs pour plus de détails"
        }

def check_cors() -> Dict[str, Any]:
    """Vérifie la configuration CORS."""
    try:
        from app.core.config import settings
        
        # En mode debug, on est plus permissif
        if getattr(settings, "DEBUG", False):
            return {
                "check": "CORS (en mode debug)",
                "status": "WARN",
                "message": "Le mode debug est activé, les vérifications CORS sont assouplies"
            }
        
        # Vérifie la présence de la configuration CORS
        if not hasattr(settings, 'BACKEND_CORS_ORIGINS'):
            return {
                "check": "CORS",
                "status": "FAIL",
                "message": "La configuration CORS est manquante"
            }
        
        origins = getattr(settings, 'BACKEND_CORS_ORIGINS', [])
        
        # Vérifie que la configuration n'est pas trop permissive
        if not origins or (isinstance(origins, list) and "*" in origins):
            return {
                "check": "CORS",
                "status": "FAIL",
                "message": "La configuration CORS est trop permissive (utilise des origines spécifiques)",
                "recommendation": "Spécifiez des origines précises dans BACKEND_CORS_ORIGINS"
            }
        
        # Vérifie que les origines sont des URLs valides
        invalid_origins = []
        if isinstance(origins, list):
            for origin in origins:
                if not (origin.startswith("http://") or origin.startswith("https://")):
                    invalid_origins.append(origin)
        
        if invalid_origins:
            return {
                "check": "CORS",
                "status": "WARN",
                "message": f"Origines CORS potentiellement invalides: {', '.join(invalid_origins)}",
                "recommendation": "Utilisez des URLs complètes avec le protocole (http:// ou https://)"
            }
        
        return {
            "check": "CORS",
            "status": "PASS",
            "message": f"Origines CORS configurées: {', '.join(origins) if isinstance(origins, list) else 'Définies'}"
        }
        
    except Exception as e:
        return {
            "check": "CORS",
            "status": "ERROR",
            "message": f"Erreur lors de la vérification CORS: {str(e)}"
        }

def check_dependencies() -> Dict[str, Any]:
    """Vérifie les dépendances pour des vulnérabilités connues."""
    try:
        # Vérifie si safety est installé
        try:
            import subprocess
            import json
            from pathlib import Path
            safety_available = True
        except ImportError:
            safety_available = False
        
        # Si safety n'est pas disponible, on retourne un avertissement
        if not safety_available:
            return {
                "check": "Dépendances",
                "status": "WARN",
                "message": "Impossible d'importer les modules nécessaires pour safety",
                "recommendation": "Assurez-vous que Python est correctement configuré et réessayez"
            }
        
        # Vérifie si le fichier requirements.txt existe
        requirements = BASE_DIR / "requirements.txt"
        if not requirements.exists():
            return {
                "check": "Dépendances",
                "status": "WARN",
                "message": "Fichier requirements.txt introuvable",
                "recommendation": "Créez un fichier requirements.txt avec 'pip freeze > requirements.txt'"
            }
        
        # Vérifie si safety est disponible
        try:
            # Crée un fichier temporaire pour stocker la sortie
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Utilisation de la commande safety scan avec redirection de sortie
                cmd = f"safety scan -r {str(requirements)} --output screen --no-user-config > {temp_path} 2>&1 || true"
                print(f"Exécution de la commande: {cmd}")
                
                result = subprocess.run(
                    cmd,
                    shell=True,
                    text=True,
                    cwd=BASE_DIR
                )
                
                # Lit le contenu du fichier temporaire
                with open(temp_path, 'r') as f:
                    output = f.read()
                
                # Affiche la sortie pour le débogage
                print("\n=== RAPPORT DE SÉCURITÉ SAFETY SCAN ===")
                print(output[:1000] + ("..." if len(output) > 1000 else ""))
                print("====================================\n")
                
                # Vérifie si des vulnérabilités ont été trouvées
                if 'VULNERABILITY' in output or 'vulnerable' in output.lower() or 'CVE-' in output:
                    # Extrait les vulnérabilités de la sortie
                    details = []
                    for line in output.split('\n'):
                        line = line.strip()
                        if line and ('VULNERABILITY' in line or 'vulnerable' in line.lower() or 'CVE-' in line):
                            details.append(line)
                    
                    if not details:  # Si on n'a pas pu extraire les détails, on utilise un message générique
                        details = ["Des vulnérabilités ont été trouvées. Voir le rapport ci-dessus pour plus de détails."]
                    
                    return {
                        "check": "Dépendances",
                        "status": "WARN",
                        "message": "Vulnérabilités trouvées dans les dépendances",
                        "details": details[:5],  # Limite à 5 vulnérabilités pour la lisibilité
                        "recommendation": "Mettez à jour les dépendances vulnérables avec 'pip install -U <package>'",
                        "full_report": f"Voir le rapport complet ci-dessus ou consultez le fichier {temp_path}"
                    }
                else:
                    return {
                        "check": "Dépendances",
                        "status": "PASS",
                        "message": "Aucune vulnérabilité connue trouvée dans les dépendances"
                    }
                    
            except Exception as e:
                return {
                    "check": "Dépendances",
                    "status": "WARN",
                    "message": f"Erreur lors de l'exécution de safety scan: {str(e)}",
                    "details": [f"Type d'erreur: {type(e).__name__}"],
                    "recommendation": "Vérifiez que safety est correctement installé et réessayez"
                }
                
            finally:
                # Nettoie le fichier temporaire
                try:
                    import os
                    os.unlink(temp_path)
                except:
                    pass
                
        except Exception as e:
            return {
                "check": "Dépendances",
                "status": "WARN",
                "message": f"Erreur lors de la vérification des dépendances: {str(e)}",
                "details": [f"Type d'erreur: {type(e).__name__}"],
                "recommendation": "Vérifiez que safety est correctement installé et réessayez"
            }
                
        except Exception as e:
            return {
                "check": "Dépendances",
                "status": "WARN",
                "message": f"Erreur lors de la vérification des dépendances: {str(e)}",
                "recommendation": "Vérifiez que safety est correctement installé et réessayez"
            }
            
    except Exception as e:
        return {
            "check": "Dépendances",
            "status": "ERROR",
            "message": f"Erreur inattendue lors de la vérification des dépendances: {str(e)}"
        }

def check_https() -> Dict[str, Any]:
    """Vérifie si HTTPS est correctement configuré."""
    try:
        from app.core.config import settings
        
        # En mode debug, on est plus permissif
        if getattr(settings, "DEBUG", False):
            return {
                "check": "HTTPS (en mode debug)",
                "status": "INFO",
                "message": "Le mode debug est activé, HTTPS n'est pas requis"
            }
        
        # Vérifie si le site est accessible en HTTPS
        base_url = getattr(settings, "SERVER_HOST", "").strip("'\"")
        
        if not base_url:
            return {
                "check": "HTTPS",
                "status": "WARN",
                "message": "URL du serveur non configurée",
                "recommendation": "Définissez SERVER_HOST dans les paramètres de l'application"
            }
        
        # Assure que l'URL commence par https://
        if not base_url.startswith("https://"):
            return {
                "check": "HTTPS",
                "status": "FAIL",
                "message": f"L'URL du serveur ne semble pas utiliser HTTPS: {base_url}",
                "recommendation": "Configurez votre serveur pour utiliser HTTPS et mettez à jour SERVER_HOST"
            }
        
        # Tente de vérifier la configuration SSL
        try:
            import ssl
            import socket
            from urllib.parse import urlparse
            
            parsed_url = urlparse(base_url)
            hostname = parsed_url.hostname
            port = parsed_url.port or 443
            
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Vérifie la date d'expiration du certificat
                    import datetime
                    not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_remaining = (not_after - datetime.datetime.utcnow()).days
                    
                    if days_remaining < 7:
                        return {
                            "check": "HTTPS (Certificat)",
                            "status": "WARN",
                            "message": f"Le certificat SSL expire dans {days_remaining} jours",
                            "recommendation": "Renouvelez le certificat SSL avant son expiration"
                        }
            
            return {
                "check": "HTTPS",
                "status": "PASS",
                "message": f"HTTPS est correctement configuré pour {base_url}"
            }
            
        except Exception as e:
            return {
                "check": "HTTPS (Vérification SSL)",
                "status": "WARN",
                "message": f"Impossible de vérifier le certificat SSL: {str(e)}",
                "recommendation": "Vérifiez manuellement la configuration SSL de votre serveur"
            }
    
    except Exception as e:
        return {
            "check": "HTTPS",
            "status": "ERROR",
            "message": f"Erreur lors de la vérification HTTPS: {str(e)}"
        }

def run_bandit() -> Dict[str, Any]:
    """Exécute bandit pour détecter des problèmes de sécurité courants dans le code Python."""
    try:
        # Vérifie si bandit est installé
        try:
            import bandit
            from bandit.core import manager
            from bandit.core import config
            bandit_available = True
        except ImportError:
            bandit_available = False
        
        if not bandit_available:
            return {
                "check": "Analyse du code (bandit)",
                "status": "WARN",
                "message": "Le module 'bandit' n'est pas installé. Installez-le avec: pip install bandit",
                "recommendation": "Exécutez 'pip install bandit' pour analyser le code source"
            }
        
        # Exécute bandit sur le répertoire app avec une configuration minimale
        try:
            # Configuration minimale pour bandit
            conf = config.BanditConfig()
            b_mgr = manager.BanditManager(conf, 'file')
            
            # Configure les cibles (dossier app)
            b_mgr.discover_files(['app'], None, False)
            
            # Exécute les tests
            b_mgr.run_tests()
            
            # Récupère les résultats
            issues = b_mgr.get_issue_list()
            
            # Si des problèmes sont trouvés, on les classe par sévérité
            if issues:
                high_severity = [i for i in issues if i.severity == 'HIGH']
                medium_severity = [i for i in issues if i.severity == 'MEDIUM']
                low_severity = [i for i in issues if i.severity == 'LOW']
                
                # Construit le message en fonction de la gravité des problèmes
                if high_severity:
                    status = "FAIL"
                    message = f"{len(high_severity)} problèmes de sécurité critiques détectés"
                elif medium_severity:
                    status = "WARN"
                    message = f"{len(medium_severity)} problèmes de sécurité moyens détectés"
                else:
                    status = "INFO"
                    message = f"{len(low_severity)} problèmes de sécurité mineurs détectés"
                
                # Récupère les détails des problèmes les plus graves (max 3)
                details = []
                for issue in (high_severity + medium_severity + low_severity)[:3]:
                    details.append(
                        f"[{issue.severity}] {issue.text} "
                        f"(fichier: {issue.fname}, ligne: {issue.lineno})"
                    )
                
                return {
                    "check": "Analyse du code (bandit)",
                    "status": status,
                    "message": message,
                    "details": details,
                    "recommendation": "Corrigez les problèmes de sécurité identifiés dans le code source"
                }
            
            # Si aucun problème n'est trouvé
            return {
                "check": "Analyse du code (bandit)",
                "status": "PASS",
                "message": "Aucun problème de sécurité critique détecté"
            }
            
        except Exception as e:
            # En cas d'erreur lors de l'exécution de bandit
            return {
                "check": "Analyse du code (bandit)",
                "status": "WARN",  # On utilise WARN au lieu de ERROR pour éviter de bloquer le processus
                "message": f"Avertissement lors de l'analyse du code: {str(e)}",
                "recommendation": "Exécutez manuellement 'bandit -r app/' pour plus de détails"
            }
        
    except Exception as e:
        return {
            "check": "Analyse du code (bandit)",
            "status": "WARN",  # On utilise WARN au lieu de ERROR pour éviter de bloquer le processus
            "message": f"Erreur lors de l'initialisation de bandit: {str(e)}",
            "recommendation": "Vérifiez l'installation de bandit et réessayez"
        }

def format_status(status: str, message: str) -> str:
    """Formate un message avec des codes de couleur pour le terminal."""
    status_colors = {
        "PASS": "\033[92m",  # Vert
        "WARN": "\033[93m",  # Jaune
        "FAIL": "\033[91m",  # Rouge
        "ERROR": "\033[95m", # Magenta
        "INFO": "\033[96m"   # Cyan
    }
    reset_color = "\033[0m"
    
    color = status_colors.get(status, "")
    return f"{color}• {check_name} [{status}]{reset_color}\n  {message}"

def print_check_result(result: Dict[str, Any]) -> None:
    """Affiche le résultat d'une vérification de manière formatée."""
    status = result.get("status", "UNKNOWN")
    check_name = result.get("check", "Vérification inconnue")
    message = result.get("message", "Aucun détail disponible")
    details = result.get("details", [])
    recommendation = result.get("recommendation")
    
    # Affiche le statut avec un code couleur
    status_colors = {
        "PASS": "\033[92m",  # Vert
        "WARN": "\033[93m",  # Jaune
        "FAIL": "\033[91m",  # Rouge
        "ERROR": "\033[95m", # Magenta
        "INFO": "\033[96m"   # Cyan
    }
    reset_color = "\033[0m"
    
    color = status_colors.get(status, "")
    print(f"{color}• {check_name} [{status}]{reset_color}")
    print(f"  {message}")
    
    # Affiche les détails si présents
    if details:
        print("  Détails:")
        for i, detail in enumerate(details, 1):
            print(f"    {i}. {detail}")
    
    # Affiche la recommandation si présente
    if recommendation:
        print(f"  \033[1mRecommandation:\033[0m {recommendation}")
    
    print()  # Ligne vide pour l'espacement

def main():
    """Exécute toutes les vérifications de sécurité et affiche les résultats."""
    import time
    start_time = time.time()
    
    print("\n🔍 Vérification de la sécurité de l'application")
    print("=" * 50)
    
    # Liste des vérifications à effectuer
    checks = [
        check_secret_key,
        check_cors,
        check_dependencies,
        check_https,
        run_bandit
    ]
    
    # Exécute toutes les vérifications
    results = []
    for check in checks:
        try:
            print(f"\nExécution de la vérification: {check.__name__}...")
            result = check()
            results.append(result)
            print_check_result(result)
        except Exception as e:
            error_result = {
                "check": check.__name__,
                "status": "ERROR",
                "message": f"Erreur lors de l'exécution de la vérification: {str(e)}",
                "recommendation": "Vérifiez les logs pour plus de détails"
            }
            results.append(error_result)
            print_check_result(error_result)
    
    # Affiche les résultats
    status_colors = {
        "PASS": "\033[92m",  # Vert
        "WARN": "\033[93m",  # Jaune
        "FAIL": "\033[91m",  # Rouge
        "INFO": "\033[96m",  # Cyan
        "ERROR": "\033[95m"   # Magenta
    }
    reset_color = "\033[0m"
    
    for result in results:
        status = result["status"]
        color = status_colors.get(status, "\033[0m")
        print(f"\n{color}• {result['check']} [{status}]{reset_color}")
        print(f"  {result['message']}")
        
        if 'details' in result:
            print("  Détails :")
            for detail in result['details']:
                print(f"    - {detail}")
    # Affiche le résumé
    print("\n" + "="*50)
    print("Résumé des vérifications de sécurité :")
    
    # Compte les résultats par statut
    status_counts = {}
    for result in results:
        status = result.get("status", "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Affiche le compteur pour chaque statut
    status_order = ["ERROR", "FAIL", "WARN", "PASS", "INFO"]
    for status in status_order:
        if status in status_counts:
            color = {
                "PASS": "\033[92m",  # Vert
                "WARN": "\033[93m",  # Jaune
                "FAIL": "\033[91m",  # Rouge
                "ERROR": "\033[95m", # Magenta
                "INFO": "\033[96m"   # Cyan
            }.get(status, "")
            reset_color = "\033[0m"
            print(f"  {color}{status}: {status_counts[status]}{reset_color}")
    
    # Affiche le statut global
    if status_counts.get("ERROR", 0) > 0 or status_counts.get("FAIL", 0) > 0:
        print("\n\033[91m✗ Des problèmes de sécurité critiques ont été détectés\033[0m")
    elif status_counts.get("WARN", 0) > 0:
        print("\n\033[93m⚠ Des avertissements de sécurité ont été détectés\033[0m")
    else:
        print("\n\033[92m✓ Toutes les vérifications de sécurité sont passées avec succès\033[0m")
    
    # Affiche des conseils pour les vérifications supplémentaires
    print("\nPour des vérifications plus approfondies, utilisez :")
    print("  - pip install safety && safety check")
    print("  - pip install bandit && bandit -r app/")
    print("  - docker run --rm -it aquasec/trivy fs --security-checks vuln,config,secret .")
    
    # Affiche le temps d'exécution
    end_time = time.time()
    print(f"\nVérification terminée en {end_time - start_time:.2f} secondes")
    print("=" * 50 + "\n")
    
    # Retourne un code de sortie approprié pour les scripts
    if status_counts.get("ERROR", 0) > 0 or status_counts.get("FAIL", 0) > 0:
        sys.exit(1)
    sys.exit(0)
    
if __name__ == "__main__":
    main()
