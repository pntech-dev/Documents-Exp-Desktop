from PyQt5.QtCore import QThread, pyqtSignal


class APIWorker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)

    def __init__(self, func, *args, **kwargs) -> None:
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs


    def run(self) -> None:
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(e)