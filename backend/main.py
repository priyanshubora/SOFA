# backend/main.py
from fastapi import FastAPI, UploadFile, File
from extraction.extractor import extract_events_from_pdf
from laytime.laytime_calc import calculate_laytime
from analytics.port_analysis import get_port_risk

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # detect file type and call extractor
    events = extract_events_from_pdf(file.filename)
    return {"events": events}

@app.post("/laytime")
async def laytime(events: list):
    return calculate_laytime(events)

@app.get("/analytics/{port}")
async def analytics(port: str):
    return get_port_risk(port)
