# tests/test_converter.py
"""Тесты для модуля конвертации."""

from pathlib import Path
import fitz  # PyMuPDF
from pdf2jpg_service.converter import convert_pdf_to_jpg
from pdf2jpg_service.config import DEFAULT_DPI


def create_sample_pdf(path: Path, pages: int = 2) -> None:
    """
    Создать простой PDF с указанным количеством страниц для теста.

    :param path: путь для сохранения PDF.
    :param pages: количество страниц.
    """
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page()
        # Добавим простой текст на страницу
        page.insert_text((72, 72), f"Test page {i+1}")
    doc.save(str(path))
    doc.close()


def test_convert_pdf_to_jpg(tmp_path: Path) -> None:
    """Проверить, что PDF конвертируется в JPG и файлы создаются."""
    pdf_path = tmp_path / "sample.pdf"
    out_dir = tmp_path / "out"
    create_sample_pdf(pdf_path, pages=3)

    saved = convert_pdf_to_jpg(pdf_path, out_dir, dpi=DEFAULT_DPI)
    assert len(saved) == 3
    for p in saved:
        assert p.exists()
        assert p.suffix.lower() == ".jpg"

