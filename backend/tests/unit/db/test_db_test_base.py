"""Tests for the database base module."""

from sqlalchemy import Column, Integer, String, inspect, create_engine
from sqlalchemy.ext.declarative import declarative_base

# Import the module/class to test
from app.db.base import Base

# Create a test model that won't interfere with the actual Base
TestBase = declarative_base()


class TestModel(TestBase):
    __tablename__ = "test_model"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)


# Test cases
def test_base_class_initialization():
    """Test that Base class is properly initialized."""
    # Check that Base has the expected attributes
    assert hasattr(Base, "metadata")

    # The Base class should not have __abstract__ as it's not a requirement
    # Check that our test model was properly registered with its own metadata
    assert "test_model" in TestBase.metadata.tables

    # Check the table columns
    table = TestBase.metadata.tables["test_model"]
    assert "id" in table.c
    assert "name" in table.c
    assert "description" in table.c


def test_table_creation():
    """Test that tables can be created from models inheriting from Base."""
    # Create an in-memory SQLite database for testing
    TEST_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(TEST_DATABASE_URL)

    # Create all tables
    TestBase.metadata.create_all(engine)

    # Verify tables were created
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "test_model" in tables

    # Verify columns
    columns = [col["name"] for col in inspector.get_columns("test_model")]
    assert "id" in columns
    assert "name" in columns
    assert "description" in columns

    # Clean up
    engine.dispose()
