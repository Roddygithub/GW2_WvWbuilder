# Guide d'Utilisation Avancée

Ce guide couvre des fonctionnalités plus avancées de l'API pour vous aider à optimiser vos interactions avec le backend.

## 1. Pagination

Tous les endpoints de listing (`GET /api/v1/...`) supportent la pagination pour gérer de grands ensembles de données de manière efficace.

- `skip` (ou `offset`) : Le nombre d'éléments à sauter. Par défaut : `0`.
- `limit` : Le nombre maximum d'éléments à retourner. Par défaut : `20`, maximum : `100`.

**Exemple :** Récupérer la deuxième page de 10 builds.
```bash
curl -X GET "http://localhost:8000/api/v1/builds/?skip=10&limit=10" \
     -H "Authorization: Bearer <token>"
```

## 2. Cache Côté Client avec ETag

L'API utilise les en-têtes `ETag` pour permettre une mise en cache efficace côté client. Cela permet d'économiser de la bande passante et d'améliorer la réactivité de votre application.

### Fonctionnement

1.  **Première Requête :** Lorsque vous effectuez une requête `GET`, la réponse inclut un en-tête `ETag`.

    ```http
    HTTP/1.1 200 OK
    ETag: "a1b2c3d4e5f6"
    Cache-Control: public, max-age=60
    ```

2.  **Requêtes Suivantes :** Pour les requêtes suivantes sur la même ressource, incluez la valeur de l'ETag dans l'en-tête `If-None-Match`.

    ```bash
    curl -X GET "http://localhost:8000/api/v1/builds/1" \
         -H "Authorization: Bearer <token>" \
         -H "If-None-Match: \"a1b2c3d4e5f6\""
    ```

3.  **Résultat :**
    - Si les données **n'ont pas changé**, le serveur répondra avec un statut `304 Not Modified` et un corps de réponse vide. Votre client peut alors utiliser la version qu'il a déjà en cache.
    - Si les données **ont changé**, le serveur répondra avec un statut `200 OK`, les nouvelles données, et un nouvel `ETag`.

L'utilisation des ETags est une bonne pratique fortement recommandée pour toutes les applications clientes consommant cette API.

## 3. Cas d'Utilisation : Suivre les Mises à Jour d'un Build

Voici un tutoriel pas à pas pour un cas d'utilisation courant : créer un build et être notifié de ses mises à jour via un webhook.

### Étape 1 : Créer un Webhook

D'abord, créez un webhook qui écoute les événements `build.create` et `build.update`.

```bash
curl -X POST "http://localhost:8000/api/v1/webhooks/" \
     -H "Authorization: Bearer <votre_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://votre-service.com/receiver",
       "event_types": ["build.create", "build.update"]
     }'
```

**Note :** Sauvegardez le `secret` retourné dans la réponse. Vous en aurez besoin pour valider les futurs payloads.

### Étape 2 : Créer un Build

Maintenant, créez un nouveau build. Cette action déclenchera l'événement `build.create`.

```bash
curl -X POST "http://localhost:8000/api/v1/builds/" \
     -H "Authorization: Bearer <votre_token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Mon Build à Suivre", "game_mode": "wvw", "profession_ids": [1]}'
```

Votre service à l'URL `https://votre-service.com/receiver` devrait recevoir une requête POST avec le payload de l'événement `build.create`. N'oubliez pas de valider la signature `X-Webhook-Signature` !

### Étape 3 : Mettre à Jour le Build

Modifions le build. Cette action déclenchera l'événement `build.update`.

```bash
curl -X PUT "http://localhost:8000/api/v1/builds/{id_du_build}" \
     -H "Authorization: Bearer <votre_token>" \
     -H "Content-Type: application/json" \
     -d '{"description": "Description mise à jour."}'
```

Votre service recevra une nouvelle notification, cette fois avec le type d'événement `build.update` et les données du build mis à jour.