"""Request/response models for the API."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class SOAPRequest(BaseModel):
    """Payload sent by the clinician form to generate a SOAP draft."""

    bullets: str = Field(..., description="Clinical bullet points (may include a demographics line).")
    patient_name: Optional[str] = ""
    mr_number: Optional[str] = ""
    provider: Optional[str] = ""
    age: Optional[str] = ""
    sex: Optional[str] = ""
    weight: Optional[str] = ""
    patient_context: Optional[dict[str, Any]] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "bullets": "55F chest pain on exertion 2 days, radiates to left arm, SOB. BP 158/94, HR 98. Hx hypertension. Meds: amlodipine. Allergy: penicillin.",
                "patient_name": "Jane Doe",
                "mr_number": "MR-1001",
                "provider": "Smith",
                "age": "55",
                "sex": "Female",
                "weight": "70",
            }
        }
    }
