# LegalEase — AI-Powered Legal Document Generator

LegalEase is a complete Streamlit + FastAPI application for generating editable legal-document drafts with Google Gemini and exporting them as TXT, DOCX, and PDF.

The implementation follows the supplied project documentation: Streamlit frontend, FastAPI backend, Gemini AI core, editable preview, branded document exports, terms table/bullets, and local deployment.

> **Important:** LegalEase generates document drafts for informational purposes. It is not a law firm, does not create an attorney-client relationship, and generated text must be reviewed by a qualified legal professional before use.

## Architecture

```text
Streamlit UI
    |
    | HTTP JSON
    v
FastAPI backend
    |
    +----> Gemini AI core
    |
    +----> DOCX/PDF/TXT exporters
```

## Project structure

```text
LegalEase/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   ├── config.py
│   ├── dependencies.py
│   ├── ai_core/
│   │   ├── __init__.py
│   │   └── gemini_generator.py
│   └── services/
│       ├── __init__.py
│       ├── document_export.py
│       └── text_utils.py
├── frontend/
│   └── app.py
├── tests/
│   ├── test_api.py
│   ├── test_exports.py
│   └── test_text_utils.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── Procfile
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- A Google Gemini API key
- VS Code
- Internet access for Gemini requests

## 1. Create the environment

Windows PowerShell:

```powershell
cd LegalEase
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

macOS/Linux:

```bash
cd LegalEase
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Configure Gemini

Copy `.env.example` to `.env`:

```text
GEMINI_API_KEY=your_real_api_key
GEMINI_MODEL=gemini-2.5-flash
```

The supplied documentation selected `gemini-1.5-pro`. That model is exposed as a configuration value rather than hard-coded because Gemini model availability changes over time. If your Google account still provides the documented model, set:

```text
GEMINI_MODEL=gemini-1.5-pro
```

Never commit `.env`.

## 3. Start FastAPI

From the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Check:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## 4. Start Streamlit

Open a second terminal and activate the same environment:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```

Open the URL Streamlit prints, normally:

```text
http://localhost:8501
```

If the backend uses another address, set:

```text
BACKEND_URL=http://127.0.0.1:8000
```

## 5. Use the application

1. Select or enter a document type.
2. Enter parties and roles.
3. Enter terms separated by semicolons.
4. Enter the effective date.
5. Optionally choose an output language.
6. Click **Generate Document**.
7. Review and edit the generated draft.
8. Download TXT, DOCX, or PDF.

## API

### POST `/generate`

Example:

```json
{
  "document_type": "Freelance Work Contract",
  "parties": "Jane Doe (Service Provider), TechNova Inc. (Client)",
  "terms": "Payment within 30 days; Confidentiality must be maintained; Either party may terminate with 15 days notice",
  "effective_date": "2026-10-01",
  "language": "English"
}
```

Response:

```json
{
  "document_type": "Freelance Work Contract",
  "content": "...",
  "model": "gemini-2.5-flash"
}
```

### POST `/export/txt`

```json
{
  "document_type": "NDA",
  "content": "..."
}
```

### POST `/export/docx`

Same payload; returns a `.docx` file.

### POST `/export/pdf`

Same payload; returns a `.pdf` file.

## Testing

Run:

```powershell
python -m pytest -q
```

The tests cover:
- health endpoint
- request validation
- export endpoints
- text sanitization
- DOCX/PDF generation
- Gemini-free API test behavior

The test suite does not make live Gemini requests.

## Docker

Build and run:

```bash
docker compose up --build
```

The backend is exposed on `8000` and Streamlit on `8501`.

## Security notes

- Keep the Gemini API key in `.env` or a deployment secret.
- Do not put API keys in Streamlit source code.
- CORS is configurable through `CORS_ORIGINS`.
- The API validates maximum input sizes.
- The app does not persist generated documents by default.
- Generated legal text should be reviewed before signing or filing.

## Deployment

The supplied documentation mentions Render, Railway, Deta, Streamlit Community Cloud, Fly.io and VPS deployment. A practical deployment is to host FastAPI and Streamlit separately and point `BACKEND_URL` at the FastAPI service.

For a production deployment:
- use HTTPS
- store secrets in the platform secret manager
- restrict CORS to the frontend domain
- add authentication/rate limiting
- add structured logging
- avoid storing sensitive generated documents unless required
- use a current Gemini model supported by the account
