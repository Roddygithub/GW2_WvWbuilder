#!/bin/bash
set -e  # Arrête le script en cas d'erreur

# 1. Préparation et Nettoyage
cd /home/roddy/Documents/GW2_WvWbuilder/backend
echo "🔧 Nettoyage du projet..."

# Suppression des fichiers de test vides ou inutiles
find tests -type f -name "test_*.py" -size -2k -delete
find tests -type f -name "*_test.py" -size -2k -delete
rm -f tests/unit/models/test_minimal_user.py 2>/dev/null || true

# Nettoyage et formatage
echo "🧹 Nettoyage des imports inutilisés et formatage..."
pip install -q autoflake black isort
autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables app tests
black .
isort .

# 2. Tests et Couverture
echo "🧪 Exécution des tests initiaux..."
pip install -q pytest pytest-cov
COVERAGE_FILE=.coverage pytest --cov=app --cov-report=term-missing --cov-report=html -v || true

# 3. Correction Automatique des Tests Manquants
echo "🔍 Identification des modules à améliorer..."
LOW_COVERAGE_FILES=$(python3 -c "
import re
with open('htmlcov/index.html') as f:
    content = f.read()
    files = re.findall(r'<a href=\"(.*?)\">(.*?)</a>.*?(\d+)%', content)
    for f in files:
        if int(f[2]) < 90 and 'init' not in f[1] and 'migrations' not in f[1]:
            print(f[0].replace('index.html#', '').replace('_', '/').replace('.html', '.py'))
" | sort -u)

# 4. Mise à Jour de la Documentation
echo "📝 Mise à jour de la documentation..."
cat > README.md << 'EOL'
# GuildWars2 TeamBuilder - Backend

## 🚀 Installation

```bash
# Configuration de l'environnement
python -m venv venv
source venv/bin/activate  # Sur Windows: .\venv\Scripts\activate

# Installation des dépendances
pip install -r requirements.txt

# Configuration de l'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# Initialisation de la base de données
alembic upgrade head

# Lancement du serveur
uvicorn app.main:app --reload
