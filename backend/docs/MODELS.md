# Modèles de données

Ce document décrit la structure des modèles de données principaux de l'application.

## Schéma de la base de données

### Tables principales

#### User
- `id`: Identifiant unique
- `username`: Nom d'utilisateur unique
- `email`: Email unique
- `hashed_password`: Mot de passe hashé
- `is_active`: Compte actif ou non
- `is_superuser`: Droits administrateur
- `created_at`: Date de création
- `updated_at`: Dernière mise à jour

#### Role
- `id`: Identifiant unique
- `name`: Nom du rôle (unique)
- `description`: Description du rôle
- `icon_url`: URL de l'icône

#### Profession
- `id`: Identifiant unique
- `name`: Nom de la profession (unique)
- `icon_url`: URL de l'icône
- `description`: Description de la profession

#### EliteSpecialization
- `id`: Identifiant unique
- `name`: Nom de la spécialisation
- `profession_id`: ID de la profession associée
- `icon_url`: URL de l'icône
- `description`: Description de la spécialisation

#### Composition
- `id`: Identifiant unique
- `name`: Nom de la composition
- `description`: Description détaillée
- `squad_size`: Taille de l'équipe (défaut: 10)
- `is_public`: Visibilité publique
- `created_by`: ID du créateur
- `created_at`: Date de création
- `updated_at`: Dernière mise à jour

#### CompositionTag
- `id`: Identifiant unique
- `name`: Nom du tag
- `composition_id`: ID de la composition associée

### Relations

1. **User ↔ Role (Many-to-Many)**
   - Un utilisateur peut avoir plusieurs rôles
   - Un rôle peut être attribué à plusieurs utilisateurs
   - Table de jonction: `user_roles`

2. **Composition ↔ User (Many-to-Many)**
   - Une composition peut avoir plusieurs membres
   - Un utilisateur peut appartenir à plusieurs compositions
   - Table de jonction: `composition_members` avec métadonnées supplémentaires:
     - `role_id`: Rôle dans la composition
     - `profession_id`: Profession choisie
     - `elite_specialization_id`: Spécialisation choisie
     - `notes`: Notes optionnelles

3. **Profession ↔ EliteSpecialization (One-to-Many)**
   - Une profession a plusieurs spécialisations élites
   - Une spécialisation élite appartient à une seule profession

4. **Composition ↔ CompositionTag (One-to-Many)**
   - Une composition peut avoir plusieurs tags
   - Un tag appartient à une seule composition

## Exemple d'utilisation

### Créer un utilisateur avec un rôle
```python
# Créer un rôle
role = Role(name="Commander", description="Chef d'escouade")
db.add(role)
db.commit()

# Créer un utilisateur avec ce rôle
user = User(
    username="joueur1",
    email="joueur1@example.com",
    hashed_password=get_password_hash("motdepasse")
)
user.roles.append(role)
db.add(user)
db.commit()
```

### Créer une composition avec des membres
```python
# Créer une composition
composition = Composition(
    name="Comp Zerg",
    description="Composition pour zerg en WvW",
    squad_size=15,
    created_by=user.id
)

# Ajouter des membres avec leurs rôles
composition.members.append(user1)  # Avec rôle par défaut
composition.members.append(user2)  # Avec rôle spécifique

db.add(composition)
db.commit()
```
