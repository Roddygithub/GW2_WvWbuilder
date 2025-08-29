<div align="center">
  <h1>GW2 Team Builder – Backend</h1>
  
  [![Tests](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/test-and-coverage.yml/badge.svg?branch=main)](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/test-and-coverage.yml)
  [![Coverage](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder/branch/main/graph/badge.svg?token=YOUR-TOKEN-HERE)](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder)
  [![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
  [![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

Backend haute performance pour Guild Wars 2 Team Builder, construit avec FastAPI, SQLAlchemy 2.0 et Pydantic v2. Inclut une suite de tests complète avec une couverture de code >90%.

## 🚀 Fonctionnalités

- **API RESTful** avec documentation interactive (Swagger/ReDoc)
- **Base de données** relationnelle avec SQLAlchemy 2.0
- **Validation des données** avec Pydantic v2
- **Authentification** JWT sécurisée
- **Tests automatisés** avec couverture de code
- **CI/CD** avec GitHub Actions et Codecov
- **Conteneurisation** prête pour le déploiement

## 🛠 Prérequis

- Python 3.13
- [Poetry](https://python-poetry.org/)
- PostgreSQL (optionnel, SQLite par défaut en développement)

## ⚙️ Installation

```bash
# Cloner le dépôt
git clone https://github.com/Roddygithub/GW2_WvWbuilder.git
cd GW2_WvWbuilder/backend

# Installer les dépendances
poetry install

# Configurer les variables d'environnement
cp .env.example .env
# Éditer le fichier .env selon vos besoins
```

## 🚀 Démarrage rapide

### Environnement de développement

```bash
# Activer l'environnement virtuel
poetry shell

# Appliquer les migrations de base de données
alembic upgrade head

# Démarrer le serveur de développement
uvicorn app.main:app --reload
```

- **Documentation interactive**: http://127.0.0.1:8000/docs
- **Documentation alternative**: http://127.0.0.1:8000/redoc
- **API Base URL**: http://127.0.0.1:8000/api/v1

## 🧪 Tests et qualité

### Exécuter les tests

```bash
# Tous les tests avec couverture
poetry run pytest --cov=app --cov-report=term-missing

# Uniquement les tests unitaires
poetry run pytest tests/unit

# Uniquement les tests d'intégration
poetry run pytest tests/integration

# Générer un rapport HTML de couverture
poetry run pytest --cov=app --cov-report=html
# Ouvrir le rapport dans le navigateur
python -m http.server --directory=htmlcov
```

### Vérification de la qualité

```bash
# Vérifier le style de code avec Black
poetry run black .

# Vérifier les imports avec isort
poetry run isort .

# Vérifier les types avec mypy
poetry run mypy .

# Vérifier le style avec flake8
poetry run flake8
```

## 📦 Déploiement

### Variables d'environnement requises

```
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# ou pour SQLite
# DATABASE_URL=sqlite:///./sql_app.db

# Sécurité
SECRET_KEY=votre_secret_key_tres_long_et_securise
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Avec Docker

```bash
docker-compose up --build
```

## 🤝 Contribuer

Les contributions sont les bienvenues ! Consultez notre [guide de contribution](CONTRIBUTING.md) pour plus de détails.

### Processus de PR

1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

### Standards de code

- Suivez [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utilisez les type hints partout
- Documentez les fonctions et classes avec des docstrings
- Écrivez des tests pour les nouvelles fonctionnalités
- Maintenez la couverture de code à au moins 90%

## 📚 Documentation additionnelle

- [Structure des modèles de données](docs/MODELS.md) - Documentation complète des modèles et relations
- [Guide des migrations](docs/MIGRATIONS.md) - Comment gérer les migrations de base de données

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [FastAPI](https://fastapi.tiangolo.com/) - Le framework web moderne et rapide
- [SQLAlchemy](https://www.sqlalchemy.org/) - L'ORM Python
- [Pydantic](https://pydantic-docs.helpmanual.io/) - La validation des données
- [Poetry](https://python-poetry.org/) - La gestion des dépendances

## 📚 Documentation additionnelle

- [Structure des modèles de données](docs/MODELS.md) - Documentation complète des modèles et relations
- [Guide des migrations](docs/MIGRATIONS.md) - Comment gérer les migrations de base de données
- [Guide de contribution](CONTRIBUTING.md) - Normes et processus de contribution
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
