import pytest
from fastapi import status
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


@pytest.mark.api
class TestWebhooksAPI:
    """Tests pour les endpoints d'API des webhooks."""

    async def test_create_webhook(
        self, async_client: AsyncClient, auth_headers, db: AsyncSession
    ):
        """Teste la création d'un nouveau webhook."""
        headers = await auth_headers()
        webhook_data = {
            "url": "https://example.com/my-webhook",
            "event_types": ["build.create", "build.update"],
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/webhooks/", json=webhook_data, headers=headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["url"] == webhook_data["url"]
        assert data["event_types"] == webhook_data["event_types"]
        assert "id" in data
        assert "secret" in data and data["secret"] is not None

        # Vérifier en base de données
        webhook_db = await crud_webhook.get(db, id=data["id"])
        assert webhook_db is not None
        assert webhook_db.secret is not None
        assert len(webhook_db.secret) == 64

    async def test_read_user_webhooks(
        self, async_client: AsyncClient, auth_headers, user_factory, db: AsyncSession
    ):
        """Teste la récupération des webhooks pour un utilisateur."""
        user = await user_factory(username="webhook_user")
        headers = await auth_headers(username=user.username)

        # Créer deux webhooks pour cet utilisateur
        await crud_webhook.create_with_owner(
            db,
            obj_in={"url": "https://example.com/1", "event_types": ["build.create"]},
            user_id=user.id,
        )
        await crud_webhook.create_with_owner(
            db,
            obj_in={"url": "https://example.com/2", "event_types": ["build.delete"]},
            user_id=user.id,
        )
        await db.commit()

        response = await async_client.get(
            f"{settings.API_V1_STR}/webhooks/", headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert {wh["url"] for wh in data} == {
            "https://example.com/1",
            "https://example.com/2",
        }

    async def test_read_specific_webhook(
        self, async_client: AsyncClient, auth_headers, user_factory, db: AsyncSession
    ):
        """Teste la récupération d'un webhook spécifique par son ID."""
        user = await user_factory(username="specific_webhook_user")
        headers = await auth_headers(username=user.username)
        webhook = await crud_webhook.create_with_owner(
            db,
            obj_in={"url": "https://specific.com", "event_types": ["*"]},
            user_id=user.id,
        )
        await db.commit()

        response = await async_client.get(
            f"{settings.API_V1_STR}/webhooks/{webhook.id}", headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == webhook.id
        assert data["url"] == "https://specific.com"

    async def test_read_other_user_webhook_fails(
        self, async_client: AsyncClient, auth_headers, user_factory, db: AsyncSession
    ):
        """Teste qu'un utilisateur ne peut pas accéder au webhook d'un autre."""
        user1 = await user_factory(username="user1_wh")
        user2_headers = await auth_headers(username="user2_wh")

        webhook_user1 = await crud_webhook.create_with_owner(
            db,
            obj_in={"url": "https://user1.com", "event_types": ["*"]},
            user_id=user1.id,
        )
        await db.commit()

        response = await async_client.get(
            f"{settings.API_V1_STR}/webhooks/{webhook_user1.id}", headers=user2_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_webhook(
        self, async_client: AsyncClient, auth_headers, user_factory, db: AsyncSession
    ):
        """Teste la mise à jour d'un webhook."""
        user = await user_factory(username="update_webhook_user")
        headers = await auth_headers(username=user.username)
        webhook = await crud_webhook.create_with_owner(
            db,
            obj_in={"url": "https://before.com", "event_types": ["build.create"]},
            user_id=user.id,
        )
        await db.commit()

        update_data = {"url": "https://after.com", "is_active": False}
        response = await async_client.put(
            f"{settings.API_V1_STR}/webhooks/{webhook.id}",
            json=update_data,
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["url"] == "https://after.com"
        assert data["is_active"] is False
        assert data["event_types"] == ["build.create"]  # Non modifié

    async def test_delete_webhook(
        self, async_client: AsyncClient, auth_headers, user_factory, db: AsyncSession
    ):
        """Teste la suppression d'un webhook."""
        user = await user_factory(username="delete_webhook_user")
        headers = await auth_headers(username=user.username)
        webhook = await crud_webhook.create_with_owner(
            db,
            obj_in={"url": "https://to-delete.com", "event_types": ["*"]},
            user_id=user.id,
        )
        await db.commit()

        # Vérifier qu'il existe
        assert await crud_webhook.get(db, id=webhook.id) is not None

        # Supprimer
        response = await async_client.delete(
            f"{settings.API_V1_STR}/webhooks/{webhook.id}", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK

        # Vérifier qu'il n'existe plus
        assert await crud_webhook.get(db, id=webhook.id) is None

    async def test_create_webhook_invalid_url(
        self, async_client: AsyncClient, auth_headers
    ):
        """Teste la création d'un webhook avec une URL invalide."""
        headers = await auth_headers()
        webhook_data = {
            "url": "not-a-valid-url",
            "event_types": ["build.create"],
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/webhooks/", json=webhook_data, headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.performance
    async def test_webhook_dispatch_performance_n_plus_one(
        self,
        async_client: AsyncClient,
        auth_headers,
        user_factory,
        db: AsyncSession,
        mocker,
    ):
        """
        Vérifie que le dispatch des webhooks ne souffre pas du problème N+1.
        Le nombre de requêtes SQL pour récupérer les webhooks doit être constant.
        """
        # Créer 10 utilisateurs et 10 webhooks, tous abonnés au même événement
        for i in range(10):
            user = await user_factory(username=f"webhook_perf_user_{i}")
            webhook_data = {
                "url": f"https://example.com/perf-webhook-{i}",
                "event_types": ["build.create"],
            }
            await crud_webhook.create_with_owner(
                db, obj_in=webhook_data, user_id=user.id
            )
        await db.commit()

        # Espionner le nombre de requêtes SQL exécutées
        sql_counter = mocker.spy(db.connection().sync_connection.cursor, "execute")

        # Déclencher un événement qui notifiera les 10 webhooks
        from app.worker import dispatch_webhook_event

        await dispatch_webhook_event(
            "build.create", {"id": 1, "name": "Perf Test Build"}
        )

        # Analyser le nombre d'appels SQL
        call_count = sql_counter.call_count
        print(f"\nNombre de requêtes SQL pour dispatcher 10 webhooks : {call_count}")

        # Le nombre de requêtes doit être très faible (1 pour récupérer tous les webhooks).
        # Une implémentation N+1 ferait 1 (webhooks) + 10 (users) = 11 requêtes.
        assert (
            call_count < 3
        ), f"Détection probable d'un problème N+1. Nombre de requêtes SQL : {call_count}"

    @pytest.mark.load_test
    async def test_webhook_dispatch_under_load(
        self, async_client: AsyncClient, auth_headers, db: AsyncSession, mocker
    ):
        """
        Teste que la création de nombreux builds déclenche correctement les tâches de webhook.
        """
        headers = await auth_headers()
        # Créer un webhook qui écoute les créations de builds
        webhook_data = {
            "url": "https://example.com/load-test-webhook",
            "event_types": ["build.create"],
        }
        await async_client.post(
            f"{settings.API_V1_STR}/webhooks/", json=webhook_data, headers=headers
        )

        # Espionner la fonction qui met les tâches en file d'attente
        mock_enqueue_job = mocker.patch("app.worker.arq_pool.enqueue_job")

        # Créer 20 builds en parallèle
        build_creation_tasks = []
        for i in range(20):
            build_data = {
                "name": f"Load Test Build {i}",
                "game_mode": "wvw",
                "profession_ids": [1],
            }
            task = async_client.post(
                f"{settings.API_V1_STR}/builds/", json=build_data, headers=headers
            )
            build_creation_tasks.append(task)

        await asyncio.gather(*build_creation_tasks)

        # Vérifier que 20 tâches de webhook ont été mises en file d'attente
        assert mock_enqueue_job.call_count == 20
        # Vérifier que la tâche appelée est bien 'send_webhook'
        assert mock_enqueue_job.call_args.args[0] == "send_webhook"
