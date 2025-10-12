# Rotation des clés de sécurité

Ce document explique comment fonctionne le système de rotation des clés de sécurité et comment le configurer.

## Fonctionnement

Le système de rotation des clés permet de :

1. **Gérer plusieurs clés** : Le service peut gérer plusieurs clés simultanément, ce qui permet une transition en douceur lors des rotations.
2. **Rotation automatique** : Les clés peuvent être automatiquement tournées selon un intervalle configuré.
3. **Rétrocompatibilité** : Les anciens tokens restent valides jusqu'à leur expiration, même après une rotation de clé.

## Configuration

### Variables d'environnement

Ajoutez ces variables à votre fichier `.env` :

```ini
# Intervalle de rotation des clés (en jours)
SECRET_KEY_ROTATION_DAYS=30

# Nombre maximum d'anciennes clés à conserver
MAX_OLD_KEYS=3

# Clé secrète principale (obligatoire)
SECRET_KEY=votre_clé_secrète_très_longue_et_sécurisée

# Clés historiques (optionnelles, pour la rétrocompatibilité)
SECRET_KEY_1=ancienne_clé_1
SECRET_KEY_2=ancienne_clé_2
```

### Configuration de l'application

Le service de rotation des clés est automatiquement initialisé au démarrage de l'application via le fichier `main.py`.

## Utilisation

### Rotation manuelle des clés

Pour forcer une rotation des clés, vous pouvez appeler la fonction `rotate_keys()` :

```python
from app.core.tasks.key_rotation_task import rotate_keys

# Effectuer une rotation manuelle
rotate_keys()
```

### Vérification de la prochaine rotation

Pour vérifier quand la prochaine rotation est prévue :

```python
from app.core.key_rotation_service import key_rotation_service

if key_rotation_service.should_rotate():
    print("Une rotation des clés est nécessaire")
else:
    next_rotation = key_rotation_service.last_rotation_date + key_rotation_service.key_rotation_interval
    print(f"Prochaine rotation prévue le {next_rotation}")
```

## Tests

Des tests unitaires sont disponibles dans `tests/unit/test_key_rotation.py`.

Pour exécuter les tests :

```bash
pytest tests/unit/test_key_rotation.py -v
```

## Sécurité

- Les clés ne sont jamais stockées en clair dans la base de données
- Les anciennes clés sont conservées uniquement pour valider les tokens existants
- La rotation automatique est désactivée en environnement de test

## Dépannage

### Problèmes courants

1. **Les tokens ne sont plus valides après un redémarrage**
   - Vérifiez que les clés sont correctement configurées dans le fichier `.env`
   - Assurez-vous que la même clé est utilisée à chaque redémarrage

2. **Erreur de validation des tokens**
   - Vérifiez que l'algorithme JWT correspond entre le service et la configuration
   - Assurez-vous que les horloges sont synchronisées entre les serveurs

Pour plus d'aide, consultez les logs de l'application.
