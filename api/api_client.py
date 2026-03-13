import requests


class APIClient:
    def __init__(self, base_url: str) -> None:
        """Initializes the APIClient.

        Args:
            base_url (str): The base URL for the API.
        """
        self.base_url = (base_url or "").rstrip("/")
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
        res = self._request("GET",
            url=self.base_url + "/auth/user", 
            headers=headers
        )
        return res
    
    
    def get_user_data(self, token: str) -> dict:
        """Retrieves user data using the provided token.

        Args:
            token (str): The access token.

        Returns:
            dict: The JSON response containing user data.
        """
        return self.verify(token)


    def update_user_data(self, token: str, user_id: int, data: dict) -> dict:
        """Updates user data.

        Args:
            token (str): The access token.
            user_id (int): The ID of the user to update.
            data (dict): The user data to update.

        Returns:
            dict: The JSON response from the API containing user data.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("PATCH",
            url=self.base_url + f"/auth/user/{user_id}", 
            headers=headers,
            json=data
        )
        

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

    def get_departments(self, token: str = None) -> dict:
        """Retrieves the list of departments (groups).

        Returns:
            dict: The JSON response containing the list of departments.
        """
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return self._request("GET", url=self.base_url + "/app/groups", headers=headers)
    

    def create_department(self, data: dict, token: str) -> dict:
        """Creates a new department.

        Args:
            data (dict): The department name.

        Returns:
            dict: The JSON response confirming the creation.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("POST",
            url=self.base_url + "/app/groups",
            headers=headers,
            json=data
        )
    

    def edit_department(self, data: dict, token: str, department_id: int) -> dict:
        """Edits an existing department.

        Args:
            data (dict): The updated department name.
            department_id (int): The ID of the department to edit.

        Returns:
            dict: The JSON response confirming the edit.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("PATCH",
            url=self.base_url + f"/app/groups/{department_id}",
            headers=headers,
            json=data
        )
    

    def delete_department(self, token: str, department_id: int) -> dict:
        """Deletes a department.

        Args:
            department_id (int): The ID of the department.

        Returns:
            dict: The JSON response confirming the deletion.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("DELETE",
            url=self.base_url + f"/app/groups/{department_id}",
            headers=headers
        )

    
    def get_categories(self, token: str = None) -> dict:
        """Retrieves the list of categories.

        Returns:
            dict: The JSON response containing the list of categories.
        """
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return self._request("GET", url=self.base_url + "/app/categories", headers=headers)
    

    def create_category(self, data: dict, token: str) -> dict:
        """Creates a new category.

        Returns:
            dict: The JSON response confirming the creation.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("POST",
            url=self.base_url + "/app/categories",
            headers=headers,
            json=data
        )
    

    def edit_category(self, data: dict, token: str, category_id: int) -> dict:
        """Edits an existing category.

        Args:
            data (dict): The updated category name.
            category_id (int): The ID of the category to edit.

        Returns:
            dict: The JSON response confirming the edit.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("PATCH",
            url=self.base_url + f"/app/categories/{category_id}",
            headers=headers,
            json=data
        )
    

    def delete_category(self, token: str, category_id: int) -> dict:
        """Deletes a category.

        Args:
            category_id (int): The ID of the category.

        Returns:
            dict: The JSON response confirming the deletion.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("DELETE",
            url=self.base_url + f"/app/categories/{category_id}",
            headers=headers
        )
    

    def get_documents(self, category_id: int = None, group_id: int = None, limit: int = 50, offset: int = 0, token: str = None) -> dict:   
        """Retrieves the list of documents.

        Returns:
            dict: The JSON response containing the list of documents.
        """
        params = {"limit": limit, "offset": offset}
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if category_id is not None:
            params["category_id"] = category_id
        if group_id is not None:
            params["group_id"] = group_id

        return self._request("GET", url=self.base_url + "/app/documents", params=params, headers=headers)
    

    def get_document(self, document_id: int) -> dict:
        """
        Retrieves a specific document by its ID using a direct API call.
        """
        url = self.base_url + f"/app/documents/{document_id}"
        response = self._request("GET", url)
        return response


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
    

    def search_data(
            self, 
            query: str, 
            group_id: int = None, 
            category_id: int = None, 
            tags: list[str] = None, 
            filters: dict = None,
            token: str = None
    ) -> dict:
        """Searches the data based on the provided query.

        Args:
            category_id (int): The ID of the category.
            group_id (int): The ID of the department (group).
            query (str): The search query.
            filters (dict): Search filters (exact_match, include_pages, etc).

        Returns:
            dict: The JSON response containing the search results.
        """
        params = {"query": query, "tags": tags}
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # Search scope
        if group_id is not None:
            params["group_id"] = group_id

        if category_id is not None:
            params["category_id"] = category_id
        
        # Filters
        if filters:
            # Search settings
            if filters.get("exact_match"):
                params["exact_match"] = "true"
            
            # Saerch pages
            if not filters.get("include_pages", True):
                params["include_pages"] = "false"

            # Search in columns
            search_fields = []
            if filters.get("search_by_name"):
                search_fields.append("name")
            if filters.get("search_by_code"):
                search_fields.append("code")
            
            if search_fields:
                params["search_fields"] = search_fields

        return self._request("GET",
            url=self.base_url + f"/app/search",
            params=params,
            headers=headers
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
    # Files
    # ====================


    def download_file(self, file_id: int, destination_path: str, token: str) -> None:
        """Downloads a file.

        Args:
            file_id (int): The ID of the file.
            destination_path (str): The local path to save the file.
            token (str): The access token.
        """
        headers = {"Authorization": f"Bearer {token}"}
        url = self.base_url + f"/app/files/{file_id}/download"

        with self.session.get(url, headers=headers, stream=True) as response:
            response.raise_for_status()
            with open(destination_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)


    def upload_file(self, document_id: int, file_path: str, token: str) -> dict:
        """Uploads a file to the server.

        Args:
            document_id (int): The ID of the document.
            file_path (str): The path to the file.
            token (str): The access token.

        Returns:
            dict: The JSON response containing the file details.
        """
        headers = {"Authorization": f"Bearer {token}"}

        with open(file_path, "rb") as f:
            files = {"file": f}
            return self._request("POST",
                url=self.base_url + f"/app/documents/{document_id}/files",
                headers=headers,
                files=files
            )


    def delete_file(self, file_id: int, token: str) -> dict:
        """Deletes a file.

        Args:
            file_id (int): The ID of the file.
            token (str): The access token.

        Returns:
            dict: The JSON response confirming the deletion.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self._request("DELETE",
            url=self.base_url + f"/app/files/{file_id}",
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