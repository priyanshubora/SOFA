import pytesseract
from PIL import Image

def extract_text_from_image(file_path: str) -> str:
    try:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)
    except Exception as e:
        return f"Image extraction failed: {str(e)}"
