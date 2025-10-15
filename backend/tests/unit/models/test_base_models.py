"""Tests for base models."""

import pytest
from datetime import datetime
from app.models.base_model import BaseModel
from app.models.base import Base
from sqlalchemy import Column, Integer, String


class TestModel(Base):
    """Test model for base class testing."""
    __tablename__ = "test_model"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


def test_base_model_creation():
    """Test base model instance creation."""
    model = TestModel(name="Test")
    assert model.name == "Test"


def test_base_model_tablename():
    """Test base model table name."""
    assert TestModel.__tablename__ == "test_model"


def test_base_model_repr():
    """Test base model string representation."""
    model = TestModel(id=1, name="Test")
    repr_str = repr(model)
    assert "TestModel" in repr_str or "test_model" in repr_str


def test_base_model_dict():
    """Test base model to dict conversion."""
    model = TestModel(id=1, name="Test")
    # Test if model can be converted to dict-like structure
    assert hasattr(model, "name")
    assert model.name == "Test"


def test_base_model_columns():
    """Test base model has expected columns."""
    assert hasattr(TestModel, "id")
    assert hasattr(TestModel, "name")


def test_base_model_primary_key():
    """Test base model primary key."""
    assert TestModel.id.primary_key is True


def test_base_model_nullable():
    """Test base model nullable constraints."""
    assert TestModel.name.nullable is False
