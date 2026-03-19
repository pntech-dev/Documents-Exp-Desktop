import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from modules.document_editor.mvc.document_editor_controller import DocumentEditorController
from modules.document_editor.mvc.document_editor_model import DocumentEditorModel



class TestDocumentEditorFiles:
    @pytest.fixture
    def controller(self, qapp):
        """Fixture to create a controller with mocked MVC components."""
        model = Mock()
        model.document_data = {"id": 1, "files": []}
        model.pending_files = []
        model.pages = [] # Fix: Initialize pages list to avoid iteration error in _init_ui
        view = Mock()
        view.get_document_data.return_value = {"tags": []} # Fix: Setup return value for len() check in _update_generate_button_state
        window = Mock()
        
        # Mock NotificationService to avoid errors during init AND execution
        with patch("modules.document_editor.mvc.document_editor_controller.NotificationService"):
            ctrl = DocumentEditorController("auth", model, view, window)
            yield ctrl


    def test_files_dropped_valid(self, controller):
        """Test dropping valid files adds them to pending and view."""
        files = ["/tmp/doc1.pdf", "/tmp/image.png"]
        
        # Mock Path to pass size check and existence
        with patch("modules.document_editor.mvc.document_editor_controller.Path") as mock_path:
            # Configure side effects for multiple files
            def path_side_effect(arg):
                p = MagicMock()
                p.name = str(arg).split("/")[-1]
                p.suffix = "." + str(arg).split(".")[-1]
                p.stat.return_value.st_size = 1024 # Small size
                return p
            
            mock_path.side_effect = path_side_effect

            controller._on_files_dropped(files)
            
            # Check view switch
            controller.view.switch_to_files_tab.assert_called_once()
            
            # Check model additions
            assert controller.model.add_pending_file.call_count == 2
            
            # Check view additions
            assert controller.view.add_file_widget.call_count == 2
            
            # Check data changed signal (UI update)
            # _on_document_data_changed sets is_document_edited = True on model
            # Since model is a Mock, we check if the attribute was set
            assert controller.model.is_document_edited is True

    def test_files_dropped_duplicate_paths_are_ignored(self, controller):
        files = ["/tmp/doc1.pdf", "/tmp/doc1.pdf"]

        with patch("modules.document_editor.mvc.document_editor_controller.Path") as mock_path:
            def path_side_effect(arg):
                p = MagicMock()
                p.name = str(arg).split("/")[-1]
                p.suffix = "." + str(arg).split(".")[-1]
                p.stat.return_value.st_size = 1024
                return p

            mock_path.side_effect = path_side_effect
            controller.model.add_pending_file.side_effect = [True, False]
            controller.model.is_document_edited = False

            controller._on_files_dropped(files)

            # Only first unique file should be shown in UI.
            assert controller.view.add_file_widget.call_count == 1
            assert controller.model.is_document_edited is True


    def test_files_dropped_blocked_extension(self, controller):
        """Test dropping files with blocked extensions."""
        files = ["/tmp/malware.exe"]
        
        with patch("modules.document_editor.mvc.document_editor_controller.Path") as mock_path, \
             patch("modules.document_editor.mvc.document_editor_controller.NotificationService") as mock_notify:
            
            p = MagicMock()
            p.suffix = ".exe"
            p.name = "malware.exe"
            mock_path.return_value = p
            
            controller._on_files_dropped(files)
            
            # Should show error toast
            mock_notify.return_value.show_toast.assert_called()
            assert "расширением" in mock_notify.return_value.show_toast.call_args[0][2]
            
            # Should NOT add to model/view
            controller.model.add_pending_file.assert_not_called()
            controller.view.add_file_widget.assert_not_called()


    def test_files_dropped_oversized(self, controller):
        """Test dropping oversized files (limit is 50MB based on context)."""
        files = ["/tmp/huge.pdf"]
        
        with patch("modules.document_editor.mvc.document_editor_controller.Path") as mock_path, \
             patch("modules.document_editor.mvc.document_editor_controller.NotificationService") as mock_notify:
            
            p = MagicMock()
            p.suffix = ".pdf"
            p.name = "huge.pdf"
            # 50MB + 1 byte
            p.stat.return_value.st_size = 50 * 1024 * 1024 + 1 
            mock_path.return_value = p
            
            controller._on_files_dropped(files)
            
            # Should show error toast
            mock_notify.return_value.show_toast.assert_called()
            assert "превышают" in mock_notify.return_value.show_toast.call_args[0][2]
            
            # Should NOT add
            controller.model.add_pending_file.assert_not_called()


    def test_delete_local_file(self, controller):
        """Test deleting a pending (local) file."""
        file_path = "/tmp/doc.pdf"
        controller._on_file_widget_deleted(file_path)
        
        controller.model.remove_pending_file.assert_called_once_with(file_path)
        controller.view.remove_file_widget.assert_called_once_with(file_path)


    def test_delete_remote_file(self, controller):
        """Test deleting an uploaded (remote) file."""
        file_id = 123
        
        with patch("modules.document_editor.mvc.document_editor_controller.NotificationService") as mock_notify:
            controller._on_file_widget_deleted(file_id)
            
            controller.model.delete_file.assert_called_once_with(file_id)
            controller.view.remove_file_widget.assert_called_once_with(file_id)
            mock_notify.return_value.show_toast.assert_called_with("success", "Файл удален", "Файл успешно удален.")


    def test_download_local_file(self, controller):
        """Test downloading (saving) a local pending file."""
        file_path = "/tmp/source.pdf"
        
        with patch("modules.document_editor.mvc.document_editor_controller.QFileDialog.getSaveFileName", return_value=("/tmp/dest.pdf", "")), \
             patch("modules.document_editor.mvc.document_editor_controller.shutil.copy2") as mock_copy, \
             patch("modules.document_editor.mvc.document_editor_controller.Path") as mock_path, \
             patch("modules.document_editor.mvc.document_editor_controller.NotificationService") as mock_notify:
            
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.name = "source.pdf"
            
            controller._on_file_download_requested(file_path)
            
            mock_copy.assert_called_once()
            mock_notify.return_value.show_toast.assert_called_with("success", "Скачивание", "Файл сохранен.")


    def test_download_remote_file(self, controller):
        """Test downloading a remote file starts a worker."""
        file_id = 123
        controller.model.document_data = {"files": [{"id": 123, "filename": "remote.pdf"}]}
        
        with patch("modules.document_editor.mvc.document_editor_controller.QFileDialog.getSaveFileName", return_value=("/tmp/remote.pdf", "")), \
             patch("modules.document_editor.mvc.document_editor_controller.APIWorker") as MockWorker:
            
            controller._on_file_download_requested(file_id)
            
            MockWorker.assert_called_once()
            assert MockWorker.return_value.start.called
            controller.window.setEnabled.assert_called_with(False)


    def test_open_remote_file(self, controller):
        """Test opening a remote file triggers download worker."""
        file_id = 123
        controller.model.document_data = {"files": [{"id": 123, "filename": "remote.pdf"}]}
        
        with patch("modules.document_editor.mvc.document_editor_controller.APIWorker") as MockWorker, \
             patch("modules.document_editor.mvc.document_editor_controller.tempfile.gettempdir", return_value="/tmp"), \
             patch("modules.document_editor.mvc.document_editor_controller.Path") as MockPath:
            
            # Setup MockPath to handle division and string conversion
            mock_path_instance = MagicMock()
            MockPath.return_value = mock_path_instance
            mock_path_instance.__truediv__.return_value = mock_path_instance
            mock_path_instance.__str__.return_value = "/tmp/Documents Exp/remote.pdf"
            
            controller._on_file_open_requested(file_id)
            
            MockWorker.assert_called_once()
            assert MockWorker.return_value.start.called



class TestDocumentEditorModelFiles:
    @pytest.fixture
    def model(self):
        with patch("modules.document_editor.mvc.document_editor_model.load_config", return_value={}), \
             patch("modules.document_editor.mvc.document_editor_model.APIClient") as MockClient, \
             patch("modules.document_editor.mvc.document_editor_model.get_app_data_dir"), \
             patch("modules.document_editor.mvc.document_editor_model.get_local_data_dir"):
            
            m = DocumentEditorModel()
            m.api = MockClient.return_value
            return m


    def test_upload_file(self, model):
        """Test upload file API call."""
        model.document_data = {"id": 1}
        file_path = "test.pdf"
        
        with patch("builtins.open", MagicMock()):
            model.upload_file(file_path)
            model.api.upload_file.assert_called_once()

    def test_add_pending_file_deduplicates_paths(self, model):
        assert model.add_pending_file("C:/Temp/test.pdf") is True
        assert model.add_pending_file("C:/Temp/test.pdf") is False
        assert len(model.pending_files) == 1


    def test_upload_pending_files_success(self, model):
        """Test uploading multiple pending files."""
        model.document_data = {"id": 1}
        model.pending_files = ["f1.pdf", "f2.pdf"]
        
        with patch("builtins.open", MagicMock()):
            model.upload_pending_files()
            
            assert model.api.upload_file.call_count == 2
            assert len(model.pending_files) == 0


    def test_upload_pending_files_failure(self, model):
        """Test upload pending files with failure."""
        model.document_data = {"id": 1}
        model.pending_files = ["f1.pdf"]
        
        with patch("builtins.open", MagicMock()):
            # Mock api.upload_file to raise exception
            model.api.upload_file.side_effect = Exception("Upload failed")
            
            with pytest.raises(Exception) as excinfo:
                model.upload_pending_files()
            
            assert "Upload failed" in str(excinfo.value)
            # File should remain in pending if failed
            assert "f1.pdf" in model.pending_files
