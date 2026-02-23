import pytest
from unittest.mock import Mock, patch

from utils.delete_info_modal import DeleteInfoDialog
from utils.email_confirm_modal import EmailConfirmDialog
from utils.update_confirm_modal import UpdateConfirmDialog
from utils.install_confirm_modal import InstallConfirmDialog
from utils.update_progress_modal import UpdateProgressDialog



class TestModalDialogs:
    
    @patch("utils.delete_info_modal.ThemeManagerInstance")
    def test_delete_info_dialog_content(self, mock_tm, qapp):
        """Test: DeleteInfoDialog sets correct text based on type."""
        mock_tm.return_value.current_theme_id = "0"
        
        # Test for 'department'
        dialog = DeleteInfoDialog(info_type="department")
        assert dialog.ui.title_label.text() == "Удаление отдела"
        assert dialog.ui.delete_pushButton.text() == "Удалить отдел"
        dialog.close()

        # Test for 'category'
        dialog = DeleteInfoDialog(info_type="category")
        assert dialog.ui.title_label.text() == "Удаление категории"
        assert dialog.ui.delete_pushButton.text() == "Удалить категорию"
        dialog.close()
        
        # Test for 'document'
        dialog = DeleteInfoDialog(info_type="document")
        assert dialog.ui.title_label.text() == "Удаление документа"
        assert dialog.ui.delete_pushButton.text() == "Удалить документ"
        dialog.close()


    @patch("ui.custom_widgets.lineedits.ThemeManagerInstance")
    def test_email_confirm_validation(self, mock_tm, qapp):
        """Test: Confirm button in EmailConfirmDialog enabled only with 6 digits."""
        mock_tm.return_value.current_theme_id = "0"
        
        # Create dialog
        dialog = EmailConfirmDialog()
        
        # Scenario 1: 3 digits (button disabled)
        dialog.ui.verification_code_lineEdit.setText("123")
        dialog.code_lineedit_changed()
        assert dialog.ui.accept_pushButton.isEnabled() is False
        
        # Scenario 2: 6 digits (button enabled)
        dialog.ui.verification_code_lineEdit.setText("123456")
        dialog.code_lineedit_changed()
        assert dialog.ui.accept_pushButton.isEnabled() is True
        
        dialog.close()


    @patch("ui.custom_widgets.buttons.ThemeManagerInstance")
    def test_update_confirm_dialog_version(self, mock_tm, qapp):
        """Test: UpdateConfirmDialog displays correct version."""
        mock_tm.return_value.current_theme_id = "0"
        version = "2.5.0"
        dialog = UpdateConfirmDialog(version=version)
        
        # Verify that the label text contains the version
        assert version in dialog.info_label.text()
        dialog.close()


    @patch("ui.custom_widgets.buttons.ThemeManagerInstance")
    def test_install_confirm_dialog_init(self, mock_tm, qapp):
        """Test: InstallConfirmDialog initializes without errors."""
        mock_tm.return_value.current_theme_id = "0"
        try:
            dialog = InstallConfirmDialog()
            assert dialog is not None
            dialog.close()
        except Exception as e:
            pytest.fail(f"InstallConfirmDialog failed to initialize: {e}")

    @patch("ui.custom_widgets.progress_bar.ThemeManagerInstance")
    @patch("ui.custom_widgets.buttons.ThemeManagerInstance")
    def test_update_progress_dialog(self, mock_tm_btn, mock_tm_pb, qapp):
        """Test: UpdateProgressDialog updates progress and handles cancel."""
        mock_tm_btn.return_value.current_theme_id = "0"
        mock_tm_pb.return_value.current_theme_id = "0"
        
        dialog = UpdateProgressDialog()
        
        # 1. Initial state
        assert dialog.title_label.text() == "Скачивание обновления..."
        assert dialog.progress_bar.value() == 0
        
        # 2. Progress update (Normal)
        # 5 MB downloaded of 10 MB
        current = 5 * 1024 * 1024
        total = 10 * 1024 * 1024
        dialog.set_progress(current, total)
        
        assert dialog.progress_bar.value() == 50
        assert "5.0" in dialog.status_label.text()
        assert "10.0" in dialog.status_label.text()
        assert "50%" in dialog.status_label.text()
        
        # 3. Progress update (Unknown size)
        dialog.set_progress(2 * 1024 * 1024, 0)
        assert dialog.progress_bar.maximum() == 0
        assert "2.0 MB" in dialog.status_label.text()
        
        # 4. Cancel signal
        mock_signal = Mock()
        dialog.canceled.connect(mock_signal)
        dialog.reject()
        mock_signal.assert_called_once()
        
        dialog.close()