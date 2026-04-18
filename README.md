# Legal Document Analyser

Production-oriented AI application built on FastAPI with a modular service layout and enterprise-friendly project structure.

## Architecture

- API Layer: FastAPI application exposed via Uvicorn
- Domain Layer: Business modules under source folders (routing, orchestration, services)
- Integration Layer: Azure/OpenAI/search/messaging integrations through environment-driven configuration
- Quality Layer: Automated tests and demo/e2e scripts

## Repository Structure

```txt
legal-document-analyser/
  src/ or orchestrator/
  tests/
  infra/
  requirements.txt
  demo_e2e.py
```

## Prerequisites

- Python 3.10+
- pip 23+
- Optional cloud credentials depending on enabled integrations

## Setup and Execution

1. Clone and enter repository

```bash
git clone https://github.com/maneeshkumar52/legal-document-analyser.git
cd legal-document-analyser
```

2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Configure environment variables

```bash
cp .env.example .env 2>/dev/null || true
```

5. Start API server

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

6. Verify API docs

- Swagger UI: http://127.0.0.1:8000/docs

## Testing

```bash
pytest -q
python demo_e2e.py
```

## Troubleshooting

- Import errors: ensure virtual environment is active and dependencies are installed
- Port conflict: change `--port` value in the Uvicorn command
- Missing cloud credentials: validate `.env` or shell exports before startup

## License

See `LICENSE` in this repository.