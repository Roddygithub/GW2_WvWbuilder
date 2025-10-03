# Guide des Tests de Performance

Ce document décrit la stratégie de test de performance pour le backend de l'application, comment exécuter les tests et comment interpréter les résultats.

## 1. Objectifs

Les tests de performance visent à :
- **Détecter les régressions** : Identifier toute dégradation des temps de réponse ou augmentation de la consommation des ressources après une modification du code.
- **Valider la robustesse** : S'assurer que l'application reste stable et réactive sous une charge modérée.
- **Établir des benchmarks** : Fournir des métriques de référence pour les opérations critiques de l'API.

## 2. Types de Tests

Nos tests de performance sont divisés en deux catégories principales, marquées avec des marqueurs `pytest` :

- **`@pytest.mark.performance`** : Tests individuels mesurant la latence des opérations CRUD de base (Création, Lecture, Mise à jour) et l'impact de payloads volumineux.
- **`@pytest.mark.load_test`** : Un test simulant une charge concurrente (ex: création de 100 builds en parallèle) pour évaluer le taux de réussite, la latence sous pression et l'impact sur les ressources (CPU/Mémoire).

## 3. Exécution des Tests

### Exécution Locale

Pour exécuter tous les tests de performance (marqués `performance` et `load_test`) :
```bash
pytest -v -m "performance or load_test"
```

Pour exécuter uniquement les tests de charge :
```bash
pytest -v -m "load_test"
```

Les seuils de performance pour l'exécution locale sont stricts et définis dans `tests/conftest.py`.

### Exécution en Intégration Continue (CI)

Les tests de performance sont automatiquement exécutés par le workflow GitHub Actions sur chaque push vers la branche `main`.

Pour simuler l'environnement CI localement :
```bash
TEST_ENV=ci pytest -v -m "performance or load_test"
```

L'environnement `ci` utilise des seuils plus tolérants pour tenir compte des variations de performance des runners GitHub.

## 4. Analyse des Résultats

### Rapports

Après chaque exécution, deux types de rapports sont générés dans le dossier `backend/reports/` (si l'option est activée) :

- **`performance-report.html`** : Un rapport HTML détaillé et interactif, idéal pour une analyse manuelle.
- **`performance-results.xml`** : Un rapport au format JUnit, utilisé par les outils de CI pour le suivi.

### Interprétation du Rapport HTML (`performance-report.html`)

Le rapport HTML généré par `pytest-html` est un outil puissant pour une analyse visuelle. Voici comment l'utiliser :

- **Vue d'ensemble (Summary)** : Affiche le nombre total de tests, les succès, les échecs et les erreurs.
- **Résultats par Test (Results)** : Chaque ligne représente un test. Vous pouvez cliquer sur une ligne pour déplier les détails.
- **Détails du Test** :
  - **`stdout`** : Affiche toutes les sorties `print()` du test. C'est ici que vous trouverez les métriques que nous affichons (temps de réponse, utilisation CPU/mémoire, etc.).
  - **`Captured log`** : Affiche les logs capturés pendant l'exécution du test.
  - **`Failures`** : Si un test échoue, cette section montre la trace de la pile d'erreurs (`traceback`) et la ligne de l'assertion qui a échoué.

Utilisez ce rapport pour rapidement identifier les tests qui échouent et pour lire les métriques de performance détaillées qui ne sont pas visibles dans la sortie standard du terminal.

### Métriques Clés à Surveiller

- **Durée (Duration)** : Le temps total d'exécution d'une requête. Une augmentation soudaine peut indiquer une régression.
- **Taux de réussite (Success Rate)** : Pour les tests de charge, un taux inférieur à 95% (local) ou 90% (CI) indique un problème de stabilité.
- **Utilisation Mémoire/CPU** : Une augmentation anormale de la consommation de ressources pendant les tests de charge peut signaler une fuite de mémoire ou une boucle inefficace.
- **Analyse des échecs** : Le rapport des tests de charge liste les types d'erreurs (ex: timeouts, erreurs 500), aidant à diagnostiquer la cause des échecs.

## 5. Ajustement des Seuils

Les seuils de performance sont centralisés dans la fixture `performance_limits` du fichier `tests/conftest.py`. Ils peuvent être ajustés si les performances de référence de l'application évoluent ou si l'environnement de test change. Toute modification doit être justifiée et validée par l'équipe.

## 6. Exemple de Sortie de Test (stdout)

Voici un exemple de la sortie que vous pouvez attendre lors de l'exécution du test de charge :

```text
--- Test de Montée en Charge (Création de Builds) ---
Taux de réussite : 100/100 (100.00%) en 8.7654s
Utilisation CPU (approximative) : 75.8%
Augmentation mémoire : 15.34 Mo
Analyse des échecs :
Aucun échec
Temps de réponse (moyenne) : 0.0851s
Temps de réponse (max) : 0.1234s
Écart-type : 0.0159s
```

Cette sortie fournit un aperçu rapide de la stabilité (taux de réussite), de l'impact sur les ressources (CPU/mémoire) et de la latence (temps de réponse) de l'application sous charge.