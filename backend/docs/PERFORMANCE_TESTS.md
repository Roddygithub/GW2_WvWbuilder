# Tests de charge avec Locust

Ce document explique comment exécuter des tests de charge pour l'application GW2 WvW Builder.

## Prérequis

- Python 3.8+
- Locust 2.0+
- L'application en cours d'exécution

## Installation

```bash
# Installer les dépendances
poetry install --with dev

# Installer Locust
poetry add --group dev locust
```

## Configuration

La configuration des tests de charge se trouve dans `locust_config.py`. Vous pouvez la personnaliser en modifiant ce fichier ou en définissant des variables d'environnement.

Variables d'environnement importantes :

- `LOCUST_HOST`: URL de l'application à tester
- `LOCUST_USERS`: Nombre d'utilisateurs simultanés
- `LOCUST_SPAWN_RATE`: Taux de création d'utilisateurs
- `LOCUST_RUN_TIME`: Durée du test (ex: 10s, 1m, 1h)
- `LOCUST_HEADLESS`: Si défini, exécute en mode sans interface web

## Exécution des tests

### Mode interactif (avec interface web)

```bash
# Lancer Locust avec l'interface web
poetry run python run_load_test.py

# Puis accédez à http://localhost:8089
```

### Mode non interactif (sans interface web)

```bash
# Exécuter un test de charge de base
poetry run python run_load_test.py --headless --users 100 --spawn-rate 10 --run-time 1m

# Générer un rapport HTML
poetry run python run_load_test.py --headless --html reports/load_test.html

# Générer des fichiers CSV
poetry run python run_load_test.py --headless --csv reports/load_test
```

### Exécuter des tests spécifiques

```bash
# Exécuter uniquement les tests avec certains tags
poetry run python run_load_test.py --tags api,public

# Exclure certains tests
poetry run python run_load_test.py --exclude-tags slow
```

## Analyse des résultats

Les résultats des tests sont disponibles dans plusieurs formats :

1. **Interface web** : http://localhost:8089 (en mode interactif)
2. **Rapport HTML** : Si généré avec `--html`
3. **Fichiers CSV** : Si générés avec `--csv`

## Bonnes pratiques

1. Commencez par un petit nombre d'utilisateurs et augmentez progressivement
2. Exécutez des tests de longue durée pour identifier les fuites de mémoire
3. Surveillez les métriques système pendant les tests
4. Documentez les résultats pour référence future

## Dépannage

### Erreurs de connexion

Assurez-vous que l'application est en cours d'exécution et accessible à l'URL spécifiée.

### Problèmes de performance

Si les performances sont médiocres, vérifiez :

- La charge du serveur
- L'utilisation de la mémoire
- Les temps de réponse de la base de données
- Les goulots d'étranglement réseau

## Intégration continue

Les tests de charge sont exécutés automatiquement dans le pipeline CI pour les branches principales. Consultez le fichier `.github/workflows/ci.yml` pour plus de détails.
