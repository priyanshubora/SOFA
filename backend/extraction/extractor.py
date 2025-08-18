# backend/extraction/extractor.py
import pdfplumber, docx2txt, pytesseract
from PIL import Image

def extract_events_from_pdf(file_path):
    # pdfplumber logic
    return [{"event": "Loading", "start": "2025-08-10 14:00", "end": "2025-08-10 18:00"}]

def extract_events_from_docx(file_path):
    # docx2txt logic
    return []

def extract_events_from_image(file_path):
    text = pytesseract.image_to_string(Image.open(file_path))
    # parse into events
    return []
