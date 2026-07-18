# EMR SOAP Draft Agent

An AI-powered clinical documentation and decision-support assistant that turns short clinical bullet points (typed or dictated) into a structured **DRAFT SOAP note** with triage, differential diagnosis, recommended investigations, clinical risk scores, a suggested prescription, drug-safety / allergy / red-flag alerts, ICD-10 suggestions, and bilingual (English + Urdu) patient instructions.

> **Medical disclaimer:** Every output is an **AI-generated draft**. It must be reviewed, verified, edited, and signed by a licensed physician before it is used or entered into a medical record. This project does not provide medical advice.

---

## Repository structure (two methods)

This repository ships **two independent ways** to run the same EMR SOAP agent. Choose **one** method — you do not need both.

| Folder | Method | Technology stack | Best for |
| --- | --- | --- | --- |
| [`n8n-emr-soap-agent/`](./n8n-emr-soap-agent) | **Method A — n8n** | n8n (low-code workflow), HTML/JS clinician UI, OpenAI-compatible LLM API (Groq), Whisper | Visual automation, Docker self-hosting inside n8n |
| [`python-emr-soap-agent/`](./python-emr-soap-agent) | **Method B — Python** | **FastAPI** (not Flask), Uvicorn, httpx, python-dotenv, HTML/JS UI, Groq LLM + Whisper | Standalone API service, Docker, easy integration with other systems |

Both methods use the same clinician UI features and the same note schema. Default AI provider: [Groq](https://console.groq.com) (`llama-3.3-70b-versatile` + `whisper-large-v3`).

---

## Features (both methods)

- SOAP note generation (Subjective / Objective / Assessment / Plan)
- Triage banner (Routine / Urgent / Emergency)
- Clinical decision support (differential, investigations, follow-up questions)
- Clinical risk scores (HEART, Wells, CHA₂DS₂-VASc, BMI, eGFR when data allows)
- Suggested prescription (Rx) for physician approval
- Drug safety, allergy, and red-flag alerts
- ICD-10 suggestions
- Patient handout in **English and Urdu**
- Voice dictation (browser record → Whisper transcription)
- Editable note, copy, print-to-PDF (note / Rx slip / handout)
- Clinic letterhead: **North Hospital New York** with auto logo badge

---

## Architecture

```
Browser UI (HTML/JS)
   │  POST clinical bullets + patient details
   ▼
Backend = Method A (n8n workflow)  OR  Method B (FastAPI)
   │  Call OpenAI-compatible LLM (Groq / OpenAI / DeepSeek)
   ▼
Strict JSON from LLM  →  formatted SOAP note + structured draft
   │
   ▼
Browser: Edit / Copy / PDF / Rx slip / Patient handout
```

Voice: `Browser records audio → Backend → Whisper → text into the form`

---

## Prerequisites (both methods)

1. **Docker** (recommended for n8n; optional for Python) **or** Python 3.10+
2. A free **Groq API key** from <https://console.groq.com>
3. Browser: **Chrome** or **Edge** (needed for voice recording)

Never commit real API keys. Use `.env.example` / `credentials.example.json` as templates only.

---

# Method A — n8n folder (step by step)

**Folder:** `n8n-emr-soap-agent/`  
**What it is:** An n8n workflow that hosts the clinician form and calls Groq for SOAP generation + voice transcription.

### Step 1 — Start n8n with Docker

```bash
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

Open <http://localhost:5678> and create your n8n owner account.

### Step 2 — Create the LLM credential

1. In n8n go to **Credentials → Add credential → OpenAI API**
2. **API Key** = your Groq key
3. **Base URL** = `https://api.groq.com/openai/v1`
4. Save (name it e.g. `Groq (Llama 3.3 70B)`)

### Step 3 — Import the workflow

1. Open **Workflows → ⋮ → Import from File**
2. Select: `n8n-emr-soap-agent/workflow/EMR-SOAP-Agent.json`
3. Open the **OpenAI - SOAP Draft** and **Groq Whisper** nodes
4. Attach the credential you created in Step 2
5. Toggle the workflow **Active**

### Step 4 — Open the clinician portal

Open in Chrome/Edge:

```
http://localhost:5678/webhook/soap-draft
```

### Step 5 — Generate a note

1. Enter **Patient name** (required)
2. Optionally fill MR number, Provider, Age / Sex / Weight
3. Enter clinical bullet points (or use **Speak** to dictate)
4. Click **Generate SOAP Draft**
5. Use **Edit note**, **Copy**, **Download PDF**, **Rx slip (PDF)**, **Patient handout (PDF)**

### n8n API endpoints

| Method + Path | Purpose |
| --- | --- |
| `GET  /webhook/soap-draft` | Clinician HTML form |
| `POST /webhook/soap-draft` | Generate SOAP draft (JSON) |
| `POST /webhook/soap-transcribe` | Voice transcription (Whisper) |

### Quick API test (n8n)

```bash
curl -X POST http://localhost:5678/webhook/soap-draft \
  -H "Content-Type: application/json" \
  -d "{\"bullets\":\"55F chest pain on exertion 2 days, BP 158/94, HR 98. Hx HTN. Allergy: penicillin.\",\"patient_name\":\"Jane Doe\",\"mr_number\":\"MR-1001\",\"provider\":\"Smith\"}"
```

More detail: [`n8n-emr-soap-agent/README.md`](./n8n-emr-soap-agent/README.md)

---

# Method B — Python folder (step by step)

**Folder:** `python-emr-soap-agent/`  
**What it is:** A standalone **FastAPI** web service (this project does **not** use Flask).

### Tech stack used in the Python folder

| Package / tool | Role |
| --- | --- |
| **FastAPI** | Main web framework (REST API + serving the HTML UI) |
| **Uvicorn** | ASGI server that runs the FastAPI app |
| **httpx** | Async HTTP client for Groq chat + Whisper API calls |
| **python-dotenv** | Loads `GROQ_API_KEY` and settings from `.env` |
| **python-multipart** | Handles audio file uploads for transcription |
| **HTML / JavaScript** | Clinician portal UI (`app/static/index.html`) |
| **Docker / docker-compose** | Optional containerised deployment |
| **pytest** | Unit tests for note formatting (`tests/`) |

### Step 1 — Open the folder

```bash
cd python-emr-soap-agent
```

### Step 2 — Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure your API key

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` and set:

```
GROQ_API_KEY=your_real_groq_key_here
```

Optional settings (already have good defaults):

| Variable | Default | Meaning |
| --- | --- | --- |
| `GROQ_API_KEY` | *(required)* | Groq / OpenAI-compatible API key |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | Provider base URL |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Chat model |
| `WHISPER_MODEL` | `whisper-large-v3` | Transcription model |
| `CLINIC_NAME` | `North Hospital New York` | Letterhead name |

### Step 5 — Run the FastAPI server

```bash
uvicorn app.main:app --reload
```

Or:

```bash
python run.py
```

### Step 6 — Open the clinician portal

Open in Chrome/Edge:

```
http://localhost:8000
```

Interactive API docs (Swagger): <http://localhost:8000/docs>

### Step 7 — Generate a note

Same UI flow as Method A: patient name → bullets → **Generate SOAP Draft** → Edit / PDF / Rx / Handout.

### Python API endpoints

| Method + Path | Purpose |
| --- | --- |
| `GET  /` | Clinician HTML form |
| `GET  /health` | Health check |
| `POST /api/generate` | Generate SOAP draft (JSON) |
| `POST /api/transcribe` | Voice transcription (Whisper) |
| `GET  /docs` | Swagger / OpenAPI docs |

### Quick API test (Python)

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"bullets\":\"55F chest pain on exertion 2 days, BP 158/94, HR 98. Hx HTN. Allergy: penicillin.\",\"patient_name\":\"Jane Doe\",\"mr_number\":\"MR-1001\",\"provider\":\"Smith\"}"
```

### Run with Docker (optional)

```bash
cd python-emr-soap-agent
cp .env.example .env   # set GROQ_API_KEY
docker compose up --build
```

Then open <http://localhost:8000>.

### Run unit tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

More detail: [`python-emr-soap-agent/README.md`](./python-emr-soap-agent/README.md)

---

## Which method should I choose?

| If you want… | Use |
| --- | --- |
| Visual workflow editor, quick webhook automation | **Method A — n8n** |
| Clean Python API, Docker service, `/docs` Swagger | **Method B — FastAPI** |
| Integrate into another backend / hospital system | **Method B — FastAPI** |
| Already run everything inside n8n | **Method A — n8n** |

---

## Security notes

- Do **not** commit `.env` or real API keys
- Outputs are **drafts only** — physician review and signature required
- Voice needs microphone permission (Windows + browser) on `localhost` or HTTPS

---

## License

Released under the [MIT License](./LICENSE).
