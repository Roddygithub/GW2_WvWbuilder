# Guide de Sécurité

Ce document résume les mesures de sécurité mises en place dans l'application et les bonnes pratiques à suivre.

## 1. Mesures Implémentées

### Authentification et Autorisation
- **JWT (JSON Web Tokens)** : L'authentification est basée sur des jetons JWT signés, garantissant que seuls les utilisateurs authentifiés peuvent accéder aux endpoints protégés.
- **Permissions Basées sur les Rôles** : Le système de rôles (ex: utilisateur, administrateur) permet de restreindre l'accès à certaines opérations (ex: suppression de ressources par un non-propriétaire).

### Protection des Endpoints
- **Validation des Données (Pydantic)** : Toutes les données entrantes sont rigoureusement validées par Pydantic. Toute donnée non conforme est rejetée avec une erreur `422 Unprocessable Entity`, prévenant les attaques par injection de données malformées.
- **Rate Limiting** : Un limiteur de débit est en place pour prévenir les attaques par force brute ou par déni de service (DoS). Les limites sont différentes pour les utilisateurs anonymes et authentifiés.

### Sécurité de la Base de Données
- **ORM (SQLAlchemy)** : L'utilisation de SQLAlchemy comme ORM prévient nativement les attaques par injection SQL, car les requêtes sont construites de manière paramétrée et sécurisée.
- **Migrations (Alembic)** : Les changements de schéma de base de données sont gérés de manière contrôlée via Alembic, réduisant les risques d'erreurs manuelles.

### En-têtes de Sécurité HTTP
Le middleware de l'application ajoute automatiquement les en-têtes suivants pour renforcer la sécurité côté client :
- **`X-Content-Type-Options: nosniff`** : Empêche le navigateur d'interpréter les fichiers avec un type MIME différent de celui déclaré.
- **`X-Frame-Options: DENY`** : Empêche l'intégration de la page dans une `<frame>` ou `<iframe>`, protégeant contre le clickjacking.
- **`Strict-Transport-Security` (HSTS)** : En production, cet en-tête force le navigateur à communiquer uniquement via HTTPS, prévenant les attaques de type "man-in-the-middle".

### Protection contre les Failles Courantes
- **Cross-Site Scripting (XSS)** : FastAPI, en utilisant Jinja2 pour le templating (non utilisé ici pour l'API pure) ou des frameworks frontend modernes, échappe automatiquement les données, ce qui prévient les attaques XSS.
- **Cross-Site Request Forgery (CSRF)** : Bien que moins critique pour une API JSON pure consommée par des clients non-navigateurs, la protection CSRF est recommandée si l'authentification est basée sur des cookies. Notre authentification par jeton `Bearer` est moins susceptible à cette attaque.

## 2. Bonnes Pratiques pour les Développeurs

1.  **Ne Jamais Stocker de Secrets en Clair** : Utilisez toujours des variables d'environnement (via un fichier `.env` localement, et des secrets en production) pour les clés secrètes, mots de passe de base de données, etc.
2.  **Mettre à Jour les Dépendances** : Utilisez `poetry update` régulièrement et des outils comme `safety` pour scanner les dépendances à la recherche de vulnérabilités connues.
    ```bash
    poetry run safety check
    ```
3.  **Principe de Moindre Privilège** : N'accordez que les permissions strictement nécessaires. Par exemple, un utilisateur standard ne doit pas pouvoir modifier les données d'un autre utilisateur.
4.  **Journalisation des Événements de Sécurité** : Assurez-vous que les tentatives de connexion échouées, les accès non autorisés et autres événements de sécurité potentiels sont journalisés.

## 3. Audit de Sécurité

Il est recommandé de réaliser des audits de sécurité périodiques, en utilisant des outils comme :
- **`bandit`** : Pour l'analyse statique du code Python à la recherche de vulnérabilités courantes.
  ```bash
  poetry run bandit -r app/
  ```
- **Scanners de vulnérabilités web** : Des outils comme OWASP ZAP peuvent être utilisés pour scanner l'application déployée à la recherche de failles.