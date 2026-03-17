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
             patch("modules.main.mvc.main_controller.QTimer"), \
             patch("modules.main.mvc.main_controller.APIWorker"):
            ctrl = MainController(model, view, window, mode="auth")
            yield ctrl


    def test_init_ui(self, controller):
        """Test UI initialization starts background loading instead of blocking."""
        with patch("modules.main.mvc.main_controller.APIWorker") as MockWorker:
            controller._init_ui()

            MockWorker.assert_called_once_with(controller.model.load_initial_data)
            MockWorker.return_value.start.assert_called_once()

    def test_initial_data_loaded(self, controller):
        """Test applying startup data after the background worker finishes."""
        controller.initial_load_worker = Mock()
        with patch.object(controller, "sender", return_value=controller.initial_load_worker):
            controller._on_initial_data_loaded({
                "departments": [{"id": 1, "name": "Dept 1", "documents_count": 5}],
                "categories": [{"id": 10, "name": "Cat 1", "group_id": 1, "documents_count": 2}],
                "user_data": {"username": "User", "department": "Dept 1"},
            })

        controller.view.update_departments.assert_called()
        controller.view.update_categories.assert_called()
        controller.view.set_username.assert_called_with(name="User")

    def test_initial_data_error(self, controller):
        """Test startup error handling leaves the window in a safe state."""
        controller.initial_load_worker = Mock()
        with patch.object(controller, "sender", return_value=controller.initial_load_worker), \
             patch.object(controller, "_handle_error") as mock_handle_error:
            controller._on_initial_data_error(Exception("boom"))

        controller.view.set_username.assert_called_with("Пользователь")
        controller.view.set_user_department.assert_called_with("Не удалось загрузить данные")
        mock_handle_error.assert_called_once()


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
        controller.view.update_categories.assert_called()

    def test_department_selection_with_search_does_not_clear_table(self, controller):
        """With active search, department switch should not clear table before search response."""
        mock_index = Mock()
        mock_index.data.return_value = 2
        mock_selection = Mock()
        mock_selection.indexes.return_value = [mock_index]
        controller.view.get_search_text.return_value = "query"

        with patch.object(controller, "_update_documents_list") as mock_update_docs, \
             patch.object(controller, "_on_search_lineedit_text_changed") as mock_search_changed:
            controller._on_department_selected(mock_selection, None)

        mock_update_docs.assert_not_called()
        mock_search_changed.assert_called_once()


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

    def test_update_documents_list_keeps_previous_table_until_success(self, controller):
        """Reloading the table should not clear the old data before the new response arrives."""
        controller.model.current_category_id = 10
        controller.current_documents = [{"id": 1, "name": "Doc"}]
        controller.view.get_search_text.return_value = ""
        controller.view.clear_documents_table.reset_mock()

        with patch.object(controller, "_load_more_documents") as mock_load_more:
            controller._update_documents_list()

        assert controller.current_documents == [{"id": 1, "name": "Doc"}]
        controller.view.clear_documents_table.assert_not_called()
        mock_load_more.assert_called_once()

    def test_load_more_error_keeps_existing_documents_visible(self, controller):
        """A failed reload should not wipe the currently visible documents."""
        controller.current_documents = [{"id": 1, "name": "Existing"}]
        controller.current_load_worker = Mock()
        controller.view.clear_documents_table.reset_mock()

        with patch.object(controller, "sender", return_value=controller.current_load_worker), \
             patch.object(controller, "_handle_error") as mock_handle_error:
            controller._on_load_more_error(Exception("boom"))

        assert controller.current_documents == [{"id": 1, "name": "Existing"}]
        controller.view.clear_documents_table.assert_not_called()
        mock_handle_error.assert_called_once()

    def test_search_error_keeps_existing_documents_visible(self, controller):
        """A failed search should leave the previously rendered table intact."""
        controller.current_documents = [{"id": 1, "name": "Existing"}]
        controller.current_search_worker = Mock()
        controller.view.clear_documents_table.reset_mock()

        with patch.object(controller, "sender", return_value=controller.current_search_worker), \
             patch.object(controller, "_handle_error") as mock_handle_error:
            controller._on_search_error(Exception("boom"))

        assert controller.current_documents == [{"id": 1, "name": "Existing"}]
        controller.view.clear_documents_table.assert_not_called()
        mock_handle_error.assert_called_once()


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

    def test_filter_tag_toggle_handles_none_search_text(self, controller):
        """Filter toggling should handle empty/None search text safely."""
        controller.view.get_search_text.return_value = None
        controller.view.set_search_text.reset_mock()

        controller._on_filter_tag_toggled(True, "alpha")

        controller.view.set_search_text.assert_called_once_with("@alpha")

    def test_search_task_handles_invalid_virtual_category_id(self, controller):
        """Malformed virtual category id should not raise and should skip group filter."""
        controller.model.current_category_id = "virtual_x"
        controller.model.search_data.return_value = []

        result = controller._search_data_task("query", {}, [])

        assert result == []
        controller.model.search_data.assert_called_once_with(
            query="query",
            tags=[],
            category_id=None,
            group_id=None,
            filters={},
        )
