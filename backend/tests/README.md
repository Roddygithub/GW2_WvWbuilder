# Guide des Tests

Ce document fournit des instructions pour exécuter et gérer les tests du backend GW2 WvW Builder.

## Structure des Tests

Les tests sont organisés en plusieurs catégories :

- **Unitaires** (`tests/unit/`) : Testent des fonctions et des classes individuelles de manière isolée.
- **D'intégration** (`tests/integration/`) : Testent les interactions entre différents composants.
- **API** (`tests/api/`) : Testent les points de terminaison de l'API.
- **Fixtures** (`tests/fixtures/`) : Contiennent les données et configurations de test.

## Prérequis

- Python 3.8+
- Dépendances de développement installées :
  ```bash
  pip install -e ".[test]"
  ```

## Exécution des Tests

### Tous les tests

```bash
./run_tests.sh
```

### Types de tests spécifiques

- **Tests unitaires uniquement** :
  ```bash
  ./run_tests.sh --unit-only
  ```

- **Tests d'intégration uniquement** :
  ```bash
  ./run_tests.sh --integration-only
  ```

- **Tests d'API uniquement** :
  ```bash
  ./run_tests.sh --api-only
  ```

### Options supplémentaires

- **Désactiver le rapport de couverture** :
  ```bash
  ./run_tests.sh --no-cov
  ```

- **Désactiver la génération de rapports** :
  ```bash
  ./run_tests.sh --no-report
  ```

- **Définir un seuil de couverture personnalisé** (par défaut : 90%) :
  ```bash
  ./run_tests.sh --threshold=95
  ```

- **Afficher l'aide** :
  ```bash
  ./run_tests.sh --help
  ```

## Marquage des Tests

Les tests peuvent être marqués avec des marqueurs pour une exécution sélective :

- `@pytest.mark.unit` : Tests unitaires
- `@pytest.mark.integration` : Tests d'intégration
- `@pytest.mark.api` : Tests d'API
- `@pytest.mark.slow` : Tests lents (peuvent être exclus avec `-m "not slow"`)
- `@pytest.mark.db` : Tests nécessitant un accès à la base de données

Exemple d'exécution de tests spécifiques :

```bash
# Exécuter uniquement les tests marqués comme lents
pytest -m "slow"

# Exécuter tous les tests sauf ceux marqués comme lents
pytest -m "not slow"
```

## Couverture de Code

La couverture de code est générée automatiquement lors de l'exécution des tests. Les rapports sont disponibles dans :

- **Terminal** : Aperçu de la couverture
- **HTML** : `htmlcov/index.html`
- **XML** : `coverage.xml` (pour l'intégration continue)

### Seuil de couverture

Le seuil de couverture minimum est défini à 90%. Le build échouera si ce seuil n'est pas atteint.

## Débogage des Tests

Pour déboguer un test spécifique :

```bash
# Activer pdb sur échec
pytest --pdb tests/path/to/test.py::test_name

# Afficher la sortie de débogage
pytest -vvs tests/path/to/test.py::test_name

# Exécuter avec des logs détaillés
pytest --log-cli-level=DEBUG
```

## Bonnes Pratiques

1. **Isolation** : Chaque test doit être indépendant et ne pas dépendre de l'état d'autres tests.
2. **Noms descriptifs** : Utilisez des noms de test clairs et descriptifs.
3. **Fixtures** : Utilisez les fixtures pour les configurations et données de test courantes.
4. **Mocks** : Utilisez les mocks pour isoler les dépendances externes.
5. **Tests asynchrones** : Utilisez `@pytest.mark.asyncio` pour les tests asynchrones.

## Intégration Continue

Les tests sont exécutés automatiquement sur chaque push et pull request via GitHub Actions. Le workflow comprend :

1. Installation des dépendances
2. Vérification du formatage du code
3. Vérification du typage statique
4. Exécution des tests avec couverture
5. Téléchargement des rapports de couverture

## Dépannage

### Problèmes courants

- **Base de données verrouillée** : Assurez-vous que tous les processus de test précédents sont terminés.
- **Problèmes de session** : Utilisez `db_session.rollback()` dans les fixtures pour nettoyer après les tests.
- **Tests flaky** : Isolez et corrigez les tests qui échouent de manière intermittente.

### Commandes utiles

```bash
# Nettoyer les fichiers de test générés
rm -rf .pytest_cache/ htmlcov/ .coverage coverage.xml

# Lancer les tests en parallèle
pytest -n auto

# Générer un rapport de couverture détaillé
pytest --cov=app --cov-report=html
```

## Ajout de Nouveaux Tests

1. Créez un nouveau fichier dans le répertoire approprié (`unit/`, `integration/`, ou `api/`).
2. Importez les fixtures et utilitaires nécessaires.
3. Écrivez des tests couvrant les cas d'utilisation normaux et les cas d'erreur.
4. Exécutez les tests localement avant de pousser vos modifications.

## Documentation supplémentaire

- [Documentation de pytest](https://docs.pytest.org/)
- [Documentation de coverage.py](https://coverage.readthedocs.io/)
- [Meilleures pratiques pour les tests Python](https://docs.python-guide.org/writing/tests/)
