# Documentation de l'Architecture Backend

Ce document décrit les décisions architecturales clés prises pour le backend de l'application GW2 WvW Builder.

## 1. Stack Technologique Principale

- **Langage :** Python 3.11+
- **Framework Web :** FastAPI
- **Base de Données :** PostgreSQL (recommandé), avec support pour SQLite en développement.
- **ORM :** SQLAlchemy 2.0 (mode asynchrone)
- **Migrations :** Alembic
- **Tâches Asynchrones :** `arq` (Asyncio-based job queue)
- **Cache :** Redis

## 2. Choix du Framework : FastAPI

FastAPI a été choisi pour plusieurs raisons stratégiques :

- **Haute Performance :** Basé sur Starlette et Pydantic, FastAPI est l'un des frameworks Python les plus rapides, ce qui est crucial pour une API réactive.
- **Support Asynchrone Natif :** Le support de `async`/`await` permet de gérer un grand nombre de connexions concurrentes efficacement, idéal pour les opérations I/O-bound comme les requêtes de base de données ou les appels d'API externes.
- **Validation des Données Intégrée :** Pydantic permet de définir des schémas de données clairs et robustes. La validation est automatique, ce qui réduit le code boilerplate et prévient les données invalides.
- **Documentation Automatique :** FastAPI génère automatiquement une documentation interactive (Swagger UI et ReDoc) à partir du code, ce qui facilite grandement le développement et l'intégration.

## 3. Accès à la Base de Données : SQLAlchemy 2.0

SQLAlchemy en version 2.0 a été adopté pour son support complet de l'asynchrone, en parfaite adéquation avec FastAPI.

- **Mode Asynchrone :** Permet d'effectuer des requêtes à la base de données sans bloquer la boucle d'événements, améliorant ainsi le débit de l'application.
- **ORM Puissant :** Fournit une abstraction de haut niveau pour interagir avec la base de données, tout en permettant d'écrire du SQL optimisé si nécessaire.
- **Prévention des Injections SQL :** En utilisant l'ORM, les requêtes sont paramétrées, ce qui élimine le risque d'injections SQL.

## 4. Tâches en Arrière-Plan : `arq`

Pour les opérations longues ou qui ne doivent pas bloquer la réponse de l'API, nous utilisons `arq`.

- **Cas d'usage :** L'envoi de webhooks est le principal cas d'utilisation. Lorsqu'un événement se produit, une tâche est ajoutée à une file d'attente dans Redis. Un worker `arq` distinct traite ensuite cette tâche de manière asynchrone.
- **Pourquoi `arq` ?** C'est une bibliothèque simple, performante et purement `asyncio`, ce qui la rend très facile à intégrer dans un écosystème FastAPI/Starlette, contrairement à des solutions plus lourdes comme Celery qui reposent sur un modèle de processus différent.

## 5. Stratégie de Cache : Redis

Une stratégie de cache à plusieurs niveaux est mise en place pour optimiser les temps de réponse.

- **Cache d'Application (Redis) :** Les réponses des requêtes `GET` fréquentes et coûteuses (ex: lister des builds, récupérer les détails d'un build) sont mises en cache dans Redis.
- **Invalidation du Cache :** Le cache est invalidé de manière ciblée lors des opérations d'écriture (`POST`, `PUT`, `DELETE`) pour garantir la fraîcheur des données.
- **Cache Côté Client (HTTP) :** L'API utilise les en-têtes `ETag` et `Cache-Control`. Cela permet aux navigateurs et aux clients API de mettre en cache les réponses et d'éviter de re-télécharger des données inchangées, économisant ainsi de la bande passante.

## 6. Tests

Le projet vise une couverture de code supérieure à 90% et utilise une stratégie de test à plusieurs niveaux :

- **Tests Unitaires :** Valident des composants isolés (ex: helpers, fonctions de validation).
- **Tests d'Intégration :** Testent l'interaction entre les composants, notamment les opérations CRUD et la logique métier.
- **Tests d'API (End-to-End) :** Valident le comportement complet des endpoints, y compris l'authentification, la validation et les réponses.
- **Tests de Performance et de Charge :** Mesurent la latence et la robustesse de l'application sous pression.