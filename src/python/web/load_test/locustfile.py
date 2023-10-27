from locust import HttpUser, between, task

from random import choice, randint
import requests
from time import sleep

WORD_SITE = "https://www.mit.edu/~ecprice/wordlist.10000"

class SearchUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.seeds = ["covid", "health", "environment", "benefits", "women", "animals", "workers"]
        self.words = requests.get(WORD_SITE).content.splitlines()

    @task
    def search(self):
        query = f"{choice(self.seeds)} and {choice(self.words).decode('UTF-8')}"
        #response = self.client.get(
        self.client.get(
            url=f"/search/?query={query}&cache_off=true",
            timeout=30,
            name="search",
            headers={
                "x-api-key": "AIzaSyAylWoWjtB90CibU2tgBOhgWBAo3GXWJOQ",
            },
        )
        #print(response.json())
        sleep(randint(1,5))
