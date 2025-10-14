# Guide de Surveillance et d'Alertes

Ce document décrit comment surveiller l'application et configurer des alertes en utilisant la stack Prometheus, Alertmanager et Grafana.

## 1. Architecture de Surveillance

L'application expose ses métriques via un endpoint `/metrics` au format Prometheus.

1.  **Prometheus** : Scrape (collecte) périodiquement les métriques de l'endpoint `/metrics`.
2.  **Grafana** : Interroge Prometheus pour afficher les métriques sur des tableaux de bord (dashboards).
3.  **Alertmanager** : Reçoit les alertes déclenchées par Prometheus et les achemine vers différentes destinations (email, Slack, etc.).

## 2. Métriques Exposées

L'application expose des métriques standards et personnalisées, notamment :

- `http_requests_latency_seconds` : Histogramme de la latence des requêtes.
- `http_requests_total` : Compteur du nombre total de requêtes, avec des labels pour la méthode, le chemin et le statut.
- `http_requests_in_progress` : Jauge du nombre de requêtes en cours.
- `cache_hits_total` : Compteur des hits du cache Redis.
- `cache_misses_total` : Compteur des misses du cache Redis.

## 3. Configuration de Prometheus

Ajoutez la configuration suivante à votre fichier `prometheus.yml` pour scraper les métriques de l'application :

```yaml
scrape_configs:
  - job_name: 'gw2-builder-backend'
    static_configs:
      - targets: ['localhost:8000'] # Remplacez par l'adresse de votre application
```

## 4. Exemples de Requêtes PromQL pour Grafana

Voici quelques requêtes PromQL utiles pour créer des tableaux de bord dans Grafana.

### Taux d'Erreurs (5xx)
```promql
# Taux d'erreurs serveur sur les 5 dernières minutes
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100
```

### Latence des Requêtes (95ème percentile)
```promql
# 95ème percentile de la latence des requêtes sur les 5 dernières minutes
histogram_quantile(0.95, sum(rate(http_requests_latency_seconds_bucket[5m])) by (le))
```

### Taux de Requêtes par Seconde (RPS)
```promql
sum(rate(http_requests_total[1m]))
```

### Taux de Hit du Cache
```promql
# Pourcentage de hits du cache sur les 5 dernières minutes
sum(rate(cache_hits_total[5m])) / (sum(rate(cache_hits_total[5m])) + sum(rate(cache_misses_total[5m]))) * 100
```

## 5. Configuration des Alertes avec Alertmanager

Créez un fichier de règles d'alerte (par exemple, `alerts.yml`) pour Prometheus.

```yaml
groups:
  - name: backend-alerts
    rules:
      - alert: HighErrorRate
        # Alerte si le taux d'erreurs 5xx dépasse 1% sur 5 minutes
        expr: (sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100 > 1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Taux d'erreur élevé sur le backend ({{ $value | printf '%.2f' }}%)"
          description: "Le taux d'erreurs 5xx a dépassé 1% pendant plus de 2 minutes."

      - alert: HighRequestLatency
        # Alerte si le 95ème percentile de la latence dépasse 500ms
        expr: histogram_quantile(0.95, sum(rate(http_requests_latency_seconds_bucket[5m])) by (le)) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Latence des requêtes élevée (p95 > 500ms)"
          description: "Le 95ème percentile de la latence des requêtes a dépassé 500ms pendant plus de 5 minutes."

      - alert: LowCacheHitRate
        # Alerte si le taux de hit du cache tombe en dessous de 80% sur 10 minutes
        expr: (sum(rate(cache_hits_total[10m])) / (sum(rate(cache_hits_total[10m])) + sum(rate(cache_misses_total[10m])))) * 100 < 80
        for: 5m
        labels:
          severity: info
        annotations:
          summary: "Taux de hit du cache faible ({{ $value | printf '%.2f' }}%)"
          description: "Le taux de hit du cache est tombé en dessous de 80% pendant plus de 5 minutes. Une optimisation du cache pourrait être nécessaire."
```

Chargez ce fichier dans votre configuration Prometheus pour que les alertes soient évaluées et envoyées à Alertmanager.