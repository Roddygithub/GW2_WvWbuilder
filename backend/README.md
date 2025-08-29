# GW2 Team Builder – Backend (FastAPI)

[![Backend Test & Coverage](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/test-and-coverage.yml/badge.svg?branch=main)](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/test-and-coverage.yml)
[![codecov](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder/branch/main/graph/badge.svg)](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder)

Backend FastAPI pour Guild Wars 2 Team Builder. Utilise SQLAlchemy 2.0, Pydantic v2, et inclut une suite de tests complète avec couverture de code.

## 🚀 Stack technique
- **Framework** : FastAPI
- **Base de données** : SQLAlchemy 2.0
- **Validation** : Pydantic v2
- **Tests** : pytest avec couverture ≥90%
- **Gestion des dépendances** : Poetry

## 📋 Prérequis
- Python 3.13
- [Poetry](https://python-poetry.org/)

## 🛠 Installation
```bash
# Cloner le dépôt
git clone [https://github.com/Roddygithub/GW2_WvWbuilder.git](https://github.com/Roddygithub/GW2_WvWbuilder.git)
cd GW2_WvWbuilder/backend

# Installer les dépendances
poetry install
undefined
🧪 Exécution des tests
bash
# Lancer les tests avec couverture
poetry run pytest --cov=app --cov-report=term-missing
Couverture cible : ≥90%
Les numéros de ligne non couverts sont affichés dans la colonne "Missing"
🚀 Développement local
bash
# Démarrer le serveur de développement
poetry run uvicorn app.main:app --reload
Documentation interactive : http://127.0.0.1:8000/docs
Documentation alternative : http://127.0.0.1:8000/redoc
🤝 Contribuer
Consultez notre guide de contribution pour :

Les conventions de code
La structure des tests
Le processus de PR
Les PR doivent :

Cibler les branches main ou develop
Inclure des tests pour les nouvelles fonctionnalités
Maintenir une couverture de code ≥90%
📊 Statut
Tests : 33/33 PASS
Couverture : 93% (objectif ≥90%)
CI : GitHub Actions actif sur push/PR EOL
Create/overwrite backend/CONTRIBUTING.md
cat > /home/roddy/Documents/GW2_WvWbuilder/backend/CONTRIBUTING.md << 'EOL'

Guide de contribution
Introduction
Ce guide explique comment contribuer au backend du GW2 Team Builder. Le projet utilise FastAPI avec SQLAlchemy 2.0 et Pydantic v2.

🛠 Prérequis
Python 3.13
Poetry
Accès au dépôt GitHub
🚀 Installation
bash
git clone https://github.com/Roddygithub/GW2_WvWbuilder.git
cd GW2_WvWbuilder/backend
poetry install
🧪 Tests et couverture
bash
# Lancer tous les tests avec couverture
poetry run pytest --cov=app --cov-report=term-missing

# Lancer les tests en mode watch (développement)
poetry run ptw -- --cov=app --cov-report=term-missing
🔍 Comprendre la couverture
La colonne "Missing" montre les lignes non couvertes
Objectif : ≥90% de couverture globale
Les tests d'API doivent couvrir les cas d'erreur (400, 403, 404, 422)
⚠️ Gestion des avertissements
Les avertissements suivants sont filtrés :

Gzip : PytestUnraisableExceptionWarning (filtrage global)
Pydantic v2 : Dépréciations des dépendances
SQLAlchemy : Avertissements de teardown inoffensifs
✨ Ajouter des tests
Placez les nouveaux tests dans backend/tests/
Utilisez TestClient pour les tests d'API
Exemple de structure :
tests/
├── test_api/
│   ├── test_compositions.py
│   └── test_users.py
└── test_models/
    └── test_user.py
🎭 Surcharge des dépendances
python
from app.api import deps

# Surcharger la base de données
client.app.dependency_overrides[deps.get_db] = lambda: iter([test_db])

# Simuler un superutilisateur
client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: test_superuser
📝 Conventions de code
Pydantic v2
python
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    email: str = Field(..., json_schema_extra={"example": "user@example.com"})
SQLAlchemy 2.0
python
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    roles: Mapped[list["Role"]] = relationship(secondary="user_roles")
🔄 Développement local
bash
# Démarrer le serveur avec rechargement automatique
poetry run uvicorn app.main:app --reload
🛠 Processus de contribution
Créer une branche : git checkout -b feature/ma-fonctionnalite
Faire des commits atomiques
Pousser les modifications : git push origin feature/ma-fonctionnalite
Créer une Pull Request vers main ou develop
✅ Exigences des PR
 Tests unitaires et d'intégration
 Documentation mise à jour
 Couverture ≥90%
 Aucun warning non géré
📊 CI & Couverture
Workflow : 
.github/workflows/test-and-coverage.yml
Badges :
Build Status
Coverage
❓ Questions ?
Ouvrez une issue avec :

Les étapes pour reproduire le problème
Le comportement attendu
Les logs et captures d'écran si nécessaire 
