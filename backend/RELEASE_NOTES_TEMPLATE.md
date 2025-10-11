# Notes de Version - vX.Y.Z

**Date de sortie :** YYYY-MM-DD

## ✨ Nouvelles Fonctionnalités

- **Nom de la fonctionnalité 1** : Brève description de ce que fait la nouvelle fonctionnalité et de sa valeur pour l'utilisateur. (Issue #123)
- **Nom de la fonctionnalité 2** : ...

## 🚀 Améliorations

- **Performance** : Optimisation des requêtes sur l'endpoint `GET /api/v1/items`, réduisant le temps de réponse de 50%. (Issue #124)
- **UI/UX** : Amélioration du message d'erreur lors de la création d'un utilisateur avec un email déjà existant.

## 🐛 Corrections de Bugs

- Correction d'un bug où les utilisateurs non-administrateurs pouvaient voir les brouillons privés d'autres utilisateurs via l'endpoint de recherche. (Issue #125)
- Correction d'une erreur 500 qui se produisait lors de la mise à jour d'un build avec une description vide.

## 📄 Documentation

- Ajout d'un guide de déploiement en production.
- Mise à jour des exemples `curl` dans le `README.md`.

## ⚠️ Changements Cassants (Breaking Changes)

- L'endpoint `GET /api/v1/old-endpoint` a été supprimé. Veuillez utiliser `GET /api/v1/new-endpoint` à la place.