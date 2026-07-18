# EMR SOAP Draft Agent

An AI-powered clinical documentation and decision-support assistant that turns short clinical bullet points (typed or dictated) into a structured **DRAFT SOAP note** with triage, differential diagnosis, recommended investigations, clinical risk scores, a suggested prescription, drug-safety / allergy / red-flag alerts, ICD-10 suggestions, and bilingual (English + Urdu) patient instructions.

> **Medical disclaimer:** Every output is an **AI-generated draft**. It must be reviewed, verified, edited, and signed by a licensed physician before it is used or entered into a medical record. This project does not provide medical advice.

This repository contains **two independent implementations** of the same agent:

| Folder | Stack | Best for |
| --- | --- | --- |
| [`n8n-emr-soap-agent/`](./n8n-emr-soap-agent) | n8n low-code workflow + HTML UI | Visual automation, quick self-hosting inside n8n |
| [`python-emr-soap-agent/`](./python-emr-soap-agent) | FastAPI (Python) + HTML UI | Standalone service, containerised deployment, integration |

Both versions expose the same clinician-facing web form and produce the same note structure. Both use an **OpenAI-compatible LLM API** (default: [Groq](https://groq.com) running `llama-3.3-70b-versatile`) and **Whisper** (`whisper-large-v3`) for voice dictation.

---

## Features

- **SOAP note generation** – Subjective / Objective / Assessment / Plan from free-text bullets.
- **Triage banner** – Routine / Urgent / Emergency with rationale.
- **Clinical decision support** – differential diagnosis, recommended investigations, follow-up questions.
- **Clinical risk scores** – HEART, Wells, CHA₂DS₂-VASc, BMI, eGFR (only when enough data is provided).
- **Suggested prescription (Rx)** – weight- and allergy-aware, for physician approval.
- **Safety alerts** – drug interactions, allergy alerts, red flags.
- **ICD-10 suggestions**.
- **Patient handout** – plain-language instructions in **English and Urdu**.
- **Voice dictation** – record in the browser, transcribed server-side via Whisper.
- **Editable note**, **copy to clipboard**, and **print-to-PDF** (note, Rx slip, and patient handout).
- **Auto letterhead** – clinic name and a generated logo badge on every document.

---

## Architecture (both implementations)

```
Browser UI (HTML/JS)
   │  1. POST bullets + patient details
   ▼
Backend (n8n workflow  OR  FastAPI)
   │  2. Prompt an OpenAI-compatible LLM (Groq / OpenAI / DeepSeek)
   ▼
LLM returns strict JSON  ──►  Backend formats a human-readable note + structured draft
   │  3. JSON response
   ▼
Browser renders the note, enables Edit / Copy / PDF / Rx / Handout
```

Voice: `Browser records audio ──► Backend ──► Whisper transcription ──► text back into the form`.

---

## Quick start

Pick the implementation you want and follow its README:

- **n8n:** [`n8n-emr-soap-agent/README.md`](./n8n-emr-soap-agent/README.md)
- **Python:** [`python-emr-soap-agent/README.md`](./python-emr-soap-agent/README.md)

You will need an API key from an OpenAI-compatible provider. The default configuration targets Groq (free tier available at <https://console.groq.com>).

---

## Configuration

Never commit real API keys. Both folders ship a `.env.example` / `credentials.example.json`; copy it, fill in your key, and keep the real file out of git (already covered by `.gitignore`).

| Variable | Default | Description |
| --- | --- | --- |
| `GROQ_API_KEY` / OpenAI credential | – | Your provider API key |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | OpenAI-compatible base URL |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Chat model |
| `WHISPER_MODEL` | `whisper-large-v3` | Transcription model |

---

## License

Released under the [MIT License](./LICENSE).
