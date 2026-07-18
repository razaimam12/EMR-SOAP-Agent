"""Runtime configuration loaded from environment variables (.env supported)."""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings sourced from environment variables."""

    def __init__(self) -> None:
        self.groq_api_key: str = os.getenv("GROQ_API_KEY", "").strip()
        self.llm_base_url: str = os.getenv(
            "LLM_BASE_URL", "https://api.groq.com/openai/v1"
        ).rstrip("/")
        self.llm_model: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        self.whisper_model: str = os.getenv("WHISPER_MODEL", "whisper-large-v3")
        self.request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "60"))
        self.clinic_name: str = os.getenv("CLINIC_NAME", "North Hospital New York")


settings = Settings()
