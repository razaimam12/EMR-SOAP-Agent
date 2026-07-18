"""FastAPI entry point for the EMR SOAP Draft Agent."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .formatting import build_note
from .schemas import SOAPRequest
from .soap_service import SoapError, generate_soap, transcribe_audio

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="EMR SOAP Draft Agent",
    version="1.0.0",
    description="AI clinical documentation assistant. Every output is a draft for physician review.",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    """Serve the clinician web form."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/health")
async def health() -> dict:
    """Simple readiness probe."""
    return {"status": "ok", "model": settings.llm_model, "has_api_key": bool(settings.groq_api_key)}


@app.post("/api/generate")
async def generate(req: SOAPRequest):
    """Generate a DRAFT SOAP note from clinical bullet points."""
    bullets = (req.bullets or "").strip()
    if not bullets:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Missing required field: bullets"},
        )
    context = req.patient_context or {}
    try:
        ai_json = await generate_soap(bullets, json.dumps(context, ensure_ascii=False))
    except SoapError as exc:
        return JSONResponse(content={"success": False, "error": str(exc), "hint": exc.hint})
    return build_note(ai_json)


@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Transcribe recorded audio to text (Whisper)."""
    content = await file.read()
    try:
        text = await transcribe_audio(content, file.filename, file.content_type)
    except SoapError as exc:
        return JSONResponse(content={"text": "", "error": str(exc), "hint": exc.hint})
    return {"text": text}
