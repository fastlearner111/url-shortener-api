from locust import HttpUser, task, between

class URLShortenerUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def shorten_url(self):
        self.client.post("/urls/shorten", json={"original_url": "https://google.com"})

class RedirectUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Clicks happen fast

    @task
    def test_redirect(self):
        self.client.get("/pZ6BdVe", name="/{code}", allow_redirects=False)