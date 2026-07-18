# EMR SOAP Draft Agent — Python (FastAPI) Implementation

A standalone [FastAPI](https://fastapi.tiangolo.com) service that serves a clinician web form and generates a structured **DRAFT SOAP note** with decision support, using an OpenAI-compatible LLM (default **Groq / `llama-3.3-70b-versatile`**) and **Whisper** (`whisper-large-v3`) for voice dictation.

> **Disclaimer:** All output is an AI-generated draft and must be reviewed and signed by a licensed physician.

---

## Project layout

```
python-emr-soap-agent/
├── app/
│   ├── main.py            # FastAPI app + routes
│   ├── config.py          # Env-based settings
│   ├── schemas.py         # Request models
│   ├── prompts.py         # LLM system prompt
│   ├── soap_service.py    # LLM chat + Whisper calls
│   ├── formatting.py      # JSON -> formatted note (port of the n8n parser)
│   └── static/
│       └── index.html     # Clinician UI
├── tests/
│   └── test_formatting.py
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── run.py
└── .env.example
```

## API

| Method + Path | Purpose |
| --- | --- |
| `GET  /` | Clinician web form |
| `GET  /health` | Readiness probe |
| `POST /api/generate` | Generate a SOAP draft (JSON in → JSON out) |
| `POST /api/transcribe` | Transcribe recorded audio (multipart file → `{ "text": ... }`) |
| `GET  /docs` | Interactive OpenAPI docs (Swagger UI) |

---

## Quick start (local)

**Prerequisites:** Python 3.10+ and a Groq API key (free at <https://console.groq.com>).

```bash
cd python-emr-soap-agent

# 1. Virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2. Dependencies
pip install -r requirements.txt

# 3. Configuration
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
# then edit .env and set GROQ_API_KEY

# 4. Run
uvicorn app.main:app --reload
```

Open <http://localhost:8000> in Chrome/Edge.

---

## Quick start (Docker)

```bash
cd python-emr-soap-agent
cp .env.example .env        # set GROQ_API_KEY
docker compose up --build
```

Open <http://localhost:8000>.

---

## Testing the API

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "bullets": "55F chest pain on exertion 2 days, radiates to left arm, SOB. BP 158/94, HR 98. Hx hypertension. Meds: amlodipine. Allergy: penicillin.",
    "patient_name": "Jane Doe",
    "mr_number": "MR-1001",
    "provider": "Smith",
    "age": "55", "sex": "Female", "weight": "70"
  }'
```

Run the unit tests (no API key needed — they test the formatter only):

```bash
pip install -r requirements-dev.txt
pytest -q
```

---

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `GROQ_API_KEY` | – | **Required.** OpenAI-compatible API key |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | Provider base URL |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Chat model |
| `WHISPER_MODEL` | `whisper-large-v3` | Transcription model |
| `REQUEST_TIMEOUT` | `60` | HTTP timeout (seconds) |
| `CLINIC_NAME` | `North Hospital New York` | Letterhead clinic name |

To use OpenAI instead of Groq: set `LLM_BASE_URL=https://api.openai.com/v1`, `LLM_MODEL=gpt-4o-mini`, `WHISPER_MODEL=whisper-1`, and `GROQ_API_KEY` to your OpenAI key.

---

## Notes

- **Voice dictation** requires a browser microphone permission and works over `localhost` or HTTPS.
- **PDF export** uses the browser's native print-to-PDF (choose "Save as PDF").
- Never commit your real `.env`; it is git-ignored.
