"""Factories pour générer des données de test."""
import factory
from faker import Faker
from sqlalchemy.orm import Session

from app.models import User, Role, Profession, Composition, EliteSpecialization, Build, BuildProfession

fake = Faker()

class RoleFactory(factory.alchemy.SQLAlchemyModelFactory):    
    class Meta:
        model = Role
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Faker("job")
    description = factory.Faker("sentence")
    icon_url = factory.Faker("image_url")

class ProfessionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Profession
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Faker("job")
    description = factory.Faker("sentence")
    icon_url = factory.Faker("image_url")

class EliteSpecializationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EliteSpecialization
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Faker("job")
    description = factory.Faker("sentence")
    icon_url = factory.Faker("image_url")
    profession = factory.SubFactory(ProfessionFactory)

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"
    
    email = factory.Faker("email")
    username = factory.Faker("user_name")
    hashed_password = factory.Faker("password")
    is_active = True
    is_superuser = False
    
    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        if not create:
            return
            
        if extracted:
            for role in extracted:
                self.roles.append(role)

class CompositionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Composition
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Faker("catch_phrase")
    description = factory.Faker("paragraph")
    squad_size = 10
    is_public = True
    
    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return
            
        if extracted:
            for member in extracted:
                self.members.append(member)

class BuildFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Build
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Faker("catch_phrase")
    description = factory.Faker("paragraph")
    game_mode = "wvw"
    team_size = 5
    is_public = False
    config = {}
    constraints = {}
    created_by = factory.SubFactory(UserFactory)
    
    @factory.post_generation
    def professions(self, create, extracted, **kwargs):
        if not create:
            return
            
        if extracted:
            for profession in extracted:
                self.professions.append(profession)

class BuildProfessionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BuildProfession
        sqlalchemy_session_persistence = "commit"
    
    build = factory.SubFactory(BuildFactory)
    profession = factory.SubFactory(ProfessionFactory)

def create_test_data(db: Session) -> dict:
    """Crée un jeu de données de test complet."""
    # Créer des rôles
    roles = [RoleFactory() for _ in range(3)]
    db.add_all(roles)
    
    # Créer des professions avec spécialisations
    professions = []
    elite_specs = []
    for _ in range(3):
        prof = ProfessionFactory()
        professions.append(prof)
        for _ in range(2):  # 2 spécialisations par profession
            elite_specs.append(EliteSpecializationFactory(profession=prof))
    
    db.add_all(professions)
    db.add_all(elite_specs)
    
    # Créer des utilisateurs avec des rôles
    users = []
    for i in range(5):
        user_roles = [roles[i % len(roles)]]  # Assigner des rôles de manière cyclique
        user = UserFactory(roles=user_roles)
        users.append(user)
    
    db.add_all(users)
    
    # Créer des compositions avec des membres
    compositions = []
    for i in range(3):
        # Chaque composition a 2-3 membres
        members = users[i:i+3] if i+3 <= len(users) else users[i:]
        comp = CompositionFactory(members=members)
        compositions.append(comp)
    
    db.add_all(compositions)
    db.commit()
    
    return {
        'roles': roles,
        'professions': professions,
        'elite_specializations': elite_specs,
        'users': users,
        'compositions': compositions,
    }
