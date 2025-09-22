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
    permission_level = 0
    is_default = False


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

<<<<<<< HEAD
class BuildProfessionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BuildProfession
        sqlalchemy_session_persistence = "commit"
    
    profession = factory.SubFactory(ProfessionFactory)

class BuildFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Build
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Faker("catch_phrase")
    description = factory.Faker("paragraph")
    game_mode = "wvw"
    team_size = 5
    is_public = True
    config = {"roles": ["heal", "dps", "support"]}
    constraints = {"max_duplicates": 2}
    owner = factory.SubFactory(UserFactory)
    
    @factory.post_generation
    def professions(self, create, extracted, **kwargs):
        if not create:
            return
            
        if extracted:
            for profession in extracted:
                BuildProfessionFactory(build=self, profession=profession)
=======
>>>>>>> a023051 (feat: optimized CRUD with Redis caching + full test coverage + docs and monitoring guide)

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
        if not create or not extracted:
            return

        for profession in extracted:
            self.professions.append(profession)


# BuildProfession is now a table, not a model, so we don't need a factory for it


def create_test_data(db: Session) -> dict:
    """Crée un jeu de données de test complet."""
    # Créer des rôles
    roles = [RoleFactory() for _ in range(3)]
    db.add_all(roles)

    # Créer des professions avec spécialisations
    professions = []
    elite_specs = []

    for _ in range(5):
        prof = ProfessionFactory()
        professions.append(prof)

        # Ajouter 1-3 spécialisations par profession
        for _ in range(fake.random_int(1, 3)):
            spec = EliteSpecializationFactory(profession=prof)
            elite_specs.append(spec)

    db.add_all(professions)
    db.add_all(elite_specs)

    # Créer des utilisateurs avec rôles
    users = []
    for i in range(5):
        user_roles = [roles[0]]  # Tous les utilisateurs ont le premier rôle
        if i == 0:  # Premier utilisateur est admin
            user_roles.append(roles[1])

        user = UserFactory(roles=user_roles)
        users.append(user)

    db.add_all(users)

    # Créer des compositions
    compositions = []
    for i in range(3):
        owner = users[i % len(users)]
        comp = CompositionFactory(created_by=owner.id)

        # Ajouter des membres aléatoires
        members = [u for u in users if u != owner][: fake.random_int(1, 3)]
        comp.members = members

        compositions.append(comp)

    db.add_all(compositions)

    # Créer des builds avec des associations de profession
    builds = []
    for i in range(5):
        owner = users[i % len(users)]
        build = BuildFactory(created_by=owner)

        # Associer 1-3 professions aléatoires
        build_professions = fake.random_elements(
            elements=professions, length=fake.random_int(1, 3), unique=True
        )
        build.professions = build_professions

        # Associer à une composition aléatoire
        if i < len(compositions):
            compositions[i].build = build

        builds.append(build)

    db.add_all(builds)
    db.commit()

    return {
        "users": users,
        "roles": roles,
        "professions": professions,
        "elite_specs": elite_specs,
        "compositions": compositions,
        "builds": builds,
    }
