# Tests de charge pour GW2 WvW Builder

Ce répertoire contient les tests de charge pour l'application GW2 WvW Builder, utilisant [Locust](https://locust.io/).

## Prérequis

- Python 3.8+
- Locust 2.0+
- L'application GW2 WvW Builder en cours d'exécution

## Installation

1. Installer les dépendances de développement :
   ```bash
   poetry install --with dev
   ```

2. Installer Locust :
   ```bash
   poetry add --group dev locust
   ```

## Structure du projet

```
tests/load_tests/
├── __init__.py
├── config.py          # Configuration des tests de charge
├── load_test.py       # Scénarios de test
└── README.md          # Ce fichier
```

## Configuration

La configuration des tests se fait via le fichier `config.py` qui charge les paramètres depuis :

1. Les variables d'environnement (préfixées par `LOCUST_`)
2. Le fichier de configuration JSON (`config/locust_config.json`)
3. Les valeurs par défaut définies dans le code

### Variables de configuration principales

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `HOST` | URL de l'application à tester | `http://localhost:8000` |
| `USERS` | Nombre d'utilisateurs simultanés | `100` |
| `SPAWN_RATE` | Taux de création d'utilisateurs par seconde | `10` |
| `RUN_TIME` | Durée du test (ex: 10s, 1m, 1h) | `1m` |
| `HEADLESS` | Mode sans interface web | `true` |
| `HTML_REPORT` | Fichier de rapport HTML | `reports/locust_report.html` |
| `CSV_PREFIX` | Préfixe pour les fichiers CSV de sortie | `reports/locust` |

## Exécution des tests

### Mode interactif (avec interface web)

```bash
poetry run python run_load_test.py
```

Puis accédez à l'interface web à l'adresse : http://localhost:8089

### Mode non interactif (sans interface web)

```bash
# Test de charge de base
poetry run python run_load_test.py --headless

# Avec un nombre spécifique d'utilisateurs et une durée
poetry run python run_load_test.py --headless --users 200 --spawn-rate 20 --run-time 5m

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

### Métriques clés à surveiller

- **Taux de requêtes par seconde (RPS)** : Nombre de requêtes traitées par seconde
- **Temps de réponse** : Moyenne, médiane, 95e et 99e percentiles
- **Taux d'échec** : Pourcentage de requêtes ayant échoué
- **Nombre d'utilisateurs** : Nombre d'utilisateurs simulés

## Bonnes pratiques

1. **Commencez petit** : Commencez avec un petit nombre d'utilisateurs et augmentez progressivement.
2. **Surveillez les ressources** : Gardez un œil sur l'utilisation du CPU, de la mémoire et des E/S pendant les tests.
3. **Testez différents scénarios** : Testez différentes charges et modèles d'utilisation.
4. **Utilisez des données réalistes** : Utilisez des données de test réalistes pour des résultats plus précis.
5. **Documentez vos tests** : Notez les paramètres utilisés et les résultats obtenus pour référence future.

## Intégration continue

Les tests de charge sont exécutés automatiquement dans le pipeline CI pour les branches principales. Consultez le fichier `.github/workflows/ci.yml` pour plus de détails.

## Dépannage

### Erreurs de connexion

Assurez-vous que l'application est en cours d'exécution et accessible à l'URL spécifiée.

### Problèmes de performance

Si les performances sont médiocres, vérifiez :

- La charge du serveur
- L'utilisation de la mémoire
- Les temps de réponse de la base de données
- Les goulots d'étranglement réseau

### Journalisation

Les journaux des tests sont enregistrés dans `reports/locust.log` par défaut. Utilisez le paramètre `--log-level` pour contrôler le niveau de détail des journaux.

## Personnalisation

Pour ajouter de nouveaux scénarios de test, modifiez le fichier `load_test.py` et ajoutez de nouvelles classes héritant de `HttpUser` ou `FastHttpUser`.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
