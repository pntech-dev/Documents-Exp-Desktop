import sys
import pytest
from PyQt5.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """Global QApplication instance for all tests requiring widgets."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app