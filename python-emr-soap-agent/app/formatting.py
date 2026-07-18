"""Turn the LLM's JSON into a human-readable note + structured draft.

This is a faithful Python port of the n8n "Parse SOAP JSON" node so both
implementations produce identical output.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def _s(value: Any) -> str:
    """String or the '[not documented]' placeholder for empty values."""
    if value is None or value == "":
        return "[not documented]"
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def _a(value: Any) -> list:
    """Coerce a value into a list."""
    if isinstance(value, list):
        return value
    return [value] if value else []


def _item(value: Any) -> str:
    """String form of a list item."""
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def build_note(d: dict) -> dict:
    """Build the formatted note and structured draft from the model JSON."""
    tri = d.get("triage") if isinstance(d.get("triage"), dict) else {}
    tri_level = str(tri.get("level")) if tri.get("level") else "Routine"
    tri_why = _s(tri.get("rationale"))

    cc = _s(d.get("chief_complaint"))
    hpi = _s(d.get("hpi") if d.get("hpi") is not None else d.get("subjective"))
    ros = _s(d.get("review_of_systems"))
    obj = _s(d.get("objective"))
    assess = _s(d.get("assessment"))

    ddx = _a(d.get("differential_diagnosis"))
    plan = _a(d.get("plan"))
    invest = _a(d.get("recommended_investigations"))
    risk = _a(d.get("risk_scores"))
    rx = _a(d.get("prescription"))
    drug = _a(d.get("drug_safety"))
    followups = _a(d.get("follow_up_questions"))
    allergy = _a(d.get("allergy_alerts"))
    red = _a(d.get("red_flags"))
    icd = _a(d.get("icd10_suggestions"))

    pi = d.get("patient_instructions") if isinstance(d.get("patient_instructions"), dict) else {}
    instr_en = pi.get("english") if isinstance(pi.get("english"), str) else (
        d.get("patient_instructions") if isinstance(d.get("patient_instructions"), str) else ""
    )
    instr_ur = pi.get("urdu") if isinstance(pi.get("urdu"), str) else ""

    lines: list[str] = []
    lines.append("SOAP NOTE - DRAFT (for physician review; not a final medical record)")
    lines.append("TRIAGE: " + tri_level + ((" - " + tri_why) if tri_why and tri_why != "[not documented]" else ""))
    lines.append("")
    lines.append("CHIEF COMPLAINT: " + cc)
    lines.append("")
    lines.append("S - SUBJECTIVE")
    lines.append("History of Present Illness: " + hpi)
    lines.append("Review of Systems: " + ros)
    lines.append("")
    lines.append("O - OBJECTIVE")
    lines.append(obj)
    lines.append("")
    lines.append("A - ASSESSMENT")
    lines.append(assess)
    if ddx:
        lines.append("Differential Diagnosis:")
        for i, x in enumerate(ddx):
            lines.append("  " + str(i + 1) + ". " + _item(x))
    lines.append("")
    lines.append("CLINICAL RISK SCORES")
    if risk:
        for r in risk:
            name = (r.get("name") if isinstance(r, dict) else "") or ""
            value = r.get("value") if isinstance(r, dict) and r.get("value") is not None else ""
            interp = (r.get("interpretation") if isinstance(r, dict) else "") or ""
            lines.append("  " + str(name) + ": " + str(value) + ((" - " + interp) if interp else ""))
    else:
        lines.append("  [none computed from provided data]")
    lines.append("")
    lines.append("P - PLAN")
    if plan:
        for i, x in enumerate(plan):
            lines.append("  " + str(i + 1) + ". " + _item(x))
    else:
        lines.append("  [not documented]")
    lines.append("")
    lines.append("SUGGESTED PRESCRIPTION (Rx) - for physician approval")
    if rx:
        for i, r in enumerate(rx):
            if isinstance(r, dict):
                parts = " | ".join(
                    str(p) for p in [r.get("drug"), r.get("dose"), r.get("route"), r.get("frequency"), r.get("duration")] if p
                )
                notes = ("  (" + str(r.get("notes")) + ")") if r.get("notes") else ""
            else:
                parts, notes = _item(r), ""
            lines.append("  " + str(i + 1) + ". " + (parts or _item(r)) + notes)
    else:
        lines.append("  [none suggested]")
    lines.append("")
    lines.append("RECOMMENDED INVESTIGATIONS")
    if invest:
        for i, x in enumerate(invest):
            lines.append("  " + str(i + 1) + ". " + _item(x))
    else:
        lines.append("  [none suggested]")
    lines.append("")
    lines.append("SUGGESTED FOLLOW-UP QUESTIONS / EXAM")
    if followups:
        for i, x in enumerate(followups):
            lines.append("  " + str(i + 1) + ". " + _item(x))
    else:
        lines.append("  [none suggested]")
    lines.append("")
    for x in drug:
        lines.append("** DRUG SAFETY: " + _item(x))
    for x in allergy:
        lines.append("** ALLERGY ALERT: " + _item(x))
    for x in red:
        lines.append("** RED FLAG: " + _item(x))
    if drug or allergy or red:
        lines.append("")
    if icd:
        lines.append("ICD-10 (suggested):")
        for c in icd:
            if isinstance(c, dict):
                code = c.get("code") or c.get("icd10") or ""
                desc = c.get("description") or c.get("desc") or ""
            else:
                code, desc = "", (c if isinstance(c, str) else "")
            lines.append("  " + str(code) + " - " + str(desc))
        lines.append("")

    now = datetime.now(timezone.utc).isoformat()
    lines.append("Generated: " + now)
    lines.append("Disclaimer: AI-generated draft. Must be reviewed, verified, and signed by a licensed physician.")

    return {
        "success": True,
        "formatted_note": "\n".join(lines),
        "draft": {
            "triage": {"level": tri_level, "rationale": tri_why},
            "chief_complaint": cc,
            "hpi": hpi,
            "review_of_systems": ros,
            "objective": obj,
            "assessment": assess,
            "differential_diagnosis": ddx,
            "plan": plan,
            "recommended_investigations": invest,
            "risk_scores": risk,
            "prescription": rx,
            "patient_instructions": {"english": instr_en or "", "urdu": instr_ur or ""},
            "drug_safety": drug,
            "follow_up_questions": followups,
            "allergy_alerts": allergy,
            "red_flags": red,
            "icd10_suggestions": icd,
        },
        "generated_at": now,
    }
