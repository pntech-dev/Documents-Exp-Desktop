import requests


class APIClient:
    def __init__(self, base_url: str) -> None:
        """Initializes the APIClient.

        Args:
            base_url (str): The base URL for the API.
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()


    # ====================
    # API Client Handlers
    # ====================

    # === User ===

    def verify(self, token: str) -> dict:
        """Verifies the user token.

        Args:
            token (str): The access token to verify.

        Returns:
            dict: The JSON response from the API containing user data.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("GET",
            url=self.base_url + "/auth/user", 
            headers=headers
        )
    
    
    def get_user_data(self, token: str) -> dict:
        """Retrieves user data using the provided token.

        Args:
            token (str): The access token.

        Returns:
            dict: The JSON response containing user data.
        """
        return self.verify(token)
        

    # === Login ===

    def login(self, email: str, password: str) -> dict:
        """Authenticates a user.

        Args:
            email (str): The user's email address.
            password (str): The user's password.

        Returns:
            dict: The JSON response containing authentication tokens.
        """
        payload = {"email": email, "password": password}
        return self._request("POST",
            url=self.base_url + "/auth/login", 
            json=payload
        )   
    

    #  === Signup ===
    
    def signup(self, code: str, email: str, password: str) -> dict:
        """Completes the signup process by verifying the code.

        Args:
            code (str): The verification code sent to email.
            email (str): The user's email address.
            password (str): The desired password.

        Returns:
            dict: The JSON response confirming signup.
        """
        payload = {"code": code, "email": email, "password": password}
        return self._request("PATCH",
            url=self.base_url + "/auth/signup/verify-code",
            json=payload
        )


    def signup_send_code(self, email: str) -> dict:
        """Sends a signup verification code to the provided email.

        Args:
            email (str): The email address to send the code to.

        Returns:
            dict: The JSON response confirming the code was sent.
        """
        payload = {"email": email}
        return self._request("POST",
            url=self.base_url + "/auth/signup/send-code",
            json=payload
        )


    # === Token ===

    def refresh(self, refresh_token: str) -> dict:
        """Refreshes the access token.

        Args:
            refresh_token (str): The refresh token.

        Returns:
            dict: The JSON response containing new tokens.
        """
        payload = {"refresh_token": refresh_token}
        return self._request("POST",
            url=self.base_url + "/auth/token/refresh",
            json=payload
        )


    #  === Reset Password ===

    def request_reset_password(self, email: str) -> dict:
        """Requests a password reset link/code.

        Args:
            email (str): The email address associated with the account.

        Returns:
            dict: The JSON response confirming the request.
        """
        payload = {"email": email}
        return self._request("POST",
            url=self.base_url + "/auth/forgot-password/request-reset",
            json=payload
        )


    def reset_password_confirm_email(self, email: str, code: str) -> dict:
        """Confirms the email for password reset using a code.

        Args:
            email (str): The user's email address.
            code (str): The verification code.

        Returns:
            dict: The JSON response confirming email verification.
        """
        payload = {"email": email, "code": code}
        return self._request("POST",
            url=self.base_url + "/auth/forgot-password/confirm-email", 
            json=payload
        )
    

    def reset_password(self, reset_token: str, password: str) -> dict:
        """Resets the password using a reset token.

        Args:
            reset_token (str): The token received after email confirmation.
            password (str): The new password.

        Returns:
            dict: The JSON response confirming the password reset.
        """
        payload = {"reset_token": reset_token, "password": password}
        return self._request("PATCH",
            url=self.base_url + "/auth/forgot-password/reset-password",
            json=payload
        )
    

    # === App Data ===

    def get_departments(self) -> dict:
        """Retrieves the list of departments (groups).

        Returns:
            dict: The JSON response containing the list of departments.
        """
        return self._request("GET", url=self.base_url + "/app/groups")

    
    def get_categories(self) -> dict:
        """Retrieves the list of categories.

        Returns:
            dict: The JSON response containing the list of categories.
        """
        return self._request("GET", url=self.base_url + "/app/categories")
    

    def get_documents(self, category_id: int = None, limit: int = 50, offset: int = 0) -> dict:   
        """Retrieves the list of documents.

        Returns:
            dict: The JSON response containing the list of documents.
        """
        params = {"limit": limit, "offset": offset}
        if category_id is not None:
            params["category_id"] = category_id

        return self._request("GET", url=self.base_url + "/app/documents", params=params)
    

    def get_document(self, document_id: int) -> dict:
        """Retrieves a specific document by ID.

        Since direct GET /documents/{id} might be 405, we try fallbacks.
        """
        # Strategy 1: Try filtering the list by ID
        try:
            response = self._request("GET",
                url=self.base_url + "/app/documents", 
                params={"id": document_id}
            )
            documents = response.get("documents", [])
            for doc in documents:
                if doc.get("id") == document_id:
                    return doc
        except Exception:
            pass

        # Strategy 2: Try getting pages, maybe document metadata is included there
        try:
            response = self.get_document_pages(document_id)
            if "document" in response:
                return response["document"]
        except Exception:
            pass
            
        return {}


    def get_document_pages(self, document_id: int) -> dict:
        """Retrieves the list of pages for a specific document.

        Args:
            document_id (int): The ID of the document.

        Returns:
            dict: The JSON response containing the list of pages.
        """
        return self._request("GET",
            url=self.base_url + f"/app/documents/{document_id}/pages"
        )
    

    def search_data(self, category_id: int, query: str) -> dict:
        """Searches the data based on the provided query.

        Args:
            category_id (int): The ID of the category.
            query (str): The search query.

        Returns:
            dict: The JSON response containing the search results.
        """
        return self._request("GET",
            url=self.base_url + f"/app/category_search",
            params={"category_id": category_id, "query": query}
        )
    

    def create_document(self, data: dict, token: str) -> dict:
        """Creates a new document.

        Args:
            data (dict): The document data.

        Returns:
            dict: The JSON response confirming the creation.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("POST",
            url=self.base_url + "/app/documents",
            headers=headers,
            json=data
        )
    

    def update_document(self, document_id: int, data: dict, token: str) -> dict:
        """Updates a document.

        Args:
            document_id (int): The ID of the document to update.
            data (dict): The updated document data.

        Returns:
            dict: The JSON response confirming the update.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("PATCH",
            url=self.base_url + f"/app/documents/{document_id}",
            headers=headers,
            json=data
        )
    

    def delete_document(self, document_id: int, token: str) -> dict:
        """Deletes a document.
        
        Args:
            document_id (int): The ID of the document to delete.

        Returns:
            dict: The JSON response confirming the deletion.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("DELETE",
            url=self.base_url + f"/app/documents/{document_id}",
            headers=headers
        )


    # ====================
    # API Client Methods
    # ====================

    def _request(self, method: str, url: str, timeout: int = 10, **kwargs) -> dict:
        """Generic method for making API requests."""
        request = self.session.request(method, url, timeout=timeout, **kwargs)
        request.raise_for_status()
        return request.json()