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


    def refresh(self, refresh_token: str) -> dict:
        r = requests.post(
            url=self.base_url + "/auth/refresh",
            json={"refresh_token": refresh_token},
            timeout=10
        )

        r.raise_for_status()

        return r.json()
    

    def forgot_password(self, email: str) -> dict:
        r = requests.post(
            url=self.base_url + "/auth/forgot-password",
            json={"email": email},
            timeout=10
        )

        r.raise_for_status()

        return r.json()


    def confirm_email(self, email: str, code: str) -> dict:
        r = requests.post(
            url=self.base_url + "/auth/confirm-email",
            json={"email": email, "code": code},
            timeout=10
        )

        r.raise_for_status()

        return r.json()
    

    def reset_password(self, reset_token: str, password: str) -> dict:
        r = requests.patch(
            url=self.base_url + "/auth/reset-password",
            json={"reset_token": reset_token, "password": password},
            timeout=10
        )

        r.raise_for_status()

        return r.json()