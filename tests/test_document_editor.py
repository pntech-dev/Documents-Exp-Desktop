import pytest
from unittest.mock import Mock, patch, MagicMock
from modules.document_editor.mvc.document_editor_model import DocumentEditorModel
from modules.document_editor.mvc.document_editor_controller import DocumentEditorController



class TestDocumentEditorModel:
    @pytest.fixture
    def model(self):
        """Fixture to create a model instance with mocked dependencies."""
        with patch("modules.document_editor.mvc.document_editor_model.load_config", return_value={}), \
             patch("modules.document_editor.mvc.document_editor_model.APIClient"), \
             patch("modules.document_editor.mvc.document_editor_model.get_app_data_dir"), \
             patch("modules.document_editor.mvc.document_editor_model.get_local_data_dir"):
            return DocumentEditorModel()


    def test_save_document_create(self, model):
        """Test saving a new document (create mode)."""
        model.document_data = {} # No ID -> Create
        model.category_id = 1
        model._make_authorized_request = Mock()
        
        data = {"name": "New Doc"}
        model.save_document(data)
        
        model._make_authorized_request.assert_called_once()
        args, kwargs = model._make_authorized_request.call_args
        # Should call create_document (passed as first arg) with category_id injected
        assert kwargs['data'] == {"name": "New Doc", "category_id": 1}


    def test_save_document_update(self, model):
        """Test saving an existing document (update mode)."""
        model.document_data = {"id": 123}
        model._make_authorized_request = Mock()
        
        data = {"name": "Updated Doc"}
        model.save_document(data)
        
        model._make_authorized_request.assert_called_once()
        args, kwargs = model._make_authorized_request.call_args
        # Should call update_document with document_id
        assert kwargs['document_id'] == 123
        assert kwargs['data'] == {"name": "Updated Doc"}


    def test_import_from_docx(self, model):
        """Test importing pages from a DOCX file."""
        with patch("modules.document_editor.mvc.document_editor_model.docx.Document") as mock_doc_cls:
            mock_doc = Mock()
            mock_doc_cls.return_value = mock_doc
            
            # Create mock table structure
            mock_table = Mock()
            
            # Header row (must match synonyms in model)
            header_row = Mock()
            header_row.cells = [Mock(text="Наименование"), Mock(text="Код")]
            
            # Data row
            data_row = Mock()
            data_row.cells = [Mock(text="Page 1"), Mock(text="CODE-001")]
            
            mock_table.rows = [header_row, data_row]
            mock_doc.tables = [mock_table]
            
            pages = model.import_from_docx("dummy.docx")
            
            assert len(pages) == 1
            assert pages[0]["name"] == "Page 1"
            assert pages[0]["designation"] == "CODE-001"


    def test_export_to_docx(self, model, tmp_path):
        """Test exporting document data to a DOCX file."""
        with patch("modules.document_editor.mvc.document_editor_model.docx.Document") as mock_doc_cls:
            mock_doc = MagicMock()
            mock_doc_cls.return_value = mock_doc
            
            data = {
                "code": "DOC-001",
                "name": "Test Doc",
                "pages": [{"name": "P1", "designation": "D1"}]
            }
            
            model.export_to_docx(str(tmp_path), "export.docx", data)
            
            # Verify interactions with python-docx
            mock_doc.add_heading.assert_called()
            mock_doc.add_table.assert_called()
            mock_doc.save.assert_called_with(str(tmp_path / "export.docx"))



class TestDocumentEditorController:
    @pytest.fixture
    def controller(self, qapp):
        """Fixture to create a controller with mocked MVC components."""
        model = Mock()
        # Fix: Initialize data attributes to avoid iteration errors during Controller init
        model.document_data = {}
        model.pages = []
        view = Mock()
        window = Mock()
        
        # Mock NotificationService to avoid errors during init AND execution
        with patch("modules.document_editor.mvc.document_editor_controller.NotificationService"):
            ctrl = DocumentEditorController("auth", model, view, window)
            yield ctrl


    def test_generate_tags(self, controller):
        """Test automatic tag generation logic."""
        # Setup mock data
        # Name has "Project" (7 chars), "Alpha" (5 chars)
        # Pages have "Page" (4 chars), "Alpha" (5 chars), "Gamma" (5 chars)
        controller.view.get_document_data.return_value = {
            "name": "Project Alpha",
            "pages": [
                {"name": "Page One Alpha"},
                {"name": "Page Two Gamma"}
            ]
        }
        
        # Reset mock calls from initialization
        controller.view.set_document_tags.reset_mock()
        
        controller._generate_tags()
        
        # Verify set_document_tags was called
        controller.view.set_document_tags.assert_called_once()
        tags = controller.view.set_document_tags.call_args[1]['tags']
        
        # Check expected tags (Capitalized)
        assert "Project" in tags
        assert "Alpha" in tags
        assert "Page" in tags
        assert "Gamma" in tags

    def test_generate_tags_handles_none_names(self, controller):
        """Tag generation should not crash when name fields are None."""
        controller.view.get_document_data.return_value = {
            "name": None,
            "pages": [
                {"name": None},
                {"name": "Valid Tag Name"},
            ],
        }

        controller.view.set_document_tags.reset_mock()
        controller._generate_tags()

        controller.view.set_document_tags.assert_called_once()


    def test_save_button_clicked(self, controller):
        """Test save button handler initiates background task."""
        controller.view.get_document_data.return_value = {"name": "Doc"}
        
        with patch("modules.document_editor.mvc.document_editor_controller.APIWorker") as MockWorker:
            controller._on_save_button_clicked()
            
            MockWorker.assert_called_once()
            args, kwargs = MockWorker.call_args
            assert args[0] == controller._save_task
            assert kwargs['data'] == {"name": "Doc"}
            MockWorker.return_value.start.assert_called_once()
            controller.window.setEnabled.assert_called_with(False)


    def test_save_task(self, controller):
        """Test background save task logic."""
        controller.model.document_data = {"id": 1}
        data = {"name": "Doc"}
        controller.model.pending_files = []
        
        is_creation, result_data = controller._save_task(data)
        
        assert is_creation is False
        assert result_data == data
        controller.model.save_document.assert_called_once_with(data=data)


    def test_on_save_finished(self, controller):
        """Test save finished handler updates UI."""
        result = (False, {"name": "Doc", "code": "123"})
        
        # Mock sender to avoid issues if called directly
        with patch.object(controller, "sender", return_value=None):
            controller._on_save_finished(result)
        
        controller.window.setEnabled.assert_called_with(True)
        controller.window.document_saved.emit.assert_called_once()
        controller.window.close.assert_called_once()


    def test_delete_document_clicked(self, controller):
        """Test delete document handler with confirmation dialog."""
        with patch("modules.document_editor.mvc.document_editor_controller.DeleteInfoDialog") as mock_dialog:
            mock_instance = mock_dialog.return_value
            mock_instance.exec_.return_value = 1 # QDialog.Accepted
            
            controller._on_delete_document_button_clicked()
            
            controller.model.delete_document.assert_called_once()
            controller.window.document_deleted.emit.assert_called_once()
            controller.window.close.assert_called_once()
