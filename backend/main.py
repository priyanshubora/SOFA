# backend/main.py
import json
import aiofiles
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from extraction.extractor import save_uploaded_file, extract_text
from db import init_db, save_upload, list_uploads, get_upload


# Lifespan handler (replaces @app.on_event("startup"))
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # initialize DB at startup
    yield       # hand over control to app
    # (optional) cleanup code here at shutdown


app = FastAPI(title="SOFA API (v0.1)", lifespan=lifespan)

# Allow frontend later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 1) Save uploaded file
        file_path = save_uploaded_file(file)

        # 2) Extract text
        extracted = extract_text(file_path)
        if isinstance(extracted, dict):
            raw_text = extracted.get("raw_text", "")
            cleaned_text = extracted.get("cleaned_text", "")
        else:
            raw_text = str(extracted)
            cleaned_text = " ".join(raw_text.split())

        # 3) Save JSON next to file
        json_path = f"{file_path}.json"
        async with aiofiles.open(json_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(
                {"filename": file.filename, "raw_text": raw_text, "cleaned_text": cleaned_text},
                ensure_ascii=False, indent=2
            ))

        # 4) Save in DB
        new_id = save_upload(
            filename=file.filename,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            original_path=file_path
        )

        # 5) Return API response
        return JSONResponse(content={
            "id": new_id,
            "filename": file.filename,
            "extracted": {
                "raw_text": raw_text,
                "cleaned_text": cleaned_text
            }
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.get("/files/")
def api_list_files():
    return list_uploads()


@app.get("/files/{file_id}")
def api_get_file(file_id: int):
    rec = get_upload(file_id)
    if not rec:
        raise HTTPException(status_code=404, detail="File not found")
    return rec
