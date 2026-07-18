"""Unit tests for the note formatter (no network / API key required)."""
from app.formatting import build_note

SAMPLE = {
    "triage": {"level": "Urgent", "rationale": "Exertional chest pain radiating to the arm."},
    "chief_complaint": "Chest pain on exertion",
    "hpi": "55F, 2 days of exertional chest pain radiating to the left arm with SOB.",
    "review_of_systems": "CVS: chest pain, dyspnoea.",
    "objective": "BP 158/94, HR 98, SpO2 96%.",
    "assessment": "Concern for cardiac ischaemia.",
    "differential_diagnosis": ["Acute Coronary Syndrome - classic exertional pattern"],
    "plan": ["ECG and troponin", "Cardiology referral"],
    "recommended_investigations": ["ECG - ischaemia", "Troponin - myocardial injury"],
    "risk_scores": [{"name": "HEART", "value": 5, "interpretation": "Moderate risk"}],
    "prescription": [
        {"drug": "Aspirin", "dose": "300 mg", "route": "PO", "frequency": "stat", "duration": "once", "notes": "if no contraindication"}
    ],
    "patient_instructions": {"english": "Rest and return if pain worsens.", "urdu": "آرام کریں۔"},
    "drug_safety": ["Avoid NSAIDs with current regimen"],
    "follow_up_questions": ["Prior cardiac history?"],
    "allergy_alerts": ["Penicillin allergy"],
    "red_flags": ["Radiation to left arm"],
    "icd10_suggestions": [{"code": "R07.1", "description": "Chest pain on exertion"}],
}


def test_build_note_success_and_structure():
    result = build_note(SAMPLE)
    assert result["success"] is True
    note = result["formatted_note"]
    for section in [
        "SOAP NOTE - DRAFT",
        "TRIAGE: Urgent",
        "S - SUBJECTIVE",
        "O - OBJECTIVE",
        "A - ASSESSMENT",
        "P - PLAN",
        "CLINICAL RISK SCORES",
        "SUGGESTED PRESCRIPTION",
        "RECOMMENDED INVESTIGATIONS",
        "ICD-10 (suggested):",
    ]:
        assert section in note
    assert "** ALLERGY ALERT: Penicillin allergy" in note
    assert result["draft"]["patient_instructions"]["urdu"] == "آرام کریں۔"
    assert result["draft"]["triage"]["level"] == "Urgent"


def test_build_note_handles_missing_fields():
    result = build_note({})
    note = result["formatted_note"]
    assert result["success"] is True
    assert "[not documented]" in note
    assert "[none suggested]" in note
    assert "[none computed from provided data]" in note
