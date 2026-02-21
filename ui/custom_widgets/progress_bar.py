from PyQt5.QtWidgets import QProgressBar, QWidget
from utils import ThemeManagerInstance


class ProgressBar(QProgressBar):
    """
    Custom ProgressBar widget with theme support.
    """
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the progress bar."""
        super().__init__(parent)
        self.setTextVisible(False)
        self.setFixedHeight(12)

        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)

    def setProgressValue(self, value: int) -> None:
        """
        Sets the progress value and forces a repaint.

        Args:
            value (int): The progress value to set.
        """
        super().setValue(value)
        self.repaint()

    def _on_theme_changed(self, theme_id: str) -> None:
        """Handles theme change events."""
        self.style().unpolish(self)
        self.style().polish(self)
