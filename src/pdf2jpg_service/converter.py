# src/pdf2jpg_service/converter.py
"""Модуль конвертации PDF в JPG."""

from pathlib import Path
from typing import Iterable, List

import fitz  # PyMuPDF
from PIL import Image

from .config import DEFAULT_DPI, JPEG_QUALITY, OUTPUT_FORMAT
import logging

logger = logging.getLogger(__name__)


def pdf_to_images(pdf_path: Path, dpi: int = DEFAULT_DPI) -> List[Image.Image]:
    """
    Преобразовать PDF в список изображений (PIL.Image).

    :param pdf_path: путь к PDF-файлу.
    :param dpi: разрешение рендеринга.
    :return: список изображений (по одной картинке на страницу).
    :raises FileNotFoundError: если файл не найден.
    :raises ValueError: если файл не PDF или пустой.
    """
    if not pdf_path.exists():
        logger.error("PDF файл не найден: %s", pdf_path)
        raise FileNotFoundError(f"Файл не найден: {pdf_path}")

    logger.debug("Открываем PDF: %s", pdf_path)
    doc = fitz.open(str(pdf_path))
    if doc.page_count == 0:
        logger.error("PDF пустой: %s", pdf_path)
        raise ValueError("PDF не содержит страниц")

    images: List[Image.Image] = []
    zoom = dpi / 72  # PyMuPDF использует 72 DPI как базу
    mat = fitz.Matrix(zoom, zoom)

    for page_number in range(doc.page_count):
        page = doc.load_page(page_number)
        logger.debug("Рендерим страницу %d/%d", page_number + 1, doc.page_count)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        mode = "RGB" if pix.n < 4 else "RGBA"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        if mode == "RGBA":
            img = img.convert("RGB")
        images.append(img)

    doc.close()
    logger.info("PDF успешно преобразован в %d изображений", len(images))
    return images


def save_images(
    images: Iterable[Image.Image],
    output_dir: Path,
    base_name: str,
    quality: int = JPEG_QUALITY,
    fmt: str = OUTPUT_FORMAT,
) -> List[Path]:
    """
    Сохранить изображения в указанную директорию.

    :param images: итерируемый объект PIL.Image.
    :param output_dir: директория для сохранения.
    :param base_name: базовое имя файлов (без расширения).
    :param quality: качество JPEG.
    :param fmt: формат сохранения (например, 'JPEG').
    :return: список путей к сохранённым файлам.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: List[Path] = []

    for idx, img in enumerate(images, start=1):
        filename = f"{base_name}_page_{idx}.jpg"
        out_path = output_dir / filename
        logger.debug("Сохраняем изображение: %s", out_path)
        img.save(out_path, fmt, quality=quality)
        saved_paths.append(out_path)

    logger.info("Сохранено %d файлов в %s", len(saved_paths), output_dir)
    return saved_paths


def convert_pdf_to_jpg(
    pdf_path: Path, output_dir: Path, dpi: int = DEFAULT_DPI, base_name: str | None = None
) -> List[Path]:
    """
    Полная операция: открыть PDF, рендерить страницы и сохранить как JPG.

    :param pdf_path: путь к PDF.
    :param output_dir: директория для сохранения JPG.
    :param dpi: разрешение рендеринга.
    :param base_name: базовое имя для файлов; если None — используется имя PDF.
    :return: список путей к сохранённым JPG.
    """
    logger.info("Начинаем конвертацию: %s -> %s", pdf_path, output_dir)
    images = pdf_to_images(pdf_path, dpi=dpi)
    if base_name is None:
        base_name = pdf_path.stem
    saved = save_images(images, output_dir, base_name)
    logger.info("Конвертация завершена: %s", pdf_path)
    return saved

