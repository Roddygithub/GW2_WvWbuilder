"""Test helpers and fixtures for the application."""

from typing import Any, Dict, Type, TypeVar
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

# Create a test base that doesn't require __init__
TestBase = declarative_base()

# Type variable for test models
T = TypeVar("T", bound=TestBase)


def create_test_model_class(table_name: str, **columns: Dict[str, Any]) -> Type[TestBase]:
    """Dynamically create a test model class.

    Args:
        table_name: Name of the database table
        **columns: Column definitions as {name: (type, options)} pairs

    Returns:
        A SQLAlchemy model class
    """
    attrs = {
        "__tablename__": table_name,
        "__table_args__": {"extend_existing": True},
        "id": Column(Integer, primary_key=True, index=True),
    }

    # Add columns
    for name, col_def in columns.items():
        if isinstance(col_def, tuple) and len(col_def) == 2 and isinstance(col_def[1], dict):
            col_type, col_kwargs = col_def
            attrs[name] = Column(col_type, **col_kwargs)
        else:
            # Handle case where no kwargs are provided
            col_type = col_def[0] if isinstance(col_def, tuple) else col_def
            attrs[name] = Column(col_type)

    # Create the model class
    return type(f"TestModel{table_name.title().replace('_', '')}", (TestBase,), attrs)


def create_test_instance(model_class: Type[T], session: Session, **kwargs: Any) -> T:
    """Create and save a test instance.

    Args:
        model_class: The model class to instantiate
        session: Database session
        **kwargs: Attributes to set on the instance

    Returns:
        The created instance
    """
    instance = model_class(**kwargs)
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance
