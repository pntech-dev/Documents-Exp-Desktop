import pytest
from unittest.mock import Mock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from ui.custom_widgets.lineedits import TagsLineEdit
from ui.custom_widgets.treeview import SidebarBlock, SidebarItem, ROLE_ID, ROLE_COUNT
from ui.custom_widgets.switchers import ThemeSwitch
from ui.custom_widgets.hints import PasswordHint
from ui.custom_widgets.table import EditorTableView, ROLE_CHECK_STATE



class TestTagsLineEdit:
    
    @patch("ui.custom_widgets.lineedits.ThemeManagerInstance")
    def test_add_tag(self, mock_tm, qapp):
        """Test adding tags logic."""
        widget = TagsLineEdit()
        
        # 1. Add normal tag
        widget.add_tag("python")
        assert widget.get_tags() == ["python"]
        
        # 2. Add duplicate (should be ignored)
        widget.add_tag("python")
        assert widget.get_tags() == ["python"]
        
        # 3. Add another tag
        widget.add_tag("qt")
        assert widget.get_tags() == ["python", "qt"]


    @patch("ui.custom_widgets.lineedits.ThemeManagerInstance")
    def test_max_tags_limit(self, mock_tm, qapp):
        """Test that input is disabled when max tags limit is reached."""
        widget = TagsLineEdit()
        # Manually set limit for testing
        widget._max_tags = 3
        
        widget.add_tag("1")
        widget.add_tag("2")
        widget.add_tag("3")
        
        # Try adding 4th tag
        widget.add_tag("4")
        
        assert widget.get_tags() == ["1", "2", "3"]
        # Verify line edit is disabled and has placeholder
        assert widget.line_edit.isEnabled() is False
        assert "максимум" in widget.line_edit.placeholderText()


    @patch("ui.custom_widgets.lineedits.ThemeManagerInstance")
    def test_remove_tag(self, mock_tm, qapp):
        """Test removing tags and re-enabling input."""
        widget = TagsLineEdit()
        widget._max_tags = 2
        widget.add_tag("tag1")
        widget.add_tag("tag2")
        
        # Input should be disabled now
        assert widget.line_edit.isEnabled() is False
        
        # Find the tag widget to remove
        # Layout structure: [Tag1, Tag2, LineEdit, Counter]
        layout = widget.layout()
        tag_widget = None
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if hasattr(w, "text") and w.text() == "tag1":
                tag_widget = w
                break
        
        widget.remove_tag(tag_widget)
        
        assert widget.get_tags() == ["tag2"]
        # Input should be re-enabled
        assert widget.line_edit.isEnabled() is True
        assert widget.line_edit.placeholderText() == ""



class TestSidebarBlock:
    
    @patch("ui.custom_widgets.treeview.ThemeManagerInstance")
    def test_set_items(self, mock_tm, qapp):
        """Test populating the sidebar with items."""
        sidebar = SidebarBlock()
        items = [
            SidebarItem(id="1", title="Dept 1", count=5),
            SidebarItem(id="2", title="Dept 2", count=0)
        ]
        
        sidebar.set_items(items, group_title="Departments")
        
        model = sidebar.model()
        # Row 0 is the group "Departments"
        group_item = model.item(0)
        assert group_item.text() == "Departments"
        
        # Children of the group
        assert group_item.rowCount() == 2
        item1 = group_item.child(0)
        assert item1.data(ROLE_ID) == "1"
        assert item1.data(ROLE_COUNT) == 5
        
        item2 = group_item.child(1)
        assert item2.data(ROLE_ID) == "2"
        assert item2.text() == "Dept 2"


    @patch("ui.custom_widgets.treeview.ThemeManagerInstance")
    def test_update_count(self, mock_tm, qapp):
        """Test updating the badge count for an item."""
        sidebar = SidebarBlock()
        items = [SidebarItem(id="1", title="Item 1", count=0)]
        sidebar.set_items(items)
        
        sidebar.update_count("1", 10)
        
        # Verify model data
        model = sidebar.model()
        item = model.item(0) # No group, so it's at root
        assert item.data(ROLE_COUNT) == 10


    @patch("ui.custom_widgets.treeview.ThemeManagerInstance")
    def test_selection(self, mock_tm, qapp):
        """Test selecting an item by ID."""
        sidebar = SidebarBlock()
        items = [
            SidebarItem(id="A", title="A"),
            SidebarItem(id="B", title="B")
        ]
        sidebar.set_items(items)
        
        sidebar.set_selected("B")
        assert sidebar.get_selected_id() == "B"



class TestThemeSwitch:
    
    @patch("ui.custom_widgets.switchers.ThemeManagerInstance")
    def test_toggle(self, mock_tm, qapp):
        """Test toggling the theme switch."""
        switch = ThemeSwitch()
        
        # Initial state
        assert switch.isChecked() is False
        
        # Toggle on
        switch.setChecked(True)
        assert switch.isChecked() is True
        
        # Toggle off
        switch.setChecked(False)
        assert switch.isChecked() is False


    @patch("ui.custom_widgets.switchers.ThemeManagerInstance")
    def test_click_signal(self, mock_tm, qapp):
        """Test that clicking emits the signal."""
        switch = ThemeSwitch()
        mock_signal = Mock()
        switch.clicked.connect(mock_signal)
        
        switch.setChecked(True)
        mock_signal.assert_called_with(True)



class TestPasswordHint:
    
    def test_update_status(self, qapp):
        """Test updating the password hint status list."""
        hint = PasswordHint()
        status = [
            {"text": "Rule 1", "valid": True},
            {"text": "Rule 2", "valid": False}
        ]
        
        hint.update_status(status)
        
        # Check if labels were created in internal list
        assert len(hint.labels) == 2
        assert hint.labels[0].text() == "• Rule 1"
        assert hint.labels[0].property("valid") is True
        assert hint.labels[1].text() == "• Rule 2"
        assert hint.labels[1].property("valid") is False



class TestEditorTableView:
    
    @patch("ui.custom_widgets.table.ThemeManagerInstance")
    def test_set_rows(self, mock_tm, qapp):
        """Test populating the editor table."""
        table = EditorTableView()
        rows = [
            ("1", "Doc 1", "Code 1"),
            ("2", "Doc 2", "Code 2")
        ]
        
        table.set_rows(rows)
        
        model = table.model()
        assert model.rowCount() == 2
        
        # Check first row
        # Col 0: Checkbox (UserRole stores ID)
        assert model.item(0, 0).data(Qt.UserRole) == "1"
        assert model.item(0, 0).data(ROLE_CHECK_STATE) == Qt.Unchecked
        
        # Col 1: Name
        assert model.item(0, 1).text() == "Doc 1"
        
        # Col 2: Designation
        assert model.item(0, 2).text() == "Code 1"
