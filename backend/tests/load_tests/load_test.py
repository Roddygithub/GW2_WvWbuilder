"""
Load testing for GW2 WvW Builder API endpoints using Locust.

This file contains load test scenarios for the API endpoints.
To run the tests, use the following command:

    locust -f tests/load_tests/load_test.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import random


class ApiUser(HttpUser):
    """Simulates API users with different behaviors."""

    # Wait between 1 and 5 seconds between tasks
    wait_time = between(1, 5)

    def on_start(self):
        """Called when a user starts the test."""
        # You can add login logic here if needed
        self.token = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @task(3)  # Higher weight = more frequent execution
    def get_public_endpoints(self):
        """Test public endpoints with GET requests."""
        endpoints = [
            "/api/v1/health",
            "/api/v1/builds",
            "/api/v1/items",
            "/api/v1/skills",
        ]

        for endpoint in endpoints:
            with self.client.get(
                endpoint, headers=self.headers, catch_response=True
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed with status code: {response.status_code}")

    @task(2)
    def get_specific_build(self):
        """Test getting a specific build by ID."""
        # You might want to fetch a list of valid build IDs first
        build_id = random.randint(1, 100)  # Adjust range based on your data

        with self.client.get(
            f"/api/v1/builds/{build_id}",
            headers=self.headers,
            name="/api/v1/builds/[id]",
            catch_response=True,
        ) as response:
            if response.status_code in [
                200,
                404,
            ]:  # 404 is expected for non-existent IDs
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)  # Lower weight as it's a write operation
    def create_build(self):
        """Test creating a new build."""
        # Example build data - adjust according to your API schema
        build_data = {
            "name": f"Test Build {random.randint(1000, 9999)}",
            "profession": random.choice(
                [
                    "Guardian",
                    "Warrior",
                    "Engineer",
                    "Ranger",
                    "Thief",
                    "Elementalist",
                    "Mesmer",
                    "Necromancer",
                    "Revenant",
                ]
            ),
            "description": "Load testing build",
            "skills": {
                "heal_skill": random.randint(1, 100),
                "utility_skills": [random.randint(1, 100) for _ in range(3)],
                "elite_skill": random.randint(1, 100),
            },
            "equipment": {
                "weapons": [
                    {"id": random.randint(1, 100), "sigils": [random.randint(1, 10)]}
                ],
                "armor": [
                    {"id": random.randint(1, 100), "rune": random.randint(1, 10)}
                    for _ in range(6)
                ],
                "accessories": [{"id": random.randint(1, 100)} for _ in range(5)],
            },
            "traits": {
                "line1": random.randint(1, 3),
                "line2": random.randint(1, 3),
                "line3": random.randint(1, 3),
                "selections": [
                    random.randint(1, 3),
                    random.randint(1, 3),
                    random.randint(1, 3),
                ],
            },
        }

        with self.client.post(
            "/api/v1/builds", json=build_data, headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(
                    f"Failed to create build: {response.status_code} - {response.text}"
                )


class AuthenticatedApiUser(ApiUser):
    """Simulates authenticated API users."""

    def on_start(self):
        """Login and get token before making authenticated requests."""
        super().on_start()

        # Replace with actual login credentials if needed
        login_data = {"username": "test_user", "password": "test_password"}

        with self.client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.token}"
            else:
                # If login fails, we'll still run the tests but with unauthenticated access
                print("Warning: Failed to authenticate test user")

    @task(2)
    def get_user_profile(self):
        """Test getting the authenticated user's profile."""
        if not self.token:
            return  # Skip if not authenticated

        with self.client.get(
            "/api/v1/users/me", headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get user profile: {response.status_code}")
