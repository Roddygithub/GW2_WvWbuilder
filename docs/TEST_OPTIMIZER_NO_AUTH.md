# Test Optimizer - Sans Authentification

**Date**: 2025-10-17  
**Durée**: 2 minutes

---

## 🚀 Accès Direct à l'Optimizer

L'optimizer peut être testé **sans authentification** en accédant directement à l'URL.

### Méthode 1: URL Directe (Recommandé)

1. **Ouvrir le navigateur**
2. **Aller à**: http://localhost:5173/optimize
3. **Si redirection vers login**: Modifier temporairement le code

---

## 🔧 Désactiver Temporairement l'Authentification

### Option A: Modifier ProtectedRoute (Temporaire)

**Fichier**: `frontend/src/components/ProtectedRoute.tsx`

```tsx
// Commenter temporairement la vérification
export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  // const token = localStorage.getItem("access_token");
  // if (!token) {
  //   return <Navigate to="/login" replace />;
  // }
  return <>{children}</>;
}
```

### Option B: Modifier App.tsx (Temporaire)

**Fichier**: `frontend/src/App.tsx`

Remplacer la route `/optimize` pour retirer `ProtectedRoute`:

```tsx
{/* Optimizer sans auth (temporaire) */}
<Route
  path="/optimize"
  element={
    <MainLayout>
      <OptimizePage />
    </MainLayout>
  }
/>
```

---

## ✅ Test Rapide (Sans Login)

### 1. Accéder à l'Optimizer
- URL: http://localhost:5173/optimize
- Devrait afficher la page avec 15 joueurs et 3 groupes

### 2. Tester l'Optimisation
1. Cliquer sur "Lancer l'optimisation"
2. Observer:
   - Status: `queued` → `running` → `complete`
   - Job ID s'affiche
   - Temps écoulé: ~2000ms
   - Joueurs réassignés à différents builds
   - Coverage badges mis à jour

### 3. Tester le Drag-and-Drop
1. Cliquer sur un joueur (icône ⋮⋮)
2. Glisser vers un autre groupe
3. Relâcher
4. Observer:
   - Joueur se déplace
   - Coverage se recalcule
   - Warnings apparaissent si contraintes non satisfaites

---

## 🐛 Fix Permanent du Login (Pour Plus Tard)

Le problème actuel est que le frontend envoie les données de login en **FormData** au lieu de **JSON**.

### Fichier à corriger: `frontend/src/pages/Login.tsx`

**Problème actuel**:
```tsx
const formData = new FormData();
formData.append("email", data.email);
formData.append("password", data.password);
```

**Solution**:
```tsx
const response = await fetch("/api/v1/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: data.email,
    password: data.password,
  }),
});
```

---

## 📝 Commandes Utiles

### Vérifier Backend
```bash
curl http://localhost:8000/api/v1/health
```

### Vérifier Frontend
```bash
curl -I http://localhost:5173/
```

### Tester Optimizer API Directement
```bash
# Créer un test
curl -X POST http://localhost:8000/api/v1/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "players": [
      {"id": 1, "name": "Player1", "eligible_build_ids": [101, 102, 103]},
      {"id": 2, "name": "Player2", "eligible_build_ids": [101, 102, 103]},
      {"id": 3, "name": "Player3", "eligible_build_ids": [101, 102, 103]},
      {"id": 4, "name": "Player4", "eligible_build_ids": [101, 102, 103]},
      {"id": 5, "name": "Player5", "eligible_build_ids": [101, 102, 103]}
    ],
    "builds": [
      {"id": 101, "profession": "Guardian", "specialization": "Firebrand", "mode": "wvw"},
      {"id": 102, "profession": "Engineer", "specialization": "Scrapper", "mode": "wvw"},
      {"id": 103, "profession": "Revenant", "specialization": "Herald", "mode": "wvw"}
    ],
    "mode": "wvw",
    "squad_size": 5,
    "targets": {
      "quickness_uptime": 0.5,
      "alacrity_uptime": 0.5,
      "resistance_uptime": 0.4,
      "protection_uptime": 0.3,
      "stability_sources": 0
    },
    "time_limit_ms": 2000
  }'

# Récupérer le job_id de la réponse, puis:
curl -N http://localhost:8000/api/v1/optimize/stream/{job_id}
```

---

## 🎯 Checklist de Test (Sans Auth)

- [ ] Page `/optimize` accessible directement
- [ ] 15 joueurs et 3 groupes affichés
- [ ] Bouton "Lancer l'optimisation" fonctionne
- [ ] Status change: idle → queued → running → complete
- [ ] Job ID s'affiche dans le panneau Live
- [ ] Coverage badges se mettent à jour
- [ ] Drag-and-drop fonctionne (joueur se déplace)
- [ ] Coverage se recalcule après DnD
- [ ] Warnings s'affichent si contraintes non satisfaites
- [ ] Bouton "Recalculer" fonctionne
- [ ] Pas d'erreurs dans la console DevTools

---

## 🔄 Remettre l'Authentification

Une fois les tests terminés, **ne pas oublier** de remettre `ProtectedRoute` dans `App.tsx` ou de décommenter la vérification dans `ProtectedRoute.tsx`.

---

## 📚 Documentation Complète

- **Guide complet**: `docs/OPTIMIZER_DND_V3.7_GUIDE.md`
- **Quick start**: `docs/QUICK_START_OPTIMIZER.md`
- **Implementation**: `docs/OPTIMIZER_V3.7_IMPLEMENTATION.md`

---

**Bon test ! 🚀**

L'optimizer est pleinement fonctionnel même sans authentification. Tu peux tester toutes les fonctionnalités DnD et SSE sans te soucier du login pour l'instant.
