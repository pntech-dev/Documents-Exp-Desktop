import requests
import sys
import os
import tempfile
import subprocess
import logging
from packaging import version
from PyQt5.QtCore import QObject, pyqtSignal, QThread, Qt, QTimer
from PyQt5.QtWidgets import QDialog, QMessageBox

from utils.update_confirm_modal import UpdateConfirmDialog
from utils.update_progress_modal import UpdateProgressDialog
from utils.install_confirm_modal import InstallConfirmDialog
from utils import NotificationService

logger = logging.getLogger(__name__)

class GitHubUpdateChecker(QThread):
    """Поток для проверки обновлений через GitHub API."""
    update_available = pyqtSignal(str, str, str, int)  # version, url, changelog, size
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
            file_size = 0
            for asset in assets:
                name = asset.get("name", "").lower()
                if name.endswith(".exe"):
                    download_url = asset.get("browser_download_url")
                    file_size = asset.get("size", 0)
                    break
            
            if not download_url:
                self.error.emit("Новая версия найдена, но установщик (.exe) отсутствует в релизе.")
                return

            # Сравнение версий
            if version.parse(remote_version_str) > version.parse(self.current_version):
                self.update_available.emit(remote_version_str, download_url, changelog, file_size)
            else:
                self.no_update.emit()

        except Exception as e:
            logger.error(f"GitHub update check failed: {e}")
            self.error.emit(str(e))


class UpdateDownloader(QThread):
    """Поток для скачивания файла обновления."""
    progress = pyqtSignal(int, int) # downloaded_bytes, total_bytes
    finished = pyqtSignal(str)  # путь к скачанному файлу
    error = pyqtSignal(str)

    def __init__(self, url: str, expected_size: int = 0):
        super().__init__()
        self.url = url
        self.expected_size = expected_size
        self._is_running = True

    def stop(self):
        """Останавливает скачивание."""
        self._is_running = False

    def run(self):
        try:
            # Используем контекстный менеджер для requests, чтобы гарантировать закрытие соединения
            with requests.get(self.url, stream=True, timeout=30, allow_redirects=True) as response:
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                # Если сервер не отдал размер, используем размер из API GitHub
                if total_size == 0:
                    total_size = self.expected_size
                
                downloaded_size = 0
                last_percent = -1
                last_emitted_size = 0
                
                # Сообщаем о начале загрузки
                self.progress.emit(0, total_size)

                # Создаем временный файл
                fd, path = tempfile.mkstemp(suffix=".exe")
                os.close(fd)

                with open(path, 'wb') as f:
                    # Увеличиваем размер чанка до 64KB для снижения нагрузки на CPU/GUI
                    for chunk in response.iter_content(chunk_size=65536):
                        if not self._is_running:
                            f.close()
                            try:
                                os.remove(path)
                            except OSError:
                                pass
                            return

                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            
                            if total_size > 0:
                                percent = int((downloaded_size / total_size) * 100)
                                if percent != last_percent:
                                    self.progress.emit(downloaded_size, total_size)
                                    last_percent = percent
                            else:
                                # Ограничиваем частоту обновлений для неизвестного размера (каждые 200 КБ)
                                if downloaded_size - last_emitted_size >= 204800:
                                    self.progress.emit(downloaded_size, total_size)
                                    last_emitted_size = downloaded_size

                if self._is_running:
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

    def _on_update_available(self, new_version, url, changelog, size):
        """Вызывается, когда найдена новая версия."""
        dialog = UpdateConfirmDialog(self.parent_widget, version=new_version)
        
        if dialog.exec_() == QDialog.Accepted:
            self._start_download(url, size)

    def _on_no_update(self):
        if not self._silent:
            NotificationService().show_toast("info", "Обновление", "У вас установлена последняя версия.")

    def _on_error(self, error_msg):
        if not self._silent:
            NotificationService().show_toast("error", "Ошибка обновления", f"Не удалось проверить обновления:\n{error_msg}")

    def _start_download(self, url, size):
        self.progress_dialog = UpdateProgressDialog(self.parent_widget)
        self.progress_dialog.set_progress(0, size)

        self._downloader = UpdateDownloader(url, size)
        self._downloader.progress.connect(self.progress_dialog.set_progress)
        self._downloader.finished.connect(self._on_download_finished)
        self._downloader.error.connect(self._on_download_error)
        
        self.progress_dialog.canceled.connect(self._downloader.stop)
        self._downloader.start()
        self.progress_dialog.exec_()

    def _on_download_error(self, error_msg):
        self.progress_dialog.close()
        # Если главное окно еще не создано (проверка при запуске), NotificationService не сработает
        if NotificationService().main_window:
            NotificationService().show_toast("error", "Ошибка", f"Ошибка скачивания: {error_msg}")
        else:
            # Используем стандартный QMessageBox как запасной вариант
            QMessageBox.critical(self.parent_widget, "Ошибка", f"Ошибка скачивания:\n{error_msg}")

    def _on_download_finished(self, file_path):
        # Принудительно ставим 100%, чтобы пользователь увидел завершение
        self.progress_dialog.set_progress(100, 100)
        # Делаем паузу 500мс перед закрытием окна для плавности
        QTimer.singleShot(500, lambda: self._show_install_confirmation(file_path))

    def _show_install_confirmation(self, file_path):
        self.progress_dialog.close()
        dialog = InstallConfirmDialog(self.parent_widget)
        if dialog.exec_() == QDialog.Accepted:
            self._install_update(file_path)

    def _install_update(self, file_path):
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            else:
                subprocess.Popen([file_path])
            sys.exit(0)
        except Exception as e:
            NotificationService().show_toast("error", "Ошибка", f"Не удалось запустить установщик:\n{e}")
