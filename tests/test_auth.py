import pytest
from unittest.mock import Mock, patch, MagicMock
from modules.auth.mvc.auth_model import AuthModel
from modules.auth.mvc.auth_controller import AuthController



class TestAuthModel:
    @pytest.fixture
    def model(self):
        """Fixture to create AuthModel with mocked dependencies."""
        with patch("modules.auth.mvc.auth_model.load_config", return_value={}), \
             patch("modules.auth.mvc.auth_model.APIClient") as MockAPIClient, \
             patch("modules.auth.mvc.auth_model.get_app_data_dir") as mock_app_dir, \
             patch("modules.auth.mvc.auth_model.get_local_data_dir") as mock_local_dir:
            
            mock_app_dir.return_value = MagicMock()
            mock_local_dir.return_value = MagicMock()
            
            model = AuthModel()
            # APIClient is instantiated in __init__, so we get the mock instance
            model.api = MockAPIClient.return_value 
            return model


    def test_login(self, model):
        """Test login method calls API correctly."""
        model.api.login.return_value = {"token": "123"}
        assert model.login("test@test.com", "pass") == {"token": "123"}
        model.api.login.assert_called_once_with(email="test@test.com", password="pass")


    def test_signup(self, model):
        """Test signup method calls API correctly."""
        model.api.signup.return_value = {"status": "ok"}
        assert model.signup("123456", "test@test.com", "pass") == {"status": "ok"}
        model.api.signup.assert_called_once_with(code="123456", email="test@test.com", password="pass")


    def test_save_user(self, model):
        """Test saving user data to keyring and file."""
        user_data = {
            "user": {"id": 1, "email": "test@test.com", "username": "User", "department": "Dept"},
            "access_token": "acc",
            "refresh_token": "ref"
        }
        
        with patch("modules.auth.mvc.auth_model.keyring.set_password") as mock_keyring, \
             patch("builtins.open", new_callable=MagicMock) as mock_open, \
             patch("json.dump") as mock_json_dump:
            
            model.save_user(user_data, True)
            
            # Check keyring
            assert mock_keyring.call_count == 2
            mock_keyring.assert_any_call(service_name="Documents Exp", username="access_token_1", password="acc")
            mock_keyring.assert_any_call(service_name="Documents Exp", username="refresh_token_1", password="ref")
            
            # Check file writing (user data and last logged)
            assert mock_open.call_count >= 2

    def test_save_token_raises_when_keyring_write_fails(self, model):
        with patch("modules.auth.mvc.auth_model.keyring.set_password", side_effect=Exception("keyring fail")):
            with pytest.raises(RuntimeError):
                model.save_token("access_token_1", "access_token", {"access_token": "acc"})


    def test_logout(self, model):
        """Test logout clears keyring and deletes last logged file."""
        # Configure the mock path object to simulate file existence
        model.LOCAL_DIR_LAST_LOGGED.exists.return_value = True

        with patch("modules.auth.mvc.auth_model.read_json", side_effect=[{"user_id": 1}, {"auto_login": True}]), \
             patch("modules.auth.mvc.auth_model.keyring.delete_password") as mock_keyring_del:
            
            with patch("builtins.open", new_callable=MagicMock) as mock_open, \
                 patch("json.dump") as mock_json_dump:
                model.logout()
            
            assert mock_keyring_del.call_count == 2
            assert mock_open.call_count >= 1
            mock_json_dump.assert_called()
            model.LOCAL_DIR_LAST_LOGGED.unlink.assert_called_once()


    def test_verify_token(self, model):
        """Test token verification logic."""
        with patch("modules.auth.mvc.auth_model.read_json", return_value={"user_id": 1}), \
             patch("modules.auth.mvc.auth_model.keyring.get_password", return_value="valid_token"):
            
            model.api.verify.return_value = {"user": "data"}
            result = model.verify_token()
            
            assert result == {"user": "data"}
            model.api.verify.assert_called_once_with(token="valid_token")



class TestAuthController:
    @pytest.fixture
    def controller(self, qapp):
        """Fixture to create AuthController with mocked MVC components."""
        model = Mock()
        view = Mock()
        window = Mock()
        
        # Mock view pages structure
        view.login_page = Mock()
        view.signup_page = Mock()
        view.forgot_page_email_confirm = Mock()
        view.forgot_page_reset_password = Mock()
        view.pages = {}
        
        # Mock NotificationService to avoid errors during init
        with patch("modules.auth.mvc.auth_controller.NotificationService"), \
             patch("modules.auth.mvc.auth_controller.FieldValidator") as mock_validator:
            
            ctrl = AuthController(model, view, window)
            # Attach validator mock to controller instance for easy access in tests
            ctrl.field_validator = mock_validator.return_value
            yield ctrl


    def test_login_flow(self, controller):
        """Test login button click initiates worker with correct params."""
        # Setup view data
        controller.view.login_page.get_email.return_value = "test@test.com"
        controller.view.login_page.get_password.return_value = "password"
        
        # Mock worker creation to execute immediately or check call
        with patch.object(controller, "_create_worker") as mock_worker:
            controller.on_login_page_login_button_clicked()
            
            mock_worker.assert_called_once()
            args, kwargs = mock_worker.call_args
            assert kwargs['method'] == controller.model.login
            assert kwargs['email'] == "test@test.com"
            assert kwargs['password'] == "password"


    def test_login_success_callback(self, controller):
        """Test login success callback saves user and emits signal."""
        data = {"user": {"id": 1}}
        controller.view.login_page.get_auto_login_state.return_value = True
        controller.model.save_user.return_value = 1
        
        # Mock signal
        mock_signal = Mock()
        controller.login_successful.connect(mock_signal)
        
        controller.login_user(data)
        
        controller.model.save_user.assert_called_once_with(user_data=data, auto_login=True)
        controller.view.login_page.clear_lineedits.assert_called_once()
        mock_signal.assert_called_once_with("auth", 1)

    def test_login_success_callback_handles_save_error(self, controller):
        data = {"user": {"id": 1}}
        controller.view.login_page.get_auto_login_state.return_value = True
        controller.model.save_user.side_effect = RuntimeError("keyring fail")

        mock_signal = Mock()
        controller.login_successful.connect(mock_signal)

        with patch("modules.auth.mvc.auth_controller.NotificationService") as MockNotify:
            controller.login_user(data)

        mock_signal.assert_not_called()
        controller.view.login_page.clear_lineedits.assert_not_called()
        MockNotify.return_value.show_toast.assert_called_once()

    def test_reset_password_page_switch_handles_save_error(self, controller):
        controller.view.pages = {"change_password_change_page": Mock()}
        controller.model.save_token.side_effect = RuntimeError("keyring fail")

        with patch("modules.auth.mvc.auth_controller.NotificationService") as MockNotify:
            controller.switch_to_reset_password_page({"reset_token": "token"})

        controller.view.switch_page.assert_not_called()
        MockNotify.return_value.show_toast.assert_called_once()


    def test_signup_flow(self, controller):
        """Test signup button click initiates code sending."""
        controller.view.signup_page.get_email.return_value = "new@test.com"
        controller.view.signup_page.get_password.return_value = "pass"
        
        with patch.object(controller, "_create_worker") as mock_worker:
            controller.on_signup_page_create_button_clicked()
            
            mock_worker.assert_called_once()
            args, kwargs = mock_worker.call_args
            assert kwargs['method'] == controller.model.signup_send_code
            assert kwargs['email'] == "new@test.com"


    def test_validation_login(self, controller):
        """Test login form validation enables submit button."""
        # Setup validator mock
        controller.field_validator.validate_email.return_value = True
        controller.field_validator.validate_password.return_value = True
        
        controller.view.login_page.get_email.return_value = "valid@email.com"
        controller.view.login_page.get_password.return_value = "ValidPass1!"
        
        controller.on_login_page_lineedits_changed()
        
        controller.view.login_page.update_submit_button_state.assert_called_with(state=True)


    def test_validation_login_invalid(self, controller):
        """Test login form validation fails with invalid email."""
        controller.field_validator.validate_email.return_value = False
        
        controller.view.login_page.get_email.return_value = "invalid"
        controller.on_login_page_lineedits_changed()
        
        controller.view.login_page.update_submit_button_state.assert_called_once_with(state=False)

    def test_validation_login_invalid_password_disables_submit(self, controller):
        controller.field_validator.validate_email.return_value = True
        controller.field_validator.validate_password.return_value = False
        controller.view.login_page.get_email.return_value = "valid@test.com"
        controller.view.login_page.get_password.return_value = "short"

        controller.on_login_page_lineedits_changed()

        controller.view.login_page.update_submit_button_state.assert_called_once_with(state=False)

    def test_validation_signup_invalid_email_disables_submit(self, controller):
        controller.field_validator.validate_email.return_value = False
        controller.view.signup_page.get_email.return_value = "invalid"

        controller.on_signup_page_lineedits_changed()

        controller.view.signup_page.update_submit_button_state.assert_called_once_with(state=False)

    def test_validation_reset_password_invalid_disables_submit(self, controller):
        controller.field_validator.validate_password.return_value = False
        controller.view.forgot_page_reset_password.get_password.return_value = "123"
        controller.view.forgot_page_reset_password.get_confirm_password.return_value = "123"

        controller.on_reset_password_page_lineedits_changed()

        controller.view.forgot_page_reset_password.update_submit_button_state.assert_called_once_with(state=False)

    def test_signup_skips_worker_when_confirmation_code_cancelled(self, controller):
        with patch("modules.auth.mvc.auth_controller.EmailConfirmDialog.get_code", return_value=None), \
             patch.object(controller, "_create_worker") as mock_create_worker, \
             patch("modules.auth.mvc.auth_controller.NotificationService") as MockNotify:
            controller.signup(data={}, email="new@test.com", password="StrongPass123")

        mock_create_worker.assert_not_called()
        MockNotify.return_value.show_toast.assert_any_call(
            notification_type="info",
            title="Подтверждение отменено",
            message="Регистрация не завершена: код подтверждения не введён."
        )

    def test_reset_confirm_skips_worker_when_confirmation_code_cancelled(self, controller):
        with patch("modules.auth.mvc.auth_controller.EmailConfirmDialog.get_code", return_value=""), \
             patch.object(controller, "_create_worker") as mock_create_worker, \
             patch("modules.auth.mvc.auth_controller.NotificationService") as MockNotify:
            controller.open_email_confirm_modal_window(data={}, email="new@test.com")

        mock_create_worker.assert_not_called()
        MockNotify.return_value.show_toast.assert_called_once()
