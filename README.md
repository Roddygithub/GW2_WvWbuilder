<div align="center">
  <h1>GW2 WvW Builder</h1>
  
  [![Backend Tests](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/test-and-coverage.yml/badge.svg?branch=main)](https://github.com/Roddygithub/GW2_WvWbuilder/actions/workflows/test-and-coverage.yml)
  [![Code Coverage](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder/branch/main/graph/badge.svg)](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder)
  [![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
  [![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
  [![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

---

Un outil d’optimisation et de création de compositions pour **Guild Wars 2 – Monde contre Monde (WvW)**.  
Le projet vise à proposer des builds en synergie, adaptés au mode WvW, en exploitant les données officielles du jeu.

---

## 🚀 Objectifs

- Utiliser l’**API Guild Wars 2** et le **wiki anglais** pour récupérer les données du jeu (professions, spécialisations, compétences, armes, buffs, etc.).
- Prendre en compte les **mécaniques spécifiques au WvW**.
- Générer des compositions pour **2 à 20 joueurs** :
  - Mode 1 : l’utilisateur choisit les classes jouées.
  - Mode 2 : le programme génère une composition optimale.
- Proposer des **builds originaux** en synergie.
- Optimisation basée sur **DPS, Heal, Buff, Debuff, CC, etc.**
- Interface web interactive inspirée de [GW2 Skills Editor](https://fr.gw2skills.net/editor/).
- Exportation et partage des compositions.

---

## 🏗️ Stack technique

- **Backend** : [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+), SQLAlchemy, PostgreSQL  
- **Frontend** : [React](https://react.dev/) + [TailwindCSS](https://tailwindcss.com/)  
- **Dev / CI/CD** :
  - [Docker](https://www.docker.com/)  
  - [Windsurf](https://windsurf.sh/)  
  - [GitHub Actions](https://docs.github.com/en/actions)

---

## ⚙️ Installation & Setup

### 1. Cloner le projet
```bash
git clone https://github.com/<ton_user>/GW2_WvWbuilder.git
cd GW2_WvWbuilder

2. Backend (FastAPI)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

3. Frontend (React)
cd frontend
yarn install
yarn dev

4. Accès

Backend : http://localhost:8000
Frontend : http://localhost:3000

👥 Collaboration

Projet open source (Licence MIT).
Contributions via issues et pull requests.
Collaborateurs ajoutés manuellement pour dev direct.

🔮 Roadmap

Implémentation backend (connexion API GW2, récupération des données)
Algorithme d’optimisation des builds et compositions
Création frontend (sélecteur de classes/joueurs, affichage des builds)
Exportation/partage des compositions
Déploiement public (CI/CD)

📜 Licence
MIT – utilisation libre, avec attribution.





