import pytest
import requests
from unittest.mock import Mock, patch

from api.api_client import APIClient



class TestAPIClient:
    BASE_URL = "http://api.example.com"

    @pytest.fixture
    def client(self):
        return APIClient(self.BASE_URL)

    def test_init(self):
        client = APIClient("http://api.example.com/")
        assert client.base_url == "http://api.example.com"
        assert isinstance(client.session, requests.Session)

    def test_verify(self, client):
        token = "test_token"
        expected_data = {"user": {"id": 1, "email": "test@example.com"}}

        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_data
            mock_request.return_value = mock_response
            
            result = client.verify(token)
            
            assert result == expected_data
            mock_request.assert_called_once_with(
                "GET",
                f"{self.BASE_URL}/auth/user",
                timeout=10,
                headers={"Authorization": f"Bearer {token}"}
            )

    def test_login(self, client):
        email = "test@example.com"
        password = "password123"
        expected_response = {"access_token": "access", "refresh_token": "refresh"}

        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_request.return_value = mock_response

            result = client.login(email, password)

            assert result == expected_response
            mock_request.assert_called_once_with(
                "POST",
                f"{self.BASE_URL}/auth/login",
                timeout=10,
                json={"email": email, "password": password}
            )

    def test_signup(self, client):
        code = "123456"
        email = "test@example.com"
        password = "password123"
        expected_response = {"message": "Signup successful"}

        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_request.return_value = mock_response

            result = client.signup(code, email, password)

            assert result == expected_response
            mock_request.assert_called_once_with(
                "PATCH",
                f"{self.BASE_URL}/auth/signup/verify-code",
                timeout=10,
                json={"code": code, "email": email, "password": password}
            )

    def test_refresh(self, client):
        refresh_token = "old_refresh_token"
        expected_response = {"access_token": "new_access", "refresh_token": "new_refresh"}

        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_request.return_value = mock_response

            result = client.refresh(refresh_token)

            assert result == expected_response
            mock_request.assert_called_once_with(
                "POST",
                f"{self.BASE_URL}/auth/token/refresh",
                timeout=10,
                json={"refresh_token": refresh_token}
            )

    def test_get_documents(self, client):
        token = "auth_token"
        category_id = 5
        limit = 20
        offset = 10
        expected_response = {"documents": [{"id": 1, "name": "Doc 1"}]}

        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_request.return_value = mock_response

            result = client.get_documents(category_id=category_id, limit=limit, offset=offset, token=token)

            assert result == expected_response
            mock_request.assert_called_once_with(
                "GET",
                f"{self.BASE_URL}/app/documents",
                timeout=10,
                params={"limit": limit, "offset": offset, "category_id": category_id},
                headers={"Authorization": f"Bearer {token}"}
            )

    def test_delete_document(self, client):
        token = "auth_token"
        doc_id = 123
        expected_response = {"status": "deleted"}

        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_request.return_value = mock_response

            result = client.delete_document(doc_id, token)

            assert result == expected_response
            mock_request.assert_called_once_with(
                "DELETE",
                f"{self.BASE_URL}/app/documents/{doc_id}",
                timeout=10,
                headers={"Authorization": f"Bearer {token}"}
            )

    def test_request_returns_empty_dict_for_204(self, client):
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 204
            mock_response.content = b""
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response

            result = client.delete_document(123, "auth_token")

            assert result == {}

    def test_request_returns_empty_dict_for_empty_body(self, client):
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b""
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response

            result = client._request("DELETE", f"{self.BASE_URL}/app/files/1")

            assert result == {}

    def test_request_returns_empty_dict_for_whitespace_json_body(self, client):
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b"   \n\t  "
            mock_response.text = "   \n\t  "
            mock_response.raise_for_status = Mock()
            mock_response.json.side_effect = ValueError("No JSON object could be decoded")
            mock_request.return_value = mock_response

            result = client._request("GET", f"{self.BASE_URL}/app/search")

            assert result == {}

    def test_request_raises_for_non_json_non_empty_body(self, client):
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b"<html>error</html>"
            mock_response.text = "<html>error</html>"
            mock_response.raise_for_status = Mock()
            mock_response.json.side_effect = ValueError("No JSON object could be decoded")
            mock_request.return_value = mock_response

            with pytest.raises(ValueError):
                client._request("GET", f"{self.BASE_URL}/app/search")

    def test_search_data(self, client):
        token = "auth_token"
        query = "test query"
        filters = {"exact_match": True, "search_by_name": True}
        expected_response = {"results": []}

        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_response
            mock_request.return_value = mock_response

            client.search_data(query=query, filters=filters, token=token)

            # Проверяем, что параметры фильтрации правильно преобразовались в query params
            call_args = mock_request.call_args
            assert call_args[0] == ("GET", f"{self.BASE_URL}/app/search")
            assert call_args[1]["params"]["query"] == query
            assert call_args[1]["params"]["exact_match"] == "true"
            assert call_args[1]["params"]["search_fields"] == ["name"]
            assert call_args[1]["headers"]["Authorization"] == f"Bearer {token}"

    def test_get_user_data(self, client):
        token = "test_token"
        expected_data = {"user": {"id": 1}}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_data
            mock_request.return_value = mock_response
            
            result = client.get_user_data(token)
            assert result == expected_data
            mock_request.assert_called_once_with(
                "GET", f"{self.BASE_URL}/auth/user", timeout=10, headers={"Authorization": f"Bearer {token}"}
            )

    def test_signup_send_code(self, client):
        email = "test@example.com"
        expected = {"message": "sent"}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.signup_send_code(email)
            assert result == expected
            mock_request.assert_called_once_with(
                "POST", f"{self.BASE_URL}/auth/signup/send-code", timeout=10, json={"email": email}
            )

    def test_request_reset_password(self, client):
        email = "test@example.com"
        expected = {"message": "sent"}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.request_reset_password(email)
            assert result == expected
            mock_request.assert_called_once_with(
                "POST", f"{self.BASE_URL}/auth/forgot-password/request-reset", timeout=10, json={"email": email}
            )

    def test_reset_password_confirm_email(self, client):
        email = "test@example.com"
        code = "123456"
        expected = {"token": "reset_token"}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.reset_password_confirm_email(email, code)
            assert result == expected
            mock_request.assert_called_once_with(
                "POST", f"{self.BASE_URL}/auth/forgot-password/confirm-email", timeout=10, json={"email": email, "code": code}
            )

    def test_reset_password(self, client):
        token = "reset_token"
        password = "new_password"
        expected = {"message": "success"}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.reset_password(token, password)
            assert result == expected
            mock_request.assert_called_once_with(
                "PATCH", f"{self.BASE_URL}/auth/forgot-password/reset-password", timeout=10, json={"reset_token": token, "password": password}
            )

    def test_get_departments(self, client):
        token = "auth_token"
        expected = {"departments": []}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.get_departments(token)
            assert result == expected
            mock_request.assert_called_once_with(
                "GET", f"{self.BASE_URL}/app/groups", timeout=10, headers={"Authorization": f"Bearer {token}"}
            )

    def test_create_department(self, client):
        token = "auth_token"
        data = {"name": "New Dept"}
        expected = {"id": 1}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.create_department(data, token)
            assert result == expected
            mock_request.assert_called_once_with(
                "POST", f"{self.BASE_URL}/app/groups", timeout=10, headers={"Authorization": f"Bearer {token}"}, json=data
            )

    def test_edit_department(self, client):
        token = "auth_token"
        dept_id = 1
        data = {"name": "Updated Dept"}
        expected = {"success": True}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.edit_department(data, token, dept_id)
            assert result == expected
            mock_request.assert_called_once_with(
                "PATCH", f"{self.BASE_URL}/app/groups/{dept_id}", timeout=10, headers={"Authorization": f"Bearer {token}"}, json=data
            )

    def test_delete_department(self, client):
        token = "auth_token"
        dept_id = 1
        expected = {"success": True}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.delete_department(token, dept_id)
            assert result == expected
            mock_request.assert_called_once_with(
                "DELETE", f"{self.BASE_URL}/app/groups/{dept_id}", timeout=10, headers={"Authorization": f"Bearer {token}"}
            )

    def test_get_categories(self, client):
        token = "auth_token"
        expected = {"categories": []}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.get_categories(token)
            assert result == expected
            mock_request.assert_called_once_with(
                "GET", f"{self.BASE_URL}/app/categories", timeout=10, headers={"Authorization": f"Bearer {token}"}
            )

    def test_create_category(self, client):
        token = "auth_token"
        data = {"name": "New Cat", "group_id": 1}
        expected = {"id": 1}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.create_category(data, token)
            assert result == expected
            mock_request.assert_called_once_with(
                "POST", f"{self.BASE_URL}/app/categories", timeout=10, headers={"Authorization": f"Bearer {token}"}, json=data
            )

    def test_edit_category(self, client):
        token = "auth_token"
        cat_id = 1
        data = {"name": "Updated Cat"}
        expected = {"success": True}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.edit_category(data, token, cat_id)
            assert result == expected
            mock_request.assert_called_once_with(
                "PATCH", f"{self.BASE_URL}/app/categories/{cat_id}", timeout=10, headers={"Authorization": f"Bearer {token}"}, json=data
            )

    def test_delete_category(self, client):
        token = "auth_token"
        cat_id = 1
        expected = {"success": True}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.delete_category(token, cat_id)
            assert result == expected
            mock_request.assert_called_once_with(
                "DELETE", f"{self.BASE_URL}/app/categories/{cat_id}", timeout=10, headers={"Authorization": f"Bearer {token}"}
            )

    def test_get_document(self, client):
        doc_id = 1
        expected = {"id": 1, "name": "Doc"}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.get_document(doc_id)
            assert result == expected
            mock_request.assert_called_once_with(
                "GET", f"{self.BASE_URL}/app/documents/{doc_id}", timeout=10
            )

    def test_get_document_pages(self, client):
        doc_id = 1
        expected = {"pages": []}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.get_document_pages(doc_id)
            assert result == expected
            mock_request.assert_called_once_with(
                "GET", f"{self.BASE_URL}/app/documents/{doc_id}/pages", timeout=10
            )

    def test_create_document(self, client):
        token = "auth_token"
        data = {"name": "New Doc"}
        expected = {"id": 1}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.create_document(data, token)
            assert result == expected
            mock_request.assert_called_once_with(
                "POST", f"{self.BASE_URL}/app/documents", timeout=10, headers={"Authorization": f"Bearer {token}"}, json=data
            )

    def test_update_document(self, client):
        token = "auth_token"
        doc_id = 1
        data = {"name": "Updated Doc"}
        expected = {"success": True}
        with patch.object(client.session, "request") as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected
            mock_request.return_value = mock_response
            
            result = client.update_document(doc_id, data, token)
            assert result == expected
            mock_request.assert_called_once_with(
                "PATCH", f"{self.BASE_URL}/app/documents/{doc_id}", timeout=10, headers={"Authorization": f"Bearer {token}"}, json=data
            )
