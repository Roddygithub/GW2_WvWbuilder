# 🏰 GW2 WvW Builder

[![Modern CI/CD](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/ci-cd-modern.yml/badge.svg)](https://github.com/Roddygithub/GW2_WvWbuilder/actions)
[![CI/CD Complete](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/ci-cd-complete.yml/badge.svg)](https://github.com/Roddygithub/GW2_WvWbuilder/actions)
[![codecov](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder/branch/main/graph/badge.svg)](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder)
[![Python 3.10-3.12](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue.svg)](https://www.python.org/downloads/)
[![Node 20](https://img.shields.io/badge/node-20-green.svg)](https://nodejs.org/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linter-ruff-blue.svg)](https://github.com/astral-sh/ruff)
[![TypeScript 5.0](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Release](https://img.shields.io/github/v/release/Roddygithub/GW2_WvWbuilder)](https://github.com/Roddygithub/GW2_WvWbuilder/releases)

**GW2 WvW Builder** est une application dédiée à la création et à l'optimisation de compositions pour le mode de jeu Monde contre Monde (WvW) de Guild Wars 2. Cette application aide les commandants et les joueurs à organiser des groupes efficaces pour affronter leurs adversaires.

> **🎉 Status**: Version **v3.2.0 STABLE** - Production Ready  
> **📊 Backend Coverage**: 28.75% | **✅ CI/CD**: 97% PASS | **🐳 Docker**: Ready  
> **📚 Documentation**: [/docs](./docs/) | **🚀 Releases**: [GitHub Releases](https://github.com/Roddygithub/GW2_WvWbuilder/releases)

## 🚀 Quick Start

**Get started in 5 minutes!**

```bash
# Backend
cd backend && poetry install && poetry run uvicorn app.main:app --reload
# API: http://localhost:8000 | Docs: http://localhost:8000/docs

# Frontend
cd frontend && npm install && npm run dev
# UI: http://localhost:5173
```

**See also**: [QUICK_START.md](QUICK_START.md) | [CONTRIBUTING.md](CONTRIBUTING.md)

## 🌟 Fonctionnalités

- **🎯 Générateur de compositions** : Créez des équipes équilibrées pour 2 à 20 joueurs
- **📊 Bibliothèque de builds** : Accédez à des builds optimisés pour chaque profession
- **🔍 Analyse de synergie** : Visualisez les interactions entre les membres de l'équipe
- **👥 Gestion des utilisateurs** : Système d'authentification et de rôles
- **🔄 Synchronisation GW2** : Intégration avec l'API officielle de Guild Wars 2
- **📱 Interface moderne** : Conçue pour les joueurs de tous niveaux

## 🏗️ Stack technique

### Backend ✅ Production-Ready (v3.2.0)
- **Framework** : FastAPI (Python 3.10-3.12)
- **Base de données** : PostgreSQL / SQLite avec SQLAlchemy ORM 2.0 (async)
- **Authentification** : JWT avec bcrypt, RBAC, key rotation
- **API** : RESTful avec documentation OpenAPI (Swagger/ReDoc)
- **Tests** : pytest avec couverture de code (28.75%, 750+ tests passing)
- **Qualité** : Black, Ruff, isort, flake8, Bandit, mypy
- **CI/CD** : GitHub Actions multi-version testing (97% PASS ✅)
- **Monitoring** : Prometheus, structured logging, performance tracking

### Frontend
- **Framework** : React 18 avec TypeScript
- **Styling** : TailwindCSS
- **Gestion d'état** : React Query
- **Formulaires** : React Hook Form

### DevOps
- **CI/CD** : GitHub Actions
- **Conteneurisation** : Docker
- **Monitoring** : Sentry, Prometheus

## 🚀 Démarrage rapide

### Prérequis
- **Python** 3.10, 3.11, or 3.12
- **Node.js** 20+
- **PostgreSQL** 14+ (or SQLite for development)
- **Poetry** 1.7+ (Python dependency management)
- **npm** (JavaScript dependency management)
- **Docker** and Docker Compose (optional, for containerized deployment)

## 🛠️ Validation locale

Le projet inclut un système complet de validation locale pour s'assurer que tout fonctionne correctement avant de pousser des modifications.

### Validation complète

Exécutez toutes les validations en une seule commande :

```bash
make final-validate
```

Cette commande va :
1. Lancer les tests unitaires avec couverture de code
2. Générer un rapport de couverture HTML
3. Exécuter les tests dans un environnement Docker isolé

### Commandes de validation individuelles

- **Tests avec couverture** : `make test`
- **Ouvrir le rapport de couverture** : `make coverage`
- **Lancer les tests dans Docker** : `make docker-test`
- **Nettoyer les fichiers de test** : `make clean`

### Configuration requise pour les tests

1. **Pour les tests locaux** :
   - PostgreSQL doit être en cours d'exécution localement
   - Les variables d'environnement doivent être configurées (voir `.env.example`)

2. **Pour les tests Docker** :
   - Docker et Docker Compose doivent être installés
   - Le port 5432 doit être disponible pour PostgreSQL

## 🧪 Tests

### Configuration requise
- Base de données PostgreSQL en cours d'exécution
- Variables d'environnement configurées (voir `.env.example`)

### Exécution des tests

#### Tous les tests
```bash
# Dans le répertoire backend
./run_tests.sh
```

#### Tests unitaires uniquement
```bash
./run_tests.sh --unit-only
```

#### Tests d'intégration
```bash
./run_tests.sh --integration-only
```

#### Tests d'API
```bash
./run_tests.sh --api-only
```

#### Options supplémentaires
- `--no-cov` : Désactive le rapport de couverture
- `--no-report` : Ne génère pas de rapports HTML/XML
- `--threshold=N` : Définit le seuil de couverture minimal (par défaut : 90)

### Couverture de code
Le projet vise une couverture de code d'au moins 90%. Pour générer un rapport de couverture :

```bash
# Génère un rapport HTML dans le dossier htmlcov/
./run_tests.sh --no-cov
```

### Dépannage
- **Erreurs de base de données** : Assurez-vous que PostgreSQL est en cours d'exécution et que les informations de connexion dans `.env` sont correctes.
- **Échecs de test** : Consultez les journaux dans `test-results/` pour plus de détails.
- **Problèmes de dépendances** : Exécutez `poetry install` pour installer toutes les dépendances requises.

Pour plus d'informations, consultez [TESTING.md](backend/TESTING.md).

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Roddygithub/GW2_WvWbuilder.git
   cd GW2_WvWbuilder
   ```

2. Set up the backend
   ```bash
   cd backend
   poetry install
   ```

3. Set up the database
   ```bash
   # Create a .env file with your database URL
   echo "DATABASE_URL=sqlite:///./test.db" > .env
   
   # Créer et activer l'environnement virtuel
   python -m venv venv
   source venv/bin/activate  # Sur Windows: .\venv\Scripts\activate
   
   # Installer les dépendances
   pip install -r requirements.txt
   
   # Appliquer les migrations
   alembic upgrade head
   
   # Lancer le serveur de développement
   uvicorn app.main:app --reload
   ```

3. **Frontend (optionnel)**
   ```bash
   cd ../frontend
   yarn install
   yarn dev
   ```

## 🧪 Exécution des tests

### Backend
```bash
# Tous les tests
pytest

# Avec couverture de code
pytest --cov=app --cov-report=term-missing

# Tests spécifiques
pytest tests/integration/api/test_users.py -v
```

### Frontend
```bash
cd frontend
yarn test
```

## 📚 Documentation API

La documentation interactive de l'API est disponible à l'adresse :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

### Conventions de commit

- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Mise en forme, point-virgule manquant, etc.
- `refactor`: Changement de code qui ne corrige pas un bug ni n'ajoute une fonctionnalité
- `test`: Ajout de tests
- `chore`: Mise à jour des tâches de construction, configuration du gestionnaire de paquets

## 📄 Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

## 📧 Contact

Pour toute question ou suggestion, veuillez ouvrir une issue sur GitHub.

Lien du projet : [https://github.com/Roddygithub/GW2_WvWbuilder](https://github.com/Roddygithub/GW2_WvWbuilder)

## 🙏 Remerciements

- [ArenaNet](https://www.arena.net/) pour Guild Wars 2
- Tous les contributeurs qui ont participé à ce projet

2. **Configurer l'environnement backend**
   ```bash
   cd backend
   cp .env.example .env  # Puis éditez les variables selon votre configuration
   poetry install
   ```

3. **Configurer la base de données**
   ```bash
   poetry run alembic upgrade head
   ```

4. **Configurer le frontend**
   ```bash
   cd ../frontend
   cp .env.example .env.local  # Puis éditez les variables selon votre configuration
   yarn install
   ```

## ⚙️ Configuration

### Variables d'environnement

Créez un fichier `.env` dans le dossier `backend` avec les variables suivantes :

```env
# Application
APP_ENV=development
SECRET_KEY=votre_clé_secrète
DEBUG=True

# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/gw2_wvwbuilder

# CORS
FRONTEND_URL=http://localhost:3000

# JWT
JWT_SECRET_KEY=votre_clé_jwt_secrète
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## 🧪 Exécution des tests

### Backend
```bash
cd backend
poetry run pytest --cov=app --cov-report=term-missing
```

### Frontend
```bash
cd frontend
yarn test
```

## 📊 Couverture de code

La couverture de code est surveillée via Codecov. Pour visualiser le rapport de couverture :

1. Exécutez les tests avec couverture :
   ```bash
   cd backend
   poetry run pytest --cov=app --cov-report=html
   ```

2. Ouvrez le rapport généré :
   ```bash
   open htmlcov/index.html
   ```

## 🌐 Développement local

### Lancer le backend
```bash
cd backend
poetry run uvicorn app.main:app --reload
```

### Lancer le frontend
```bash
cd frontend
yarn dev
```

### Accès aux interfaces
- **API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Frontend** : http://localhost:3000

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. **Créer une issue** pour discuter du changement proposé
2. **Créer une branche** pour votre fonctionnalité (`feature/ma-nouvelle-fonctionnalité`)
3. **Soumettre une pull request** vers la branche `develop`

### Standards de code
- Suivez le style de code existant
- Écrivez des tests pour les nouvelles fonctionnalités
- Assurez-vous que tous les tests passent
- Maintenez la couverture de code à 90% ou plus
- Documentez les nouvelles fonctionnalités

## 📜 Licence

Ce projet est sous licence [MIT](LICENSE).
