"""
Tests d'intégration pour les opérations CRUD sur les builds.
"""
import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_build import build as crud_build
from app.models import Build, User, Profession, EliteSpecialization
from app.schemas.build import BuildCreate, BuildUpdate
from tests.integration.conftest import test_data

@pytest.mark.integration
@pytest.mark.db
class TestCRUDBuilds:
    """Tests pour les opérations CRUD sur les builds."""
    
    async def test_create_build(self, db: AsyncSession, test_data: dict):
        """Teste la création d'un nouveau build."""
        # Récupérer les données de test
        user = test_data["users"]["user"]
        profession = test_data["professions"]["warrior"]
        elite_spec = test_data["elite_specs"]["berserker"]
        
        # Données pour la création du build
        build_in = BuildCreate(
            name="New Test Build",
            description="A test build for integration testing",
            is_public=True,
            profession_id=profession.id,
            elite_spec_id=elite_spec.id,
            weapons=["Axe", "Axe"],
            skills=["Banner of Strength", "Banner of Discipline"],
            traits={"Strength": [1, 2, 1], "Discipline": [2, 2, 1], "Berserker": [1, 2, 3]},
            equipment={"weapons": ["Axe", "Axe"], "armor": ["Berserker's"], "trinkets": ["Berserker's"]},
            infusions={"weapons": ["+9 Agony Infusion"], "armor": [], "trinkets": []},
            consumables={"food": "Bowl of Sweet and Spicy Butternut Squash Soup", "utility": "Superior Sharpening Stone"},
            attributes={"power": 3000, "precision": 2000, "ferocity": 1500, "vitality": 1000},
            skills_guide="Start with banner and burst rotation...",
            rotation_guide="Maintain might stacks and use banners on cooldown...",
            video_guide_url="https://example.com/build-video",
            gw2skills_url="https://lucky-noobs.com/builds/view/12345"
        )
        
        # Créer le build
        created_build = await crud_build.create_with_owner(
            db=db,
            obj_in=build_in,
            owner_id=user.id
        )
        
        # Vérifications
        assert created_build.id is not None
        assert created_build.name == "New Test Build"
        assert created_build.user_id == user.id
        assert created_build.profession_id == profession.id
        assert created_build.elite_spec_id == elite_spec.id
        assert created_build.is_public is True
        assert len(created_build.weapons) == 2
        assert "Axe" in created_build.weapons
        assert len(created_build.skills) == 2
        assert "Banner of Strength" in created_build.skills
        
        # Vérifier que le build est bien en base de données
        db_build = await db.get(Build, created_build.id)
        assert db_build is not None
        assert db_build.name == "New Test Build"
    
    async def test_get_build(self, db: AsyncSession, test_data: dict):
        """Teste la récupération d'un build par son ID."""
        # Récupérer un build existant
        existing_build = test_data["builds"]["berserker_build"]
        
        # Récupérer le build
        retrieved_build = await crud_build.get(db=db, id=existing_build.id)
        
        # Vérifications
        assert retrieved_build is not None
        assert retrieved_build.id == existing_build.id
        assert retrieved_build.name == existing_build.name
    
    async def test_get_multi_builds(self, db: AsyncSession, test_data: dict):
        """Teste la récupération de plusieurs builds avec pagination."""
        # Récupérer tous les builds
        builds = await crud_build.get_multi(db=db, skip=0, limit=10)
        
        # Vérifications
        assert len(builds) >= 2  # Au moins les deux builds créés dans les fixtures
        
        # Vérifier la pagination
        paginated_builds = await crud_build.get_multi(db=db, skip=1, limit=1)
        assert len(paginated_builds) == 1
    
    async def test_update_build(self, db: AsyncSession, test_data: dict):
        """Teste la mise à jour d'un build existant."""
        # Récupérer un build existant
        existing_build = test_data["builds"]["berserker_build"]
        
        # Données de mise à jour
        update_data = BuildUpdate(
            name="Updated Build Name",
            description="Updated description",
            is_public=False,
            weapons=["Greatsword", "Axe/Axe"],
            skills=["Banner of Strength", "Banner of Discipline", "Signet of Might"],
            traits={"Strength": [1, 2, 1], "Discipline": [2, 2, 1], "Berserker": [1, 2, 3]}
        )
        
        # Mettre à jour le build
        updated_build = await crud_build.update(
            db=db,
            db_obj=existing_build,
            obj_in=update_data
        )
        
        # Vérifications
        assert updated_build.name == "Updated Build Name"
        assert updated_build.description == "Updated description"
        assert updated_build.is_public is False
        assert "Greatsword" in updated_build.weapons
        assert len(updated_build.skills) == 3
        assert "Signet of Might" in updated_build.skills
        
        # Vérifier que les champs non mis à jour sont inchangés
        assert updated_build.profession_id == existing_build.profession_id
        assert updated_build.user_id == existing_build.user_id
    
    async def test_remove_build(self, db: AsyncSession, test_data: dict):
        """Teste la suppression d'un build."""
        # Récupérer un build existant
        existing_build = test_data["builds"]["dragonhunter_build"]
        build_id = existing_build.id
        
        # Supprimer le build
        deleted_build = await crud_build.remove(db=db, id=build_id)
        
        # Vérifications
        assert deleted_build is not None
        assert deleted_build.id == build_id
        
        # Vérifier que le build a bien été supprimé de la base de données
        db_build = await db.get(Build, build_id)
        assert db_build is None
    
    async def test_get_builds_by_profession(self, db: AsyncSession, test_data: dict):
        """Teste la récupération des builds par profession."""
        # Récupérer une profession existante
        profession = test_data["professions"]["warrior"]
        
        # Récupérer les builds pour cette profession
        builds = await crud_build.get_by_field(
            db=db,
            field="profession_id",
            value=profession.id
        )
        
        # Vérifications
        assert len(builds) >= 1  # Au moins un build pour cette profession
        for build in builds:
            assert build.profession_id == profession.id
    
    async def test_get_public_builds(self, db: AsyncSession, test_data: dict):
        """Teste la récupération des builds publics."""
        # Récupérer les builds publics
        public_builds = await crud_build.get_by_field(
            db=db,
            field="is_public",
            value=True
        )
        
        # Vérifications
        assert len(public_builds) >= 1  # Au moins un build public
        for build in public_builds:
            assert build.is_public is True
    
    async def test_get_builds_by_owner(self, db: AsyncSession, test_data: dict):
        """Teste la récupération des builds d'un utilisateur spécifique."""
        # Récupérer un utilisateur existant
        user = test_data["users"]["user"]
        
        # Récupérer les builds de cet utilisateur
        user_builds = await crud_build.get_by_owner(
            db=db,
            owner_id=user.id,
            skip=0,
            limit=10
        )
        
        # Vérifications
        assert len(user_builds) >= 1  # Au moins un build pour cet utilisateur
        for build in user_builds:
            assert build.user_id == user.id
    
    async def test_search_builds(self, db: AsyncSession, test_data: dict):
        """Teste la recherche de builds par terme de recherche."""
        # Rechercher des builds avec un terme spécifique
        search_term = "Berserker"
        search_results = await crud_build.search(
            db=db,
            search_term=search_term,
            skip=0,
            limit=10
        )
        
        # Vérifications
        assert len(search_results) >= 1  # Au moins un résultat
        for build in search_results:
            # Vérifier que le terme de recherche est dans le nom ou la description
            assert (search_term.lower() in build.name.lower()) or \
                   (build.description and search_term.lower() in build.description.lower())

@pytest.mark.integration
@pytest.mark.db
class TestBuildPermissions:
    """Tests pour les permissions des builds."""
    
    async def test_private_build_visibility(self, db: AsyncSession, test_data: dict):
        """Teste que les builds privés ne sont visibles que par leur propriétaire."""
        # Récupérer un build privé et son propriétaire
        private_build = test_data["builds"]["dragonhunter_build"]
        owner = test_data["users"]["admin"]
        other_user = test_data["users"]["user"]
        
        # Le propriétaire devrait pouvoir voir son build privé
        owner_builds = await crud_build.get_by_owner(
            db=db,
            owner_id=owner.id,
            skip=0,
            limit=10
        )
        assert any(build.id == private_build.id for build in owner_builds)
        
        # Un autre utilisateur ne devrait pas voir le build privé dans ses résultats
        other_user_builds = await crud_build.get_by_owner(
            db=db,
            owner_id=other_user.id,
            skip=0,
            limit=10
        )
        assert not any(build.id == private_build.id for build in other_user_builds)
        
        # Le build ne devrait pas apparaître dans les résultats de recherche globaux
        search_results = await crud_build.search(
            db=db,
            search_term=private_build.name,
            skip=0,
            limit=10
        )
        assert not any(build.id == private_build.id for build in search_results)
    
    async def test_update_build_permissions(self, db: AsyncSession, test_data: dict):
        """Teste que seuls les propriétaires peuvent mettre à jour leurs builds."""
        # Récupérer un build et son propriétaire
        build = test_data["builds"]["berserker_build"]
        owner = test_data["users"]["user"]
        other_user = test_data["users"]["admin"]
        
        # Le propriétaire devrait pouvoir mettre à jour son build
        update_data = BuildUpdate(name="Updated by owner")
        updated_build = await crud_build.update(
            db=db,
            db_obj=build,
            obj_in=update_data,
            owner_id=owner.id
        )
        assert updated_build.name == "Updated by owner"
        
        # Un autre utilisateur ne devrait pas pouvoir mettre à jour le build
        with pytest.raises(PermissionError):
            await crud_build.update(
                db=db,
                db_obj=build,
                obj_in=BuildUpdate(name="Updated by other user"),
                owner_id=other_user.id
            )
    
    async def test_delete_build_permissions(self, db: AsyncSession, test_data: dict):
        """Teste que seuls les propriétaires peuvent supprimer leurs builds."""
        # Créer un nouveau build pour le test
        user = test_data["users"]["user"]
        other_user = test_data["users"]["admin"]
        
        build_in = BuildCreate(
            name="Temporary Build",
            description="A temporary build for testing deletion",
            is_public=True,
            profession_id=test_data["professions"]["warrior"].id,
            elite_spec_id=test_data["elite_specs"]["berserker"].id,
            weapons=["Axe", "Axe"],
            skills=[],
            traits={}
        )
        
        # Créer le build
        build = await crud_build.create_with_owner(
            db=db,
            obj_in=build_in,
            owner_id=user.id
        )
        
        # Le propriétaire devrait pouvoir supprimer son build
        deleted_build = await crud_build.remove(
            db=db,
            id=build.id,
            owner_id=user.id
        )
        assert deleted_build is not None
        
        # Vérifier que le build a bien été supprimé
        db_build = await db.get(Build, build.id)
        assert db_build is None
        
        # Créer un autre build pour tester la suppression par un non-propriétaire
        another_build = await crud_build.create_with_owner(
            db=db,
            obj_in=build_in,
            owner_id=user.id
        )
        
        # Un autre utilisateur ne devrait pas pouvoir supprimer le build
        with pytest.raises(PermissionError):
            await crud_build.remove(
                db=db,
                id=another_build.id,
                owner_id=other_user.id
            )
        
        # Vérifier que le build n'a pas été supprimé
        db_build = await db.get(Build, another_build.id)
        assert db_build is not None
        
        # Nettoyage
        await crud_build.remove(db=db, id=another_build.id)
