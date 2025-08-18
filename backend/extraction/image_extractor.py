import pytesseract
from PIL import Image
import os

# 🔹 Point to your Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from image using Tesseract OCR.
    Supports common formats like JPG, PNG, TIFF.
    """
    try:
        # Open image
        image = Image.open(file_path)

        # Run OCR
        text = pytesseract.image_to_string(image)

        return text.strip() if text.strip() else "No text detected in the image."

    except Exception as e:
        return f"Image extraction failed: {e}"
