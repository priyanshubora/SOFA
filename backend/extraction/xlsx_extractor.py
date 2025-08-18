import openpyxl

def extract_text_from_xlsx(file_path: str) -> str:
    text = ""
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                text += " ".join([str(cell) for cell in row if cell is not None]) + "\n"
    except Exception as e:
        text = f"XLSX extraction failed: {str(e)}"
    return text.strip()
