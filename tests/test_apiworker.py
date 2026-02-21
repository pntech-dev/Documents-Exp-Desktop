from unittest.mock import Mock
from core.worker import APIWorker

class TestAPIWorker:
    def test_run_success(self):
        """Test successful execution of the worker function."""
        expected_result = {"data": 123}

        mock_func = Mock(return_value=expected_result)

        worker = APIWorker(mock_func, "arg1", key="value")
        worker.finished = Mock()
        worker.error = Mock()
        worker.run()

        mock_func.assert_called_once_with("arg1", key="value")

        worker.finished.emit.assert_called_once_with(expected_result)
        worker.error.emit.assert_not_called()


    def test_run_error(self):
        """Test error handling in the worker."""
        exception = ValueError("Test error")

        mock_func = Mock(side_effect=exception)

        worker = APIWorker(mock_func)
        worker.finished = Mock()
        worker.error = Mock()
        worker.run()

        mock_func.assert_called_once()

        worker.finished.emit.assert_not_called()
        worker.error.emit.assert_called_once_with(exception)
