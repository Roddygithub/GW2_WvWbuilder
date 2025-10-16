# Thème Guild Wars 2 - Guide d'Utilisation

**Date**: 2025-10-17 01:06 UTC+2  
**Version**: v3.4.5  
**Type**: UI/UX Redesign avec palette GW2 officielle

---

## 🎨 Palette de Couleurs GW2

### Couleurs Principales

**Or GW2** (Couleur iconique):
- `--primary: 45 100% 51%` → #FFC107
- Utilisation: Boutons primaires, titres, accents
- Inspiration: Or des récompenses GW2

**Fractal Dark** (Fond sombre):
- `--background: 210 15% 8%` → #0D1117
- Utilisation: Fond principal en mode dark
- Inspiration: Fractales des Brumes

**Rouge GW2** (Destructif):
- `--destructive: 0 80% 50%` → #FF0000
- Utilisation: Actions de suppression, erreurs
- Inspiration: Couleur des ennemis

**Bronze/Cuivre** (Secondaire):
- `--secondary: 30 50% 60%` → Tons bronze
- Utilisation: Boutons secondaires, badges
- Inspiration: Monnaie GW2

---

## 🌓 Mode Clair vs Sombre

### Light Mode - "Tyria"
- Fond: Parchemin clair (#F5F5F5)
- Texte: Noir doux
- Cartes: Blanc cassé avec bordures dorées subtiles
- Inspiration: Cartes de Tyria, parchemins

### Dark Mode - "Fractales" ✨
- Fond: Noir-bleu fractal (#0D1117)
- Texte: Doré clair
- Cartes: Gris foncé avec reflets dorés
- Inspiration: Fractales des Brumes, UI in-game

---

## 🎯 Classes CSS Utilitaires GW2

### `.gw2-button`
Bouton principal avec style GW2
```tsx
<button className="gw2-button">
  Créer un Build
</button>
```
- Fond or brillant
- Hover: Scale + glow
- Transition fluide

### `.gw2-button-secondary`
Bouton secondaire bronze
```tsx
<button className="gw2-button-secondary">
  Annuler
</button>
```

### `.gw2-card`
Carte avec gradient doré subtil
```tsx
<div className="gw2-card p-6">
  Contenu de la carte
</div>
```

### `.gw2-gold-glow`
Effet lumineux doré
```tsx
<div className="gw2-gold-glow">
  Élément avec glow
</div>
```

### `.gw2-fractal-bg`
Fond style fractales
```tsx
<div className="gw2-fractal-bg">
  Section avec fond fractal
</div>
```

### `.gw2-tyria-pattern`
Motif répétitif doré
```tsx
<div className="gw2-tyria-pattern">
  Background avec pattern
</div>
```

---

## 🎨 Exemple d'Utilisation

### Page Login avec Thème GW2

```tsx
<div className="min-h-screen gw2-fractal-bg flex items-center justify-center">
  <div className="gw2-card max-w-md w-full p-8">
    <h1 className="text-3xl mb-6 text-center">
      Connexion WvW Builder
    </h1>
    
    <form className="space-y-4">
      <input
        type="email"
        placeholder="Email"
        className="w-full px-4 py-2 bg-input border border-border rounded-md
                   focus:ring-2 focus:ring-primary"
      />
      
      <button type="submit" className="gw2-button w-full py-3">
        Se connecter
      </button>
      
      <button type="button" className="gw2-button-secondary w-full py-3">
        Créer un compte
      </button>
    </form>
  </div>
</div>
```

### Dashboard avec Cards GW2

```tsx
<div className="gw2-tyria-pattern min-h-screen p-8">
  <h1 className="text-4xl mb-8">Dashboard WvW</h1>
  
  <div className="grid grid-cols-3 gap-6">
    <div className="gw2-card gw2-gold-glow p-6">
      <h3 className="text-xl mb-2">Mes Builds</h3>
      <p className="text-muted-foreground">42 builds actifs</p>
    </div>
    
    <div className="gw2-card p-6">
      <h3 className="text-xl mb-2">Compositions</h3>
      <p className="text-muted-foreground">15 compositions</p>
    </div>
    
    <div className="gw2-card p-6">
      <h3 className="text-xl mb-2">Équipes</h3>
      <p className="text-muted-foreground">3 équipes</p>
    </div>
  </div>
</div>
```

---

## 🌟 Améliorations Visuelles

### Avant (Générique shadcn/ui)
- ❌ Bleu/gris générique
- ❌ Pas d'identité GW2
- ❌ Fade et sans personnalité
- ❌ Ressemble à n'importe quelle app

### Après (Thème GW2)
- ✅ Or doré iconique
- ✅ Fond fractal immersif
- ✅ Identité GW2 claire
- ✅ Interface premium
- ✅ Glow effects subtils
- ✅ Transitions fluides

---

## 📱 Responsive & Dark Mode

### Responsive
- Mobile: Gradients simplifiés
- Tablet: Layout adaptatif
- Desktop: Tous les effets actifs

### Toggle Dark/Light
```tsx
import { useTheme } from 'next-themes'

function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  
  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      {theme === 'dark' ? '☀️ Tyria' : '🌙 Fractales'}
    </button>
  )
}
```

---

## 🎮 Inspiration GW2 Officielle

### UI In-Game
- **Inventaire**: Fond sombre avec bordures dorées → Cartes
- **Menu Hero**: Titres en or → Headings h1-h6
- **Boutique gemmes**: Boutons dorés → .gw2-button
- **Fractales**: Ambiance sombre bleue → Dark mode
- **Récompenses**: Éclat doré → .gw2-gold-glow

### Palette Exacte GW2
```css
/* Or récompense */
--gw2-gold: #FFC107;

/* Rouge ennemi */
--gw2-red: #B71C1C;

/* Fractal bleu-noir */
--gw2-fractal: #0D1117;

/* Parchemin Tyria */
--gw2-parchment: #F5F5F5;
```

---

## 🔧 Customisation Avancée

### Ajouter une Nouvelle Couleur GW2

Dans `tailwind.config.js`:
```js
gw2: {
  emerald: {
    DEFAULT: '#00BC8C', // Jade Maw
    light: '#26FFCA',
    dark: '#008060',
  }
}
```

### Créer un Nouveau Style de Carte

Dans `index.css`:
```css
.gw2-card-legendary {
  @apply gw2-card;
  border: 2px solid theme('colors.primary');
  box-shadow: 0 0 20px rgba(255, 193, 7, 0.5);
  animation: pulse 2s infinite;
}
```

---

## ✨ Animations GW2

### Glow Pulse (Légendaire)
```css
@keyframes gw2-legendary-glow {
  0%, 100% { box-shadow: 0 0 10px rgba(255, 193, 7, 0.3); }
  50% { box-shadow: 0 0 25px rgba(255, 193, 7, 0.6); }
}

.gw2-legendary {
  animation: gw2-legendary-glow 2s ease-in-out infinite;
}
```

### Hover Scale (Interaction)
```css
.gw2-interactive {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.gw2-interactive:hover {
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(255, 193, 7, 0.4);
}
```

---

## 📸 Avant/Après

### Dashboard
**Avant**: Fond blanc/gris, boutons bleus, pas d'identité  
**Après**: Fond fractal, boutons dorés, cartes avec glow, immersion GW2

### Formulaires
**Avant**: Inputs blancs génériques  
**Après**: Inputs avec bordure dorée au focus, placeholders stylés

### Boutons
**Avant**: Bleu plat sans personnalité  
**Après**: Or brillant avec hover scale et glow

---

## 🚀 Migration Rapide

Pour migrer un composant existant vers le thème GW2:

### Étape 1: Remplacer les Boutons
```tsx
// Avant
<Button variant="default">Action</Button>

// Après
<button className="gw2-button">Action</button>
```

### Étape 2: Styliser les Cartes
```tsx
// Avant
<Card>Contenu</Card>

// Après
<div className="gw2-card p-6">Contenu</div>
```

### Étape 3: Ajouter les Effets
```tsx
// Ajouter glow sur éléments importants
<div className="gw2-gold-glow">Important</div>

// Ajouter pattern de fond
<div className="gw2-tyria-pattern">Section</div>
```

---

## 🎯 Checklist UI/UX GW2

### Must Have ✅
- [x] Couleurs or/fractal appliquées
- [x] Dark mode style Fractales
- [x] Boutons dorés avec hover
- [x] Cartes avec bordures subtiles
- [x] Titres en or
- [x] Transitions fluides

### Nice to Have
- [ ] Logo GW2-style
- [ ] Icons professions GW2
- [ ] Animations d'apparition
- [ ] Sounds effects (optionnel)
- [ ] Easter eggs GW2

---

## 🔗 Ressources

**Palette GW2 officielle**:
- https://wiki.guildwars2.com/wiki/UI
- In-game screenshots référence

**Inspiration UI**:
- Fractales des Brumes
- Trading Post
- Hero Panel
- WvW Map UI

**Fonts similaires**:
- Inter (actuel) - bon compromis
- Roboto Condensed - style GW2
- Exo - futuriste comme GW2

---

## 📝 Notes de Version

**v3.4.5** (2025-10-17):
- ✅ Thème GW2 complet implémenté
- ✅ Dark mode Fractales
- ✅ Light mode Tyria
- ✅ Classes utilitaires GW2
- ✅ Animations et effets
- ✅ Documentation complète

**Prochaines améliorations**:
- Animations avancées
- Micro-interactions
- Sons d'UI (optionnel)
- Plus de variantes de cartes

---

**Créé**: 2025-10-17 01:06 UTC+2  
**Auteur**: Claude (Cascade AI)  
**Version**: v3.4.5  
**Statut**: ✅ Thème GW2 Appliqué
