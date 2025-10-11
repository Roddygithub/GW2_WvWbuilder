# Guide de Déploiement en Production

Ce guide décrit une méthode de déploiement robuste pour l'application backend en utilisant Docker Compose, Nginx comme reverse proxy, et Gunicorn comme serveur d'application.

## 1. Architecture Cible

```
Internet -> Nginx (Reverse Proxy, SSL) -> Gunicorn (Serveur d'application) -> Application FastAPI
                                             |
                                             v
                                     PostgreSQL (Base de données)
                                             |
                                             v
                                        Redis (Cache)
```

- **Nginx** : Gère les requêtes entrantes, termine les connexions SSL/TLS, sert les fichiers statiques et transmet les requêtes dynamiques à Gunicorn.
- **Gunicorn** : Gère plusieurs processus workers Uvicorn pour exécuter l'application FastAPI de manière concurrente et résiliente.
- **Docker Compose** : Orchestre le lancement et la liaison de tous les conteneurs (Nginx, App, DB, Redis).

## 2. Prérequis

- Un serveur avec Docker et Docker Compose installés.
- Un nom de domaine pointant vers l'adresse IP de votre serveur.
- Certificats SSL/TLS pour votre domaine (par exemple, obtenus via Let's Encrypt).

## 3. Configuration

### a. Fichier `docker-compose.prod.yml`

Créez un fichier `docker-compose.prod.yml` à la racine du projet `backend/`.

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  app:
    build:
      context: .
      dockerfile: Dockerfile
    command: /start-prod.sh # Script qui lance Gunicorn
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    restart: always

  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      # Montez vos certificats SSL ici
      # - /path/to/your/certs:/etc/nginx/certs:ro
    depends_on:
      - app
    restart: always

volumes:
  postgres_data:
```

### b. Fichier de configuration Nginx

Créez un dossier `nginx/` avec un fichier `nginx.conf`. Ce fichier doit gérer la redirection HTTP vers HTTPS et le proxy vers l'application.

### c. Fichier `.env` de Production

Créez un fichier `.env` avec les variables d'environnement pour la production (secrets, configuration de la base de données, etc.). **Ne committez jamais ce fichier.**

### d. Script de démarrage `start-prod.sh`

Créez un script `start-prod.sh` qui exécute les migrations Alembic puis lance Gunicorn.

```bash
#!/bin/sh
# Appliquer les migrations
alembic upgrade head
# Lancer le serveur d'application
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 app.main:app
```

## 4. Lancement

1.  Assurez-vous que votre fichier `.env` est correctement configuré.
2.  Construisez et lancez les conteneurs :

    ```bash
    docker-compose -f docker-compose.prod.yml up --build -d
    ```

Votre application devrait maintenant être accessible via votre nom de domaine.