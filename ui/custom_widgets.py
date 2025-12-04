from PyQt5.QtWidgets import QPushButton, QLabel


"""=== Buttons ==="""

class PrimaryButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class SecondaryButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class TertiaryButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class ThemeButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


"""=== Labels ==="""

class LogoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class InfoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class TextButton(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)