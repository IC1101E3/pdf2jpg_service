# src/pdf2jpg_service/main.py
"""Точка входа приложения."""

import sys
import logging

from .logger_setup import setup_logging
from .gui import run_app

logger = logging.getLogger(__name__)


def main() -> int:
    """
    Основная функция запуска приложения.

    :return: код возврата.
    """
    setup_logging()
    logger.info("Запуск приложения PDF→JPG")
    try:
        return run_app(sys.argv)
    except Exception as exc:
        logger.exception("Критическая ошибка при запуске: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

