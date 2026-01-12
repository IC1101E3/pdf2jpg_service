# src/pdf2jpg_service/gui.py
"""Графический интерфейс приложения на PyQt5."""

from pathlib import Path
from typing import Optional, List

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QProgressBar,
    QMessageBox,
)
import sys
import logging

from .converter import convert_pdf_to_jpg
from .config import DEFAULT_DPI

logger = logging.getLogger(__name__)


class ConverterWorker(QtCore.QRunnable):
    """
    Фоновая задача для конвертации, чтобы не блокировать GUI.
    Использует QRunnable + сигналы через QObject.
    """

    class Signals(QtCore.QObject):
        progress = QtCore.pyqtSignal(int)
        finished = QtCore.pyqtSignal(list)
        error = QtCore.pyqtSignal(str)

    def __init__(self, pdf_path: Path, output_dir: Path, dpi: int = DEFAULT_DPI) -> None:
        super().__init__()
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.dpi = dpi
        self.signals = ConverterWorker.Signals()

    def run(self) -> None:
        """Выполнение задачи в отдельном потоке."""
        try:
            logger.debug("Worker запущен для %s", self.pdf_path)
            saved = convert_pdf_to_jpg(self.pdf_path, self.output_dir, dpi=self.dpi)
            # Простая имитация прогресса: отправляем 100% в конце
            self.signals.progress.emit(100)
            self.signals.finished.emit(saved)
        except Exception as exc:  # pragma: no cover - GUI error handling
            logger.exception("Ошибка в фоновом потоке: %s", exc)
            self.signals.error.emit(str(exc))


class MainWindow(QWidget):
    """Главное окно приложения."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF → JPG Converter")
        self.resize(500, 200)
        self._pdf_path: Optional[Path] = None
        self._output_dir: Optional[Path] = None
        self._setup_ui()
        self.thread_pool = QtCore.QThreadPool.globalInstance()

    def _setup_ui(self) -> None:
        """Создать элементы интерфейса."""
        layout = QVBoxLayout()

        self.label_pdf = QLabel("PDF: не выбран")
        self.btn_select_pdf = QPushButton("Выбрать PDF")
        self.btn_select_pdf.clicked.connect(self.select_pdf)

        self.label_output = QLabel("Папка вывода: не выбрана")
        self.btn_select_output = QPushButton("Выбрать папку вывода")
        self.btn_select_output.clicked.connect(self.select_output)

        self.btn_convert = QPushButton("Конвертировать")
        self.btn_convert.clicked.connect(self.start_conversion)
        self.btn_convert.setEnabled(False)

        self.progress = QProgressBar()
        self.progress.setValue(0)

        layout.addWidget(self.label_pdf)
        layout.addWidget(self.btn_select_pdf)
        layout.addWidget(self.label_output)
        layout.addWidget(self.btn_select_output)
        layout.addWidget(self.btn_convert)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def select_pdf(self) -> None:
        """Открыть диалог выбора PDF."""
        path, _ = QFileDialog.getOpenFileName(self, "Выберите PDF", filter="PDF Files (*.pdf)")
        if path:
            self._pdf_path = Path(path)
            self.label_pdf.setText(f"PDF: {self._pdf_path}")
            self._update_convert_button()

    def select_output(self) -> None:
        """Открыть диалог выбора папки вывода."""
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения")
        if folder:
            self._output_dir = Path(folder)
            self.label_output.setText(f"Папка вывода: {self._output_dir}")
            self._update_convert_button()

    def _update_convert_button(self) -> None:
        """Активировать кнопку конвертации, если заданы вход и выход."""
        self.btn_convert.setEnabled(bool(self._pdf_path and self._output_dir))

    def start_conversion(self) -> None:
        """Запустить фоновую задачу конвертации."""
        if not self._pdf_path or not self._output_dir:
            return

        self.progress.setValue(0)
        worker = ConverterWorker(self._pdf_path, self._output_dir, dpi=DEFAULT_DPI)
        worker.signals.progress.connect(self.progress.setValue)
        worker.signals.finished.connect(self.on_finished)
        worker.signals.error.connect(self.on_error)
        self.thread_pool.start(worker)

    def on_finished(self, saved: List[Path]) -> None:
        """Обработчик успешного завершения."""
        self.progress.setValue(100)
        QMessageBox.information(self, "Готово", f"Сохранено {len(saved)} файлов.")
        logger.info("Пользователь завершил конвертацию: %d файлов", len(saved))

    def on_error(self, message: str) -> None:
        """Обработчик ошибок."""
        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {message}")
        logger.error("Ошибка в GUI: %s", message)


def run_app(argv: Optional[list] = None) -> int:
    """
    Запустить приложение PyQt5.

    :param argv: аргументы командной строки (опционально).
    :return: код возврата.
    """
    app = QApplication(argv or sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()

