# src/pdf2jpg_service/config.py
"""Конфигурационные константы проекта."""

from pathlib import Path

# Формат выходных изображений
OUTPUT_FORMAT: str = "JPEG"

# Качество JPEG (1-95)
JPEG_QUALITY: int = 85

# DPI для рендеринга PDF страниц (чем выше — тем лучше качество и больше размер)
DEFAULT_DPI: int = 150

# Максимальное количество потоков при параллельной обработке (опционально)
MAX_WORKERS: int = 4

# Лог-файл
LOG_FILE: Path = Path("pdf2jpg_service.log")

