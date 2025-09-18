<div align="center">
  <h1>GW2 WvW Team Builder – Backend</h1>
  
  [![Tests](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/ci.yml)
  [![Coverage](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder/branch/develop/graph/badge.svg?token=YOUR-TOKEN-HERE)](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
  [![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
  [![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

High-performance backend for Guild Wars 2 WvW Team Builder, built with FastAPI, SQLAlchemy 2.0, and Pydantic v2. Includes a comprehensive test suite with >90% code coverage.

## 📋 Table of Contents
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
- [Development](#-development)
- [Testing](#-testing)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

- **RESTful API** with interactive documentation (Swagger/ReDoc)
- **Relational Database** with SQLAlchemy 2.0
- **Data Validation** with Pydantic v2
- **Secure JWT Authentication**
- **Automated Testing** with code coverage
- **CI/CD Pipeline** with GitHub Actions and Codecov
- **Docker** ready for deployment
- **Asynchronous** for high performance
- **Type Annotations** throughout the codebase
- **Modular Architecture** for easy maintenance

## 🛠 Prerequisites

- Python 3.13
- [Poetry](https://python-poetry.org/) for dependency management
- PostgreSQL (recommended for production, SQLite for development)
- Docker (optional, for containerized deployment)
- Git (for version control)

## ⚙️ Getting Started

### Clone the Repository

```bash
git clone https://github.com/Roddygithub/GW2_WvWbuilder.git
cd GW2_WvWbuilder/backend
```

### Install Dependencies

```bash
# Install Python dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

### Configure Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your configuration:
   ```env
   # Database
   DATABASE_URL=sqlite:///./gw2_wvwbuilder.db
   # or for PostgreSQL:
   # DATABASE_URL=postgresql://user:password@localhost:5432/gw2_wvwbuilder

   # JWT
   SECRET_KEY=your-secret-key-here
   ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

   # App
   ENVIRONMENT=development
   DEBUG=true
   ```

### Initialize the Database

```bash
# Run migrations
alembic upgrade head

# Create initial data (optional)
python -m app.initial_data
```

### Run the Development Server

```bash
# Start the development server with auto-reload
uvicorn app.main:app --reload
```

Once running, you can access:
- **Interactive API Docs**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc
- **API Base URL**: http://127.0.0.1:8000/api/v1

## 🧪 Testing & Coverage

### Running Tests

```bash
# Install dependencies
poetry install --with test

# Run all tests
make test

# Run tests with coverage report in terminal
make test-cov

# Generate HTML coverage report
make test-coverage

# Run a specific test file
poetry run pytest tests/unit/test_example.py -v

# Run tests matching a pattern
poetry run pytest -k "test_name" -v
```

### Test Coverage

We aim to maintain >90% test coverage. The test runner will fail if coverage falls below this threshold.

View the coverage report:

```bash
# After running tests, open the HTML report
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

For more information on writing and running tests, see [TESTING.md](TESTING.md).

### Code Quality Checks

```bash
# Format code with Black
poetry run black .

# Sort imports with isort
poetry run isort .

# Check types with mypy
poetry run mypy .

# Check style with flake8
poetry run flake8

# Run all checks (configured in pre-commit)
poetry run pre-commit run --all-files
```

### Test Structure

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for API endpoints
- `tests/conftest.py` - Test fixtures and configuration
- `tests/factories/` - Test data factories

### Continuous Integration

Tests are automatically run on every push and pull request via GitHub Actions. The workflow includes:

1. Linting with `black`, `isort`, and `mypy`
2. Running the full test suite
3. Generating coverage reports
4. Uploading coverage to Codecov
```

## 📚 API Documentation

### Authentication

The API uses JWT for authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

### Available Endpoints

- `GET /api/v1/builds/` - List all builds
- `POST /api/v1/builds/` - Create a new build
- `GET /api/v1/builds/{build_id}` - Get build details
- `PUT /api/v1/builds/{build_id}` - Update a build
- `DELETE /api/v1/builds/{build_id}` - Delete a build
- `POST /api/v1/builds/generate/` - Generate a new build

For detailed API documentation, visit the interactive documentation at `http://localhost:8000/docs` when running the development server.

## 🚀 Deployment

### Production with Docker

1. Build the Docker image:
   ```bash
   docker build -t gw2-wvwbuilder-backend .
   ```

2. Run the container:
   ```bash
   docker run -d --name gw2-wvwbuilder-backend \
     -p 8000:80 \
     -e DATABASE_URL=postgresql://user:password@db:5432/gw2_wvwbuilder \
     -e SECRET_KEY=your-secret-key \
     gw2-wvwbuilder-backend
   ```

### Production with Gunicorn

```bash
# Install gunicorn
poetry add gunicorn

# Run with gunicorn (adjust workers based on CPU cores)
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection URL | `sqlite:///./gw2_wvwbuilder.db` |
| `SECRET_KEY` | Secret key for JWT token generation | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration time in minutes | `1440` (24h) |
| `ENVIRONMENT` | Application environment (`development`/`production`) | `development` |
| `DEBUG` | Enable debug mode | `False` in production |

## 🏗 Project Structure

```
backend/
├── alembic/                 # Database migrations
├── app/
│   ├── api/                 # API routes
│   ├── core/                # Core functionality
│   ├── crud/                # Database operations
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic
│   ├── tests/               # Test utilities
│   ├── main.py              # FastAPI application
│   └── initial_data.py      # Database initialization
├── tests/                   # Test suite
│   ├── integration/         # Integration tests
│   └── unit/                # Unit tests
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore file
├── alembic.ini              # Alembic configuration
├── docker-compose.yml       # Docker Compose file
├── Dockerfile               # Docker configuration
├── poetry.lock             # Dependency lock file
├── pyproject.toml          # Project metadata and dependencies
└── README.md               # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Commit Message Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation only changes
- `style:` Changes that do not affect the meaning of the code
- `refactor:` A code change that neither fixes a bug nor adds a feature
- `perf:` A code change that improves performance
- `test:` Adding missing tests or correcting existing tests
- `chore:` Changes to the build process or auxiliary tools

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [SQLAlchemy](https://www.sqlalchemy.org/) - The ORM used
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [Poetry](https://python-poetry.org/) - Dependency management

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
