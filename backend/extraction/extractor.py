import os
import mimetypes
from .pdf_extractor import extract_text_from_pdf
from .docx_extractor import extract_text_from_docx
from .xlsx_extractor import extract_text_from_xlsx
from .image_extractor import extract_text_from_image


def extract_text(file_path: str) -> str:
    """
    Detect file type and send to correct extractor.
    Returns extracted text.
    """
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type == "application/pdf":
        return extract_text_from_pdf(file_path)

    elif mime_type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]:
        return extract_text_from_docx(file_path)

    elif mime_type in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]:
        return extract_text_from_xlsx(file_path)

    elif mime_type in ["image/jpeg", "image/png", "image/tiff"]:
        return extract_text_from_image(file_path)

    else:
        return "❌ Unsupported file type"


def extract_events_from_pdf(file_path: str) -> str:
    """
    Wrapper kept for compatibility with main.py.
    Uses PDF extractor under the hood.
    """
    return extract_text_from_pdf(file_path)
