"""
SecurePulse Load Tests
======================
Run locally:  locust -f tests/locustfile.py --host http://localhost:8000
Run headless: locust -f tests/locustfile.py --headless --users 10 --spawn-rate 2 --run-time 60s --host http://localhost:8000

Note: The NVD API enforces rate limits (~5 req/30s without an API key).
502 errors during load tests against localhost are expected — they indicate
the NVD upstream is throttling requests, not that our app is failing.
With an NVD API key (set via env var), rate limits increase significantly.
"""
from locust import HttpUser, task, between


class SecurePulseUser(HttpUser):
    """
    Simulates a real user hitting the SecurePulse API.
    Locust will spawn multiple users and run these tasks concurrently
    to prove the app can handle load within its resource limits.
    """
    wait_time = between(1, 3)

    @task(3)
    def health_check(self):
        """Liveness probe — highest frequency, lightest request."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(2)
    def get_critical_cves(self):
        """Fetch critical CVEs — most common real-world use case."""
        with self.client.get(
            "/cves",
            params={"severity": "CRITICAL", "limit": 5},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "cves" not in data:
                    response.failure("Response missing 'cves' field")
                else:
                    response.success()
            else:
                response.failure(f"CVE fetch failed: {response.status_code}")

    @task(2)
    def get_high_cves(self):
        """Fetch high severity CVEs."""
        with self.client.get(
            "/cves",
            params={"severity": "HIGH", "limit": 5},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"High CVE fetch failed: {response.status_code}")

    @task(1)
    def get_cves_by_keyword(self):
        """Search CVEs by keyword — tests the filter logic."""
        with self.client.get(
            "/cves",
            params={"keyword": "nginx", "limit": 3},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Keyword search failed: {response.status_code}")

    @task(1)
    def invalid_severity(self):
        """
        Intentionally sends invalid input — proves the API
        handles bad requests gracefully under load.
        """
        with self.client.get(
            "/cves",
            params={"severity": "EXTREME"},
            catch_response=True
        ) as response:
            if response.status_code == 400:
                response.success()
            else:
                response.failure(f"Expected 400 but got: {response.status_code}")