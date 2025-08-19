# backend/main.py

import os
import json
import aiofiles
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from extraction.extractor import save_uploaded_file, extract_text

app = FastAPI(title="SOF Extractor API")


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save file to uploads dir
        file_path = save_uploaded_file(file)

        # Extract text
        extracted = extract_text(file_path)

        if "error" in extracted:
            raise HTTPException(status_code=400, detail=extracted["error"])

        # Save extracted JSON for record
        json_path = f"{file_path}.json"
        async with aiofiles.open(json_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(extracted, ensure_ascii=False, indent=2))

        return JSONResponse(
            content={
                "filename": file.filename,
                "extracted": extracted
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

