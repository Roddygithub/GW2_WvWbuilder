#!/bin/bash

# Configuration
USERS=100
SPAWN_RATE=10
DURATION="5m"
HOST="http://localhost:8000"
LOCUSTFILE="locustfile.py"

# Vérifier si Locust est installé
if ! command -v locust &> /dev/null; then
    echo "Locust n'est pas installé. Installation en cours..."
    pip install locust
fi

echo "Démarrage du test de charge avec $USERS utilisateurs..."
locust -f $LOCUSTFILE \
    --host=$HOST \
    --headless \
    --users=$USERS \
    --spawn-rate=$SPAWN_RATE \
    --run-time=$DURATION \
    --csv=load_test_results

echo "Résultats du test de charge :"
cat load_test_results_stats.csv
