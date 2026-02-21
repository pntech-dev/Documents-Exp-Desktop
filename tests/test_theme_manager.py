import json
import pytest
from unittest.mock import Mock, patch
from utils.theme_manager import ThemeManager



@pytest.fixture
def mock_configs(tmp_path):
    """Creates a temporary configuration file structure."""
    # Create config.yaml
    config_yaml = tmp_path / "config.yaml"
    config_yaml.write_text("ui_config_path: ui/ui_config.json", encoding="utf-8")
    
    # Create ui_config.json
    ui_config_dir = tmp_path / "ui"
    ui_config_dir.mkdir()
    ui_config_file = ui_config_dir / "ui_config.json"
    
    ui_data = {
        "paths": {
            "themes_path": "ui/styles/themes/",
            "templates_path": "ui/styles/templates/"
        },
        "themes": {
            "0": "light",
            "1": "dark"
        },
        "notifications": {
            "spacing": 10,
            "toast_duration": 5000
        },
        "tokens": {
            "light_theme": {"color": "#FFFFFF"},
            "dark_theme": {"color": "#000000"}
        }
    }
    ui_config_file.write_text(json.dumps(ui_data), encoding="utf-8")
    
    return tmp_path



class TestThemeManager:
    
    def test_init_success(self, mock_configs):
        """Test successful initialization and config loading."""
        with patch("utils.theme_manager.get_app_root", return_value=mock_configs):
            tm = ThemeManager()
            assert tm.current_theme_id == "0"
            assert tm.themes["0"] == "light"
            assert tm.themes["1"] == "dark"


    def test_init_no_config(self, tmp_path):
        """Test initialization when config is missing (should not crash)."""
        with patch("utils.theme_manager.get_app_root", return_value=tmp_path):
            tm = ThemeManager()
            assert tm.themes == {}
            assert tm.current_theme_id == "0"


    def test_switch_theme_toggle(self, mock_configs):
        """Test toggling theme (0 <-> 1)."""
        with patch("utils.theme_manager.get_app_root", return_value=mock_configs):
            tm = ThemeManager()
            
            # Mock _apply_theme to avoid touching QApplication
            with patch.object(tm, "_apply_theme") as mock_apply:
                # 0 -> 1
                tm.switch_theme()
                assert tm.current_theme_id == "1"
                mock_apply.assert_called_once()
                
                # 1 -> 0
                mock_apply.reset_mock()
                tm.switch_theme()
                assert tm.current_theme_id == "0"
                mock_apply.assert_called_once()


    def test_switch_theme_specific(self, mock_configs):
        """Test switching to a specific theme ID."""
        with patch("utils.theme_manager.get_app_root", return_value=mock_configs):
            tm = ThemeManager()
            with patch.object(tm, "_apply_theme") as mock_apply:
                tm.switch_theme(1) # int
                assert tm.current_theme_id == "1"
                
                tm.switch_theme("0") # str
                assert tm.current_theme_id == "0"
                
                # Non-existent theme
                tm.switch_theme("999")
                assert tm.current_theme_id == "0" # Should not change


    def test_compile_themes(self, mock_configs):
        """Test compiling Jinja2 templates into QSS."""
        # Create template
        templates_dir = mock_configs / "ui/styles/templates"
        templates_dir.mkdir(parents=True)
        (templates_dir / "light.j2").write_text("QWidget { background: {{ color }}; }", encoding="utf-8")
        
        themes_dir = mock_configs / "ui/styles/themes"
        themes_dir.mkdir(parents=True, exist_ok=True)
        
        with patch("utils.theme_manager.get_app_root", return_value=mock_configs):
            tm = ThemeManager()
            
            # Run compilation
            success = tm._compile_all_themes()
            assert success is True
            
            # Verify file creation and token substitution
            light_qss = themes_dir / "light.qss"
            assert light_qss.exists()
            content = light_qss.read_text(encoding="utf-8")
            assert "background: #FFFFFF;" in content


    def test_notification_config(self, mock_configs):
        """Test accessing notification configuration."""
        with patch("utils.theme_manager.get_app_root", return_value=mock_configs):
            tm = ThemeManager()
            config = tm.notification_config
            assert config["spacing"] == 10
            assert config["toast_duration"] == 5000


    def test_auto_compile_on_missing_qss(self, mock_configs):
        """Test that themes are recompiled if QSS is missing during switch."""
        # Create templates but NO qss files
        templates_dir = mock_configs / "ui/styles/templates"
        templates_dir.mkdir(parents=True)
        (templates_dir / "light.j2").write_text("QWidget { background: {{ color }}; }", encoding="utf-8")
        
        themes_dir = mock_configs / "ui/styles/themes"
        themes_dir.mkdir(parents=True, exist_ok=True)
        
        with patch("utils.theme_manager.get_app_root", return_value=mock_configs):
            tm = ThemeManager()
            
            # Mock QApplication to avoid errors when applying stylesheet
            with patch("utils.theme_manager.QApplication") as mock_app:
                mock_app.instance.return_value = Mock()
                
                # Trigger switch, which calls _apply_theme -> _validate -> _compile
                tm.switch_theme("0")
                
                # Check if QSS was created automatically
                light_qss = themes_dir / "light.qss"
                assert light_qss.exists()
                content = light_qss.read_text(encoding="utf-8")
                assert "background: #FFFFFF;" in content