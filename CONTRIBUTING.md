# Contributing

Thank you for your interest in improving the **EMR SOAP Draft Agent**.

## Scope

This repository ships two independent implementations of the same agent:

- `n8n-emr-soap-agent/` — n8n workflow + embedded HTML UI
- `python-emr-soap-agent/` — FastAPI service + HTML UI

Please keep both implementations feature-aligned when you change clinical output fields, the system prompt, or the clinician UI.

## Rules

1. **Never commit secrets.** Use `.env.example` / `credentials.example.json` only.
2. **Medical safety.** Do not remove the draft disclaimer, or change the model into a definitive diagnosis / final-prescription tool.
3. **Tests.** For Python changes that touch formatting, run:

   ```bash
   cd python-emr-soap-agent
   pip install -r requirements-dev.txt
   pytest -q
   ```

4. **UI parity.** If you edit the clinician form, update:
   - `n8n-emr-soap-agent/frontend/soap_form.html`
   - `python-emr-soap-agent/app/static/index.html`
   and keep API paths correct for each stack (`/webhook/...` vs `/api/...`).

## Pull requests

Open a PR against `main` with a short summary of what changed and how you tested it.
