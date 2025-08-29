# Gestion des Migrations avec Alembic

Ce document explique comment gérer les migrations de base de données avec Alembic dans le projet.

## Configuration

Le fichier `alembic.ini` contient la configuration de base. La configuration est chargée depuis les variables d'environnement via `app.core.config`.

## Commandes de base

### Créer une nouvelle migration
```bash
# Activer l'environnement Poetry
poetry shell

# Créer une nouvelle migration basée sur les modèles
cd backend
alembic revision --autogenerate -m "Description des changements"
```

### Appliquer les migrations
```bash
# Appliquer toutes les migrations en attente
alembic upgrade head

# Revenir à une version spécifique
alembic downgrade -1  # Version précédente
alembic downgrade <revision_id>  # Version spécifique
```

### Vérifier l'état actuel
```bash
alembic current  # Affiche la version actuelle
alembic history  # Affiche l'historique des migrations
```

## Bonnes pratiques

1. **Vérifier les migrations générées** : Toujours examiner le code généré avant de l'appliquer.
2. **Une migration par fonctionnalité** : Garder les migrations petites et ciblées.
3. **Tester les migrations** : Toujours tester les migrations en environnement de développement avant la production.
4. **Données de test** : Utiliser `downgrade` et `upgrade` pour tester les migrations dans les deux sens.

## Structure d'une migration

```python
"""<description>

Revision ID: <revision_id>
Revises: <parent_revision_id>
Create Date: <creation_date>

"""
from alembic import op
import sqlalchemy as sa

# Références des révisions utilisées par Alembic
revision = '<revision_id>'
down_revision = '<parent_revision_id>'
branch_labels = None
depends_on = None

def upgrade():
    # Commandes pour appliquer la migration
    pass

def downgrade():
    # Commandes pour annuler la migration
    pass
```

## Résolution des problèmes courants

### Migration vide
Si `alembic revision --autogenerate` ne détecte aucun changement :
1. Vérifiez que les modèles sont correctement importés dans `models/__init__.py`
2. Assurez-vous que les modèles héritent de `Base`
3. Vérifiez que la configuration d'Alembic pointe vers la bonne base de données

### Conflits de migrations
En cas de conflit :
1. Annulez la migration problématique : `alembic downgrade -1`
2. Supprimez le fichier de migration problématique
3. Recréez la migration

## Intégration continue

Les migrations sont automatiquement testées dans le workflow GitHub Actions. Assurez-vous que :
1. Toutes les migrations sont commitées
2. Les migrations sont applicables en production
3. Les données existantes sont préservées
