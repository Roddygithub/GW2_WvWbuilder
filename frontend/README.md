# GW2 WvW Builder - Frontend

Ce dossier contient le code source du frontend pour l'application GW2 WvW Builder. L'application est développée avec React (Vite) et TypeScript.

## Stack Technique

- **Framework**: React 18 (avec Vite)
- **Langage**: TypeScript
- **Styling**: TailwindCSS
- **UI Components**: Radix UI, Lucide React
- **Gestion d'état**: TanStack (React) Query
- **Routage**: React Router
- **Formulaires**: React Hook Form
- **Validation de Schéma**: Zod
- **Tests**: Vitest, React Testing Library

## Démarrage Rapide

### Prérequis

- Node.js 18+
- Yarn (ou npm/pnpm)

### Installation

1.  Naviguez vers le dossier `frontend` :
    ```bash
    cd frontend
    ```

2.  Installez les dépendances :
    ```bash
    yarn install
    ```

### Lancer le serveur de développement

Pour lancer l'application en mode développement avec rechargement automatique :

```bash
yarn dev
```

L'application sera accessible à l'adresse `http://localhost:5173` (ou un autre port si celui-ci est occupé).

## Scripts Disponibles

- `yarn dev`: Lance le serveur de développement.
- `yarn build`: Compile et optimise l'application pour la production dans le dossier `dist/`.
- `yarn preview`: Sert le build de production localement pour le tester.
- `yarn test`: Lance les tests unitaires et d'intégration.
- `yarn test:coverage`: Lance les tests et génère un rapport de couverture.
- `yarn lint`: Analyse le code avec ESLint pour trouver des erreurs.
- `yarn format`: Formatte le code avec Prettier.

## Structure du Projet

```
frontend/
├── public/              # Fichiers statiques
├── src/
│   ├── components/      # Composants React réutilisables
│   ├── hooks/           # Hooks personnalisés
│   ├── pages/           # Pages principales de l'application
│   ├── services/        # Logique de communication API
│   ├── styles/          # Fichiers CSS/SCSS globaux
│   ├── types/           # Définitions de types TypeScript
│   ├── utils/           # Fonctions utilitaires
│   ├── App.tsx          # Composant racine
│   └── main.tsx         # Point d'entrée de l'application
├── package.json         # Dépendances et scripts
└── tsconfig.json        # Configuration TypeScript
```

## Contribution

Les contributions sont les bienvenues. Veuillez suivre les conventions de code et de commit établies pour le projet.
