#!/bin/bash
echo "🔎 Vérification complète du dépôt Git"

# 1️⃣ Branche actuelle
current_branch=$(git branch --show-current)
echo -e "\n🌿 Branche actuelle : $current_branch"

# 2️⃣ État du dépôt
echo -e "\n📂 État du dépôt :"
git status

# 3️⃣ Derniers commits locaux
echo -e "\n📝 5 derniers commits (local) :"
git log --oneline --decorate --graph -5

# 4️⃣ Vérification du remote
echo -e "\n🌐 Remotes :"
git remote -v

# 5️⃣ Derniers commits comparés au remote
echo -e "\n📦 Branche locale vs remote :"
git fetch origin >/dev/null 2>&1
git log --oneline --decorate --graph --left-right --boundary origin/$current_branch..$current_branch

# 6️⃣ Vérification si push possible
echo -e "\n🚀 Tentative dry-run de push vers $current_branch :"
git push --dry-run origin "$current_branch"

echo -e "\n✅ Vérification terminée."
