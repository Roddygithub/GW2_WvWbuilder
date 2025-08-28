from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from app.config import get_settings

# Import Base from models to avoid circular imports
# Note: We still need to import models to register them with SQLAlchemy
from app.models import Base, User, Role, Profession, EliteSpecialization, Composition, CompositionTag, composition_members

settings = get_settings()

SQLALCHEMY_DATABASE_URL = settings.get_database_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
