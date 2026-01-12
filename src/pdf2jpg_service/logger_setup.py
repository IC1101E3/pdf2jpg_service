# src/pdf2jpg_service/logger_setup.py
"""Настройка логгирования для приложения."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Final

from .config import LOG_FILE

LOG_FORMAT: Final[str] = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"


def setup_logging(level: int = logging.INFO) -> None:
    """
    Настроить логирование: консоль + файл с ротацией.

    :param level: уровень логирования (по умолчанию INFO).
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    # Файловый обработчик с ротацией
    log_file = LOG_FILE
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Если не удалось создать директорию — продолжаем, файл будет создан в рабочей директории
        pass

    file_handler = RotatingFileHandler(str(log_file), maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)

