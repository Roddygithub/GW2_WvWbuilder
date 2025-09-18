"""Tests for the base SQLAlchemy model."""
import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.models.base import Base


class TestBaseModel:
    """Tests for the Base SQLAlchemy model class."""
    
    def test_base_model_tablename(self):
        """Test that the table name is automatically generated from the class name."""
        class TestModel(Base):
            pass
            
        assert TestModel.__tablename__ == "testmodels"
    
    def test_base_model_id_column(self):
        """Test that the ID column is properly defined."""
        class TestModel(Base):
            pass
            
        assert hasattr(TestModel, 'id')
        assert TestModel.id.property.columns[0].primary_key is True
        assert str(TestModel.id.property.columns[0].type) == 'INTEGER'
    
    def test_base_model_repr(self):
        """Test the string representation of a model."""
        class TestModel(Base):
            pass
            
        instance = TestModel()
        instance.id = 1
        assert repr(instance) == "<TestModel 1>"
    
    def test_base_model_inheritance(self):
        """Test that a model can be created by inheriting from Base."""
        class TestModel(Base):
            name = Column(String(50))
            
        # Create an in-memory SQLite database for testing
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        
        # Create a session and add a test record
        Session = sessionmaker(bind=engine)
        session = Session()
        
        test_instance = TestModel(name="Test")
        session.add(test_instance)
        session.commit()
        
        # Verify the record was saved
        result = session.query(TestModel).first()
        assert result is not None
        assert result.name == "Test"
        assert result.id == 1
    
    def test_base_model_metadata(self):
        """Test that the Base model has metadata."""
        assert hasattr(Base, 'metadata')
        assert hasattr(Base.metadata, 'tables')
    
    def test_base_model_type_annotations(self):
        """Test that type annotations work with the Base model."""
        class TestModel(Base):
            name: str
            
        # This is just to verify the class can be created with type annotations
        # The actual type checking would be handled by mypy
        assert hasattr(TestModel, '__annotations__')
        assert 'name' in TestModel.__annotations__
    
    def test_base_model_with_additional_columns(self):
        """Test that additional columns can be added to a model."""
        class TestModel(Base):
            name = Column(String(50))
            description = Column(String(200))
            
        assert hasattr(TestModel, 'name')
        assert hasattr(TestModel, 'description')
        assert str(TestModel.name.type) == 'VARCHAR(50)'
        assert str(TestModel.description.type) == 'VARCHAR(200)'
    
    def test_base_model_multiple_inheritance(self):
        """Test that a model can inherit from multiple classes."""
        class Mixin:
            """A simple mixin class."""
            extra_field = Column(String(50))
            
        class TestModel(Base, Mixin):
            name = Column(String(50))
            
        assert hasattr(TestModel, 'name')
        assert hasattr(TestModel, 'extra_field')
        assert str(TestModel.extra_field.type) == 'VARCHAR(50)'
    
    def test_base_model_table_args(self):
        """Test that table_args can be used with the Base model."""
        class TestModel(Base):
            __tablename__ = 'custom_table_name'
            __table_args__ = {'sqlite_autoincrement': True}
            
            name = Column(String(50))
            
        assert TestModel.__tablename__ == 'custom_table_name'
        assert TestModel.__table__.dialect_kwargs['sqlite_autoincrement'] is True
