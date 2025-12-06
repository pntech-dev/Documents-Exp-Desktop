import requests


class APIClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url


    def login(self, email: str, password: str) -> dict:
        r = requests.post(
            url=self.base_url + "/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )

        r.raise_for_status()

        return r.json()
    

    def signup(self, email: str, password: str) -> dict:
        r = requests.post(
            url=self.base_url + "/auth/signup",
            json={"email": email, "password": password},
            timeout=10
        )

        r.raise_for_status()

        return r.json()


    def verify(self, token: str) -> dict:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(
            url=self.base_url + "/auth/user",
            headers=headers,
            timeout=10
        )

        r.raise_for_status()

        return r.json()