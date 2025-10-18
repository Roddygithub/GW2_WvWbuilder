# Quick Start - Optimizer WvW avec DnD

**Date**: 2025-10-17  
**Version**: v3.7.1  
**Durée**: 5 minutes

---

## 🚀 Démarrage Rapide

### 1. Vérifier que les serveurs sont en cours d'exécution

**Backend** (port 8000):
```bash
curl http://localhost:8000/api/v1/health
# Attendu: {"status":"ok","database":"ok","version":"1.0.0"}
```

**Frontend** (port 5173):
```bash
curl -I http://localhost:5173/
# Attendu: HTTP/1.1 200 OK
```

### 2. Se connecter

**Option A: Utiliser le compte de test existant**
- Email: `test@test.com`
- Password: `Test123!`

**Option B: Créer un nouveau compte**
1. Cliquer sur "Register here"
2. Remplir le formulaire
3. Se connecter avec les nouveaux identifiants

### 3. Accéder à l'Optimizer

Une fois connecté:
1. Naviguer vers `/optimize` dans l'URL ou via le menu
2. Ou accéder directement: http://localhost:5173/optimize

---

## 🎯 Test de l'Optimizer (5 scénarios)

### Scénario 1: Initialisation de base
1. **Action**: Ouvrir `/optimize`
2. **Attendu**:
   - 15 joueurs affichés (par défaut)
   - 3 groupes de 5
   - Tous les joueurs ont le build "Firebrand"
   - Coverage badges affichent des valeurs faibles

### Scénario 2: Lancer l'optimisation
1. **Action**: Cliquer sur "Lancer l'optimisation"
2. **Attendu**:
   - Status change: `idle` → `queued` → `running` → `complete`
   - Job ID s'affiche dans le panneau Live
   - Temps écoulé ~2000ms
   - Joueurs réassignés à différents builds
   - Coverage badges se mettent à jour
   - Score global augmente (ex: 0% → 60%)

### Scénario 3: Drag-and-Drop basique
1. **Prérequis**: Avoir lancé une optimisation
2. **Action**: 
   - Cliquer et maintenir sur un joueur (icône grip ⋮⋮)
   - Glisser vers un autre groupe
   - Relâcher
3. **Attendu**:
   - Le joueur se déplace vers le nouveau groupe
   - Coverage badges se recalculent instantanément
   - Warnings apparaissent si contraintes non satisfaites

### Scénario 4: Groupe plein (rejet)
1. **Prérequis**: Un groupe a 5 joueurs
2. **Action**: Essayer de glisser un 6ème joueur dans ce groupe
3. **Attendu**:
   - Le groupe ne s'illumine pas au survol
   - Le joueur ne peut pas être déposé
   - Le joueur reste dans son groupe d'origine

### Scénario 5: Warnings de contraintes
1. **Action**: Créer une composition avec tous Scourge (pas de quickness/stability)
2. **Méthode**:
   - Changer la taille d'escouade à 5
   - Lancer l'optimisation (le solver assignera des builds)
   - Ou manuellement déplacer des joueurs pour créer un groupe faible
3. **Attendu**:
   - Badges rouges pour quickness, stability
   - Panel d'avertissement: "⚠️ Contraintes non satisfaites"
   - Liste des violations:
     - "Quickness < 90%"
     - "Stability < 50%"

---

## 🔍 Indicateurs à vérifier

### Panneau Live (coin supérieur droit)
- **Job ID**: UUID du job d'optimisation
- **Temps écoulé**: ~2000ms pour 15 joueurs
- **Groupes**: Nombre de sous-groupes (ceil(squad_size / 5))
- **Joueurs**: Total de joueurs dans l'escouade

### Coverage Badges (par groupe)
- **Quickness**: Cible 90% (rouge si <90%)
- **Resistance**: Cible 80% (rouge si <80%)
- **Protection**: Cible 60% (rouge si <60%)
- **Stability**: Cible 50% (rouge si <50%)
- **Might**: Pas de cible (informatif)
- **Fury**: Pas de cible (informatif)

### Warnings Panel (si violations)
```
⚠️ Contraintes non satisfaites:
• Quickness < 90%
• Resistance < 80%
• Stability < 50%
```

---

## 🐛 Troubleshooting

### "Failed to fetch" sur login
**Cause**: Backend non accessible ou CORS
**Solution**:
```bash
# Vérifier backend
curl http://localhost:8000/api/v1/health

# Redémarrer backend si nécessaire
cd backend
poetry run uvicorn app.main:app --reload
```

### Page blanche après login
**Cause**: Erreur JavaScript
**Solution**:
1. Ouvrir DevTools (F12)
2. Vérifier Console pour erreurs
3. Vérifier Network pour requêtes échouées
4. Redémarrer frontend:
```bash
cd frontend
npm run dev
```

### DnD ne fonctionne pas
**Cause**: dnd-kit non installé ou erreur de build
**Solution**:
```bash
cd frontend
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
npm run dev
```

### Coverage ne se met pas à jour
**Cause**: Recalcul non déclenché
**Solution**:
- Cliquer sur le bouton "Recalculer" (icône ↻)
- Ou déplacer un joueur pour forcer le recalcul

### SSE stream ne fonctionne pas
**Cause**: Backend non accessible ou job_id invalide
**Solution**:
1. Vérifier que le backend est en cours d'exécution
2. Vérifier le job_id dans le panneau Live
3. Tester manuellement:
```bash
JOB_ID="<copier depuis UI>"
curl -N http://localhost:8000/api/v1/optimize/stream/$JOB_ID
```

---

## 📊 Builds de test disponibles

Les 6 builds suivants sont disponibles par défaut:

1. **Guardian - Firebrand** (WvW)
   - Quickness: 60%, Stability: 90%, Protection: 70%
   
2. **Engineer - Scrapper** (WvW)
   - Quickness: 30%, Stability: 85%, Resistance: 60%
   
3. **Revenant - Herald** (WvW)
   - Quickness: 90%, Might: 80%, Fury: 70%
   
4. **Elementalist - Tempest** (WvW)
   - Resistance: 50%, Protection: 60%, Healing
   
5. **Necromancer - Scourge** (WvW)
   - Resistance: 60%, Barrier, Conditions
   
6. **Engineer - Mechanist** (WvW)
   - Alacrity: 30%, Might: 90%

---

## 🎮 Workflow complet (2 minutes)

1. **Login**: `test@test.com` / `Test123!`
2. **Navigate**: `/optimize`
3. **Configure**: Taille escouade = 15 (par défaut)
4. **Optimize**: Cliquer "Lancer l'optimisation"
5. **Wait**: ~2s pour le solver
6. **Review**: Vérifier coverage badges et warnings
7. **Refine**: Glisser-déposer joueurs entre groupes
8. **Validate**: Vérifier que coverage se recalcule
9. **Re-optimize**: Cliquer à nouveau pour une nouvelle solution

---

## ✅ Checklist de validation

- [ ] Backend répond sur http://localhost:8000/api/v1/health
- [ ] Frontend accessible sur http://localhost:5173
- [ ] Login fonctionne avec `test@test.com`
- [ ] Page `/optimize` s'affiche
- [ ] 15 joueurs et 3 groupes visibles
- [ ] Bouton "Lancer l'optimisation" cliquable
- [ ] Optimisation se lance (status → running → complete)
- [ ] Coverage badges s'affichent
- [ ] Drag-and-drop fonctionne (joueur se déplace)
- [ ] Coverage se recalcule après DnD
- [ ] Warnings s'affichent si contraintes non satisfaites
- [ ] Bouton "Recalculer" fonctionne
- [ ] Pas d'erreurs dans la console DevTools

---

## 🔗 Liens utiles

- **Frontend**: http://localhost:5173/optimize
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **Mode Splits**: http://localhost:8000/api/v1/mode-splits/

---

## 📝 Notes

- **Compte test**: `test@test.com` / `Test123!` (créé lors de la validation v3.4.5)
- **Proxy Vite**: Les requêtes `/api/*` sont automatiquement proxifiées vers `http://127.0.0.1:8000`
- **CORS**: Configuré pour `localhost:5173` dans le backend
- **SSE**: EventSource natif du navigateur (pas de WebSocket)
- **State**: Zustand (reactive, pas de Redux)
- **DnD**: dnd-kit (pas de react-dnd)

---

**Bon test ! 🚀**

Si tu rencontres des problèmes, vérifie d'abord:
1. Backend en cours d'exécution (`curl http://localhost:8000/api/v1/health`)
2. Frontend en cours d'exécution (`curl -I http://localhost:5173/`)
3. Console DevTools pour erreurs JavaScript
4. Network tab pour requêtes échouées
