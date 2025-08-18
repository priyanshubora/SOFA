from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from extraction.extractor import save_uploaded_file, extract_text

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the file
        file_path = save_uploaded_file(file)

        # Extract text
        extracted_text = extract_text(file_path)

        return JSONResponse(content={"filename": file.filename, "text": extracted_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
