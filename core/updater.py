import requests
import sys
import os
import tempfile
import subprocess
import logging
from packaging import version
from PyQt5.QtCore import QObject, pyqtSignal, QThread, Qt
from PyQt5.QtWidgets import QMessageBox, QProgressDialog

logger = logging.getLogger(__name__)

class GitHubUpdateChecker(QThread):
    """Поток для проверки обновлений через GitHub API."""
    update_available = pyqtSignal(str, str, str)  # version, url, changelog
    no_update = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, current_version: str, repo_name: str):
        super().__init__()
        self.current_version = current_version
        self.repo_name = repo_name

    def run(self):
        try:
            # API GitHub для получения последнего релиза
            url = f"https://api.github.com/repos/{self.repo_name}/releases/latest"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 404:
                self.error.emit("Репозиторий или релиз не найден.")
                return
                
            response.raise_for_status()
            data = response.json()

            # Теги на GitHub часто имеют префикс 'v' (например, v1.0.0)
            remote_version_str = data.get("tag_name", "").lstrip("v")
            changelog = data.get("body", "Нет описания изменений.")
            assets = data.get("assets", [])

            if not remote_version_str:
                self.no_update.emit()
                return

            # Ищем .exe файл в ассетах релиза
            download_url = None
            for asset in assets:
                name = asset.get("name", "").lower()
                if name.endswith(".exe"):
                    download_url = asset.get("browser_download_url")
                    break
            
            if not download_url:
                self.error.emit("Новая версия найдена, но установщик (.exe) отсутствует в релизе.")
                return

            # Сравнение версий
            if version.parse(remote_version_str) > version.parse(self.current_version):
                self.update_available.emit(remote_version_str, download_url, changelog)
            else:
                self.no_update.emit()

        except Exception as e:
            logger.error(f"GitHub update check failed: {e}")
            self.error.emit(str(e))


class UpdateDownloader(QThread):
    """Поток для скачивания файла обновления."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)  # путь к скачанному файлу
    error = pyqtSignal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            # Создаем временный файл
            fd, path = tempfile.mkstemp(suffix=".exe")
            os.close(fd)

            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            percent = int((downloaded_size / total_size) * 100)
                            self.progress.emit(percent)

            self.finished.emit(path)

        except Exception as e:
            logger.error(f"Download failed: {e}")
            self.error.emit(str(e))


class UpdateManager(QObject):
    """Контроллер процесса обновления."""
    
    def __init__(self, current_version: str, repo_name: str, parent=None):
        super().__init__(parent)
        self.current_version = current_version
        self.repo_name = repo_name
        self.parent_widget = parent
        self._checker = None
        self._downloader = None
        self._silent = True

    def check_for_updates(self, silent: bool = True):
        self._silent = silent
        if not self.repo_name:
            if not silent:
                QMessageBox.warning(self.parent_widget, "Ошибка", "Репозиторий GitHub не настроен.")
            return

        self._checker = GitHubUpdateChecker(self.current_version, self.repo_name)
        self._checker.update_available.connect(self._on_update_available)
        self._checker.no_update.connect(self._on_no_update)
        self._checker.error.connect(self._on_error)
        self._checker.start()

    def _on_update_available(self, new_version, url, changelog):
        msg = f"Доступна новая версия: {new_version}\n\nСписок изменений:\n{changelog}\n\nХотите обновить сейчас?"
        reply = QMessageBox.question(
            self.parent_widget, "Обновление доступно", msg, QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._start_download(url)

    def _on_no_update(self):
        if not self._silent:
            QMessageBox.information(self.parent_widget, "Обновление", "У вас установлена последняя версия.")

    def _on_error(self, error_msg):
        if not self._silent:
            QMessageBox.warning(self.parent_widget, "Ошибка обновления", f"Не удалось проверить обновления:\n{error_msg}")

    def _start_download(self, url):
        self.progress_dialog = QProgressDialog("Скачивание обновления...", "Отмена", 0, 100, self.parent_widget)
        self.progress_dialog.setWindowModality(Qt.ApplicationModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)

        self._downloader = UpdateDownloader(url)
        self._downloader.progress.connect(self.progress_dialog.setValue)
        self._downloader.finished.connect(self._on_download_finished)
        self._downloader.error.connect(lambda e: QMessageBox.critical(self.parent_widget, "Ошибка", f"Ошибка скачивания: {e}"))
        self.progress_dialog.canceled.connect(self._downloader.terminate)
        self._downloader.start()

    def _on_download_finished(self, file_path):
        self.progress_dialog.close()
        reply = QMessageBox.question(
            self.parent_widget, "Установка", "Обновление скачано. Приложение будет закрыто для установки. Продолжить?", QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._install_update(file_path)

    def _install_update(self, file_path):
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            else:
                subprocess.Popen([file_path])
            sys.exit(0)
        except Exception as e:
            QMessageBox.critical(self.parent_widget, "Ошибка", f"Не удалось запустить установщик:\n{e}")
