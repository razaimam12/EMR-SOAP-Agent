"""Calls to the OpenAI-compatible LLM (chat + Whisper transcription)."""
from __future__ import annotations

import json

import httpx

from .config import settings
from .prompts import SYSTEM_PROMPT


class SoapError(Exception):
    """Raised when the AI provider cannot fulfil a request; carries a user hint."""

    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.hint = hint


def _require_key() -> None:
    if not settings.groq_api_key:
        raise SoapError(
            "Server is missing the API key.",
            "Set GROQ_API_KEY in the .env file and restart the service.",
        )


async def generate_soap(bullets: str, context_json: str) -> dict:
    """Prompt the chat model and return the parsed JSON draft."""
    _require_key()
    payload = {
        "model": settings.llm_model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"CONTEXT: {context_json}\n\nBULLETS:\n{bullets}\n\n"
                    "Return the professional SOAP note and decision support as a JSON object now."
                ),
            },
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            resp = await client.post(
                f"{settings.llm_base_url}/chat/completions", json=payload, headers=headers
            )
    except httpx.RequestError as exc:
        raise SoapError(
            f"Could not reach the AI provider: {exc}",
            "Check your internet connection and LLM_BASE_URL.",
        )

    if resp.status_code != 200:
        low = resp.text.lower()
        if resp.status_code == 429 or "rate" in low or "quota" in low:
            hint = "Rate limit / no quota on the AI provider. Wait a moment or top up, then retry."
        elif resp.status_code in (401, 403) or "api key" in low or "authoriz" in low:
            hint = "The AI provider rejected the request. Check GROQ_API_KEY and LLM_BASE_URL."
        else:
            hint = "Check the AI provider status and the model name."
        raise SoapError(f"AI provider error ({resp.status_code}).", hint)

    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        content = data.get("content") or data.get("text") or ""

    if not content:
        raise SoapError("AI response was empty.", "Try again; if it persists, check the model configuration.")

    cleaned = content.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise SoapError(
            "The AI returned invalid JSON.",
            "Retry. Lower the temperature or switch model if this recurs.",
        )


async def transcribe_audio(content: bytes, filename: str | None, content_type: str | None) -> str:
    """Send recorded audio to the Whisper endpoint and return the transcript."""
    _require_key()
    files = {"file": (filename or "audio.webm", content, content_type or "audio/webm")}
    form = {"model": settings.whisper_model}
    headers = {"Authorization": f"Bearer {settings.groq_api_key}"}
    try:
        async with httpx.AsyncClient(timeout=max(settings.request_timeout, 120)) as client:
            resp = await client.post(
                f"{settings.llm_base_url}/audio/transcriptions",
                data=form,
                files=files,
                headers=headers,
            )
    except httpx.RequestError as exc:
        raise SoapError(
            f"Could not reach the transcription provider: {exc}",
            "Check your internet connection.",
        )
    if resp.status_code != 200:
        raise SoapError(
            f"Transcription failed ({resp.status_code}).",
            "Check GROQ_API_KEY and that the audio format is supported.",
        )
    return resp.json().get("text", "")
