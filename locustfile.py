from locust import HttpUser, task, between

class URLShortenerUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def list_urls(self):
        self.client.get("/urls")

    @task(3)
    def get_single_url(self):
        import random
        url_id = random.randint(1, 2000)
        self.client.get(f"/urls/{url_id}")

    @task(2)
    def list_users(self):
        self.client.get("/users")

    @task(2)
    def get_single_user(self):
        import random
        user_id = random.randint(1, 398)
        self.client.get(f"/users/{user_id}")

    @task(1)
    def health_check(self):
        self.client.get("/health")

    @task(1)
    def get_metrics(self):
        self.client.get("/metrics")