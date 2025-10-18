# GW2Optimizer – Frontend Specifications v1.0

**Date**: 2025-10-18  
**Version**: 1.0  
**Status**: 🚀 Ready for Implementation  

---

## 1️⃣ Objectif Général

Créer un frontend moderne, clair, responsive, aux couleurs de Guild Wars 2, qui remplace totalement l'ancien GW2_WvWbuilder.

### Fonctionnalités Clés
- ✅ Interaction directe avec **Mistral 7B** via chatbox
- ✅ Visualisation compositions optimales (cards interactives)
- ✅ Suivi évolution méta via **Meta Evolution Dashboard**
- ✅ Sélection builds alternative à Skilleditor
- ✅ Intégration complète backend existant

---

## 2️⃣ Charte Graphique GW2

### Palette de Couleurs

| Élément | Couleur | Hex | Usage |
|---------|---------|-----|-------|
| **Primaire** | Rouge GW2 | `#b02c2c` | Boutons, accents, liens |
| **Secondaire** | Or GW2 | `#d4af37` | Highlights, badges premium |
| **Fond Principal** | Gris sombre | `#1f1f1f` | Background app |
| **Fond Cards** | Gris moyen | `#2c2c2c` | Cards, panels |
| **Texte Normal** | Blanc | `#ffffff` | Texte principal |
| **Texte Secondaire** | Gris clair | `#aaaaaa` | Labels, descriptions |
| **Success / Buff** | Vert | `#4caf50` | Buffs, succès |
| **Warning** | Orange | `#ff9800` | Alertes |
| **Danger / Nerf** | Rouge vif | `#f44336` | Nerfs, erreurs |
| **Border** | Gris foncé | `#3a3a3a` | Bordures cards |

### Design System

```typescript
// Tailwind Config
colors: {
  gw2: {
    red: '#b02c2c',
    gold: '#d4af37',
    dark: '#1f1f1f',
    cardBg: '#2c2c2c',
    border: '#3a3a3a',
  },
  success: '#4caf50',
  warning: '#ff9800',
  danger: '#f44336',
}

borderRadius: {
  card: '12px',
}

spacing: {
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
}
```

### Typographie

- **Police principale**: `font-family: 'Inter', sans-serif`
- **H1**: 32px, bold, `#d4af37` (or)
- **H2**: 24px, bold, `#ffffff`
- **H3**: 20px, semi-bold, `#ffffff`
- **Body**: 16px, normal, `#ffffff`
- **Caption**: 14px, normal, `#aaaaaa`

---

## 3️⃣ Architecture Composants React

### Structure Dossiers

```
frontend/src/
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   └── MainLayout.tsx
│   ├── chat/
│   │   ├── ChatBox.tsx
│   │   ├── ChatMessage.tsx
│   │   └── ChatInput.tsx
│   ├── squad/
│   │   ├── SquadCard.tsx
│   │   ├── BuildBadge.tsx
│   │   └── SynergyIndicator.tsx
│   ├── meta/
│   │   ├── MetaEvolutionGraph.tsx
│   │   ├── SynergyHeatmap.tsx
│   │   └── PatchTimeline.tsx
│   └── builds/
│       ├── BuildSelector.tsx
│       └── BuildCard.tsx
├── pages/
│   ├── HomePage.tsx
│   ├── MetaEvolutionPage.tsx
│   └── (suppression anciennes pages)
├── api/
│   ├── compositions.ts
│   ├── metaEvolution.ts
│   └── builds.ts
├── types/
│   ├── squad.ts
│   ├── meta.ts
│   └── build.ts
└── styles/
    └── gw2-theme.css
```

### Pages

| Page | Route | Composants | Fonctionnalité |
|------|-------|------------|----------------|
| **Home** | `/` | Header, ChatBox, SquadCard, Badges | Chat + Compositions |
| **Meta Evolution** | `/meta` | Header, MetaGraph, Heatmap, Timeline | Visualisation méta |
| **Build Selector** | Modal | BuildSelector, BuildCard | Sélection builds |

---

## 4️⃣ Composants Détaillés

### Header

**Fichier**: `components/layout/Header.tsx`

**Props**: Aucune

**Design**:
```
┌─────────────────────────────────────────────────────────┐
│ 🔥 GW2Optimizer                    Empowered by Ollama   │
│                                    with Mistral 7B       │
└─────────────────────────────────────────────────────────┘
```

**Couleurs**:
- Background: `#1f1f1f`
- Logo: `#d4af37` (or)
- Mention: `#aaaaaa` (gris clair)

---

### ChatBox

**Fichier**: `components/chat/ChatBox.tsx`

**Props**:
```typescript
interface ChatBoxProps {
  onSendMessage: (message: string) => Promise<void>;
  messages: ChatMessage[];
  isLoading?: boolean;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}
```

**Design**:
```
┌────────────────────────────────────────┐
│ Messages Area (scroll)                  │
│ ┌──────────────────────────────────┐   │
│ │ User: Compo pour 15 joueurs      │   │
│ └──────────────────────────────────┘   │
│ ┌──────────────────────────────────┐   │
│ │ AI: Voici la composition...      │   │
│ └──────────────────────────────────┘   │
├────────────────────────────────────────┤
│ [Input] Demandez une compo...    [→]  │
└────────────────────────────────────────┘
```

**Couleurs**:
- Background: `#2c2c2c`
- User message: `#3a3a3a`
- AI message: `#2c2c2c` avec border `#d4af37`
- Input: `#1f1f1f`

---

### SquadCard

**Fichier**: `components/squad/SquadCard.tsx`

**Props**:
```typescript
interface SquadCardProps {
  name: string;
  builds: BuildInfo[];
  weight: number;
  synergy: number;
  buffs: string[];
  nerfs: string[];
  timestamp: string;
}

interface BuildInfo {
  id: string;
  profession: string;
  specialization: string;
  role: string;
  weight: number;
}
```

**Design**:
```
┌──────────────────────────────────────────────┐
│ Squad Alpha - 15 joueurs                      │
│ Weight: 0.95 | Synergy: 0.87 | 12:34         │
├──────────────────────────────────────────────┤
│ 🛡️ Firebrand x3  📈 Scrapper x2  ⚔️ Herald x2│
│ 🔮 Scourge x3    🔧 Mechanist x2  ⚡ Weaver x3│
├──────────────────────────────────────────────┤
│ 📈 Buffs: +15% Quickness, +20% Stability     │
│ 📉 Nerfs: -10% Firebrand (patch 2025-10-15) │
└──────────────────────────────────────────────┘
```

**Couleurs**:
- Background: `#2c2c2c`
- Border: `#3a3a3a`
- Buffs: `#4caf50` (vert)
- Nerfs: `#f44336` (rouge)
- Weight/Synergy: `#d4af37` (or)

---

### MetaEvolutionGraph

**Fichier**: `components/meta/MetaEvolutionGraph.tsx`

**Props**:
```typescript
interface MetaEvolutionGraphProps {
  data: MetaDataPoint[];
  selectedSpecs?: string[];
}

interface MetaDataPoint {
  timestamp: string;
  weights: Record<string, number>; // { "firebrand": 0.85, ... }
}
```

**Design**: LineChart Recharts
- X-axis: Timestamp
- Y-axis: Weight [0.1, 2.0]
- Lignes: Top 5 specs colorées

**Couleurs**:
- Firebrand: `#b02c2c` (rouge)
- Scrapper: `#4caf50` (vert)
- Herald: `#d4af37` (or)
- Scourge: `#9c27b0` (violet)
- Mechanist: `#2196f3` (bleu)

---

### BuildSelector

**Fichier**: `components/builds/BuildSelector.tsx`

**Props**:
```typescript
interface BuildSelectorProps {
  onSelect: (buildId: string) => void;
  onClose: () => void;
}
```

**Design**:
```
┌─────────────────────────────────────┐
│ Select Build                     [X] │
├─────────────────────────────────────┤
│ Filter: [Guardian ▼] [Support ▼]    │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ 🛡️ Firebrand Support             │ │
│ │ Weight: 0.85 | Synergy: High    │ │
│ │ [Select]                        │ │
│ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────┐ │
│ │ ⚔️ Willbender DPS                │ │
│ │ Weight: 0.92 | Synergy: Medium  │ │
│ │ [Select]                        │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 5️⃣ Flux des Données / API Integration

### Chat → Compositions

**Endpoint**: `POST /api/v1/compositions`

**Request**:
```json
{
  "prompt": "Composition optimale pour 15 joueurs zerg",
  "squad_size": 15,
  "mode": "zerg"
}
```

**Response**:
```json
{
  "squads": [
    {
      "name": "Squad Alpha",
      "builds": [
        { "profession": "Guardian", "spec": "Firebrand", "count": 3 },
        { "profession": "Engineer", "spec": "Scrapper", "count": 2 }
      ],
      "weight": 0.95,
      "synergy": 0.87,
      "buffs": ["Quickness +15%", "Stability +20%"],
      "nerfs": ["Firebrand -10% (2025-10-15)"],
      "timestamp": "2025-10-18T12:45:00"
    }
  ]
}
```

### Meta Evolution

**Endpoint**: `GET /api/v1/meta/weights`

**Response**:
```json
{
  "firebrand": 0.85,
  "scrapper": 1.10,
  "herald": 0.95,
  ...
}
```

**Endpoint**: `GET /api/v1/meta/synergies`

**Response**:
```json
{
  "firebrand-scrapper": 0.90,
  "herald-mechanist": 0.85,
  ...
}
```

### Build Selector

**Endpoint**: `GET /api/v1/builds`

**Response**:
```json
{
  "builds": [
    {
      "id": "101",
      "profession": "Guardian",
      "specialization": "Firebrand",
      "role": "Support",
      "weight": 0.85,
      "synergy": "high"
    },
    ...
  ]
}
```

---

## 6️⃣ Wireframes / Layout

### Home Page

```
┌───────────────────────────────────────────────────────────────┐
│ Header: GW2Optimizer | Empowered by Ollama with Mistral 7B    │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ChatBox                                                   │ │
│  │ ┌────────────────────────────────────────────────────┐   │ │
│  │ │ User: Compo pour 15 joueurs zerg                   │   │ │
│  │ └────────────────────────────────────────────────────┘   │ │
│  │ ┌────────────────────────────────────────────────────┐   │ │
│  │ │ AI: Voici la composition optimale...               │   │ │
│  │ └────────────────────────────────────────────────────┘   │ │
│  │ [Input: Demandez une composition...] [Envoyer]           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ SquadCard: Squad Alpha                                   │ │
│  │ Weight: 0.95 | Synergy: 0.87                             │ │
│  │ 🛡️ Firebrand x3 | 📈 Scrapper x2 | ⚔️ Herald x2          │ │
│  │ Buffs: +15% Quick | Nerfs: -10% FB                      │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ SquadCard: Squad Beta                                    │ │
│  │ ...                                                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

### Meta Evolution Page

```
┌───────────────────────────────────────────────────────────────┐
│ Header: GW2Optimizer | Meta Evolution                         │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ LineChart: Évolution Poids des Builds                    │ │
│  │                                                           │ │
│  │  2.0 ┤                                     Firebrand ──── │ │
│  │  1.5 ┤                     Scrapper ──────────           │ │
│  │  1.0 ┼─────────────────────────────────────────────────  │ │
│  │  0.5 ┤           Herald ───────                          │ │
│  │  0.0 └──────────────────────────────────────────────────  │ │
│  │       Oct 1    Oct 8    Oct 15   Oct 18                  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Heatmap: Top Synergies                                   │ │
│  │ FB-Scrap: 0.90 ████████░                                 │ │
│  │ Her-Mech: 0.85 ███████░░                                 │ │
│  │ Scou-Temp: 0.82 ██████░░░                                │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Timeline: Recent Patch Notes                             │ │
│  │ 📉 2025-10-15: Firebrand quickness -15%                  │ │
│  │ 📈 2025-10-12: Mechanist barrier +20%                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

### BuildSelector Modal

```
┌─────────────────────────────────────┐
│ Select Build                     [X] │
├─────────────────────────────────────┤
│ Filter by:                           │
│ Class: [Guardian ▼]                  │
│ Role:  [Support ▼]                   │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ 🛡️ Firebrand Support             │ │
│ │ Weight: 0.85 | Synergy: High    │ │
│ │ [Select Build]                  │ │
│ └─────────────────────────────────┘ │
│                                      │
│ ┌─────────────────────────────────┐ │
│ │ ⚔️ Willbender DPS                │ │
│ │ Weight: 0.92 | Synergy: Medium  │ │
│ │ [Select Build]                  │ │
│ └─────────────────────────────────┘ │
│                                      │
│ ┌─────────────────────────────────┐ │
│ │ 🔮 Dragonhunter DPS              │ │
│ │ Weight: 0.88 | Synergy: Low     │ │
│ │ [Select Build]                  │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 7️⃣ Types TypeScript

**Fichier**: `types/squad.ts`

```typescript
export interface Squad {
  id: string;
  name: string;
  builds: BuildInfo[];
  weight: number;
  synergy: number;
  buffs: string[];
  nerfs: string[];
  timestamp: string;
}

export interface BuildInfo {
  id: string;
  profession: string;
  specialization: string;
  role: string;
  count: number;
  weight: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}
```

**Fichier**: `types/meta.ts`

```typescript
export interface MetaDataPoint {
  timestamp: string;
  weights: Record<string, number>;
}

export interface SynergyPair {
  spec1: string;
  spec2: string;
  score: number;
}

export interface PatchNote {
  date: string;
  spec: string;
  change_type: 'nerf' | 'buff' | 'rework';
  impact: string;
  magnitude?: string;
}
```

---

## 8️⃣ Ordre d'Implémentation

### ✅ Étape 1: Spécifications (COMPLÉTÉ)
- Document détaillé
- Charte graphique
- Wireframes

### 🔄 Étape 2: Architecture
- Configuration Tailwind (couleurs GW2)
- Types TypeScript
- Structure dossiers

### 🔄 Étape 3: Header + ChatBox
- Header avec logo
- ChatBox fonctionnelle
- API client compositions

### ⏳ Étape 4: SquadCard + Badges
- SquadCard design
- Badges buffs/nerfs
- Synergy indicators

### ⏳ Étape 5: BuildSelector
- Modal BuildSelector
- Filtres classe/rôle
- Sélection builds

### ⏳ Étape 6: Meta Evolution
- LineChart évolution poids
- Heatmap synergies
- Timeline patch notes

### ⏳ Étape 7: Intégration Backend
- Tests endpoints
- Gestion états
- Error handling

### ⏳ Étape 8: Style & UX
- Responsive design
- Animations
- Polish UI

### ⏳ Étape 9: Tests
- Unit tests composants
- Integration tests
- E2E tests

### ⏳ Étape 10: Documentation
- README frontend
- Storybook composants
- Guide développeur

---

## 9️⃣ Notes Techniques

### Stack Technologique
- **Framework**: React 18 + TypeScript
- **UI Library**: shadcn/ui
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **State Management**: React Context + Hooks
- **API Client**: Axios
- **Icons**: Lucide React

### Bonnes Pratiques
- ✅ Props bien typés (TypeScript strict)
- ✅ Composants réutilisables
- ✅ Responsive design (mobile-first)
- ✅ Accessibilité (ARIA labels)
- ✅ Performance (React.memo, useMemo)
- ✅ Error boundaries
- ✅ Loading states

### Configuration Requise

**Tailwind Config** (`tailwind.config.js`):
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        gw2: {
          red: '#b02c2c',
          gold: '#d4af37',
          dark: '#1f1f1f',
          cardBg: '#2c2c2c',
          border: '#3a3a3a',
        },
      },
    },
  },
}
```

**Dépendances** (`package.json`):
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "recharts": "^2.10.0",
    "axios": "^1.6.0",
    "lucide-react": "^0.294.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-select": "^2.0.0"
  }
}
```

---

## 🔟 Suppression Ancien Code

### Fichiers à Supprimer
```
frontend/src/pages/
├─ BuildsPage.tsx ❌
├─ ProfessionsPage.tsx ❌
├─ CompositionsPage.tsx ❌
├─ OptimizePage.tsx ❌ (remplacé par HomePage)
└─ (tous anciens composants forms/selects)
```

### Fichiers à Conserver
```
frontend/src/
├─ App.tsx ✅ (refactor routes)
├─ main.tsx ✅
├─ components/layout/MainLayout.tsx ✅
└─ api/ ✅ (refactor endpoints)
```

---

## ✅ Checklist Validation

Avant de passer à l'étape suivante :
- [ ] Spécifications validées
- [ ] Wireframes approuvés
- [ ] Charte graphique confirmée
- [ ] Architecture composants validée
- [ ] API endpoints confirmés disponibles

---

**STATUS**: 🚀 Prêt pour Étape 2 - Architecture & Setup

**Next**: Configuration Tailwind + Types TypeScript + Structure dossiers
