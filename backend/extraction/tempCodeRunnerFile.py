import os
import mimetypes
from pathlib import Path

from .pdf_extractor import extract_text_from_pdf
from .docx_extractor import extract_text_from_docx
from .xlsx_extractor import extract_text_from_xlsx
from .image_extractor import extract_text_from_image


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # ✅ Create the uploads folder if it doesn't exist


def save_uploaded_file(upload_file) -> str:
    """
    Save uploaded file to UPLOAD_DIR and return the saved path.
    """
    file_path = UPLOAD_DIR / upload_file.filename
    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
    return str(file_path)


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
        return f"❌ Unsupported file type: {mime_type}"


def extract_events_from_pdf(file_path: str) -> str:
    """
    Wrapper kept for compatibility with main.py.
    Uses PDF extractor under the hood.
    """
    return extract_text_from_pdf(file_path)
