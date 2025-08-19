import re

def clean_text(text: str) -> str:
    """
    Basic cleanup for extracted text:
    - Remove weird OCR artifacts
    - Collapse multiple spaces/newlines
    """
    if not text:
        return ""

    # Remove non-printable chars
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text
