import pytest
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QDialog
from modules.categories_editings.create_category import CreateCategory
from modules.categories_editings.edit_category import EditCategory



class TestCategoryDialogs:
    
    @patch("ui.custom_widgets.lineedits.ThemeManagerInstance")
    def test_create_category_validation(self, mock_tm, qapp):
        """Test validation logic in CreateCategory dialog."""
        # Mock theme manager to avoid errors in IconLineEdit
        mock_tm.return_value.current_theme_id = "0"
        
        dialog = CreateCategory(None)
        
        # 1. Initial state: empty name -> button disabled
        assert dialog.ui.name_lineEdit.text() == ""
        assert dialog.ui.accept_pushButton.isEnabled() is False
        
        # 2. Valid name -> button enabled
        dialog.ui.name_lineEdit.setText("New Category")
        assert dialog.ui.accept_pushButton.isEnabled() is True
        
        # 3. Empty name -> button disabled
        dialog.ui.name_lineEdit.setText("")
        assert dialog.ui.accept_pushButton.isEnabled() is False
        
        dialog.close()


    @patch("ui.custom_widgets.buttons.ThemeManagerInstance")
    @patch("ui.custom_widgets.lineedits.ThemeManagerInstance")
    def test_edit_category_init(self, mock_tm_le, mock_tm_btn, qapp):
        """Test initialization of EditCategory dialog with existing data."""
        mock_tm_le.return_value.current_theme_id = "0"
        mock_tm_btn.return_value.current_theme_id = "0"
        
        dialog = EditCategory(None, current_name="Old Name", current_show_for_guest=True)
        
        assert dialog.ui.name_lineEdit.text() == "Old Name"
        assert dialog.ui.guest_show_checkBox.isChecked() is True
        # Button should be disabled as no changes were made yet
        assert dialog.ui.accept_pushButton.isEnabled() is False 
        
        dialog.close()


    @patch("ui.custom_widgets.buttons.ThemeManagerInstance")
    @patch("ui.custom_widgets.lineedits.ThemeManagerInstance")
    def test_edit_category_validation(self, mock_tm_le, mock_tm_btn, qapp):
        """Test validation logic in EditCategory dialog (change detection)."""
        mock_tm_le.return_value.current_theme_id = "0"
        mock_tm_btn.return_value.current_theme_id = "0"
        
        dialog = EditCategory(None, current_name="Original", current_show_for_guest=False)
        
        # 1. Change name -> button enabled
        dialog.ui.name_lineEdit.setText("Changed")
        assert dialog.ui.accept_pushButton.isEnabled() is True
        
        # 2. Revert name -> button disabled
        dialog.ui.name_lineEdit.setText("Original")
        assert dialog.ui.accept_pushButton.isEnabled() is False
        
        # 3. Change checkbox -> button enabled
        dialog.ui.guest_show_checkBox.setChecked(True)
        assert dialog.ui.accept_pushButton.isEnabled() is True
        
        # 4. Revert checkbox -> button disabled
        dialog.ui.guest_show_checkBox.setChecked(False)
        assert dialog.ui.accept_pushButton.isEnabled() is False
        
        # 5. Empty name (should be disabled even if changed from original)
        dialog.ui.name_lineEdit.setText("")
        assert dialog.ui.accept_pushButton.isEnabled() is False
        
        dialog.close()


    @patch("modules.categories_editings.edit_category.DeleteInfoDialog")
    @patch("ui.custom_widgets.buttons.ThemeManagerInstance")
    @patch("ui.custom_widgets.lineedits.ThemeManagerInstance")
    def test_edit_category_delete(self, mock_tm_le, mock_tm_btn, mock_delete_dialog, qapp):
        """Test delete button logic in EditCategory."""
        mock_tm_le.return_value.current_theme_id = "0"
        mock_tm_btn.return_value.current_theme_id = "0"
        
        # Setup DeleteInfoDialog mock to simulate user clicking "Delete"
        mock_delete_instance = mock_delete_dialog.return_value
        mock_delete_instance.exec_.return_value = QDialog.Accepted
        
        dialog = EditCategory(None, current_name="Cat")
        
        # Trigger delete action
        dialog.delete_button_clicked()
        
        # Verify DeleteInfoDialog was called correctly
        mock_delete_dialog.assert_called_with(parent=None, info_type="category")
        assert dialog.action == "delete"