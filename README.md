# 🏰 GW2 WvW Builder

[![Backend Tests](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/test-and-coverage.yml/badge.svg?branch=develop)](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/test-and-coverage.yml)
[![Code Coverage](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder/branch/develop/graph/badge.svg?token=YOUR-TOKEN-HERE)](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder)
[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**GW2 WvW Builder** est une application dédiée à la création et à l'optimisation de compositions pour le mode de jeu Monde contre Monde (WvW) de Guild Wars 2. Cette application aide les commandants et les joueurs à organiser des groupes efficaces pour affronter leurs adversaires.

## 🌟 Fonctionnalités

- 🎯 Création et gestion de compositions d'équipe
- 🔍 Optimisation des rôles et des compétences
- 👥 Gestion des utilisateurs et des rôles
- 🔄 Synchronisation avec l'API officielle de Guild Wars 2
- 📊 Tableaux de bord et statistiques

## 🚀 Démarrage rapide

### Prérequis

- Python 3.13+
- PostgreSQL 14+
- Node.js 18+ (pour le frontend)
- Compte GW2 avec les autorisations API nécessaires

### Installation du backend

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/Roddygithub/GW2_WvWbuilder.git
   cd GW2_WvWbuilder/backend
   ```

2. Créer un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: .\venv\Scripts\activate
   ```

3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurer les variables d'environnement :
   ```bash
   cp .env.example .env
   # Éditer le fichier .env avec vos paramètres
   ```

5. Appliquer les migrations :
   ```bash
   alembic upgrade head
   ```

6. Lancer le serveur de développement :
   ```bash
   uvicorn app.main:app --reload
   ```

### Installation du frontend (optionnel)

```bash
cd ../frontend
npm install
npm run dev
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
npm test
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

Votre nom - [@votretwitter](https://twitter.com/votretwitter) - email@exemple.com

Lien du projet : [https://github.com/Roddygithub/GW2_WvWbuilder](https://github.com/Roddygithub/GW2_WvWbuilder)

## 🙏 Remerciements

- [ArenaNet](https://www.arena.net/) pour Guild Wars 2
- Tous les contributeurs qui ont participé à ce projet

## 📋 Table des matières

- [🎯 Objectifs](#-objectifs)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🏗️ Stack technique](#%EF%B8%8F-stack-technique)
- [🚀 Installation rapide](#-installation-rapide)
- [⚙️ Configuration](#%EF%B8%8F-configuration)
- [🧪 Exécution des tests](#-exécution-des-tests)
- [📊 Couverture de code](#-couverture-de-code)
- [🌐 Développement local](#-développement-local)
- [🤝 Contribution](#-contribution)
- [📜 Licence](#-licence)

## 🎯 Objectifs

GW2 WvW Builder est une application web conçue pour aider les joueurs de Guild Wars 2 à optimiser leurs compositions d'équipe pour le mode WvW. Notre objectif est de fournir des outils puissants pour :

- Générer des compositions d'équipe optimisées pour 2 à 20 joueurs
- Proposer des builds en synergie basés sur les métas actuels
- Analyser les forces et faiblesses des compositions
- Faciliter le partage des builds entre joueurs

## ✨ Fonctionnalités

- **Générateur de compositions** : Créez des équipes équilibrées pour le WvW
- **Bibliothèque de builds** : Accédez à des builds optimisés pour chaque profession
- **Analyse de synergie** : Visualisez les interactions entre les membres de l'équipe
- **Export/Import** : Partagez facilement vos compositions
- **Interface intuitive** : Conçue pour les joueurs de tous niveaux

## 🏗️ Stack technique

### Backend
- **Framework** : FastAPI (Python 3.13+)
- **Base de données** : PostgreSQL avec SQLAlchemy ORM
- **Authentification** : JWT
- **API** : RESTful avec documentation OpenAPI (Swagger/ReDoc)

### Frontend
- **Framework** : React 18 avec TypeScript
- **Styling** : TailwindCSS
- **Gestion d'état** : React Query
- **Formulaires** : React Hook Form

### DevOps
- **CI/CD** : GitHub Actions
- **Tests** : pytest avec couverture de code (90%+)
- **Conteneurisation** : Docker
- **Monitoring** : Sentry, Prometheus

## 🚀 Installation rapide

### Prérequis
- Python 3.13+
- Node.js 18+
- PostgreSQL 14+
- Poetry (gestion des dépendances Python)
- Yarn (gestion des dépendances JavaScript)

### Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/Roddygithub/GW2_WvWbuilder.git
   cd GW2_WvWbuilder
   ```

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
