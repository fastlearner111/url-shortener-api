import random
import uuid
from locust import HttpUser, task, between


class ShortenerUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        creds = {"email": f"load-{uuid.uuid4().hex[:10]}@example.com", "password": "loadtest123"}
        self.client.post("/auth/register", json=creds, name="/auth/register")
        resp = self.client.post("/auth/login", json=creds, name="/auth/login")
        resp.raise_for_status()
        self.headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
        self.codes = []
        self.seen = set()

    @task(1)
    def shorten(self):
        resp = self.client.post(
            "/urls/shorten",
            json={"original_url": f"https://example.com/{uuid.uuid4().hex}"},
            headers=self.headers,
            name="/urls/shorten",
        )
        if resp.status_code == 200:
            self.codes.append(resp.json()["short_code"])

    @task(9)
    def redirect(self):
        if not self.codes:
            return
        code = random.choice(self.codes)
        label = "/{code} (hit)" if code in self.seen else "/{code} (miss)"
        self.seen.add(code)
        self.client.get(f"/{code}", name=label, allow_redirects=False)