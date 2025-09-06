"""Tests for build CRUD operations."""
import logging
import sys
import json
import traceback
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker, joinedload
from typing import Dict, Any, List, Generator
from app.api.deps import get_db as deps_get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Import settings and database configuration
from app.core.config import settings
from app.db.session import engine, get_db
from app.db.base import Base

# Import models to ensure they are registered with SQLAlchemy
from app.models import (
    Build,
    BuildProfession,
    Profession,
    EliteSpecialization,
    Composition
)

# Import CRUD operations
from app.crud.build import build as build_crud

# Import test utilities
from tests.integration.fixtures.factories import (
    BuildFactory, 
    UserFactory, 
    ProfessionFactory,
    EliteSpecializationFactory
)

# Import other utilities
import json
import traceback
from typing import Optional

# Import settings
from app.core.config import settings

# Create a new test database session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    from sqlalchemy import event
    
    # Create all tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Begin a nested transaction
    nested = connection.begin_nested()
    
    # If the application code calls commit, it will end the nested transaction
    # So we need to start a new one
    @event.listens_for(session, 'after_transaction_end')
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()
    
    logger.info("Database session created")
    
    # Yield the session for testing
    yield session
    
    # Cleanup
    logger.info("Cleaning up database...")
    session.close()
    transaction.rollback()
    connection.close()
    logger.info("Database cleanup complete")


def test_create_build(client: TestClient, db: Session) -> None:
    """Test creating a new build with associated professions."""
        except Exception as e:
            logger.error(f"Failed to parse response as JSON: {e}")
            logger.error(f"Response content: {response.text}")
            raise
        
        # Log the complete response for debugging
        logger.info("=== Response Data ===")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers)}")
        logger.info(f"Response Body: {json.dumps(response_data, indent=2)}")
        
        # Log the structure of the response data
        logger.info("=== Response Data Structure ===")
        logger.info(f"Keys in response: {list(response_data.keys())}")
        
        # Log all build data from the database for debugging
        # Make sure we're not in a transaction when starting a new one
        if db.in_transaction():
            db.rollback()
            
        # Use a new transaction for verification
        db.begin()
        try:
            all_builds = db.query(Build).all()
            logger.info(f"Found {len(all_builds)} builds in database")
            
            # Log details for each build
            for i, b in enumerate(all_builds, 1):
                logger.info(f"Build {i}: id={b.id}, name='{b.name}', created_by_id={b.created_by_id}")
                
                # Get build-profession associations
                build_profs = db.query(BuildProfession).filter_by(build_id=b.id).all()
                logger.info(f"  - Has {len(build_profs)} profession associations")
                
                # Log each build-profession association
                for bp in build_profs:
                    logger.info(f"    - BuildProfession: build_id={bp.build_id}, profession_id={bp.profession_id}")
                    if hasattr(bp, 'profession'):
                        logger.info(f"      - Profession: id={bp.profession.id}, name='{bp.profession.name}'")
                
                # Log associated professions if available
                if hasattr(b, 'professions'):
                    logger.info(f"  - Has {len(b.professions)} professions")
                    
    except Exception as e:
        logger.error(f"Error querying database: {e}")
        raise
    finally:
        # Always rollback the transaction to clean up
        if db.in_transaction():
            db.rollback()
    
    # Verify required fields are present
    required_fields = ['id', 'name', 'description', 'game_mode', 'team_size', 
                     'is_public', 'created_by_id', 'created_at', 'updated_at',
                     'professions']
    
    for field in required_fields:
        assert field in response_data, f"Missing required field in response: {field}"
        logger.info(f"{field}: {response_data.get(field)}")
    
    # Verify the build data matches the request
    assert response_data['name'] == build_data['name']
    assert response_data['description'] == build_data['description']
    assert response_data['game_mode'] == build_data['game_mode']
    assert response_data['team_size'] == build_data['team_size']
    assert response_data['is_public'] == build_data['is_public']
    
    # Log the user IDs for debugging
    logger.info(f"Response created_by_id: {response_data['created_by_id']}")
    logger.info(f"Test user ID: {test_user.id}")
    
    # Verify profession associations
    assert 'professions' in response_data, "Response is missing 'professions' field"
    
    # Log profession details
    logger.info(f"Expected profession IDs: {profession_ids}")
    logger.info(f"Professions in response: {response_data.get('professions', [])}")
    
    # Extract profession IDs from the response
    response_profession_ids = [prof['id'] for prof in response_data.get('professions', [])]
    logger.info(f"Profession IDs in response: {response_profession_ids}")
    # Check if professions is a list
    assert isinstance(response_data['professions'], list), "'professions' should be a list"
    
    # Verify the number of professions matches
    assert len(response_data['professions']) == len(profession_ids), \
        f"Expected {len(profession_ids)} professions, got {len(response_data['professions'])}"
    
    # Verify the profession IDs in the response
    response_prof_ids = [prof['id'] for prof in response_data['professions']]
    assert set(response_prof_ids) == set(profession_ids), \
        f"Expected profession IDs {set(profession_ids)}, got {set(response_prof_ids)}"
    
    # Log the build ID for further debugging
    build_id = response_data['id']
    logger.info(f"Created build with ID: {build_id}")
    
    # Verify the build was saved to the database with the correct associations
    try:
        # Use the existing transaction
        db.expire_all()  # Expire all objects to ensure we get fresh data
        
        # Log the current transaction state
        logger.info(f"\n=== Transaction State ===")
        logger.info(f"In transaction: {db.in_transaction()}")
        logger.info(f"Is active: {db.is_active}")
        required_fields = ['id', 'name', 'description', 'game_mode', 'team_size', 
                         'is_public', 'created_by_id', 'created_at', 'updated_at',
                         'professions']
        
        for field in required_fields:
            assert field in response_data, f"Missing required field in response: {field}"
            logger.info(f"{field}: {response_data.get(field)}")
        
        # Verify the build data matches the request
        assert response_data['name'] == build_data['name']
        assert response_data['description'] == build_data['description']
        assert response_data['game_mode'] == build_data['game_mode']
        assert response_data['team_size'] == build_data['team_size']
        assert response_data['is_public'] == build_data['is_public']
        
        # Log the user IDs for debugging
        logger.info(f"Response created_by_id: {response_data['created_by_id']}")
        logger.info(f"Test user ID: {test_user.id}")
        
        # Verify profession associations
        assert 'professions' in response_data, "Response is missing 'professions' field"
        
        # Log profession details
        logger.info(f"Expected profession IDs: {profession_ids}")
        logger.info(f"Professions in response: {response_data.get('professions', [])}")
        
        # Extract profession IDs from the response
        response_profession_ids = [prof['id'] for prof in response_data.get('professions', [])]
        logger.info(f"Profession IDs in response: {response_profession_ids}")
        # Check if professions is a list
        assert isinstance(response_data['professions'], list), "'professions' should be a list"
        
        # Verify the number of professions matches
        assert len(response_data['professions']) == len(profession_ids), \
            f"Expected {len(profession_ids)} professions, got {len(response_data['professions'])}"
        
        # Verify the profession IDs in the response
        response_prof_ids = [prof['id'] for prof in response_data['professions']]
        assert set(response_prof_ids) == set(profession_ids), \
            f"Expected profession IDs {set(profession_ids)}, got {set(response_prof_ids)}"
        
        # Log the build ID for further debugging
        build_id = response_data['id']
        logger.info(f"Created build with ID: {build_id}")
        
        # Verify the build was saved to the database with the correct associations
        try:
            # Use the existing transaction
            db.expire_all()  # Expire all objects to ensure we get fresh data
            
            # Log the current transaction state
            logger.info(f"\n=== Transaction State ===")
            logger.info(f"In transaction: {db.in_transaction()}")
            logger.info(f"Is active: {db.is_active}")
            
            # Log all builds in the database
            all_builds = db.query(Build).all()
            logger.info(f"\n=== All Builds in Database ({len(all_builds)}) ===")
            for b in all_builds:
                logger.info(f"Build {b.id}: {b.name} (created by {b.created_by_id})")
                
            # Log all build-profession associations
            all_build_profs = db.query(BuildProfession).all()
            logger.info(f"\n=== All Build-Profession Associations ({len(all_build_profs)}) ===")
            for bp in all_build_profs:
                logger.info(f"Build {bp.build_id} <-> Profession {bp.profession_id}")
                
            # Log all professions
            all_professions = db.query(Profession).all()
            logger.info(f"\n=== All Professions ({len(all_professions)}) ===")
            for p in all_professions:
                logger.info(f"Profession {p.id}: {p.name}")
            
            # Verify the build exists in the database
            db_build = db.query(Build).filter_by(id=build_id).first()
            logger.info(f"Build from database: {db_build}")
            
            # If build is not found, log more details
            if db_build is None:
                all_builds = db.query(Build).all()
                logger.error(f"Build with ID {build_id} not found in database")
                logger.error(f"All builds in database: {all_builds}")
                raise AssertionError(f"Build with ID {build_id} not found in database")
                
            # Explicitly load the build with its relationships
            db_build = db.query(Build).options(
                joinedload(Build.build_professions).joinedload(BuildProfession.profession)
            ).filter_by(id=build_id).first()
            
            # Log the build and its relationships
            logger.info(f"Build with relationships: {db_build}")
            if hasattr(db_build, 'build_professions'):
                for bp in db_build.build_professions:
                    logger.info(f"Build-Profession: build_id={bp.build_id}, profession_id={bp.profession_id}")
                    if hasattr(bp, 'profession'):
                        logger.info(f"  - Profession: id={bp.profession.id}, name={bp.profession.name}")
            
            # Log all builds for debugging
            all_builds = db.query(Build).all()
            logger.info(f"All builds in database: {all_builds}")
            
            # Verify the build has the correct profession associations
            db_build_professions = db.query(BuildProfession).filter_by(build_id=build_id).all()
            db_profession_ids = [bp.profession_id for bp in db_build_professions]
            
            # If no associations found, try a direct query
            if not db_build_professions:
                logger.warning("No build_professions found with direct query, trying raw SQL")
                try:
                    result = db.execute(
                        "SELECT profession_id FROM build_professions WHERE build_id = :build_id",
                        {"build_id": build_id}
                    ).fetchall()
                    db_profession_ids = [r[0] for r in result]
                    logger.info(f"Raw SQL query found {len(db_profession_ids)} associations")
                except Exception as e:
                    logger.error(f"Error executing raw SQL: {e}")
                    db_profession_ids = []
            
            if db_build is None:
                # Log all builds in the database for debugging
                all_builds = db_session.query(Build).all()
                logger.error(f"No build found with ID {build_id}. All builds in database: {all_builds}")
                
                # Log all build_professions for debugging
                all_build_profs = db_session.query(BuildProfession).all()
                logger.error(f"All build_professions in database: {all_build_profs}")
                
                # Log the current transaction status
                logger.error(f"Is session in transaction: {db_session.in_transaction()}")
                logger.error(f"Is session active: {db_session.is_active}")
                
                # Close the session and re-raise the error
                try:
                    next(db_gen)  # This will close the session
                except StopIteration:
                    pass
                
                raise AssertionError(f"Build with ID {build_id} not found in database")
            
            # Refresh the build to ensure we have the latest data
            db_session.refresh(db_build)
            
            # Verify the build has the correct profession associations
            db_build_professions = db.query(BuildProfession).filter_by(build_id=build_id).all()
            db_profession_ids = [bp.profession_id for bp in db_build_professions]
            
            # If no associations found, try a direct query
            if not db_build_professions:
                logger.warning("No build_professions found with direct query, trying raw SQL")
                try:
                    result = db.execute(
                        "SELECT profession_id FROM build_professions WHERE build_id = :build_id",
                        {"build_id": build_id}
                    ).fetchall()
                    db_profession_ids = [r[0] for r in result]
                    logger.info(f"Raw SQL query found {len(db_profession_ids)} associations")
                except Exception as e:
                    logger.error(f"Error executing raw SQL: {e}")
                    db_profession_ids = []
            
            # Log the profession associations for debugging
            logger.info(f"Build professions from join table: {db_build_professions}")
            logger.info(f"Expected profession IDs: {set(profession_ids)}")
            logger.info(f"Found profession IDs in join table: {set(db_profession_ids)}")
            
            logger.info(f"Build professions from join table: {db_build_professions}")
            logger.info(f"Expected profession IDs: {set(profession_ids)}")
            logger.info(f"Found profession IDs in join table: {set(db_profession_ids)}")
            
            # Verify the join table entries
            assert set(db_profession_ids) == set(profession_ids), \
                f"Mismatch in join table. Expected {set(profession_ids)}, got {set(db_profession_ids)}"
            
            # Also verify using the relationship
            if hasattr(db_build, 'build_professions'):
                rel_profession_ids = [bp.profession_id for bp in db_build.build_professions]
                logger.info(f"Profession IDs from relationship: {rel_profession_ids}")
                
                # Check if the relationship is loaded
                if not rel_profession_ids:
                    logger.warning("No professions found through relationship, trying to load them")
                    # Explicitly load the relationship
                    db.refresh(db_build)
                    db_build = db.query(Build).options(joinedload(Build.build_professions)).filter_by(id=build_id).first()
                    rel_profession_ids = [bp.profession_id for bp in db_build.build_professions]
                    logger.info(f"After refresh, profession IDs from relationship: {rel_profession_ids}")
                
                assert set(rel_profession_ids) == set(profession_ids), \
                    f"Mismatch in relationship. Expected {set(profession_ids)}, got {set(rel_profession_ids)}"
            else:
                logger.warning("Build object has no 'build_professions' relationship")
                # Try to get the build with the relationship explicitly loaded
                db_build = db.query(Build).options(joinedload(Build.build_professions)).filter_by(id=build_id).first()
                if hasattr(db_build, 'build_professions'):
                    rel_profession_ids = [bp.profession_id for bp in db_build.build_professions]
                    logger.info(f"After explicit load, profession IDs from relationship: {rel_profession_ids}")
                    assert set(rel_profession_ids) == set(profession_ids), \
                        f"Mismatch in relationship after explicit load. Expected {set(profession_ids)}, got {set(rel_profession_ids)}"
                else:
                    raise AssertionError("Build has no build_professions relationship even after explicit loading")
                
            # Verify the build data
            assert db_build.name == build_data["name"]
            assert db_build.description == build_data["description"]
            assert db_build.game_mode == build_data["game_mode"]
            assert db_build.team_size == build_data["team_size"]
            assert db_build.is_public == build_data["is_public"]
            assert db_build.created_by_id == test_user.id
            
            # Commit the transaction
            db.commit()
            
        except Exception as e:
            # Rollback the transaction in case of any error
            if db.in_transaction():
                db.rollback()
            logger.error(f"Error during database verification: {str(e)}")
            raise
        
        # Verify the build has the correct profession associations
        db_build_professions = db.query(BuildProfession).filter_by(build_id=build_id).all()
        db_profession_ids = [bp.profession_id for bp in db_build_professions]
        
        logger.info(f"Build professions from join table: {db_build_professions}")
        logger.info(f"Expected profession IDs: {set(profession_ids)}")
        logger.info(f"Found profession IDs in join table: {set(db_profession_ids)}")
        
        # Verify the join table entries
        assert set(db_profession_ids) == set(profession_ids), \
            f"Mismatch in join table. Expected {set(profession_ids)}, got {set(db_profession_ids)}"
        
        # Also verify using the relationship
        if hasattr(db_build, 'build_professions'):
            rel_profession_ids = [bp.profession_id for bp in db_build.build_professions]
            logger.info(f"Profession IDs from relationship: {rel_profession_ids}")
            assert set(rel_profession_ids) == set(profession_ids), \
                f"Mismatch in relationship. Expected {set(profession_ids)}, got {set(rel_profession_ids)}"
        else:
            logger.warning("Build object has no 'build_professions' relationship")
            
        # Verify the build data
        assert db_build.name == build_data["name"]
        assert db_build.description == build_data["description"]
        assert db_build.game_mode == build_data["game_mode"]
        assert db_build.team_size == build_data["team_size"]
        assert db_build.is_public == build_data["is_public"]
        assert db_build.created_by_id == test_user.id
            
        # Verify each profession has the required fields
        for prof in response_data['professions']:
            assert 'id' in prof, "Profession is missing 'id' field"
            assert 'name' in prof, f"Profession {prof.get('id')} is missing 'name' field"
            assert 'description' in prof, f"Profession {prof.get('id')} is missing 'description' field"
        
        # Verify the profession IDs in the response match the expected ones
        response_prof_ids = {prof['id'] for prof in response_data['professions']}
        expected_prof_ids = set(profession_ids)
        
        logger.info(f"Response profession IDs: {response_prof_ids}")
        logger.info(f"Expected profession IDs: {expected_prof_ids}")
        
        assert response_prof_ids == expected_prof_ids, \
            f"Expected profession IDs {expected_prof_ids}, got {response_prof_ids}"
        
        # Save build ID for cleanup
        build_id = response_data.get("id")
        
        # Log the database state after the request
        with db.begin():
            # Check if build exists in database
            db_build = db.query(Build).filter_by(id=build_id).first()
            logger.info(f"Build in database: {db_build is not None}")
            
            if db_build:
                # Check build_professions table
                build_profs = db.query(BuildProfession).filter_by(build_id=build_id).all()
                logger.info(f"Build-Profession associations in database: {len(build_profs)}")
                
                for bp in build_profs:
                    logger.info(f"  - BuildProfession: build_id={bp.build_id}, profession_id={bp.profession_id}")
                
                # Check if we can access professions through the relationship
                if hasattr(db_build, 'professions'):
                    logger.info(f"Professions through relationship: {len(db_build.professions)}")
                    for p in db_build.professions:
                        logger.info(f"  - Profession: id={p.id}, name={p.name}")
                
                # Check if we can access build_professions through the relationship
                if hasattr(db_build, 'build_professions'):
                    logger.info(f"BuildProfession objects through relationship: {len(db_build.build_professions)}")
                    for bp in db_build.build_professions:
                        logger.info(f"  - BuildProfession: id={bp.id}, build_id={bp.build_id}, profession_id={bp.profession_id}")
                        if hasattr(bp, 'profession'):
                            logger.info(f"    - Profession: id={bp.profession.id}, name={bp.profession.name}")
        
        # Verify response data matches request
        for field in ["name", "description", "game_mode", "team_size", "is_public", "config", "constraints"]:
            assert response_data[field] == build_data[field], f"Mismatch in field: {field}"
        
        # Verify profession associations
        assert len(response_data.get("professions", [])) == len(profession_ids), \
            f"Expected {len(profession_ids)} professions, got {len(response_data.get('professions', []))}"
        
        # Verify the build was saved to the database
        with db.begin():
            # Log all builds in the database
            all_builds = db.query(Build).all()
            logger.info(f"All builds in database: {[b.id for b in all_builds]}")
            
            # Log all build-profession associations
            all_build_profs = db.query(BuildProfession).all()
            logger.info(f"All build-profession associations: {[(bp.build_id, bp.profession_id) for bp in all_build_profs]}")
            
            # Get the build with its professions using raw SQL to bypass any ORM issues
            from sqlalchemy import text
            build_profs = db.execute(
                text("SELECT * FROM build_professions WHERE build_id = :build_id"),
                {"build_id": build_id}
            ).fetchall()
            logger.info(f"Raw build-profession associations for build {build_id}: {build_profs}")
            
            # Get the build with its professions using ORM
            db_build = db.query(Build).options(
                joinedload(Build.build_professions).joinedload(BuildProfession.profession)
            ).filter(Build.id == build_id).first()
            
            logger.info(f"Build from DB: {db_build}")
            if hasattr(db_build, 'build_professions'):
                logger.info(f"Build has {len(db_build.build_professions)} build_professions")
                for bp in db_build.build_professions:
                    logger.info(f"  - BuildProfession: build_id={bp.build_id}, profession_id={bp.profession_id}")
                    if hasattr(bp, 'profession'):
                        logger.info(f"    - Profession: id={bp.profession.id}, name={bp.profession.name}")
            
            # Verify the build has the correct number of professions
            assert len(build_profs) == len(profession_ids), \
                f"Expected {len(profession_ids)} build-profession associations, got {len(build_profs)}"
            
            assert db_build is not None, "Build was not created in the database"
            assert db_build.name == build_data["name"]
            assert db_build.created_by_id == test_user.id
            
            # Verify build-profession associations
            build_professions = db.query(BuildProfession).filter(
                BuildProfession.build_id == build_id
            ).all()
            logger.info(f"Found {len(build_professions)} build-profession associations")
            for bp in build_professions:
                logger.info(f"  - BuildProfession: build_id={bp.build_id}, profession_id={bp.profession_id}")
                
            assert len(build_professions) == len(professions), \
                f"Expected {len(professions)} build-profession associations, got {len(build_professions)}"
        
        logger.info("=== Test passed successfully ===")
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Log database state for debugging
        try:
            logger.error("\n=== Database State on Error ===")
            logger.error(f"All builds: {db.query(Build).all()}")
            logger.error(f"All build_professions: {db.query(BuildProfession).all()}")
            logger.error(f"All professions: {db.query(Profession).all()}")
            
            # Try to get more detailed information about the build
            if 'build_id' in locals():
                logger.error(f"\n=== Detailed Build Info (ID: {build_id}) ===")
                build = db.query(Build).filter_by(id=build_id).first()
                if build:
                    logger.error(f"Build: {build}")
                    if hasattr(build, 'build_professions'):
                        logger.error(f"Build-Profession associations: {build.build_professions}")
                else:
                    logger.error("Build not found in database")
                    
                # Check if the build exists in the builds table
                try:
                    build_exists = db.execute(
                        "SELECT 1 FROM builds WHERE id = :build_id",
                        {"build_id": build_id}
                    ).scalar()
                    logger.error(f"Build exists in builds table: {bool(build_exists)}")
                except Exception as sql_err:
                    logger.error(f"Error checking build in database: {sql_err}")
                    
                # Check if there are any build_professions for this build
                try:
                    bp_count = db.execute(
                        "SELECT COUNT(*) FROM build_professions WHERE build_id = :build_id",
                        {"build_id": build_id}
                    ).scalar()
                    logger.error(f"Number of build_professions for build {build_id}: {bp_count}")
                except Exception as sql_err:
                    logger.error(f"Error checking build_professions: {sql_err}")
                # List all build-profession associations
                all_build_profs = db.query(BuildProfession).all()
                logger.info(f"\n=== All Build-Profession Associations ({len(all_build_profs)}) ===")
                for bp in all_build_profs:
                    logger.info(f"Build {bp.build_id} <-> Profession {bp.profession_id}")
                    
        except Exception as db_err:
            logger.error(f"Error querying database state: {str(db_err)}")
        
        # Re-raise the original exception to fail the test
        raise
        
    finally:
        # Cleanup test resources
        logger.info("Cleaning up test resources...")
        
        try:
            with db.begin():
                # Clean up the build if it was created
                if 'build_id' in locals() and build_id:
                    logger.info(f"Cleaning up test build with ID: {build_id}")
                    db.query(BuildProfession).filter(
                        BuildProfession.build_id == build_id
                    ).delete(synchronize_session=False)
                    db.query(Build).filter(Build.id == build_id).delete(synchronize_session=False)
                
                # Clean up test professions if they exist
                if 'profession_ids' in locals() and profession_ids:
                    logger.info("Cleaning up test professions...")
                    db.query(BuildProfession).filter(
                        BuildProfession.profession_id.in_(profession_ids)
                    ).delete(synchronize_session=False)
                    
                    # Only delete professions that aren't referenced by other builds
                    for prof_id in profession_ids:
                        has_references = db.query(
                            db.query(BuildProfession)
                            .filter(BuildProfession.profession_id == prof_id)
                            .exists()
                        ).scalar()
                        if not has_references:
                            db.query(Profession).filter(Profession.id == prof_id).delete(synchronize_session=False)
                
                # Commit the transaction
                db.commit()
            
        except Exception as cleanup_err:
            logger.error(f"Error during cleanup: {str(cleanup_err)}")
            try:
                db.rollback()
            except Exception as rollback_err:
                logger.error(f"Error during rollback: {str(rollback_err)}")
        finally:
            # Ensure the session is clean for the next test
            db.expire_all()


def test_get_build(client: TestClient, db: Session) -> None:
    """Test retrieving a build by ID."""
    try:
        # Setup - use the test client's test user
        test_user = client._test_user
        build = BuildFactory(created_by_id=test_user.id)
        db.add(build)
        db.commit()
        db.refresh(build)
        
        # Set the current user for the test client
        client.set_current_user(test_user)
        
        # Test
        response = client.get(f"{settings.API_V1_STR}/builds/{build.id}")
        
        # Verify
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        content = response.json()
        assert content["id"] == build.id
        assert content["owner_id"] == test_user.id, f"Expected owner_id {test_user.id}, got {content.get('owner_id')}"
        
    except Exception as e:
        print(f"Error in test_get_build: {str(e)}")
        if 'response' in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        raise  # Re-raise the exception to fail the test


def test_list_builds(client: TestClient, db: Session) -> None:
    """Test listing builds with different visibility settings."""
    try:
        # Setup users
        test_user = client._test_user
        other_user = UserFactory()
        
        # Create builds with different visibility
        public_build = BuildFactory(created_by_id=test_user.id, is_public=True)
        private_build = BuildFactory(created_by_id=test_user.id, is_public=False)
        other_public_build = BuildFactory(created_by_id=other_user.id, is_public=True)
        
        db.add_all([other_user, public_build, private_build, other_public_build])
        db.commit()
        
        # Test as authenticated user - should see their builds plus public ones
        client.set_current_user(test_user)
        response = client.get(f"{settings.API_V1_STR}/builds/")
        
        # Verify authenticated user can see their builds and public ones
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        builds = response.json()
        build_ids = {b["id"] for b in builds}
        
        assert public_build.id in build_ids, "User should see their own public builds"
        assert private_build.id in build_ids, "User should see their own private builds"
        assert other_public_build.id in build_ids, "User should see public builds from other users"
        
        # Test as anonymous user - should only see public builds
        client.clear_auth()
        response = client.get(f"{settings.API_V1_STR}/builds/")
        
        # Verify anonymous user can only see public builds
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        builds = response.json()
        build_ids = {b["id"] for b in builds}
        
        assert public_build.id in build_ids, "Public builds should be visible to anonymous users"
        assert private_build.id not in build_ids, "Private builds should not be visible to anonymous users"
        assert other_public_build.id in build_ids, "Public builds from other users should be visible to anonymous users"
        
    except Exception as e:
        print(f"Error in test_list_builds: {str(e)}")
        if 'response' in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        raise  # Re-raise the exception to fail the test


def test_update_build(client: TestClient, db: Session) -> None:
    """Test updating a build."""
    try:
        # Setup - use the test client's test user
        test_user = client._test_user
        build = BuildFactory(created_by_id=test_user.id)
        db.add(build)
        db.commit()
        db.refresh(build)
        
        # Create some test professions for the update
        new_professions = [ProfessionFactory() for _ in range(2)]
        db.add_all(new_professions)
        db.commit()
        
        # Set the current user for the test client
        client.set_current_user(test_user)
        
        # Test data for update
        update_data = {
            "name": "Updated Build Name",
            "description": "Updated description",
            "is_public": True,
            "config": {"roles": ["support", "dps"]},
            "constraints": {"max_duplicates": 3},
            "profession_ids": [p.id for p in new_professions]
        }
        
        # Test update
        response = client.put(
            f"{settings.API_V1_STR}/builds/{build.id}",
            json=update_data
        )
        
        # Verify response
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        content = response.json()
        
        # Verify response data
        assert content["name"] == update_data["name"]
        assert content["description"] == update_data["description"]
        assert content["is_public"] is True
        assert content["config"] == update_data["config"]
        assert content["constraints"] == update_data["constraints"]
        assert len(content["professions"]) == len(new_professions)
        
        # Verify database was updated
        db.refresh(build)
        assert build.name == update_data["name"]
        assert build.description == update_data["description"]
        assert build.is_public is True
        assert build.config == update_data["config"]
        assert build.constraints == update_data["constraints"]
        assert {p.id for p in build.professions} == {p.id for p in new_professions}
        
    except Exception as e:
        print(f"Error in test_update_build: {str(e)}")
        if 'response' in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        raise  # Re-raise the exception to fail the test


def test_delete_build(client: TestClient, db: Session) -> None:
    """Test deleting a build."""
    try:
        # Setup - use the test client's test user
        test_user = client._test_user
        build = BuildFactory(created_by_id=test_user.id)
        db.add(build)
        db.commit()
        db.refresh(build)
        
        # Set the current user for the test client
        client.set_current_user(test_user)
        
        # Test delete
        response = client.delete(f"{settings.API_V1_STR}/builds/{build.id}")
        
        # Verify response
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        content = response.json()
        assert content["id"] == build.id
        assert content["is_deleted"] is True
        
        # Verify soft delete in database
        db.refresh(build)
        assert build.is_deleted is True
        assert build.deleted_at is not None
        
        # Verify the build is not returned in list
        response = client.get(f"{settings.API_V1_STR}/builds/")
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
        builds = response.json()
        assert all(b["id"] != build.id for b in builds), "Deleted build should not appear in list"
        
    except Exception as e:
        print(f"Error in test_delete_build: {str(e)}")
        if 'response' in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        raise  # Re-raise the exception to fail the test


def test_unauthorized_access(client: TestClient, db: Session) -> None:
    """Test unauthorized access to build operations."""
    try:
        # Setup users
        owner = UserFactory()
        other_user = UserFactory()
        build = BuildFactory(created_by_id=owner.id, is_public=False)
        db.add_all([owner, other_user, build])
        db.commit()
        db.refresh(build)
        
        # Test 1: Other user cannot access private build
        client.set_current_user(other_user)
        response = client.get(f"{settings.API_V1_STR}/builds/{build.id}")
        assert response.status_code == 403, "Other users should not be able to access private builds"
        
        # Test 2: Other user cannot update build
        response = client.put(
            f"{settings.API_V1_STR}/builds/{build.id}",
            json={"name": "Unauthorized Update"}
        )
        assert response.status_code == 403, "Other users should not be able to update builds"
        
        # Test 3: Other user cannot delete build
        response = client.delete(f"{settings.API_V1_STR}/builds/{build.id}")
        assert response.status_code == 403, "Other users should not be able to delete builds"
        
        # Test 4: Anonymous user cannot access private build
        client.clear_auth()
        response = client.get(f"{settings.API_V1_STR}/builds/{build.id}")
        assert response.status_code in [401, 403], "Anonymous users should not be able to access private builds"
        
        # Test 5: Owner can access their private build
        client.set_current_user(owner)
        response = client.get(f"{settings.API_V1_STR}/builds/{build.id}")
        assert response.status_code == 200, "Owners should be able to access their private builds"
        
        # Test 6: Owner can update their build
        update_data = {"name": "Authorized Update"}
        response = client.put(
            f"{settings.API_V1_STR}/builds/{build.id}",
            json=update_data
        )
        assert response.status_code == 200, "Owners should be able to update their builds"
        
        # Test 7: Owner can delete their build
        response = client.delete(f"{settings.API_V1_STR}/builds/{build.id}")
        assert response.status_code == 200, "Owners should be able to delete their builds"
        
        # Verify build was actually deleted
        db_build = build_crud.get(db, id=build.id)
        assert db_build is None or db_build.is_deleted is True, "Build should be deleted or marked as deleted"
        
    except Exception as e:
        print(f"Error in test_unauthorized_access: {str(e)}")
        if 'response' in locals():
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        raise  # Re-raise the exception to fail the test
    assert response.status_code in [401, 403], "Anonymous users should not be able to access private builds"
    
    # Test 5: Owner can access their private build
    client.set_current_user(owner)
    response = client.get(f"{settings.API_V1_STR}/builds/{build.id}")
    assert response.status_code == 200, "Owners should be able to access their private builds"
    
    # Test 6: Owner can update their build
    update_data = {"name": "Authorized Update"}
    response = client.put(
        f"{settings.API_V1_STR}/builds/{build.id}",
        json=update_data
    )
    assert response.status_code == 200, "Owners should be able to update their builds"
    
    # Test 7: Owner can delete their build
    response = client.delete(f"{settings.API_V1_STR}/builds/{build.id}")
    assert response.status_code == 200, "Owners should be able to delete their builds"
    
    # Verify build was actually deleted
    from app.crud.build import build as build_crud
    db_build = build_crud.get(db, id=build.id)
    assert db_build is None, "Build should be deleted from the database"
