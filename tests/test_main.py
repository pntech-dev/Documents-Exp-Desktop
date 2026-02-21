import pytest
from unittest.mock import Mock, patch, MagicMock
from modules.main.mvc.main_controller import MainController



class TestMainController:
    @pytest.fixture
    def controller(self, qapp):
        """Fixture to create MainController with mocked MVC components."""
        model = Mock()
        # Setup default model data
        model.departments = [{"id": 1, "name": "Dept 1", "documents_count": 5}]
        model.categories = [{"id": 10, "name": "Cat 1", "group_id": 1, "documents_count": 2}]
        model.current_department_id = 1
        model.current_category_id = None
        
        view = Mock()
        window = Mock()
        
        # Mock NotificationService and QTimer to avoid side effects
        with patch("modules.main.mvc.main_controller.NotificationService"), \
             patch("modules.main.mvc.main_controller.QTimer"):
            ctrl = MainController(model, view, window, mode="auth")
            yield ctrl


    def test_init_ui(self, controller):
        """Test UI initialization loads sidebar and user data."""
        controller.model.get_user_data.return_value = {"username": "User", "department": "IT"}
        
        controller._init_ui()
        
        controller.view.update_departments.assert_called()
        controller.view.update_categories.assert_called()
        controller.view.set_username.assert_called_with(name="User")


    def test_search_trigger(self, controller):
        """Test that typing in search triggers the search worker."""
        controller.view.get_search_text.return_value = "query"
        controller.view.get_search_filters.return_value = {}
        
        with patch("modules.main.mvc.main_controller.APIWorker") as MockWorker:
            controller._perform_search()
            
            MockWorker.assert_called()
            args, kwargs = MockWorker.call_args
            assert kwargs['query'] == "query"
            assert MockWorker.return_value.start.assert_called


    def test_department_selection(self, controller):
        """Test selecting a department updates state and UI."""
        # Mock selection event
        mock_index = Mock()
        mock_index.data.return_value = 2 # New Dept ID
        mock_selection = Mock()
        mock_selection.indexes.return_value = [mock_index]
        
        controller._on_department_selected(mock_selection, None)
        
        assert controller.model.current_department_id == 2
        assert controller.model.current_category_id is None
        controller.view.clear_documents_table.assert_called()
        controller.view.update_categories.assert_called()


    def test_category_selection(self, controller):
        """Test selecting a category triggers document loading."""
        mock_index = Mock()
        mock_index.data.return_value = 20 # New Cat ID
        mock_selection = Mock()
        mock_selection.indexes.return_value = [mock_index]
        
        # Ensure search text is empty so it triggers document loading
        controller.view.get_search_text.return_value = ""

        # Mock load worker
        with patch("modules.main.mvc.main_controller.APIWorker") as MockWorker:
            controller._on_category_selected(mock_selection, None)
            
            assert controller.model.current_category_id == 20
            # Should start loading documents
            MockWorker.assert_called()
            args, kwargs = MockWorker.call_args
            assert kwargs['category_id'] == 20


    def test_load_more_documents(self, controller):
        """Test pagination logic."""
        controller.model.current_category_id = 10
        controller.is_loading = False
        controller.has_more = True
        controller.offset = 0
        
        # Ensure search text is empty so it proceeds
        controller.view.get_search_text.return_value = ""

        with patch("modules.main.mvc.main_controller.APIWorker") as MockWorker:
            controller._load_more_documents()
            
            assert controller.is_loading is True
            MockWorker.assert_called()
            args, kwargs = MockWorker.call_args
            assert kwargs['offset'] == 0
            assert kwargs['limit'] == controller.limit


    def test_create_department_flow(self, controller):
        """Test create department dialog and model update."""
        with patch("modules.main.mvc.main_controller.CreateDepartment") as MockDialog:
            # Simulate dialog accepted with data
            MockDialog.get_data.return_value = ("New Dept", True, False)
            
            # Simulate API response
            controller.model.create_department.return_value = {"id": 99, "name": "New Dept"}
            
            controller._on_craete_department_clicked()
            
            controller.model.create_department.assert_called_with(
                name="New Dept", show_for_guest=True, has_all_docs_search=False
            )
            controller.model.refresh_data.assert_called()
            assert controller.model.current_department_id == 99


    def test_edit_department_flow(self, controller):
        """Test edit department dialog and model update."""
        # Setup existing department
        controller.model.departments = [{"id": 1, "name": "Old Name"}]
        
        with patch("modules.main.mvc.main_controller.EditDepartment") as MockDialog:
            # Simulate dialog accepted with 'edit' action
            MockDialog.show_dialog.return_value = ("edit", ("New Name", False, False))
            
            controller._on_edit_department_clicked("1")
            
            controller.model.edit_department.assert_called_with(
                name="New Name", department_id=1, show_for_guest=False, has_all_docs_search=False
            )
            controller.model.refresh_data.assert_called()


    def test_delete_department_flow(self, controller):
        """Test delete department action."""
        controller.model.departments = [{"id": 1, "name": "To Delete"}]
        
        with patch("modules.main.mvc.main_controller.EditDepartment") as MockDialog:
            # Simulate dialog accepted with 'delete' action
            MockDialog.show_dialog.return_value = ("delete", None)
            
            controller._on_edit_department_clicked("1")
            
            controller.model.delete_department.assert_called_with(department_id=1)
            controller.model.refresh_data.assert_called()


    def test_create_document_button(self, controller):
        """Test create document button opens editor."""
        controller.model.current_category_id = 10
        
        with patch("modules.main.mvc.main_controller.EditorWindow") as MockEditor:
            controller._on_create_button_clicked()
            
            MockEditor.assert_called_with(
                mode="auth",
                parent=controller.window,
                category_id=10,
                document_data={},
                pages=[]
            )
            MockEditor.return_value.show.assert_called_once()


    def test_logout(self, controller):
        """Test logout emits signal."""
        mock_slot = Mock()
        controller.logout_requested.connect(mock_slot)
        controller._on_logout_clicked()
        mock_slot.assert_called_once()