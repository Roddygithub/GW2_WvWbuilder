from locust import HttpUser, task, between, TaskSet, constant
from random import randint
import json

class UserBehavior(TaskSet):
    def on_start(self):
        """Exécuté au démarrage de chaque utilisateur virtuel."""
        self.client.verify = False
        self.token = self.login()
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    def login(self):
        """Simule une connexion utilisateur et retourne le token JWT."""
        try:
            response = self.client.post(
                "/api/v1/auth/login",
                json={"username": "test@example.com", "password": "testpassword"}
            )
            if response.status_code == 200:
                return response.json().get("access_token")
            return None
        except Exception:
            return None
    
    @task(3)
    def view_builds(self):
        """Teste la récupération de la liste des builds."""
        self.client.get("/api/v1/builds/", headers=self.headers)
    
    @task(2)
    def view_build_details(self):
        """Teste la récupération des détails d'un build aléatoire."""
        build_id = randint(1, 100)  # Supposons qu'il y ait jusqu'à 100 builds
        self.client.get(f"/api/v1/builds/{build_id}", headers=self.headers)
    
    @task(1)
    def create_build(self):
        """Teste la création d'un nouveau build."""
        if not self.token:
            return
            
        build_data = {
            "name": f"Test Build {randint(1, 10000)}",
            "profession": "Guardian",
            "specialization": "Firebrand",
            "skills": [1, 2, 3],
            "equipment": {"weapon": "Axe", "armor": "Heavy"}
        }
        self.client.post(
            "/api/v1/builds/", 
            json=build_data, 
            headers={"Content-Type": "application/json", **self.headers}
        )

class WebsiteUser(HttpUser):
    """Classe utilisateur pour les tests de charge."""
    tasks = [UserBehavior]
    wait_time = between(1, 5)  # Temps d'attente entre les requêtes en secondes
    host = "http://localhost:8000"  # URL de l'API à tester
