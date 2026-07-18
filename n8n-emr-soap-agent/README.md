# EMR SOAP Draft Agent — n8n Method

Self-hosted **[n8n](https://n8n.io)** implementation of the EMR SOAP Draft Agent (visual low-code workflow + HTML clinician UI).

This is **Method A** in the root README. The alternative is the **Python FastAPI** folder (`../python-emr-soap-agent`).

> **Disclaimer:** All output is an AI-generated draft and must be reviewed and signed by a licensed physician.

---

## Technology stack (n8n method)

| Component | What we use |
| --- | --- |
| Orchestration | **n8n** workflow (webhook → LLM → parse → respond) |
| Clinician UI | **HTML + JavaScript** (`frontend/soap_form.html`) |
| LLM | OpenAI-compatible API (default **Groq** `llama-3.3-70b-versatile`) |
| Voice | **Whisper** (`whisper-large-v3`) via Groq |
| Runtime | **Docker** (recommended) or any n8n host |

---

## What's inside

```
n8n-emr-soap-agent/
├── workflow/
│   └── EMR-SOAP-Agent.json        # Import this into n8n
├── frontend/
│   └── soap_form.html             # The clinician UI (also embedded in the workflow)
├── scripts/
│   └── update_features.js         # Helper to re-inject the UI/prompt into an exported workflow
├── credentials.example.json       # Template for the LLM API credential (no real key)
└── .env.example
```

## The workflow

The webhook node exposes **two paths** on the same base URL:

| Method + Path | Purpose |
| --- | --- |
| `GET  /webhook/soap-draft` | Serves the clinician HTML form |
| `POST /webhook/soap-draft` | Generates the SOAP note (JSON in → JSON out) |
| `POST /webhook/soap-transcribe` | Accepts recorded audio, returns a transcript (Whisper) |

Node flow:

```
Webhook ─► Has SOAP Input? ─┬─(GET/empty)─► Respond - Browser UI (serves soap_form.html)
                            └─(POST)──────► Prepare Input ─► LLM (SOAP Draft) ─► Parse SOAP JSON ─► Respond - JSON
Webhook - Transcribe ─► Groq Whisper ─► Respond - Transcript
```

---

## Step-by-step setup

### 1. Run n8n

Docker (recommended):

```bash
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

Open <http://localhost:5678> and create your owner account.

### 2. Add the LLM credential

1. In n8n: **Credentials → New → "OpenAI API"**.
2. Set the **API Key** to your Groq key (get one free at <https://console.groq.com>).
3. Set the **Base URL** to `https://api.groq.com/openai/v1`.
4. Save. (See `credentials.example.json` for the shape.)

> You can point this at OpenAI, DeepSeek, or any OpenAI-compatible endpoint by changing the Base URL and model.

### 3. Import the workflow

**Editor:** Workflows → **⋮ → Import from File** → select `workflow/EMR-SOAP-Agent.json`.

**CLI (Docker):**

```bash
docker cp workflow/EMR-SOAP-Agent.json n8n:/tmp/wf.json
docker exec n8n n8n import:workflow --input=/tmp/wf.json
docker restart n8n
```

### 4. Attach the credential & activate

Open the imported workflow, click the **LLM (SOAP Draft)** and **Groq Whisper** nodes, select your OpenAI credential, then toggle the workflow **Active**.

### 5. Use it

Open <http://localhost:5678/webhook/soap-draft> in Chrome/Edge.

---

## Testing the API

```bash
curl -X POST http://localhost:5678/webhook/soap-draft \
  -H "Content-Type: application/json" \
  -d '{
    "bullets": "55F chest pain on exertion 2 days, radiates to left arm, SOB. BP 158/94, HR 98. Hx hypertension. Meds: amlodipine. Allergy: penicillin.",
    "patient_name": "Jane Doe",
    "mr_number": "MR-1001",
    "provider": "Smith",
    "age": "55", "sex": "Female", "weight": "70"
  }'
```

Response: `{ "success": true, "formatted_note": "...", "draft": { ... }, "generated_at": "..." }`.

---

## Re-deploying UI / prompt changes

`scripts/update_features.js` reads `frontend/soap_form.html` plus an exported workflow and re-injects the UI, the LLM system prompt, and the note formatter. Typical loop:

```bash
docker exec n8n n8n export:workflow --id=<ID> --output=/tmp/wf.json
docker cp frontend/soap_form.html n8n:/tmp/soap_form.html
docker cp scripts/update_features.js n8n:/tmp/update_features.js
docker exec n8n node /tmp/update_features.js
docker exec n8n n8n import:workflow --input=/tmp/wf_out.json
docker restart n8n
```

---

## Security notes

- The workflow JSON references a credential **by name/id only** — no secret is stored in this repo.
- Keep your real API key in the n8n credential store or a local `.env`, never in git.
