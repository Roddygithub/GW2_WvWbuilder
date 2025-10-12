# Notes de Version - v0.3.0

**Date de sortie :** 2024-05-25

## 🚀 Améliorations

- **Qualité du Code et CI** : Le pipeline d'intégration continue a été renforcé avec l'ajout de `mypy` (vérification de type statique) et `flake8` (linting), garantissant une meilleure qualité et cohérence du code.
- **Tests de Mutation** : Implémentation des tests de mutation avec `mutmut` pour évaluer et améliorer la qualité de la suite de tests. Le seuil de couverture de test a été augmenté à 95%.
- **Automatisation des Tests de Performance** : Les tests de performance sont désormais exécutés automatiquement sur la branche `main` pour détecter les régressions de performance.
- **Tests de Cas Limites** : Ajout de tests supplémentaires pour les cas limites, notamment la création d'utilisateurs avec des identifiants dupliqués et la mise à jour de builds avec des données invalides.

## 📄 Documentation

- **Guide de Test** : Le fichier `TESTING.md` a été mis à jour pour inclure des instructions sur l'exécution et l'interprétation des tests de mutation.

## 🔧 Technique

- Ajout de la dépendance `mutmut` pour les tests de mutation.