import mimetypes
from pathlib import Path
from .pdf_extractor import extract_text_from_pdf
from .docx_extractor import extract_text_from_docx
from .xlsx_extractor import extract_text_from_xlsx
from .image_extractor import extract_text_from_image
from .utils import clean_text

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def save_uploaded_file(upload_file) -> str:
    file_path = UPLOAD_DIR / upload_file.filename
    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
    return str(file_path)

def extract_text(file_path: str) -> dict:
    mime_type, _ = mimetypes.guess_type(file_path)
    text = ""
    print(f"DEBUG >>> File: {file_path}, Mime: {mime_type}")

    try:
        if mime_type == "application/pdf":
            text = extract_text_from_pdf(file_path)

        elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(file_path)

        elif mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            text = extract_text_from_xlsx(file_path)

        elif mime_type and mime_type.startswith("image/"):
            text = extract_text_from_image(file_path)

        else:
            return {"error": f"Unsupported file type: {mime_type}"}

    except Exception as e:
        return {"error": str(e)}

    # Cleanup
    cleaned = clean_text(text)

    return {
        "raw_text": text,
        "cleaned_text": cleaned
    }
