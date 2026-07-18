# EMR SOAP Draft Agent — Python (FastAPI) Method

Standalone **Python** implementation of the EMR SOAP Draft Agent.

> This project uses **FastAPI** (with **Uvicorn**). It does **not** use Flask.

> **Disclaimer:** All output is an AI-generated draft and must be reviewed and signed by a licensed physician.

---

## Technology stack

| Component | What we use | Why |
| --- | --- | --- |
| Web framework | **FastAPI** | Modern async Python API framework |
| Server | **Uvicorn** | Runs the FastAPI ASGI app |
| HTTP client | **httpx** | Calls Groq chat completions + Whisper |
| Config | **python-dotenv** | Loads secrets/settings from `.env` |
| Uploads | **python-multipart** | Audio upload for voice transcription |
| Frontend | **HTML + JavaScript** | Clinician portal (`app/static/index.html`) |
| Containers | **Docker / docker-compose** | Optional one-command deploy |
| Tests | **pytest** | Formatter unit tests |

Default AI provider: **Groq** (`llama-3.3-70b-versatile`, `whisper-large-v3`). Any OpenAI-compatible API works by changing `.env`.

---

## Project layout

```
python-emr-soap-agent/
├── app/
│   ├── main.py            # FastAPI app + routes
│   ├── config.py          # Env-based settings
│   ├── schemas.py         # Request models
│   ├── prompts.py         # LLM system prompt
│   ├── soap_service.py    # LLM chat + Whisper calls (httpx)
│   ├── formatting.py      # JSON → formatted note
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

---

## Step-by-step: run locally

### 1. Prerequisites

- Python **3.10+**
- Groq API key from <https://console.groq.com>

### 2. Enter the folder

```bash
cd python-emr-soap-agent
```

### 3. Create and activate a virtual environment

**Windows:**

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install packages

```bash
pip install -r requirements.txt
```

### 5. Add your API key

```bash
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
```

Edit `.env`:

```
GROQ_API_KEY=your_real_key_here
```

### 6. Start FastAPI (Uvicorn)

```bash
uvicorn app.main:app --reload
```

or:

```bash
python run.py
```

### 7. Open the portal

- Clinician UI: <http://localhost:8000>
- Swagger docs: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

### 8. Use it

1. Enter patient name (required)
2. Optional: MR #, Provider, Age / Sex / Weight
3. Enter clinical bullets (or **Speak**)
4. Click **Generate SOAP Draft**
5. Edit / Copy / PDF / Rx slip / Patient handout

---

## Step-by-step: run with Docker

```bash
cd python-emr-soap-agent
cp .env.example .env        # set GROQ_API_KEY
docker compose up --build
```

Open <http://localhost:8000>.

---

## API

| Method + Path | Purpose |
| --- | --- |
| `GET  /` | Clinician web form |
| `GET  /health` | Readiness probe |
| `POST /api/generate` | Generate a SOAP draft |
| `POST /api/transcribe` | Transcribe recorded audio |
| `GET  /docs` | Interactive OpenAPI (Swagger) |

### Example

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d "{
    \"bullets\": \"55F chest pain on exertion 2 days, radiates to left arm, SOB. BP 158/94, HR 98. Hx hypertension. Meds: amlodipine. Allergy: penicillin.\",
    \"patient_name\": \"Jane Doe\",
    \"mr_number\": \"MR-1001\",
    \"provider\": \"Smith\",
    \"age\": \"55\", \"sex\": \"Female\", \"weight\": \"70\"
  }"
```

---

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

---

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `GROQ_API_KEY` | – | **Required** API key |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | Provider base URL |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Chat model |
| `WHISPER_MODEL` | `whisper-large-v3` | Transcription model |
| `REQUEST_TIMEOUT` | `60` | HTTP timeout (seconds) |
| `CLINIC_NAME` | `North Hospital New York` | Letterhead clinic name |

To use OpenAI instead of Groq: set `LLM_BASE_URL=https://api.openai.com/v1`, `LLM_MODEL=gpt-4o-mini`, `WHISPER_MODEL=whisper-1`, and put your OpenAI key in `GROQ_API_KEY`.

---

## Notes

- Voice needs microphone permission (Chrome/Edge on `localhost` or HTTPS)
- PDF export uses the browser print dialog → **Save as PDF**
- Never commit your real `.env`
