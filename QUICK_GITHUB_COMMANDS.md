# ⚡ Quick Commands - GitHub Setup

**Copy-paste ces commandes dans l'ordre!**

---

## 🚀 Étape 1: Setup Automatique

```bash
cd /home/roddy/GW2_WvWbuilder
./github_setup.sh
```

---

## 🧹 Étape 2: Nettoyage Branches (Optionnel)

```bash
# Supprimer anciennes branches locales
git branch -d release/v3.1.1-pre
git branch -d release/v3.2.0-pre
git branch -d release/v3.2.1
git branch -d release/v3.2.2
git branch -d release/v3.2.3
git branch -d release/v3.2.5
git branch -d release/v3.3.0
```

---

## 🔄 Étape 3: Merge vers Main

```bash
# Merge release → develop
git checkout develop
git merge release/v3.4.0 -m "merge: Release v3.4.7 to develop"

# Merge develop → main
git checkout main
git merge develop -m "merge: v3.4.7 to main - Production release"
```

---

## 📤 Étape 4: Push Tout vers GitHub

```bash
# Push branches
git push origin main
git push origin develop
git push origin release/v3.4.0

# Push tag
git push origin v3.4.7
```

---

## 🗑️ Étape 5: Supprimer Branches Remote (Optionnel)

```bash
# Après avoir vérifié que main et develop ont tout
git push origin --delete release/v3.1.1-pre
git push origin --delete release/v3.2.0-pre
git push origin --delete release/v3.2.1
git push origin --delete release/v3.2.3
git push origin --delete release/v3.2.5
git push origin --delete release/v3.3.0
```

---

## 🌐 Étape 6: Renommer sur GitHub

**Allez sur**: https://github.com/Roddygithub/GW2_WvWbuilder/settings

1. **Repository name**: `GW2_WvWbuilder` → `GW2Optimizer`
2. **Description**: `Professional Squad Composition Optimizer for Guild Wars 2 World vs World. AI-powered composition builder with boon coverage, role distribution, and synergy analysis. Built with FastAPI + React + TypeScript.`
3. **Topics**: `guildwars2, wvw, optimizer, squad-builder, fastapi, react, typescript, tailwindcss, python, gaming, mmo, web-app`
4. **Default branch**: `main`
5. **Features**: Enable Issues, Projects, Wiki, Discussions

---

## 💻 Étape 7: Mettre à Jour Local

```bash
# Changer remote URL
git remote set-url origin https://github.com/Roddygithub/GW2Optimizer.git

# Vérifier
git remote -v

# Renommer dossier local (optionnel)
cd /home/roddy
mv GW2_WvWbuilder GW2Optimizer
cd GW2Optimizer

# Test
git fetch origin
git status
```

---

## ✅ Étape 8: Vérification

```bash
# Vérifier que tout est bon
git log --oneline -5
git tag
git branch -a
```

---

## 🎉 C'est Fini!

**Repository renommé**: ✅  
**Branches mergées**: ✅  
**Tag v3.4.7 créé**: ✅  
**Local mis à jour**: ✅  

**GitHub**: https://github.com/Roddygithub/GW2Optimizer

---

## 📋 One-Liner (Tout Faire d'un Coup)

**⚠️ ATTENTION: Vérifier chaque commande avant d'exécuter!**

```bash
cd /home/roddy/GW2_WvWbuilder && \
./github_setup.sh && \
git checkout develop && git merge release/v3.4.0 -m "merge: v3.4.7 to develop" && \
git checkout main && git merge develop -m "merge: v3.4.7 to main" && \
git push origin main develop release/v3.4.0 v3.4.7 && \
echo "✅ Done! Now rename on GitHub and run: git remote set-url origin https://github.com/Roddygithub/GW2Optimizer.git"
```

---

**Questions?** Voir `GITHUB_RENAME_GUIDE.md` pour le guide complet.
