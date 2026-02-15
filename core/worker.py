from PyQt5.QtCore import QThread, pyqtSignal


class APIWorker(QThread):
    """
    A QThread subclass for executing blocking API calls in a background thread.

    Attributes:
        finished (pyqtSignal): Signal emitted when the task is completed successfully.
        error (pyqtSignal): Signal emitted when an exception occurs.
    """
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)

    def __init__(self, func, *args, **kwargs) -> None:
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs


    def run(self) -> None:
        """Executes the function and emits signals based on the result."""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(e)