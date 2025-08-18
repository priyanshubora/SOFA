from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        text = f"PDF extraction failed: {str(e)}"
    return text.strip()
