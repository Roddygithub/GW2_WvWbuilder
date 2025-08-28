# Gestion des migrations de base de données

Ce répertoire contient les migrations de base de données générées par Alembic pour l'application GW2 WvW Builder.

## Commandes utiles

### Créer une nouvelle migration
```bash
alembic revision --autogenerate -m "Description des changements"
```

### Appliquer les migrations
```bash
alembic upgrade head
```

### Revenir en arrière d'une migration
```bash
alembic downgrade -1
```

### Voir l'état actuel
```bash
alembic current
```

### Voir l'historique des migrations
```bash
alembic history --verbose
```

## Configuration

Le fichier `alembic.ini` à la racine du projet contient la configuration principale.

## Bonnes pratiques

- Toujours vérifier les migrations générées automatiquement avant de les appliquer
- Ne jamais modifier manuellement les fichiers de migration existants
- Tester systématiquement les migrations en environnement de développement avant de les appliquer en production
- Utiliser des noms descriptifs pour les messages de migration

## Structure des fichiers

- `versions/` : Contient les fichiers de migration
- `env.py` : Configuration d'Alembic pour ce projet
- `script.py.mako` : Modèle pour les nouveaux fichiers de migration
