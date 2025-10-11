# Configuration de surveillance

Ce dossier contient les configurations pour la surveillance de l'application avec Prometheus et Grafana.

## Structure

```
monitoring/
├── grafana/
│   └── provisioning/
│       └── datasources/
│           └── datasource.yml  # Configuration des sources de données Grafana
└── prometheus/
    └── prometheus.yml          # Configuration de Prometheus
```

## Prérequis

- Docker et Docker Compose
- Accès aux ports 3000 (Grafana) et 9090 (Prometheus)

## Démarrer la surveillance

1. Copiez le fichier `.env.example` vers `.env` et ajustez les variables si nécessaire :
   ```bash
   cp .env.example .env
   ```

2. Démarrer les services de surveillance :
   ```bash
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

3. Accédez aux interfaces :
   - Grafana: http://localhost:3000
     - Utilisateur: `admin`
     - Mot de passe: `admin` (à changer à la première connexion)
   - Prometheus: http://localhost:9090

## Tableaux de bord recommandés

Après avoir démarré Grafana, importez les tableaux de bord suivants :

1. **Node Exporter Full** (ID: 1860)
   - Fournit des métriques système complètes

2. **Docker and system monitoring** (ID: 10619)
   - Surveillance des conteneurs Docker et du système

3. **FastAPI Monitoring** (ID: 12611)
   - Métriques spécifiques à FastAPI

## Configuration des alertes

1. Dans Grafana, configurez les canaux de notification (Slack, Email, etc.)
2. Créez des règles d'alerte dans Prometheus ou utilisez les alertes intégrées de Grafana

## Arrêter la surveillance

```bash
docker-compose -f docker-compose.monitoring.yml down
```

## Dépannage

- Vérifiez les logs des conteneurs :
  ```bash
  docker-compose -f docker-compose.monitoring.yml logs -f
  ```

- Vérifiez que les cibles sont actives dans Prometheus : http://localhost:9090/targets

- Si des métriques ne s'affichent pas, assurez-vous que l'application expose bien ses métriques sur `/metrics`
