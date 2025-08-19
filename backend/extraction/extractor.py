# backend/extraction/extractor.py
import mimetypes
from pathlib import Path

from .pdf_extractor import extract_text_from_pdf
from .docx_extractor import extract_text_from_docx
from .xlsx_extractor import extract_text_from_xlsx
from .image_extractor import extract_text_from_image

# ✅ uploads folder at project root
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

def save_uploaded_file(file) -> str:
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return str(file_path)

def extract_text(file_path: str):
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type == "application/pdf":
        return extract_text_from_pdf(file_path)
    elif mime_type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ]:
        return extract_text_from_docx(file_path)
    elif mime_type in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    ]:
        return extract_text_from_xlsx(file_path)
    elif mime_type and mime_type.startswith("image/"):
        return extract_text_from_image(file_path)
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return {"raw_text": content, "cleaned_text": " ".join(content.split())}
