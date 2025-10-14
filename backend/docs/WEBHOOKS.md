# Guide d'Intégration des Webhooks

Ce guide explique comment utiliser les webhooks pour recevoir des notifications en temps réel sur les événements se produisant dans l'application.

## Table des Matières
1. Introduction
2. Gérer les Webhooks (CRUD)
3. Sécuriser vos Webhooks (Validation de Signature)
4. Événements et Payloads
5. Fiabilité : Tentatives et Échecs

## 1. Introduction

Un webhook est un mécanisme qui permet à notre application d'envoyer des informations (un "payload") à une URL de votre choix dès qu'un événement spécifique se produit. Par exemple, vous pouvez être notifié chaque fois qu'un nouveau build est créé ou mis à jour.

## 2. Gérer les Webhooks (CRUD)

Vous pouvez gérer vos webhooks via les endpoints de l'API.

### Créer un Webhook

Créez un webhook en spécifiant une URL et les types d'événements que vous souhaitez écouter.

`POST /api/v1/webhooks/`
```bash
curl -X POST "http://localhost:8000/api/v1/webhooks/" \
     -H "Authorization: Bearer <votre_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://votre-service.com/receiver",
       "event_types": ["build.create", "build.update"]
     }'
```
La réponse contiendra un `secret`. **Ce secret est crucial pour la sécurité et ne sera affiché qu'une seule fois.** Conservez-le en lieu sûr.

### Lister vos Webhooks

`GET /api/v1/webhooks/`
```bash
curl -X GET "http://localhost:8000/api/v1/webhooks/" \
     -H "Authorization: Bearer <votre_token>"
```

### Mettre à jour un Webhook

`PUT /api/v1/webhooks/{webhook_id}`
```bash
curl -X PUT "http://localhost:8000/api/v1/webhooks/{webhook_id}" \
     -H "Authorization: Bearer <votre_token>" \
     -H "Content-Type: application/json" \
     -d '{"is_active": false}'
```

### Supprimer un Webhook

`DELETE /api/v1/webhooks/{webhook_id}`
```bash
curl -X DELETE "http://localhost:8000/api/v1/webhooks/{webhook_id}" \
     -H "Authorization: Bearer <votre_token>"
```

## 3. Sécuriser vos Webhooks (Validation de Signature)

Pour garantir que les requêtes que vous recevez proviennent bien de notre service, chaque payload de webhook est signé avec une signature HMAC-SHA256. La signature est envoyée dans l'en-tête HTTP `X-Webhook-Signature`.

**Le processus de validation est le suivant :**
1.  Récupérez le `secret` que vous avez sauvegardé lors de la création du webhook.
2.  Calculez une signature HMAC-SHA256 sur le **corps brut (raw body)** de la requête que vous avez reçue, en utilisant votre `secret` comme clé.
3.  Comparez la signature que vous avez calculée avec celle présente dans l'en-tête `X-Webhook-Signature` en utilisant une fonction de comparaison sécurisée (qui prévient les attaques par synchronisation).

### Exemple de validation en Python
```python
import hmac
import hashlib

def verify_signature(secret: str, request_body: bytes, received_signature: str) -> bool:
    """Vérifie la signature HMAC-SHA256 d'un payload de webhook."""
    computed_signature = "sha256=" + hmac.new(secret.encode("utf-8"), request_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_signature, received_signature)
```

### Exemple de validation en Node.js (JavaScript)
```javascript
const crypto = require('crypto');

function verifySignature(secret, requestBody, receivedSignature) {
  const computedSignature = `sha256=${crypto.createHmac('sha256', secret).update(requestBody).digest('hex')}`;
  // Utilisez crypto.timingSafeEqual pour une comparaison sécurisée
  return crypto.timingSafeEqual(Buffer.from(computedSignature), Buffer.from(receivedSignature));
}
```

## 4. Événements et Payloads

Chaque payload de webhook suit une structure commune :
```json
{
  "event_type": "build.create",
  "timestamp": "2024-05-25T10:00:00Z",
  "data": { /* ... objet de données spécifique à l'événement ... */ }
}
```

### `build.create`
Déclenché lors de la création d'un nouveau build. Le champ `data` contient l'objet complet du build créé.

### `build.update`
Déclenché lors de la mise à jour d'un build. Le champ `data` contient l'objet complet du build mis à jour.

### `build.delete`
Déclenché lors de la suppression d'un build. Le champ `data` contient l'objet complet du build qui a été supprimé.

## 5. Fiabilité : Tentatives et Échecs

Notre système est conçu pour être résilient.

- **Logique de tentatives :** Si votre endpoint ne répond pas avec un statut `2xx` (succès) dans un délai de 10 secondes, notre service tentera de renvoyer le webhook plusieurs fois. Les tentatives suivent une stratégie de **délai exponentiel (exponential backoff)**.
- **Désactivation automatique :** Si un webhook échoue de manière consécutive après **5 tentatives**, il sera automatiquement marqué comme `is_active: false` pour préserver les ressources du système. Vous devrez le réactiver manuellement via l'API une fois le problème sur votre serveur résolu.