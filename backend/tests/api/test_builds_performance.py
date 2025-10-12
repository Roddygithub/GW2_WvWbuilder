"""
Tests de performance pour les endpoints des builds.

Ces tests sont marqués 'performance' et peuvent être exécutés séparément
de la suite de tests standard.

Exécution : pytest -m performance
"""

import pytest
import time
import asyncio
import psutil
from statistics import mean, stdev
import os
from httpx import AsyncClient
from fastapi import status

from app.core.config import settings


@pytest.mark.performance
class TestBuildsPerformance:
    """Tests de performance pour les endpoints de builds."""

    async def test_create_build_performance(
        self, async_client: AsyncClient, auth_headers, profession_factory, performance_limits
    ):
        """
        Teste la performance de la création de builds, y compris la validation
        des combinaisons de professions.
        """
        headers = await auth_headers()
        prof1 = await profession_factory(name="PerfProf1")
        prof2 = await profession_factory(name="PerfProf2")
        prof3 = await profession_factory(name="PerfProf3")

        build_data = {
            "name": "Performance Test Build",
            "game_mode": "wvw",
            "profession_ids": [prof1.id, prof2.id, prof3.id],
        }

        # Mesurer le temps de réponse
        start_time = time.time()
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers=headers,
        )
        duration = time.time() - start_time

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f"Expected 201, got {response.status_code}: {response.text}"
        # S'assurer que la création est rapide
        assert (
            duration < performance_limits["create_build"]
        ), f"La création du build a pris trop de temps : {duration:.4f}s (limite: {performance_limits['create_build']:.4f}s)"
        print(f"\nTemps de création du build : {duration:.4f}s")

    async def test_get_build_performance(
        self, async_client: AsyncClient, build_factory, auth_headers, performance_limits
    ):
        """Teste les performances de récupération d'un build."""
        headers = await auth_headers()
        build = await build_factory(is_public=True)

        start_time = time.time()
        response = await async_client.get(f"{settings.API_V1_STR}/builds/{build.id}", headers=headers)
        duration = time.time() - start_time

        assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}: {response.text}"
        assert (
            duration < performance_limits["get_build"]
        ), f"La récupération du build a pris trop de temps : {duration:.4f}s (limite: {performance_limits['get_build']:.4f}s)"
        print(f"\nTemps de récupération du build : {duration:.4f}s")

    async def test_update_build_performance(
        self, async_client: AsyncClient, build_factory, auth_headers, performance_limits
    ):
        """Teste la performance de la mise à jour d'un build."""
        # 1. Créer un build initial
        headers = await auth_headers()
        build = await build_factory(name="Performance Test Build to Update", is_public=True)

        update_data = {
            "name": "Updated Performance Build",
            "description": "This description was updated during a performance test.",
            "is_public": False,
        }

        # 2. Mesurer le temps de la requête de mise à jour
        start_time = time.time()
        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{build.id}",
            json=update_data,
            headers=headers,
        )
        duration = time.time() - start_time

        assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}: {response.text}"
        assert (
            duration < performance_limits["update_build"]
        ), f"La mise à jour du build a pris trop de temps : {duration:.4f}s (limite: {performance_limits['update_build']:.4f}s)"
        print(f"\nTemps de mise à jour du build : {duration:.4f}s")

    async def test_multiple_builds_creation_performance(
        self, async_client: AsyncClient, auth_headers, profession_factory, performance_limits
    ):
        """Teste la création de plusieurs builds en parallèle pour simuler une charge."""
        headers = await auth_headers()
        profession = await profession_factory()

        async def create_build(i: int):
            build_data = {
                "name": f"Load Test Build {i}",
                "game_mode": "wvw",
                "profession_ids": [profession.id],
            }
            return await async_client.post(f"{settings.API_V1_STR}/builds/", json=build_data, headers=headers)

        # Création de 10 builds en parallèle
        start_time = time.time()
        tasks = [create_build(i) for i in range(10)]
        responses = await asyncio.gather(*tasks)
        duration = time.time() - start_time

        assert all(
            r.status_code == status.HTTP_201_CREATED for r in responses
        ), f"Not all builds created successfully. Responses: {[r.status_code for r in responses]}"
        # Vérifier le seuil de performance
        assert (
            duration < performance_limits["create_10_builds"]
        ), f"La création de 10 builds a pris trop de temps : {duration:.4f}s (limite: {performance_limits['create_10_builds']:.4f}s)"
        print(f"\nTemps de création de 10 builds en parallèle : {duration:.4f}s")

    async def test_large_payload_build_creation(
        self, async_client: AsyncClient, auth_headers, profession_factory, performance_limits
    ):
        """Teste la création d'un build avec une description volumineuse."""
        headers = await auth_headers()
        profession = await profession_factory()
        large_description = "a" * 1000  # La description est limitée à 1000 caractères par le schéma

        build_data = {
            "name": "Large Payload Build",
            "description": large_description,
            "game_mode": "wvw",
            "profession_ids": [profession.id],
        }

        start_time = time.time()
        response = await async_client.post(f"{settings.API_V1_STR}/builds/", json=build_data, headers=headers)
        duration = time.time() - start_time

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f"Expected 201, got {response.status_code}: {response.text}"
        assert (
            duration < performance_limits["large_payload"]
        ), f"La création d'un build avec payload volumineux a pris trop de temps : {duration:.4f}s (limite: {performance_limits['large_payload']:.4f}s)"
        print(f"\nTemps de création (payload volumineux) : {duration:.4f}s")

    async def test_memory_usage_on_listing(
        self, async_client: AsyncClient, build_factory, auth_headers, user_factory, performance_limits
    ):
        """Teste l'utilisation mémoire lors de la récupération d'une grande liste de builds."""
        process = psutil.Process(os.getpid())
        user = await user_factory(username="mem_test_user")
        headers = await auth_headers(username=user.username)

        # Créer 100 builds pour cet utilisateur
        [await build_factory(user=user, is_public=False) for _ in range(100)]

        start_time = time.time()
        initial_memory = process.memory_info().rss / 1024 / 1024  # en Mo
        response = await async_client.get(f"{settings.API_V1_STR}/builds/", headers=headers)
        final_memory = process.memory_info().rss / 1024 / 1024  # en Mo
        duration = time.time() - start_time

        assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}: {response.text}"

        memory_increase = final_memory - initial_memory
        assert (
            memory_increase < performance_limits["memory_increase_mb"]
        ), f"L'augmentation de la mémoire est trop élevée : {memory_increase:.2f} Mo (limite: {performance_limits['memory_increase_mb']:.2f} Mo)"
        assert (
            duration < performance_limits["list_builds"]
        ), f"La récupération de la liste de builds a pris trop de temps : {duration:.4f}s (limite: {performance_limits['list_builds']:.4f}s)"

        print(f"\nAugmentation mémoire pour lister 100 builds : {memory_increase:.2f} Mo")
        print(f"Temps de récupération de 100 builds : {duration:.4f}s")

    def _analyze_failures(self, responses):
        """Analyse les échecs et retourne un message détaillé."""
        failures = [
            r for r in responses if not (hasattr(r, "status_code") and r.status_code == status.HTTP_201_CREATED)
        ]
        if not failures:
            return "Aucun échec"

        error_counts = {}
        for r in failures:
            error_msg = str(r) if isinstance(r, Exception) else r.json().get("detail", str(r.status_code))
            error_msg_str = str(error_msg)  # Assurer que la clé est une chaîne
            error_counts[error_msg_str] = error_counts.get(error_msg_str, 0) + 1

        return "\n".join(f"- {count}x: {error}" for error, count in error_counts.items())

    def _monitor_resources(self):
        """Surveille l'utilisation des ressources CPU et mémoire."""
        process = psutil.Process(os.getpid())
        return {"cpu_percent": process.cpu_percent(interval=0.1), "memory_mb": process.memory_info().rss / 1024 / 1024}

    def _check_resource_usage(self, start_metrics, end_metrics, limits):
        """Vérifie l'utilisation des ressources par rapport aux limites."""
        memory_increase = end_metrics["memory_mb"] - start_metrics["memory_mb"]
        cpu_usage = end_metrics["cpu_percent"]

        if memory_increase > limits["max_memory_increase_mb"]:
            raise AssertionError(
                f"Trop de mémoire utilisée : {memory_increase:.2f} Mo (limite: {limits['max_memory_increase_mb']:.2f} Mo)"
            )

        if cpu_usage > limits["max_cpu_percent"]:
            raise AssertionError(f"CPU trop sollicité : {cpu_usage:.1f}% (limite: {limits['max_cpu_percent']:.1f}%)")

    @pytest.mark.load_test
    async def test_build_creation_under_load(
        self, async_client: AsyncClient, auth_headers, profession_factory, performance_limits
    ):
        """Teste la création de builds sous charge (100 requêtes en parallèle)."""
        headers = await auth_headers()
        prof = await profession_factory(name="LoadTestProf")

        async def create_build_task(i):
            data = {"name": f"Load Test Build {i}", "game_mode": "pve", "profession_ids": [prof.id]}
            try:
                timeout = performance_limits["timeouts"]["medium"]
                response = await async_client.post(
                    f"{settings.API_V1_STR}/builds/", json=data, headers=headers, timeout=timeout
                )
                return response
            except Exception as e:
                return e  # Retourner l'exception pour l'analyse

        # Exécuter 100 requêtes en parallèle
        num_requests = 100

        start_resources = self._monitor_resources()
        start = time.time()
        tasks = [create_build_task(i) for i in range(num_requests)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start

        success_count = sum(
            1 for r in responses if hasattr(r, "status_code") and r.status_code == status.HTTP_201_CREATED
        )
        success_rate = success_count / num_requests

        end_resources = self._monitor_resources()
        failures_analysis = self._analyze_failures(responses)

        print("\n--- Test de Montée en Charge (Création de Builds) ---")
        print(f"Taux de réussite : {success_count}/{num_requests} ({success_rate:.2%}) en {duration:.4f}s")
        print(f"Utilisation CPU (approximative) : {end_resources['cpu_percent']:.1f}%")
        mem_increase = end_resources["memory_mb"] - start_resources["memory_mb"]
        print(f"Augmentation mémoire : {mem_increase:.2f} Mo")

        print(f"Analyse des échecs :\n{failures_analysis}")

        response_times = [r.elapsed.total_seconds() for r in responses if hasattr(r, "elapsed")]
        if response_times:
            print(f"Temps de réponse (moyenne) : {mean(response_times):.4f}s")
            print(f"Temps de réponse (max) : {max(response_times):.4f}s")
            print(f"Écart-type : {stdev(response_times):.4f}s" if len(response_times) > 1 else "Écart-type : N/A")

        # Vérifier les seuils de ressources
        self._check_resource_usage(start_resources, end_resources, performance_limits)

        assert (
            success_rate >= performance_limits["load_test_success_rate"]
        ), f"Taux de réussite trop faible: {success_rate:.2%} (attendu: {performance_limits['load_test_success_rate']:.2%})"
        assert (
            duration < performance_limits["load_test_duration"]
        ), f"Le test de charge a pris trop de temps : {duration:.4f}s (limite: {performance_limits['load_test_duration']:.4f}s)"

    @pytest.mark.load_test
    async def test_user_journey_under_load(
        self, async_client: AsyncClient, auth_headers, profession_factory, performance_limits
    ):
        """Teste un parcours utilisateur complet (CRUD) sous une charge modérée."""

        async def user_journey_task(i: int):
            try:
                # Chaque tâche utilise un utilisateur différent pour simuler des sessions parallèles
                headers = await auth_headers(username=f"journey_user_{i}", password="password")
                profession = await profession_factory()

                # 1. Création
                create_data = {"name": f"Journey Build {i}", "game_mode": "wvw", "profession_ids": [profession.id]}
                create_res = await async_client.post(
                    f"{settings.API_V1_STR}/builds/", json=create_data, headers=headers
                )
                if create_res.status_code != status.HTTP_201_CREATED:
                    return create_res

                build_id = create_res.json()["id"]

                # 2. Lecture
                read_res = await async_client.get(f"{settings.API_V1_STR}/builds/{build_id}", headers=headers)
                if read_res.status_code != status.HTTP_200_OK:
                    return read_res

                # 3. Mise à jour
                update_data = {"description": "Updated during journey test"}
                update_res = await async_client.put(
                    f"{settings.API_V1_STR}/builds/{build_id}", json=update_data, headers=headers
                )
                if update_res.status_code != status.HTTP_200_OK:
                    return update_res

                # 4. Suppression
                return await async_client.delete(f"{settings.API_V1_STR}/builds/{build_id}", headers=headers)

            except Exception as e:
                return e

        start_time = time.time()
        # Exécuter 20 parcours utilisateurs en parallèle
        tasks = [user_journey_task(i) for i in range(20)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time

        success_count = sum(1 for r in responses if hasattr(r, "status_code") and r.status_code == status.HTTP_200_OK)
        response_times = [r.elapsed.total_seconds() for r in responses if hasattr(r, "elapsed")]

        print("\n--- Test de Parcours Utilisateur ---")
        print(f"Taux de réussite : {success_count}/{len(tasks)} en {duration:.2f}s")
        if response_times:
            avg_response_time = mean(response_times)
            print(f"Temps de réponse moyen : {avg_response_time:.4f}s")
            # Add an assertion for average response time
            assert avg_response_time < 1.0, f"Le temps de réponse moyen ({avg_response_time:.4f}s) est trop élevé."

        assert (
            success_count / len(tasks)
        ) >= 0.9, f"Le taux de réussite du parcours utilisateur est trop faible: {success_count}/{len(tasks)}"

    @pytest.mark.security
    async def test_rate_limiting_on_build_creation(self, async_client: AsyncClient, auth_headers, profession_factory):
        """Teste que le rate limiting est appliqué sur la création de builds."""
        headers = await auth_headers()
        profession = await profession_factory()
        build_data = {
            "name": "Rate Limit Test Build",
            "game_mode": "wvw",
            "profession_ids": [profession.id],
        }

        # Le endpoint est limité à 10 requêtes par minute.
        # Faisons 11 appels rapides pour déclencher la limite.
        responses = []
        for i in range(11):
            response = await async_client.post(
                f"{settings.API_V1_STR}/builds/",
                json={**build_data, "name": f"Rate Limit Test {i}"},
                headers=headers,
            )
            responses.append(response)

        # Les 10 premiers appels devraient réussir, le 11ème devrait échouer.
        assert all(r.status_code == status.HTTP_201_CREATED for r in responses[:10])
        assert responses[10].status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Rate limit exceeded" in responses[10].text
