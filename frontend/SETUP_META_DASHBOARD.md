# 🎨 Setup Meta Evolution Dashboard

Guide pour finaliser l'installation du dashboard Meta Evolution v4.3.

---

## 📦 Composants shadcn/ui Requis

Le dashboard utilise des composants shadcn/ui. Installez-les avec :

```bash
cd frontend

# Card (pour les widgets stats)
npx shadcn-ui@latest add card

# Badge (pour les labels nerf/buff)
npx shadcn-ui@latest add badge

# Tabs (pour navigation entre vues)
npx shadcn-ui@latest add tabs

# Alert (pour les notifications changements)
npx shadcn-ui@latest add alert
```

---

## 🔧 Installation Recharts

Le dashboard utilise Recharts pour les graphes temporels :

```bash
npm install recharts
# ou
yarn add recharts
# ou
pnpm add recharts
```

---

## ⚙️ Vérifier Configuration

### 1. Query Client (React Query)

Vérifiez que `@tanstack/react-query` est configuré dans `src/main.tsx` ou `src/App.tsx` :

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Dans votre composant racine
<QueryClientProvider client={queryClient}>
  <App />
</QueryClientProvider>
```

### 2. API Client Base URL

Vérifiez que `src/api/client.ts` pointe vers le bon endpoint :

```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});
```

---

## 🚀 Démarrer le Dashboard

```bash
# Terminal 1 : Backend
cd backend
poetry run uvicorn app.main:app --reload

# Terminal 2 : Frontend
cd frontend
npm run dev
```

**Accès** : http://localhost:5173/meta-evolution

---

## 🎯 Fonctionnalités du Dashboard

### 1. **Stats Overview**
- Total specs tracked
- Average weight
- Active synergies
- History entries

### 2. **Timeline Graph**
- Évolution temporelle des poids
- Top 5 specs affichées
- Zoom/pan sur période

### 3. **Current Weights**
- **Top Specs** : Les plus performantes
- **Bottom Specs** : Les plus nerfées/sous-performantes
- Tri dynamique

### 4. **Synergies Heatmap**
- Top 15 paires de synergies
- Score visuel [0-100%]
- Filtrage par spec

### 5. **History Timeline**
- 10 derniers ajustements
- Reasoning LLM complet
- Source tracking (patch_analysis, manual, rollback)

### 6. **Recent Changes Alert**
- Badges visuels nerf/buff
- Delta affiché
- Auto-update 30s

---

## 🔄 Auto-Refresh

Le dashboard se rafraîchit automatiquement :
- **Stats** : 30s
- **Weights** : 30s
- **Synergies** : 30s
- **History** : 60s
- **Changes** : 60s

---

## 🐛 Troubleshooting

### Erreur : Cannot find module '@/components/ui/...'

**Solution** : Installez les composants shadcn/ui manquants :
```bash
npx shadcn-ui@latest add card badge tabs alert
```

### Erreur : axios undefined

**Solution** : Installez axios :
```bash
npm install axios
```

### Erreur : React Query not working

**Solution** : Vérifiez QueryClientProvider dans main.tsx :
```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
);
```

### Dashboard vide (No data)

**Solution** : Exécutez le système adaptatif pour générer des données :
```bash
cd backend
poetry run python app/ai/adaptive_meta_runner.py --with-llm
```

---

## 📊 Structure Composants

```
MetaEvolutionPage.tsx
├── Stats Overview (4 Cards)
│   ├── Total Specs
│   ├── Avg Weight
│   ├── Synergies Count
│   └── History Entries
│
├── Recent Changes Alert
│   └── Badges nerf/buff dynamiques
│
└── Tabs Navigation
    ├── Timeline (LineChart Recharts)
    │   └── Top 5 specs over time
    │
    ├── Current Weights
    │   ├── Top Specs Card
    │   └── Bottom Specs Card
    │
    ├── Synergies
    │   └── Top 15 pairs with bars
    │
    └── History
        └── Last 10 adjustments with reasoning
```

---

## 🎨 Personnalisation

### Modifier le nombre de specs affichées

Dans `MetaEvolutionPage.tsx` :

```typescript
// Ligne ~270 : Top specs dans le graphe
{stats?.top_specs.slice(0, 5).map(...)}
// Changez 5 pour afficher plus/moins

// Ligne ~320 : Synergies affichées
{synergies?.slice(0, 15).map(...)}
// Changez 15 pour plus/moins de paires
```

### Changer l'intervalle de refresh

```typescript
// Ligne ~45-60
refetchInterval: 30000, // 30s en millisecondes
// Changez selon vos besoins (10000 = 10s, 60000 = 1min)
```

---

## ✅ Checklist Installation

- [ ] shadcn/ui components installés (card, badge, tabs, alert)
- [ ] Recharts installé
- [ ] QueryClient configuré
- [ ] API client baseURL correct
- [ ] Backend démarré (port 8000)
- [ ] Frontend démarré (port 5173)
- [ ] Route /meta-evolution accessible
- [ ] Données générées (run adaptive_meta_runner.py)

---

## 🔗 Liens Utiles

- [shadcn/ui Docs](https://ui.shadcn.com/)
- [Recharts Docs](https://recharts.org/)
- [React Query Docs](https://tanstack.com/query/latest/docs/react/overview)
- [Backend API Swagger](http://localhost:8000/docs)

---

**Version** : v4.3.1  
**Auteur** : Roddy + Claude  
**Status** : Dashboard UI prêt, installation finale requise
