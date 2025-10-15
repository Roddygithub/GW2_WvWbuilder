"""
Tests de charge pour les webhooks de l'API GW2 WvW Builder.
"""

from locust import HttpUser, task, between, tag
import random
from typing import List
import logging

# Configuration du logger
logger = logging.getLogger(__name__)


class WebhookUser(HttpUser):
    """Classe de test pour les webhooks avec différents scénarios de charge."""

    wait_time = between(1, 3)
    webhook_urls: List[str] = []

    def on_start(self):
        """Initialisation avant l'exécution des tests."""
        if not self.webhook_urls:
            self.setup_test_webhooks()

    def setup_test_webhooks(self):
        """Configure des webhooks de test si nécessaire."""
        # Ici, vous pouvez ajouter la logique pour créer des webhooks de test
        # ou les récupérer depuis une source de données
        self.webhook_urls = ["/api/v1/webhooks/endpoint1", "/api/v1/webhooks/endpoint2"]

    @tag("webhook_trigger")
    @task(3)
    def trigger_webhook(self):
        """Déclenche un webhook avec des données aléatoires."""
        if not self.webhook_urls:
            return

        url = random.choice(self.webhook_urls)
        payload = {
            "event": f"test_event_{random.randint(1, 10)}",
            "data": {
                "test_id": random.randint(1000, 9999),
                "timestamp": "2025-10-08T12:00:00Z",
                "payload": {"key": f"value_{random.randint(1, 100)}"},
            },
        }

        with self.client.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            name="/api/v1/webhooks/[id]",
        ) as response:
            if response.status_code >= 400:
                logger.error(
                    f"Erreur lors du déclenchement du webhook: {response.text}"
                )

    @tag("webhook_create")
    @task(1)
    def create_webhook(self):
        """Test la création de webhooks."""
        webhook_data = {
            "name": f"test_webhook_{random.randint(1000, 9999)}",
            "url": "https://example.com/webhook",
            "events": ["build.created", "build.updated"],
            "active": True,
            "secret": "test_secret",
        }

        with self.client.post(
            "/api/v1/webhooks", json=webhook_data, name="/api/v1/webhooks [POST]"
        ) as response:
            if response.status_code == 201:
                try:
                    webhook = response.json()
                    self.webhook_urls.append(f"/api/v1/webhooks/{webhook['id']}")
                except Exception as e:
                    logger.error(f"Erreur lors de l'analyse de la réponse: {e}")


class AuthenticatedWebhookUser(WebhookUser):
    """Utilisateur authentifié pour les tests de webhook."""

    def on_start(self):
        """Authentification avant les tests."""
        # Remplacez par votre logique d'authentification
        self.client.headers.update({"Authorization": "Bearer test_token"})
        super().on_start()


class HighLoadWebhookUser(WebhookUser):
    """Utilisateur pour les tests de charge élevée."""

    wait_time = between(0.1, 0.5)

    @task(5)
    def trigger_webhook_high_load(self):
        """Déclenche des webhooks avec une charge plus élevée."""
        super().trigger_webhook()
