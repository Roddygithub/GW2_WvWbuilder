#!/bin/bash

# Script pour exécuter les tests de mutation avec mutmut

echo "🔍 Exécution des tests de mutation avec mutmut..."

# Exécuter mutmut. Il va créer des mutants et lancer les tests pour chacun.
poetry run mutmut run

echo "📊 Génération du rapport HTML..."

# Générer le rapport HTML
poetry run mutmut html

echo "✅ Rapport généré dans ./html/mutmut/index.html"
echo "🚀 Ouverture du rapport dans le navigateur..."

# Ouvrir le rapport (compatible macOS et Linux)
open ./html/mutmut/index.html || xdg-open ./html/mutmut/index.html