# 🏰 GW2 WvW Builder

[![Backend Tests](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/test-and-coverage.yml/badge.svg?branch=develop)](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/test-and-coverage.yml)
![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)
[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**GW2 WvW Builder** est une application dédiée à la création et à l'optimisation de compositions pour le mode de jeu Monde contre Monde (WvW) de Guild Wars 2. Cette application aide les commandants et les joueurs à organiser des groupes efficaces pour affronter leurs adversaires.

## 🌟 Fonctionnalités

- **🎯 Générateur de compositions** : Créez des équipes équilibrées pour 2 à 20 joueurs
- **📊 Bibliothèque de builds** : Accédez à des builds optimisés pour chaque profession
- **🔍 Analyse de synergie** : Visualisez les interactions entre les membres de l'équipe
- **👥 Gestion des utilisateurs** : Système d'authentification et de rôles
- **🔄 Synchronisation GW2** : Intégration avec l'API officielle de Guild Wars 2
- **📱 Interface moderne** : Conçue pour les joueurs de tous niveaux

## 🏗️ Stack technique

### Backend
- **Framework** : FastAPI (Python 3.13+)
- **Base de données** : PostgreSQL avec SQLAlchemy ORM
- **Authentification** : JWT
- **API** : RESTful avec documentation OpenAPI (Swagger/ReDoc)
- **Tests** : pytest avec couverture de code (90%+)

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
- Python 3.13+
- Node.js 18+
- PostgreSQL 14+
- Poetry (gestion des dépendances Python)
- Yarn (gestion des dépendances JavaScript)
- Docker et Docker Compose (pour les tests en conteneur)

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

### Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/Roddygithub/GW2_WvWbuilder.git
   cd GW2_WvWbuilder
   ```

2. **Configurer l'environnement**
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   # Éditer le fichier .env avec vos paramètres
   
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
