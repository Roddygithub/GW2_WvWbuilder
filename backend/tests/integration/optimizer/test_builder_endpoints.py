"""Integration tests for builder API endpoints."""
import pytest
from httpx import AsyncClient
from fastapi import status

from app.main import app
from tests.conftest import get_test_db


@pytest.mark.asyncio
class TestBuilderOptimizeEndpoint:
    """Test /builder/optimize endpoint."""

    async def test_optimize_wvw_zerg(self, client: AsyncClient, normal_user_token_headers):
        """Test optimizing WvW zerg composition."""
        request_data = {
            "squad_size": 15,
            "game_type": "wvw",
            "game_mode": "zerg",
        }
        
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "composition" in data
        assert "global_score" in data
        assert "metrics" in data
        assert data["composition"]["squad_size"] == 15
        assert len(data["composition"]["members"]) == 15
        assert data["global_score"] > 0

    async def test_optimize_pve_fractale(self, client: AsyncClient, normal_user_token_headers):
        """Test optimizing PvE fractale composition."""
        request_data = {
            "squad_size": 5,
            "game_type": "pve",
            "game_mode": "fractale",
        }
        
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["composition"]["squad_size"] == 5
        assert len(data["composition"]["members"]) == 5
        # PvE should have good quickness/alacrity
        assert data["metrics"]["boon_coverage"]["quickness"] > 0.5
        assert data["metrics"]["boon_coverage"]["alacrity"] > 0.5

    async def test_optimize_with_fixed_professions(self, client: AsyncClient, normal_user_token_headers):
        """Test optimizing with fixed professions."""
        request_data = {
            "squad_size": 5,
            "game_type": "pve",
            "game_mode": "fractale",
            "fixed_professions": [1, 1, 2],  # 2 Guardians, 1 Revenant
        }
        
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check fixed professions are respected
        professions = [m["profession_id"] for m in data["composition"]["members"]]
        assert professions.count(1) >= 2
        assert 2 in professions

    async def test_optimize_with_min_boon_uptime(self, client: AsyncClient, normal_user_token_headers):
        """Test optimizing with minimum boon uptime constraints."""
        request_data = {
            "squad_size": 5,
            "game_type": "pve",
            "game_mode": "raid",
            "min_boon_uptime": {
                "quickness": 0.9,
                "alacrity": 0.9,
            }
        }
        
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should try to meet requirements
        assert data["metrics"]["boon_coverage"]["quickness"] >= 0.8
        assert data["metrics"]["boon_coverage"]["alacrity"] >= 0.8

    async def test_optimize_invalid_game_type(self, client: AsyncClient, normal_user_token_headers):
        """Test optimize with invalid game type."""
        request_data = {
            "squad_size": 5,
            "game_type": "invalid",
            "game_mode": "zerg",
        }
        
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_optimize_invalid_squad_size(self, client: AsyncClient, normal_user_token_headers):
        """Test optimize with invalid squad size."""
        request_data = {
            "squad_size": 0,
            "game_type": "pve",
            "game_mode": "fractale",
        }
        
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_optimize_requires_authentication(self, client: AsyncClient):
        """Test that optimize endpoint requires authentication."""
        request_data = {
            "squad_size": 5,
            "game_type": "pve",
            "game_mode": "fractale",
        }
        
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_optimize_wvw_roaming(self, client: AsyncClient, normal_user_token_headers):
        """Test optimizing WvW roaming composition."""
        request_data = {
            "squad_size": 5,
            "game_type": "wvw",
            "game_mode": "roaming",
        }
        
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["composition"]["squad_size"] == 5
        assert data["global_score"] > 0

    async def test_optimize_pve_openworld(self, client: AsyncClient, normal_user_token_headers):
        """Test optimizing PvE open world composition."""
        request_data = {
            "squad_size": 3,
            "game_type": "pve",
            "game_mode": "openworld",
        }
        
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["composition"]["squad_size"] == 3
        assert len(data["composition"]["members"]) == 3


@pytest.mark.asyncio
class TestBuilderModesEndpoint:
    """Test /builder/modes endpoint."""

    async def test_get_game_modes(self, client: AsyncClient, normal_user_token_headers):
        """Test getting available game modes."""
        response = await client.get(
            "/api/v1/builder/modes",
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "game_types" in data
        assert "wvw" in data["game_types"]
        assert "pve" in data["game_types"]

    async def test_get_wvw_modes(self, client: AsyncClient, normal_user_token_headers):
        """Test getting WvW modes."""
        response = await client.get(
            "/api/v1/builder/modes",
            headers=normal_user_token_headers,
        )
        
        data = response.json()
        wvw_modes = data["game_types"]["wvw"]["modes"]
        
        assert len(wvw_modes) >= 3
        mode_ids = [m["id"] for m in wvw_modes]
        assert "zerg" in mode_ids
        assert "roaming" in mode_ids
        assert "guild_raid" in mode_ids

    async def test_get_pve_modes(self, client: AsyncClient, normal_user_token_headers):
        """Test getting PvE modes."""
        response = await client.get(
            "/api/v1/builder/modes",
            headers=normal_user_token_headers,
        )
        
        data = response.json()
        pve_modes = data["game_types"]["pve"]["modes"]
        
        assert len(pve_modes) >= 3
        mode_ids = [m["id"] for m in pve_modes]
        assert "openworld" in mode_ids
        assert "fractale" in mode_ids
        assert "raid" in mode_ids

    async def test_modes_have_required_fields(self, client: AsyncClient, normal_user_token_headers):
        """Test that modes have all required fields."""
        response = await client.get(
            "/api/v1/builder/modes",
            headers=normal_user_token_headers,
        )
        
        data = response.json()
        wvw_modes = data["game_types"]["wvw"]["modes"]
        
        for mode in wvw_modes:
            assert "id" in mode
            assert "name" in mode
            assert "description" in mode
            assert "squad_size_range" in mode
            assert "emphasis" in mode

    async def test_modes_requires_authentication(self, client: AsyncClient):
        """Test that modes endpoint requires authentication."""
        response = await client.get("/api/v1/builder/modes")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
class TestBuilderProfessionsEndpoint:
    """Test /builder/professions endpoint."""

    async def test_get_professions(self, client: AsyncClient, normal_user_token_headers):
        """Test getting available professions."""
        response = await client.get(
            "/api/v1/builder/professions",
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "professions" in data
        assert len(data["professions"]) == 9

    async def test_professions_have_required_fields(self, client: AsyncClient, normal_user_token_headers):
        """Test that professions have all required fields."""
        response = await client.get(
            "/api/v1/builder/professions",
            headers=normal_user_token_headers,
        )
        
        data = response.json()
        
        for profession in data["professions"]:
            assert "id" in profession
            assert "name" in profession
            assert "color" in profession

    async def test_professions_list(self, client: AsyncClient, normal_user_token_headers):
        """Test that all 9 professions are present."""
        response = await client.get(
            "/api/v1/builder/professions",
            headers=normal_user_token_headers,
        )
        
        data = response.json()
        profession_names = [p["name"] for p in data["professions"]]
        
        expected = ["Guardian", "Revenant", "Necromancer", "Warrior", 
                   "Elementalist", "Engineer", "Ranger", "Thief", "Mesmer"]
        
        for name in expected:
            assert name in profession_names

    async def test_professions_requires_authentication(self, client: AsyncClient):
        """Test that professions endpoint requires authentication."""
        response = await client.get("/api/v1/builder/professions")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
class TestBuilderRolesEndpoint:
    """Test /builder/roles endpoint."""

    async def test_get_roles(self, client: AsyncClient, normal_user_token_headers):
        """Test getting available roles."""
        response = await client.get(
            "/api/v1/builder/roles",
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "roles" in data
        assert len(data["roles"]) > 0

    async def test_roles_have_required_fields(self, client: AsyncClient, normal_user_token_headers):
        """Test that roles have all required fields."""
        response = await client.get(
            "/api/v1/builder/roles",
            headers=normal_user_token_headers,
        )
        
        data = response.json()
        
        for role in data["roles"]:
            assert "id" in role
            assert "name" in role

    async def test_roles_requires_authentication(self, client: AsyncClient):
        """Test that roles endpoint requires authentication."""
        response = await client.get("/api/v1/builder/roles")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
class TestBuilderPerformance:
    """Test builder endpoint performance."""

    async def test_optimize_completes_within_time_budget(self, client: AsyncClient, normal_user_token_headers):
        """Test that optimization completes within reasonable time."""
        import time
        
        request_data = {
            "squad_size": 10,
            "game_type": "wvw",
            "game_mode": "zerg",
        }
        
        start_time = time.time()
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
            headers=normal_user_token_headers,
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == status.HTTP_200_OK
        # Should complete within 10 seconds (5s budget + overhead)
        assert elapsed < 10.0

    async def test_optimize_large_squad(self, client: AsyncClient, normal_user_token_headers):
        """Test optimizing large squad (50 players)."""
        request_data = {
            "squad_size": 50,
            "game_type": "wvw",
            "game_mode": "zerg",
        }
        
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["composition"]["members"]) == 50
        assert data["global_score"] > 0


@pytest.mark.asyncio
class TestBuilderEdgeCases:
    """Test edge cases and error handling."""

    async def test_optimize_minimum_squad(self, client: AsyncClient, normal_user_token_headers):
        """Test optimizing with minimum squad size (1)."""
        request_data = {
            "squad_size": 1,
            "game_type": "pve",
            "game_mode": "openworld",
        }
        
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["composition"]["members"]) == 1

    async def test_optimize_with_many_fixed_professions(self, client: AsyncClient, normal_user_token_headers):
        """Test optimizing with many fixed professions."""
        request_data = {
            "squad_size": 10,
            "game_type": "wvw",
            "game_mode": "guild_raid",
            "fixed_professions": [1, 1, 1, 2, 2, 3, 3, 4, 5],  # 9 fixed
        }
        
        response = await client.post(
            "/api/v1/builder/optimize",
            json=request_data,
            headers=normal_user_token_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should handle many constraints
        assert len(data["composition"]["members"]) == 10

    async def test_optimize_all_game_modes(self, client: AsyncClient, normal_user_token_headers):
        """Test that all game modes can be optimized."""
        game_modes = [
            ("wvw", "zerg", 30),
            ("wvw", "roaming", 5),
            ("wvw", "guild_raid", 20),
            ("pve", "openworld", 3),
            ("pve", "fractale", 5),
            ("pve", "raid", 10),
        ]
        
        for game_type, game_mode, squad_size in game_modes:
            request_data = {
                "squad_size": squad_size,
                "game_type": game_type,
                "game_mode": game_mode,
            }
            
            response = await client.post(
                "/api/v1/builder/optimize",
                json=request_data,
                headers=normal_user_token_headers,
            )
            
            assert response.status_code == status.HTTP_200_OK, f"Failed for {game_type}/{game_mode}"
            data = response.json()
            assert data["composition"]["squad_size"] == squad_size
