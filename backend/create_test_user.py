"""Créer un utilisateur de test."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security.password_utils import get_password_hash

def create_test_user():
    """Crée un utilisateur de test."""
    db_path = Path(__file__).parent / "gw2_wvwbuilder.db"
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Vérifier si l'utilisateur existe déjà
    existing = session.query(User).filter(User.email == "test@test.com").first()
    if existing:
        print(f"✅ Utilisateur test@test.com existe déjà (ID: {existing.id})")
        session.close()
        return
    
    # Créer l'utilisateur
    user = User(
        email="test@test.com",
        username="testuser",
        hashed_password=get_password_hash("Test123!"),
        first_name="Test",
        last_name="User",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    
    session.add(user)
    session.commit()
    
    print(f"✅ Utilisateur créé:")
    print(f"   Email: test@test.com")
    print(f"   Password: Test123!")
    print(f"   Username: testuser")
    print(f"   ID: {user.id}")
    
    session.close()

if __name__ == "__main__":
    create_test_user()
