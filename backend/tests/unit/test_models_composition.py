"""
Tests for the Composition model and its relationships.

This module contains unit tests for the Composition model, including:
- Model validations and constraints
- Relationships with other models (User, Build, CompositionTag)
- CRUD operations with edge cases
"""

import pytest
import pytest_asyncio
import traceback
import uuid
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException, status

# Modèles
from app.models.user import User
from app.models.build import Build
from app.models.composition import Composition
from app.models.role import Role
from app.models.profession import Profession
from app.models.tag import Tag
from app.models.composition_tag import CompositionTag

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuration pour les tests
pytestmark = pytest.mark.asyncio

# Activer les logs SQL
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Test data
TEST_COMPOSITION_DATA = {
    "name": "Test Composition",
    "description": "A test composition",
    "squad_size": 10,
    "is_public": False,
    "status": "draft",
    "game_mode": "wvw",
}

# Fixtures


@pytest_asyncio.fixture
async def sample_user(db: AsyncSession):
    """Create a sample user for testing."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_build(db: AsyncSession, sample_user: User):
    """Create a sample build for testing."""
    build = Build(
        name="Test Build",
        description="A test build",
        game_mode="wvw",
        team_size=5,
        is_public=False,
        created_by_id=sample_user.id,
        config={"test": "config"},
        constraints={"test": "constraint"},
    )
    db.add(build)
    await db.commit()
    await db.refresh(build)
    return build


@pytest_asyncio.fixture
async def sample_role(db: AsyncSession):
    """Create a sample role for testing."""
    role = Role(
        name=f"TestRole_{uuid.uuid4().hex[:8]}",
        description="Test Role Description",
        permission_level=1,
        is_default=False,
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@pytest_asyncio.fixture
async def sample_profession(db: AsyncSession):
    """Create a sample profession for testing."""
    prof = Profession(
        name=f"TestProfession_{uuid.uuid4().hex[:8]}",
        description="A test profession for WvW",
        game_modes=["wvw", "pve"],
        is_active=True,
        icon_url="http://example.com/profession_icon.png",
    )
    db.add(prof)
    await db.commit()
    await db.refresh(prof)
    return prof


@pytest_asyncio.fixture
async def sample_composition(db: AsyncSession, sample_user: User, sample_build: Build):
    """Create a sample composition for testing."""
    # Generate a unique name for the composition
    unique_name = f"{TEST_COMPOSITION_DATA['name']}_{uuid.uuid4().hex[:8]}"

    composition = Composition(
        name=unique_name,
        description=TEST_COMPOSITION_DATA["description"],
        squad_size=TEST_COMPOSITION_DATA["squad_size"],
        is_public=TEST_COMPOSITION_DATA["is_public"],
        status=TEST_COMPOSITION_DATA["status"],
        game_mode=TEST_COMPOSITION_DATA["game_mode"],
        created_by=sample_user.id,
        build_id=sample_build.id,
    )
    db.add(composition)
    await db.commit()
    await db.refresh(composition)
    return composition


@pytest_asyncio.fixture
async def sample_composition_async(
    db: AsyncSession, sample_user: User, sample_build: Build
):
    """Create a sample composition for async testing."""
    # Generate a unique name for the composition
    unique_name = f"{TEST_COMPOSITION_DATA['name']}_async_{uuid.uuid4().hex[:8]}"

    composition = Composition(
        name=unique_name,
        description=TEST_COMPOSITION_DATA["description"] + " (async)",
        squad_size=TEST_COMPOSITION_DATA["squad_size"],
        is_public=TEST_COMPOSITION_DATA["is_public"],
        status=TEST_COMPOSITION_DATA["status"],
        game_mode=TEST_COMPOSITION_DATA["game_mode"],
        created_by=sample_user.id,
        build_id=sample_build.id,
    )
    db.add(composition)
    await db.commit()
    await db.refresh(composition)
    return composition


# Test cases


class TestCompositionModel:
    """Test cases for the Composition model."""

    @pytest.mark.asyncio
    async def test_composition_creation(
        self, db: AsyncSession, sample_user: User, sample_build: Build
    ) -> None:
        """
        Test basic composition creation with valid data.

        This test verifies that a composition can be created with valid data and that
        all relationships are properly set up.
        """
        logger.info("\n=== Starting test_composition_creation ===")

        # Start a transaction with savepoint for this test
        async with db.begin() as transaction:
            try:
                # Afficher les informations de base
                logger.debug(f"[TEST] Sample user: {sample_user}")
                logger.debug(f"[TEST] Sample build: {sample_build}")
                logger.debug(
                    f"[TEST] Sample user ID: {getattr(sample_user, 'id', 'No ID')}"
                )
                logger.debug(
                    f"[TEST] Sample build ID: {getattr(sample_build, 'id', 'No ID')}"
                )

                # Vérifier la connexion à la base de données
                try:
                    result = await db.execute(text("SELECT 1"))
                    logger.debug("[TEST] Connexion à la base de données réussie")
                except Exception as e:
                    logger.error(
                        f"[ERROR] Erreur de connexion à la base de données: {e}"
                    )
                    raise

                # Vérifier que les IDs sont valides
                assert sample_user.id is not None, "L'utilisateur n'a pas d'ID valide"
                assert sample_build.id is not None, "Le build n'a pas d'ID valide"

                # Créer une composition simple
                logger.debug("[TEST] Création de la composition...")

                # Charger explicitement les relations nécessaires
                from sqlalchemy import select
                from sqlalchemy.orm import selectinload

                # Recharger l'utilisateur avec ses relations
                user_result = await db.execute(
                    select(User)
                    .options(
                        selectinload(User.compositions),
                        selectinload(User.created_compositions),
                    )
                    .filter(User.id == sample_user.id)
                )
                sample_user = user_result.scalar_one()

                # Recharger le build avec ses relations
                build_result = await db.execute(
                    select(Build)
                    .options(selectinload(Build.compositions))
                    .filter(Build.id == sample_build.id)
                )
                sample_build = build_result.scalar_one()

                # Afficher l'état des relations avant création
                logger.debug("[TEST] État des relations avant création:")
                logger.debug(
                    f"[TEST] sample_user.compositions: {getattr(sample_user, 'compositions', 'Non chargé')}"
                )
                logger.debug(
                    f"[TEST] sample_user.created_compositions: {getattr(sample_user, 'created_compositions', 'Non chargé')}"
                )
                logger.debug(
                    f"[TEST] sample_build.compositions: {getattr(sample_build, 'compositions', 'Non chargé')}"
                )

                # Create a savepoint to rollback to in case of errors
                savepoint = await db.begin_nested()

                # Créer la composition avec des logs détaillés
                try:
                    logger.debug("[TEST] Création de l'objet Composition...")
                    composition = Composition(
                        name="Test Composition",
                        description="A test composition",
                        created_by=sample_user.id,
                        build_id=sample_build.id,
                        squad_size=5,
                        is_public=True,
                        status="draft",
                        game_mode="wvw",
                    )
                    logger.debug("[TEST] Objet Composition créé avec succès")
                except Exception as e:
                    logger.error(
                        f"[ERROR] Erreur lors de la création de l'objet Composition: {e}"
                    )
                    logger.error(f"[ERROR] Type d'erreur: {type(e).__name__}")
                    logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
                    await savepoint.rollback()
                    raise

                logger.debug("[TEST] Composition créée avec succès")
                logger.debug(f"[TEST] Composition avant ajout: {composition}")

                # Vérifier les valeurs avant ajout
                assert composition.name == "Test Composition"
                assert composition.created_by == sample_user.id
                assert composition.build_id == sample_build.id

                try:
                    logger.debug("[TEST] Ajout de la composition à la session...")
                    db.add(composition)
                    logger.debug("[TEST] Composition ajoutée à la session")

                    # Afficher l'état de la session avant le commit
                    logger.debug("[TEST] État de la session avant commit:")
                    logger.debug(
                        f"[TEST] Nouvelles instances dans la session: {db.new}"
                    )
                    logger.debug(f"[TEST] Instances modifiées: {db.dirty}")

                    # Vérifier si la table compositions existe
                    try:
                        logger.debug(
                            "[TEST] Vérification de la table 'compositions'..."
                        )
                        # Vérifier si la table existe
                        result = await db.execute(
                            text(
                                "SELECT name FROM sqlite_master WHERE type='table' AND name='compositions'"
                            )
                        )
                        table_row = result.fetchone()
                        table_exists = table_row is not None
                        logger.debug(
                            f"[TEST] La table 'compositions' existe: {table_exists}"
                        )

                        if table_exists:
                            # Récupérer la définition de la table
                            result = await db.execute(
                                text(
                                    "SELECT sql FROM sqlite_master WHERE type='table' AND name='compositions'"
                                )
                            )
                            table_definition = result.fetchone()
                            logger.debug(
                                f"[TEST] Définition de la table 'compositions': {table_definition[0] if table_definition else 'Non trouvée'}"
                            )

                            # Afficher les colonnes de la table
                            result = await db.execute(
                                text("PRAGMA table_info(compositions)")
                            )
                            columns = result.fetchall()
                            logger.debug("[TEST] Colonnes de la table 'compositions':")
                            if columns:
                                for col in columns:
                                    logger.debug(f"  - {col}")
                            else:
                                logger.debug("  Aucune colonne trouvée")
                    except Exception as e:
                        logger.error(
                            f"[ERROR] Erreur lors de la vérification de la table: {e}"
                        )
                        logger.error(f"[ERROR] Type d'erreur: {type(e).__name__}")
                        logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
                        await savepoint.rollback()
                        raise

                    # Commit the transaction
                    logger.debug("[TEST] Commit des changements...")
                    await db.commit()
                    logger.debug("[TEST] Commit réussi")

                    # Rafraîchir la composition pour s'assurer qu'elle est bien enregistrée
                    logger.debug("Rafraîchissement de la composition...")
                    try:
                        await db.refresh(composition)
                        logger.debug("Composition rafraîchie avec succès")
                        logger.debug(
                            f"Composition après rafraîchissement: {composition}"
                        )
                        logger.debug(
                            f"ID de la composition après rafraîchissement: {getattr(composition, 'id', 'Non défini')}"
                        )
                    except Exception as e:
                        logger.error(f"Erreur lors du rafraîchissement: {e}")
                        logger.error(f"Type d'erreur: {type(e).__name__}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        raise

                    # Vérifier que la composition a été créée
                    logger.debug("Vérification des attributs de la composition...")
                    try:
                        assert composition.id is not None, "La composition n'a pas d'ID"
                        assert (
                            composition.name == "Test Composition"
                        ), f"Le nom de la composition ne correspond pas: {composition.name}"
                        assert (
                            composition.created_by == sample_user.id
                        ), f"L'ID du créateur ne correspond pas: {composition.created_by} vs {sample_user.id}"
                        assert (
                            composition.build_id == sample_build.id
                        ), f"L'ID du build ne correspond pas: {composition.build_id} vs {sample_build.id}"
                        logger.debug("Tous les tests d'assertion ont réussi")
                    except AssertionError as e:
                        logger.error(f"Échec de l'assertion: {e}")
                        logger.debug(f"État de la composition: {composition.__dict__}")
                        # Essayer de récupérer toutes les compositions pour débogage
                        try:
                            result = await db.execute(
                                text("SELECT * FROM compositions")
                            )
                            all_compositions = result.fetchall()
                            logger.debug(
                                f"Compositions dans la base de données: {all_compositions}"
                            )
                        except Exception as query_err:
                            logger.error(
                                f"Erreur lors de la récupération des compositions: {query_err}"
                            )
                        raise

                    # Nettoyer
                    logger.debug("Nettoyage de la base de données...")
                    try:
                        await db.delete(composition)
                        await db.commit()
                        logger.debug("Nettoyage terminé avec succès")
                    except Exception as e:
                        logger.error(f"[ERROR] Erreur lors du nettoyage: {e}")
                        await savepoint.rollback()
                        raise

                except Exception as e:
                    error_msg = f"[ERROR] Erreur lors du commit: {e}\nType: {type(e).__name__}\n{traceback.format_exc()}"
                    logger.error(error_msg)
                    await savepoint.rollback()
                    raise

            except Exception as e:
                error_msg = (
                    f"[ERROR] Erreur lors de la création de la composition: {e}\n"
                    f"Type: {type(e).__name__}\n"
                    f"Traceback: {traceback.format_exc()}"
                )
                logger.error(error_msg)

                # Log de l'état de la session si possible
                try:
                    logger.debug(f"[DEBUG] État de la session (dirty): {db.dirty}")
                    logger.debug(f"[DEBUG] Nouveaux objets dans la session: {db.new}")
                except Exception as session_err:
                    logger.error(
                        f"[ERROR] Impossible de lire l'état de la session: {session_err}"
                    )

                await transaction.rollback()
                raise

        # Section de débogage - à supprimer en production
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("\n=== Débogage des objets de test ===")

            # Informations sur la connexion
            try:
                db_url = (
                    db.bind.url
                    if hasattr(db, "bind") and hasattr(db.bind, "url")
                    else "Non disponible"
                )
                logger.debug(f"[DEBUG] URL de la base de données: {db_url}")

                # Vérification des objets dans la session
                logger.debug("\n[DEBUG] État des objets dans la session:")
                logger.debug(
                    f"- sample_user: {'Présent' if sample_user in db else 'Absent'}"
                )
                logger.debug(
                    f"- sample_build: {'Présent' if sample_build in db else 'Absent'}"
                )

                # Détails des objets
                logger.debug("\n[DEBUG] Détails des objets:")
                logger.debug(
                    f"- sample_user: id={getattr(sample_user, 'id', 'N/A')}, email={getattr(sample_user, 'email', 'N/A')}"
                )
                logger.debug(
                    f"- sample_build: id={getattr(sample_build, 'id', 'N/A')}, name={getattr(sample_build, 'name', 'N/A')}"
                )

            except Exception as debug_err:
                logger.error(f"[ERROR] Erreur lors du débogage: {debug_err}")

        # Vérification des relations si le niveau de log est DEBUG
        if logger.isEnabledFor(logging.DEBUG):
            try:
                logger.debug("\n[DEBUG] Vérification des relations:")

                # Chargement des relations si nécessaire
                await db.refresh(sample_user, ["compositions", "created_compositions"])
                await db.refresh(sample_build, ["compositions"])

                # Log des relations
                logger.debug(
                    f"- Compositions de l'utilisateur: {len(getattr(sample_user, 'compositions', []))} éléments"
                )
                logger.debug(
                    f"- Compositions créées par l'utilisateur: {len(getattr(sample_user, 'created_compositions', []))} éléments"
                )
                logger.debug(
                    f"- Compositions du build: {len(getattr(sample_build, 'compositions', []))} éléments"
                )

            except Exception as e:
                logger.error(
                    f"[ERROR] Erreur lors de la vérification des relations: {e}"
                )

            # Informations supplémentaires sur les types d'objets
            logger.debug("\n[DEBUG] Types des objets:")
            logger.debug(f"- db: {type(db).__name__}")
            logger.debug(f"- sample_user: {type(sample_user).__name__}")
            logger.debug(f"- sample_build: {type(sample_build).__name__}")

            # Vérification des relations chargées
            logger.debug("\n[DEBUG] Vérification des relations chargées:")
            logger.debug(
                f"- Relations de sample_user: {', '.join(k for k, v in sample_user.__dict__.items() if not k.startswith('_') and hasattr(v, '__call__') is False)}"
            )
            logger.debug(
                f"- Relations de sample_build: {', '.join(k for k, v in sample_build.__dict__.items() if not k.startswith('_') and hasattr(v, '__call__') is False)}"
            )

            logger.debug("\n=== Fin des vérifications de débogage ===\n")

        # Vérifier la connexion à la base de données
        print("\n[DEBUG] === Connexion à la base de données ===")
        print(
            f"[DEBUG] URL de la base de données: {db.bind.url if hasattr(db, 'bind') else 'Pas de bind'}"
        )

        # Vérifier si les objets sont dans la session
        print("\n[DEBUG] === Vérification des objets dans la session ===")
        try:
            print(f"[DEBUG] sample_user dans la session: {sample_user in db}")
            print(f"[DEBUG] sample_build dans la session: {sample_build in db}")
        except Exception as e:
            print(
                f"[ERROR] Erreur lors de la vérification des objets dans la session: {e}"
            )

        # Afficher plus d'informations sur les objets
        print("\n[DEBUG] === Détails des objets ===")
        print(f"[DEBUG] sample_user: {sample_user}")
        print(f"[DEBUG] sample_build: {sample_build}")

        # Vérifier les relations
        print("\n[DEBUG] === Vérification des relations ===")
        try:
            print(
                f"[DEBUG] sample_user.compositions: {getattr(sample_user, 'compositions', 'Non chargé')}"
            )
            print(
                f"[DEBUG] sample_user.created_compositions: {getattr(sample_user, 'created_compositions', 'Non chargé')}"
            )
            print(
                f"[DEBUG] sample_build.compositions: {getattr(sample_build, 'compositions', 'Non chargé')}"
            )
        except Exception as e:
            print(f"[ERROR] Erreur lors de la vérification des relations: {e}")

        print("\n[DEBUG] === Fin des informations de débogage ===\n")

        # Afficher les informations de débogage
        print("\n[DEBUG] === Informations de débogage ===")
        print(f"[DEBUG] Type de db: {type(db)}")
        print(f"[DEBUG] Type de sample_user: {type(sample_user)}")
        print(f"[DEBUG] Type de sample_build: {type(sample_build)}")

        # Afficher les IDs
        print("\n[DEBUG] === IDs des objets ===")
        print(f"[DEBUG] Sample user ID: {getattr(sample_user, 'id', 'No ID')}")
        print(f"[DEBUG] Sample build ID: {getattr(sample_build, 'id', 'No ID')}")

        # Vérifier la connexion à la base de données
        print("\n[DEBUG] === Connexion à la base de données ===")
        print(
            f"[DEBUG] URL de la base de données: {db.bind.url if hasattr(db, 'bind') else 'Pas de bind'}"
        )

        # Vérifier si les objets sont dans la session
        print("\n[DEBUG] === Vérification des objets dans la session ===")
        try:
            print(f"[DEBUG] sample_user dans la session: {sample_user in db}")
            print(f"[DEBUG] sample_build dans la session: {sample_build in db}")
        except Exception as e:
            print(
                f"[ERROR] Erreur lors de la vérification des objets dans la session: {e}"
            )

        # Afficher plus d'informations sur les objets
        print("\n[DEBUG] === Détails des objets ===")
        print(f"[DEBUG] sample_user: {sample_user}")
        print(f"[DEBUG] sample_build: {sample_build}")

        # Vérifier les relations
        print("\n[DEBUG] === Vérification des relations ===")
        try:
            print(
                f"[DEBUG] sample_user.compositions: {getattr(sample_user, 'compositions', 'Non chargé')}"
            )
            print(
                f"[DEBUG] sample_user.created_compositions: {getattr(sample_user, 'created_compositions', 'Non chargé')}"
            )
            print(
                f"[DEBUG] sample_build.compositions: {getattr(sample_build, 'compositions', 'Non chargé')}"
            )
        except Exception as e:
            print(f"[ERROR] Erreur lors de la vérification des relations: {e}")

        print("\n[DEBUG] === Fin des informations de débogage ===\n")

        # Generate a unique name for the composition
        unique_name = f"New Test Composition {uuid.uuid4().hex[:8]}"
        print(f"[TEST] Using unique name: {unique_name}")

        # Afficher les attributs de sample_user
        print("\n[DEBUG] === Attributs de sample_user ===")
        for attr in dir(sample_user):
            if not attr.startswith("_"):
                try:
                    print(
                        f"[DEBUG] sample_user.{attr}: {getattr(sample_user, attr, 'N/A')}"
                    )
                except Exception as e:
                    print(f"[DEBUG] Erreur lors de l'accès à sample_user.{attr}: {e}")

        # Afficher les attributs de sample_build
        print("\n[DEBUG] === Attributs de sample_build ===")
        for attr in dir(sample_build):
            if not attr.startswith("_"):
                try:
                    print(
                        f"[DEBUG] sample_build.{attr}: {getattr(sample_build, attr, 'N/A')}"
                    )
                except Exception as e:
                    print(f"[DEBUG] Erreur lors de l'accès à sample_build.{attr}: {e}")

        # Vérifier les clés étrangères
        print("\n[DEBUG] === Vérification des clés étrangères ===")
        print(f"[DEBUG] sample_user.id: {getattr(sample_user, 'id', 'N/A')}")
        print(f"[DEBUG] sample_build.id: {getattr(sample_build, 'id', 'N/A')}")
        print(
            f"[DEBUG] sample_build.created_by_id: {getattr(sample_build, 'created_by_id', 'N/A')}"
        )

        # Arrange
        comp_data = {
            "name": unique_name,
            "description": "A new test composition",
            "squad_size": 15,
            "is_public": True,
            "status": "draft",
            "game_mode": "wvw",
            "created_by": sample_user.id,
            "build_id": sample_build.id,
        }

        print("[TEST] Composition data prepared")
        print(f"[TEST] Sample user ID: {sample_user.id}")
        print(f"[TEST] Sample build ID: {sample_build.id}")

        try:
            # Act - Create composition
            print("[TEST] Creating composition...")
            composition = Composition(**comp_data)
            db.add(composition)
            await db.flush()  # Flush to get the ID without committing

            print(f"[TEST] Composition created with ID: {composition.id}")

            # Verify the composition was created with correct data
            print("[TEST] Verifying composition data...")
            assert composition.id is not None, "Composition ID should not be None"
            assert (
                composition.name == unique_name
            ), f"Expected name '{unique_name}', got '{composition.name}'"
            assert composition.description == "A new test composition"
            assert composition.squad_size == 15
            assert composition.is_public is True
            assert composition.status == "draft"
            assert composition.game_mode == "wvw"
            assert composition.created_by == sample_user.id
            assert composition.build_id == sample_build.id
            assert composition.created_at is not None
            assert composition.updated_at is None  # Not updated yet
            print("[TEST] Composition data verified")

            # Verify relationships
            print("[TEST] Verifying relationships...")

            # Refresh the composition to ensure relationships are loaded
            print("[TEST] Refreshing composition with relationships...")
            # Utiliser selectinload pour charger explicitement les relations
            from sqlalchemy.future import select
            from sqlalchemy.orm import selectinload

            # Requête pour recharger la composition avec les relations
            result = await db.execute(
                select(Composition)
                .options(
                    selectinload(Composition.creator), selectinload(Composition.build)
                )
                .where(Composition.id == composition.id)
            )
            composition = result.scalar_one()

            # Debug relationship attributes
            print(f"[DEBUG] Composition attributes: {dir(composition)}")
            print(
                f"[DEBUG] Composition creator: {getattr(composition, 'creator', 'Not loaded')}"
            )
            print(
                f"[DEBUG] Composition build: {getattr(composition, 'build', 'Not loaded')}"
            )

            # Verify creator relationship
            print("[TEST] Verifying creator relationship...")
            assert hasattr(
                composition, "creator"
            ), "Composition should have 'creator' relationship"
            assert (
                composition.creator is not None
            ), "Composition creator should not be None"
            print(
                f"[DEBUG] Creator ID: {getattr(composition.creator, 'id', 'No ID')}, Expected: {sample_user.id}"
            )
            assert (
                composition.creator.id == sample_user.id
            ), f"Creator ID mismatch: expected {sample_user.id}, got {getattr(composition.creator, 'id', 'No ID')}"

            # Verify build relationship
            print("[TEST] Verifying build relationship...")
            assert hasattr(
                composition, "build"
            ), "Composition should have 'build' relationship"
            assert composition.build is not None, "Composition build should not be None"
            assert (
                composition.build.id == sample_build.id
            ), f"Build ID mismatch: expected {sample_build.id}, got {getattr(composition.build, 'id', 'No ID')}"

            # Verify the composition is in the user's created_compositions
            print("[TEST] Verifying user's created_compositions...")
            # Recharger l'utilisateur avec ses créations
            from sqlalchemy.future import select
            from sqlalchemy.orm import selectinload
            from app.models.user import User

            # Use a fresh query to get the user with their created_compositions
            user_result = await db.execute(
                select(User)
                .options(selectinload(User.created_compositions))
                .where(User.id == sample_user.id)
            )
            user = user_result.scalar_one()

            # Access the relationship attribute directly (it's already loaded by selectinload)
            created_compositions = user.created_compositions
            print(
                f"[DEBUG] User's created_compositions: {[c.id for c in created_compositions]}"
            )

            # Check if the composition is in the list
            composition_found = any(
                c.id == composition.id for c in created_compositions
            )
            assert (
                composition_found
            ), f"Composition {composition.id} not found in user's created_compositions"

            # Verify the composition is in the build's compositions
            print("[TEST] Verifying build's compositions...")
            # Recharger le build avec ses compositions
            from sqlalchemy.future import select
            from sqlalchemy.orm import selectinload
            from app.models.build import Build

            # Use a fresh query to get the build with its compositions
            build_result = await db.execute(
                select(Build)
                .options(selectinload(Build.compositions))
                .where(Build.id == sample_build.id)
            )
            build = build_result.scalar_one()

            # Access the relationship attribute directly (it's already loaded by selectinload)
            build_compositions = build.compositions
            print(f"[DEBUG] Build's compositions: {[c.id for c in build_compositions]}")

            # Check if the composition is in the list
            composition_in_build = any(
                c.id == composition.id for c in build_compositions
            )
            assert (
                composition_in_build
            ), f"Composition {composition.id} not found in build's compositions"

            # Commit if all assertions pass
            print("[TEST] All assertions passed, committing transaction...")
            await db.commit()
            print("[TEST] Transaction committed successfully")

        except Exception as e:
            # Rollback on error
            print(f"\n[ERROR] Test failed: {str(e)}")
            await db.rollback()
            raise

        finally:
            # Clean up: Delete the composition if it was created
            if "composition" in locals() and hasattr(composition, "id"):
                try:
                    print(f"[CLEANUP] Deleting test composition {composition.id}...")
                    await db.delete(composition)
                    await db.commit()
                    print("[CLEANUP] Composition deleted successfully")
                except Exception as e:
                    print(f"[WARNING] Failed to clean up composition: {e}")
                    await db.rollback()

        print("=== test_composition_creation completed ===\n")

    @pytest.mark.asyncio
    async def test_composition_relationships(
        self,
        db: AsyncSession,
        sample_composition,
        sample_user: User,
        sample_build: Build,
    ) -> None:
        """
        Test relationships with User and Build models.

        This test verifies that all relationships between Composition, User and Build
        models are properly established and can be navigated in both directions.
        """
        logger.info("\n=== Starting test_composition_relationships ===")

        # Start a transaction with savepoint for this test
        async with db.begin() as transaction:
            try:
                # Log test data for debugging
                logger.debug(
                    f"[TEST] Sample user ID: {getattr(sample_user, 'id', 'No ID')}"
                )
                logger.debug(
                    f"[TEST] Sample build ID: {getattr(sample_build, 'id', 'No ID')}"
                )
                logger.debug(
                    f"[TEST] Sample composition ID: {getattr(sample_composition, 'id', 'No ID')}"
                )

                # Refresh the user and build to ensure relationships are loaded
                logger.debug("[TEST] Refreshing sample_user and sample_build")
                await db.refresh(sample_user, ["created_compositions"])
                await db.refresh(sample_build, ["compositions"])

                # Test relationship with User
                logger.debug("[TEST] Testing User relationship")
                assert (
                    sample_composition.creator_id == sample_user.id
                ), f"Creator ID {sample_composition.creator_id} does not match user ID {sample_user.id}"
                assert (
                    sample_composition in sample_user.created_compositions
                ), "Composition not found in user's created_compositions"

                # Test relationship with Build
                logger.debug("[TEST] Testing Build relationship")
                assert (
                    sample_composition.build_id == sample_build.id
                ), f"Build ID {sample_composition.build_id} does not match expected {sample_build.id}"
                assert (
                    sample_composition in sample_build.compositions
                ), "Composition not found in build's compositions"

                # Test backref from User to Compositions with explicit loading
                from sqlalchemy.future import select
                from sqlalchemy.orm import selectinload
                from app.models.user import User

                # Load user with created_compositions using selectinload
                logger.debug("[TEST] Loading user with created_compositions")
                result = await db.execute(
                    select(User)
                    .options(selectinload(User.created_compositions))
                    .where(User.id == sample_user.id)
                )
                user = result.scalar_one_or_none()
                assert user is not None, "User not found in database"
                assert (
                    sample_composition in user.created_compositions
                ), "Composition not found in user's created_compositions (explicit load)"

                # Load build with compositions using selectinload
                from app.models.build import Build

                logger.debug("[TEST] Loading build with compositions")
                result = await db.execute(
                    select(Build)
                    .options(selectinload(Build.compositions))
                    .filter(Build.id == sample_build.id)
                )
                build = result.scalar_one_or_none()
                assert build is not None, "Build not found in database"
                assert (
                    sample_composition in build.compositions
                ), "Composition not found in build's compositions (explicit load)"

                logger.info("[SUCCESS] All relationship tests passed")

            except Exception as e:
                logger.error(f"[ERROR] Test failed: {str(e)}")
                await transaction.rollback()
                raise
            else:
                # Rollback the transaction to undo any changes
                await transaction.rollback()
                logger.info("[CLEANUP] Transaction rolled back")

    @pytest.mark.asyncio
    async def test_composition_members(
        self,
        db: AsyncSession,
        sample_composition,
        sample_user: User,
        sample_role,
        sample_profession,
    ) -> None:
        """
        Test adding members to a composition.

        This test verifies that members can be added to a composition and that
        all relationships are properly established.
        """
        logger.info("\n=== Starting test_composition_members ===")

        # Start a transaction with savepoint for this test
        async with db.begin() as transaction:
            try:
                from app.models import Composition
                from app.models.association_tables import composition_members
                from sqlalchemy.future import select
                from sqlalchemy.orm import selectinload

                # Log test data for debugging
                logger.debug(
                    f"[TEST] Sample user ID: {getattr(sample_user, 'id', 'No ID')}"
                )
                logger.debug(
                    f"[TEST] Sample composition ID: {getattr(sample_composition, 'id', 'No ID')}"
                )
                logger.debug(
                    f"[TEST] Sample role ID: {getattr(sample_role, 'id', 'No ID')}"
                )
                logger.debug(
                    f"[TEST] Sample profession ID: {getattr(sample_profession, 'id', 'No ID')}"
                )

                # Add member to composition
                logger.debug("[TEST] Adding member to composition")
                stmt = composition_members.insert().values(
                    composition_id=sample_composition.id,
                    user_id=sample_user.id,
                    role_id=sample_role.id,
                    profession_id=sample_profession.id,
                    notes="Test member",
                )
                await db.execute(stmt)

                # Load the composition with members using a fresh query with explicit loading
                logger.debug("[TEST] Loading composition with members")
                result = await db.execute(
                    select(Composition)
                    .options(
                        selectinload(Composition.members).selectinload("user"),
                        selectinload(Composition.members).selectinload("role"),
                        selectinload(Composition.members).selectinload("profession"),
                    )
                    .filter(Composition.id == sample_composition.id)
                )
                composition = result.scalar_one_or_none()
                assert composition is not None, "La composition n'a pas été trouvée"

                # Test the relationship
                logger.debug("[TEST] Verifying member relationships")
                assert (
                    len(composition.members) == 1
                ), "Le nombre de membres ne correspond pas"

                member = composition.members[0]
                assert member.user_id == sample_user.id, "User ID mismatch"
                assert member.role_id == sample_role.id, "Role ID mismatch"
                assert (
                    member.profession_id == sample_profession.id
                ), "Profession ID mismatch"

                # Vérifier que l'utilisateur est bien associé à la composition
                logger.debug("[TEST] Verifying user composition association")
                assert sample_composition.id in [
                    c.id for c in member.user.compositions
                ], "Composition not found in user's compositions"

                logger.info("[SUCCESS] All member tests passed")

            except Exception as e:
                logger.error(f"[ERROR] Test failed: {str(e)}")
                await transaction.rollback()
                raise
            else:
                # Rollback the transaction to undo any changes
                await transaction.rollback()
                logger.info("[CLEANUP] Transaction rolled back")

    @pytest.mark.asyncio
    async def test_composition_tags(self, db_session, sample_composition):
        """Test adding tags to a composition."""

        # Create a tag
        tag = Tag(name="Test Tag", description="A test tag", category="test")
        db_session.add(tag)
        await db_session.commit()
        await db_session.refresh(tag)

        # Create the association
        comp_tag = CompositionTag(composition_id=sample_composition.id, tag_id=tag.id)
        db_session.add(comp_tag)
        await db_session.commit()

        # Load the composition with tags using a fresh query
        from sqlalchemy.orm import selectinload
        from sqlalchemy.future import select

        result = await db_session.execute(
            select(Composition)
            .options(
                selectinload(Composition.composition_tags).selectinload(
                    CompositionTag.tag
                )
            )
            .filter(Composition.id == sample_composition.id)
        )
        composition = result.scalar_one_or_none()
        assert composition is not None, "La composition n'a pas été trouvée"

        # Test the relationship
        assert (
            len(composition.composition_tags) == 1
        ), "Le nombre de tags ne correspond pas"
        assert composition.composition_tags[0].tag.name == "Test Tag"

        # Test the tag details
        tag = composition.composition_tags[0].tag
        assert tag.description == "A test tag"
        assert tag.category == "test"

    @pytest.mark.asyncio
    async def test_composition_validation(
        self, db_session: AsyncSession, sample_user: User, sample_build: Build
    ):
        """Test field validations and constraints."""
        from sqlalchemy.exc import IntegrityError
        from app.models.composition import Composition

        # Test missing required fields
        async with db_session.begin_nested():
            with pytest.raises(IntegrityError):
                composition = Composition()  # Missing required fields
                db_session.add(composition)
                await db_session.flush()
        await db_session.rollback()

        # Test invalid squad size (0) - Python validation
        with pytest.raises(ValueError, match="squad_size must be greater than 0"):
            composition = Composition(
                name=f"Invalid Squad Size {uuid.uuid4().hex[:8]}",
                description="A composition with invalid squad size",
                squad_size=0,  # Must be > 0
                created_by=sample_user.id,
                build_id=sample_build.id,
            )

        # Test invalid status - Python validation
        with pytest.raises(ValueError, match="Invalid status"):
            composition = Composition(
                name=f"Invalid Status {uuid.uuid4().hex[:8]}",
                description="A composition with invalid status",
                squad_size=5,
                status="invalid_status",  # Invalid status
                created_by=sample_user.id,
                build_id=sample_build.id,
            )

        # Test invalid game mode - Python validation
        with pytest.raises(ValueError, match="Invalid game_mode"):
            composition = Composition(
                name=f"Invalid Game Mode {uuid.uuid4().hex[:8]}",
                description="A composition with invalid game mode",
                squad_size=5,
                game_mode="invalid_mode",  # Invalid game mode
                created_by=sample_user.id,
                build_id=sample_build.id,
            )

        # Test missing required fields
        async with db_session.begin_nested():
            with pytest.raises((IntegrityError, ValueError)) as exc_info:
                composition = Composition(
                    name=None,  # Required field
                    created_by=sample_user.id,
                    build_id=sample_build.id,
                    squad_size=5,  # Add required field to avoid other validation errors
                )
                db_session.add(composition)
                await db_session.flush()

            # Check if the exception is due to the null name
            if isinstance(exc_info.value, IntegrityError):
                assert "NOT NULL constraint failed" in str(exc_info.value)

        await db_session.rollback()

        # Test valid status values
        for comp_status in ["draft", "published", "archived"]:
            async with db_session.begin():
                composition = Composition(
                    name=f"Test Status {comp_status} {uuid.uuid4().hex[:8]}",
                    squad_size=5,
                    status=comp_status,
                    created_by=sample_user.id,
                    build_id=sample_build.id,
                )
                db_session.add(composition)
                await db_session.flush()
                assert composition.status == comp_status
                await db_session.delete(composition)

        # Test valid game modes
        for game_mode in ["wvw", "pve", "pvp"]:
            async with db_session.begin():
                composition = Composition(
                    name=f"Test Game Mode {game_mode} {uuid.uuid4().hex[:8]}",
                    squad_size=5,
                    game_mode=game_mode,
                    created_by=sample_user.id,
                    build_id=sample_build.id,
                )
                db_session.add(composition)
                await db_session.flush()
                assert composition.game_mode == game_mode
                await db_session.delete(composition)

        # Test unique constraint on name
        unique_name = f"Unique Test {uuid.uuid4().hex[:8]}"

        # Create first composition with unique name
        async with db_session.begin():
            comp1 = Composition(
                name=unique_name,
                created_by=sample_user.id,
                build_id=sample_build.id,
                squad_size=5,  # Add required field
            )
            db_session.add(comp1)

        # Try to create second composition with same name
        async with db_session.begin_nested():
            with pytest.raises(IntegrityError) as exc_info:
                comp2 = Composition(
                    name=unique_name,  # Same name
                    created_by=sample_user.id,
                    build_id=sample_build.id,
                    squad_size=5,  # Add required field
                )
                db_session.add(comp2)
                await db_session.flush()

            assert "UNIQUE constraint failed" in str(exc_info.value)

        # Clean up
        async with db_session.begin():
            await db_session.delete(comp1)

    @pytest.mark.asyncio
    async def test_composition_default_values(
        self, db_session, sample_user, sample_build
    ):
        """Test default values for Composition model."""
        # Test with minimal required fields
        composition = Composition(
            name="Test Default Values",
            created_by=sample_user.id,
            build_id=sample_build.id,
        )

        # Verify default values
        assert composition.squad_size == 10, "Default squad_size should be 10"
        assert composition.is_public is True, "Default is_public should be True"
        assert composition.status == "draft", "Default status should be 'draft'"
        assert composition.game_mode == "wvw", "Default game_mode should be 'wvw'"
        assert composition.description is None, "Default description should be None"
        assert composition.team_id is None, "Default team_id should be None"
        assert (
            composition.created_at is not None
        ), "created_at should be set automatically"
        assert composition.updated_at is None, "updated_at should be None initially"

        # Test with all fields provided
        now = datetime.utcnow()
        composition2 = Composition(
            name="Test All Fields",
            description="A test description",
            squad_size=15,
            is_public=False,
            status="published",
            game_mode="pve",
            created_by=sample_user.id,
            build_id=sample_build.id,
            created_at=now,
            updated_at=now,
        )

        # Verify all fields are set correctly
        assert composition2.name == "Test All Fields"
        assert composition2.description == "A test description"
        assert composition2.squad_size == 15
        assert composition2.is_public is False
        assert composition2.status == "published"
        assert composition2.game_mode == "pve"
        assert composition2.created_at == now
        assert composition2.updated_at == now

    @pytest.mark.asyncio
    async def test_composition_to_dict(self, db_session, sample_composition):
        """Test the to_dict method of Composition model."""
        # Test with a sample composition
        composition_dict = sample_composition.to_dict()

        # Verify the dictionary structure and values
        assert isinstance(
            composition_dict, dict
        ), "to_dict() should return a dictionary"
        assert composition_dict["id"] == sample_composition.id, "ID should match"
        assert composition_dict["name"] == sample_composition.name, "Name should match"
        assert (
            composition_dict["description"] == sample_composition.description
        ), "Description should match"
        assert (
            composition_dict["squad_size"] == sample_composition.squad_size
        ), "Squad size should match"
        assert (
            composition_dict["is_public"] == sample_composition.is_public
        ), "is_public should match"
        assert (
            composition_dict["status"] == sample_composition.status
        ), "Status should match"
        assert (
            composition_dict["game_mode"] == sample_composition.game_mode
        ), "Game mode should match"
        assert (
            composition_dict["created_by"] == sample_composition.created_by
        ), "Created by should match"
        assert (
            composition_dict["build_id"] == sample_composition.build_id
        ), "Build ID should match"

        # Test datetime fields
        assert "created_at" in composition_dict, "created_at should be in the dict"
        assert "updated_at" in composition_dict, "updated_at should be in the dict"

        # Test with None values
        sample_composition.description = None
        sample_composition.build_id = None
        composition_dict = sample_composition.to_dict()
        assert (
            composition_dict["description"] is None
        ), "None description should be preserved"
        assert composition_dict["build_id"] is None, "None build_id should be preserved"

        # Test with related objects
        from sqlalchemy.orm import selectinload
        from sqlalchemy.future import select

        # Load composition with relationships
        result = await db_session.execute(
            select(Composition)
            .options(selectinload(Composition.creator), selectinload(Composition.build))
            .filter(Composition.id == sample_composition.id)
        )
        composition = result.scalar_one_or_none()
        assert composition is not None, "La composition n'a pas été trouvée"

        # Test to_dict with include_relationships=True
        composition_dict = composition.to_dict(include_relationships=True)

        # Check if relationships are included
        assert "creator" in composition_dict, "Creator should be included in the dict"
        assert "build" in composition_dict, "Build should be included in the dict"
        assert isinstance(composition_dict["creator"], dict), "Creator should be a dict"
        assert isinstance(composition_dict["build"], dict), "Build should be a dict"

        # Test with specific fields only
        composition_dict = composition.to_dict(fields=["id", "name", "status"])
        assert set(composition_dict.keys()) == {
            "id",
            "name",
            "status",
        }, "Only specified fields should be included"
        assert composition_dict["id"] == composition.id
        assert composition_dict["name"] == composition.name
        assert composition_dict["status"] == composition.status

    @pytest.mark.asyncio
    async def test_composition_update_timestamp(self, db, sample_composition):
        """Test that updated_at is set when composition is modified."""
        # Get the initial timestamps
        initial_created_at = sample_composition.created_at
        initial_updated_at = sample_composition.updated_at

        # Make a small delay to ensure the timestamps would be different
        import asyncio

        await asyncio.sleep(0.1)

        # Test update with direct attribute change
        sample_composition.name = "Updated Name"
        db.add(sample_composition)
        await db.commit()
        await db.refresh(sample_composition)

        # Verify the timestamps after first update
        assert (
            sample_composition.updated_at is not None
        ), "updated_at should be set after update"
        assert (
            sample_composition.updated_at > initial_updated_at
        ), "updated_at timestamp should be updated when composition is modified"
        assert (
            sample_composition.created_at == initial_created_at
        ), "created_at timestamp should not change when composition is updated"

        # Store the updated timestamp
        first_updated_at = sample_composition.updated_at

        # Make another small delay
        await asyncio.sleep(0.1)

        # Test update with another change
        sample_composition.description = "Updated description"
        db.add(sample_composition)
        await db.commit()
        await db.refresh(sample_composition)

        # Verify the timestamps after second update
        assert (
            sample_composition.updated_at > first_updated_at
        ), "updated_at should be updated on each modification"

        # Test that saving without changes doesn't update the timestamp
        previous_updated_at = sample_composition.updated_at
        sample_composition.updated_at = (
            previous_updated_at  # Explicitly set to test if it changes
        )
        db.add(sample_composition)
        await db.commit()
        await db.refresh(sample_composition)

        assert (
            sample_composition.updated_at == previous_updated_at
        ), "updated_at should not change if no actual changes were made"

    @pytest.mark.asyncio
    async def test_composition_relationships_details(
        self, db, sample_composition, sample_user, sample_build
    ):
        """Test relationships with related models."""
        # Test creator relationship
        assert sample_composition.creator.id == sample_user.id
        assert sample_composition in sample_composition.creator.compositions

        # Test build relationship
        assert sample_composition.build.id == sample_build.id
        assert sample_composition in sample_composition.build.compositions

        # Test team relationship (when team is set)
        assert sample_composition.team is None  # No team by default

        # Test composition_tags relationship
        assert len(sample_composition.composition_tags) == 0  # No tags by default


class TestCompositionCRUD:
    """Test CRUD operations for the Composition model."""

    def test_create_composition(self, db, sample_user, sample_build):
        """Test creating a new composition."""
        from app.crud.composition import create_composition

        # Prepare data
        comp_data = {
            **TEST_COMPOSITION_DATA,
            "build_id": sample_build.id,
            "user_id": sample_user.id,
        }

        # Act
        composition = create_composition(db, comp_data)

        # Assert
        assert composition.id is not None
        assert composition.name == TEST_COMPOSITION_DATA["name"]
        assert composition.created_by == sample_user.id
        assert composition.build_id == sample_build.id

    def test_get_composition(self, db, sample_composition):
        """Test retrieving a composition by ID."""
        from app.crud.composition import get_composition

        # Act
        result = get_composition(db, composition_id=sample_composition.id)

        # Assert
        assert result is not None
        assert result.id == sample_composition.id
        assert result.name == sample_composition.name

    def test_update_composition(self, db, sample_composition):
        """Test updating a composition."""
        from app.crud.composition import update_composition

        # Prepare update data
        update_data = {
            "name": "Updated Composition",
            "is_public": True,
            "description": "Updated description",
        }

        # Act
        updated_comp = update_composition(
            db, composition_id=sample_composition.id, composition_data=update_data
        )

        # Assert
        assert updated_comp.name == "Updated Composition"
        assert updated_comp.is_public is True
        assert updated_comp.description == "Updated description"
        assert updated_comp.updated_at is not None

    def test_delete_composition(self, db, sample_composition):
        """Test deleting a composition."""
        from app.crud.composition import delete_composition, get_composition

        # Act
        deleted = delete_composition(db, composition_id=sample_composition.id)

        # Assert
        assert deleted is True
        assert get_composition(db, composition_id=sample_composition.id) is None

    def test_composition_search(self, db, sample_composition, sample_user):
        """Test searching for compositions."""
        from app.crud.composition import search_compositions

        # Create a public composition
        public_comp = Composition(
            name="Public Test Composition",
            is_public=True,
            created_by=sample_user.id,
            build_id=sample_composition.build_id,
        )
        db.add(public_comp)
        db.commit()

        # Test search by name
        results = search_compositions(db, name="Test")
        assert len(results) >= 1

        # Test search by is_public
        results = search_compositions(db, is_public=True)
        assert len(results) == 1
        assert results[0].id == public_comp.id

        # Test search by creator
        results = search_compositions(db, created_by=sample_user.id)
        assert len(results) >= 2


class TestCompositionEdgeCases:
    """Test edge cases and error conditions for Composition operations."""

    def test_create_composition_nonexistent_build(self, db, sample_user):
        """Test creating a composition with a non-existent build."""
        from app.crud.composition import create_composition

        # Prepare data with non-existent build ID
        comp_data = {
            **TEST_COMPOSITION_DATA,
            "build_id": 999,  # Non-existent
            "user_id": sample_user.id,
        }

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            create_composition(db, comp_data)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_update_nonexistent_composition(self, db):
        """Test updating a non-existent composition."""
        from app.crud.composition import update_composition

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            update_composition(
                db, composition_id=999, composition_data={"name": "New Name"}
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_composition(self, db):
        """Test deleting a non-existent composition."""
        from app.crud.composition import delete_composition

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_composition(db, composition_id=999)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_composition_permissions(self, db, sample_composition):
        """Test composition ownership and permissions."""
        from app.crud.composition import update_composition, delete_composition

        # Create a different user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password",
        )
        db.add(other_user)
        db.commit()

        # Test updating someone else's composition
        with pytest.raises(HTTPException) as exc_info:
            update_composition(
                db,
                composition_id=sample_composition.id,
                composition_data={"name": "Hacked"},
                user_id=other_user.id,
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

        # Test deleting someone else's composition
        with pytest.raises(HTTPException) as exc_info:
            delete_composition(
                db, composition_id=sample_composition.id, user_id=other_user.id
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_composition_member_management(
        self, db, sample_composition, sample_user, sample_role, sample_profession
    ):
        """Test adding and removing members from a composition."""
        from app.crud.composition import (
            add_composition_member,
            remove_composition_member,
            get_composition_members,
        )

        # Test adding a member
        add_composition_member(
            db,
            composition_id=sample_composition.id,
            user_id=sample_user.id,
            role_id=sample_role.id,
            profession_id=sample_profession.id,
            notes="Test member",
        )

        # Verify the member was added
        members = get_composition_members(db, composition_id=sample_composition.id)
        assert len(members) == 1
        assert members[0].id == sample_user.id

        # Test removing the member
        remove_composition_member(
            db, composition_id=sample_composition.id, user_id=sample_user.id
        )

        # Verify the member was removed
        members = get_composition_members(db, composition_id=sample_composition.id)
        assert len(members) == 0

    @pytest.mark.asyncio
    async def test_composition_tag_management(self, async_db, sample_composition_async):
        """
        Test adding and removing tags from a composition.

        This test verifies that:
        1. Tags can be created and associated with a composition
        2. The association is properly reflected in the database
        3. Tags can be removed from a composition
        4. All operations are properly rolled back in case of errors
        """
        import logging
        import uuid
        from sqlalchemy import select, inspect
        from sqlalchemy.exc import SQLAlchemyError
        from app.models.composition_tag import CompositionTag
        from app.models.composition import Composition

        # Configure logging
        logger = logging.getLogger(__name__)

        # Start a transaction for this test
        async with async_db.begin() as transaction:
            try:
                logger.info("\n=== Starting test_composition_tag_management ===")

                # Verify database connection
                logger.debug(f"[TEST] Database URL: {async_db.bind.url}")

                # Check and create necessary tables if they don't exist
                inspector = inspect(async_db.bind)
                tables = inspector.get_table_names()
                logger.debug(f"[DEBUG] Tables in database: {tables}")

                # Ensure required tables exist
                from app.models.base import Base

                if "tags" not in tables:
                    logger.warning("[WARN] Table 'tags' not found, creating...")
                    Base.metadata.create_all(bind=async_db.bind, tables=[Tag.__table__])
                    logger.info("[INFO] Table 'tags' created")

                if "composition_tags" not in tables:
                    logger.warning(
                        "[WARN] Table 'composition_tags' not found, creating..."
                    )
                    Base.metadata.create_all(
                        bind=async_db.bind, tables=[CompositionTag.__table__]
                    )
                    logger.info("[INFO] Table 'composition_tags' created")

                # Verify the test composition exists
                result = await async_db.execute(
                    select(Composition).where(
                        Composition.id == sample_composition_async.id
                    )
                )
                db_comp = result.scalar_one_or_none()
                assert db_comp is not None, "Test composition not found in database"

                # Create a test tag with a unique name
                tag_name = f"TestTag_{uuid.uuid4().hex[:8]}"
                tag = Tag(name=tag_name, description="A test tag for composition")
                logger.debug(f"[TEST] Creating tag: {tag}")

                try:
                    async_db.add(tag)
                    await async_db.flush()
                    logger.debug("[TEST] Tag created successfully")
                except SQLAlchemyError as e:
                    await transaction.rollback()
                    logger.error(f"[ERROR] Failed to create tag: {e}")
                    raise

                # Test tag creation
                result = await async_db.execute(select(Tag).where(Tag.id == tag.id))
                db_tag = result.scalar_one_or_none()
                assert db_tag is not None, "Tag was not created in the database"

                # Create tag association
                logger.debug("[TEST] Creating tag association...")

                # Check for existing association
                existing_assoc = await async_db.execute(
                    select(CompositionTag)
                    .where(CompositionTag.composition_id == sample_composition_async.id)
                    .where(CompositionTag.tag_id == tag.id)
                )
                existing_assoc = existing_assoc.scalars().first()

                if existing_assoc:
                    logger.warning("[WARN] Tag association already exists")
                    comp_tag = existing_assoc
                else:
                    comp_tag = CompositionTag(
                        composition_id=sample_composition_async.id, tag_id=tag.id
                    )

                    try:
                        async_db.add(comp_tag)
                        await async_db.flush()
                        logger.debug("[TEST] Tag association created successfully")
                    except SQLAlchemyError as e:
                        await transaction.rollback()
                        logger.error(f"[ERROR] Failed to create tag association: {e}")
                        raise

                # Verify the association
                result = await async_db.execute(
                    select(CompositionTag)
                    .where(CompositionTag.composition_id == sample_composition_async.id)
                    .where(CompositionTag.tag_id == tag.id)
                )
                association = result.scalar_one_or_none()
                assert association is not None, "Tag association not found in database"

                # Refresh and verify the relationship
                await async_db.refresh(
                    sample_composition_async,
                    ["composition_tags", "composition_tags.tag"],
                )
                assert (
                    len(sample_composition_async.composition_tags) == 1
                ), f"Expected 1 tag, got {len(sample_composition_async.composition_tags)}"

                # Test tag removal
                logger.debug("[TEST] Removing tag association...")
                await async_db.delete(comp_tag)
                await async_db.flush()

                # Verify removal
                result = await async_db.execute(
                    select(CompositionTag)
                    .where(CompositionTag.composition_id == sample_composition_async.id)
                    .where(CompositionTag.tag_id == tag.id)
                )
                assert (
                    result.scalar_one_or_none() is None
                ), "Tag association was not removed"

                # Refresh and verify the relationship is gone
                await async_db.refresh(sample_composition_async, ["composition_tags"])
                assert (
                    len(sample_composition_async.composition_tags) == 0
                ), "Composition should have no tags after removal"

                logger.info("[SUCCESS] All tag management tests passed")

            except Exception as e:
                logger.error(f"[ERROR] Test failed: {e}")
                await transaction.rollback()
                raise
            else:
                # Rollback the transaction to undo all changes
                await transaction.rollback()
                logger.debug("[CLEANUP] Transaction rolled back")
