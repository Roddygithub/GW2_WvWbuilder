# GW2_WvWbuilder

Un outil d’optimisation et de création de compositions pour **Guild Wars 2 – Monde contre Monde (WvW)**.  
Le projet vise à proposer des builds et des compositions en synergie, adaptés spécifiquement au mode WvW, en exploitant les données officielles et publiques du jeu.

---

## 🚀 Objectifs

- Utiliser l’**API Guild Wars 2** et le **wiki anglais** pour récupérer les données du jeu (professions, spécialisations, compétences, armes, buffs, etc.).
- Prendre en compte les **mécaniques spécifiques au WvW** (différent du PvE).
- Permettre la génération de compositions pour **2 à 20 joueurs** :
  - Mode 1 : l’utilisateur choisit les classes jouées (ex : 2 Gardiens, 1 Nécro, 3 Élémentalistes).
  - Mode 2 : le programme génère une composition optimale parmi toutes les classes/spécialisations.
- Proposer des **builds originaux** en synergie (pas de builds "copiés" d’Internet).
- Optimisation basée sur la couverture maximale des rôles : **DPS, Heal, Buff, Debuff, CC, etc.**
- Interface web interactive inspirée de [GW2 Skills Editor](https://fr.gw2skills.net/editor/).
- Exportation et partage des compositions.

---

## 🏗️ Stack technique

- **Backend** : [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+), SQLAlchemy, PostgreSQL  
- **Frontend** : [React](https://react.dev/) + [TailwindCSS](https://tailwindcss.com/)  
- **Gestion projet / Dev** :
  - [Docker](https://www.docker.com/) (environnement reproductible, déploiement facile)
  - [Windsurf](https://windsurf.sh/) (assistant IA pour le développement collaboratif)
  - [GitHub Actions](https://docs.github.com/en/actions) (CI/CD)

---

## ⚙️ Installation & Setup

### 1. Cloner le projet
```bash
git clone https://github.com/<ton_user>/GW2_WvWbuilder.git
cd GW2_WvWbuilder

cd backend
# Créer un venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload

cd frontend
yarn install
yarn dev

4. Accès

Backend : http://localhost:8000

Frontend : http://localhost:3000

👥 Collaboration

Le projet est open source (licence MIT par défaut).

Contributions bienvenues via issues et pull requests.

Collaborateurs ajoutés manuellement pour développement direct.

🔮 Roadmap

 Implémentation du backend (connexion API GW2, récupération des données).

 Système d’optimisation des builds et compositions.

 Création du frontend (sélecteur de classes/joueurs, affichage des builds).

 Exportation/partage des compositions.

 Déploiement public (CI/CD).

📜 Licence

MIT – utilisation libre, avec attribution

---

👉 Veux-tu que je fasse aussi un **logo / bannière stylisée en ASCII ou image** pour ton projet (qui apparaîtra en haut du README sur GitHub) ? Ça peut donner un côté pro et attractif.

