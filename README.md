# Legal Document Analyser

Professional-grade legal AI analysis system designed for production-style development with clear service boundaries, repeatable setup, and deterministic execution steps.

## 1. Executive Overview

This repository provides:
- A FastAPI service entrypoint for API-first integration
- Structured modules for orchestration, domain logic, and integrations
- Test scaffolding for incremental quality assurance
- Environment-driven configuration for local, staging, and production workflows

## 2. Architecture

### 2.1 Logical Architecture

```txt
Client / Integrator
      |
      v
FastAPI API Layer (Uvicorn)
      |
      +--> Application Layer (routing, orchestration)
      +--> Domain Layer (business rules)
      +--> Integration Layer (Azure/OpenAI/search/messaging)
      +--> Data/State Layer (configured adapters)
```

### 2.2 Runtime Components
- API Server: FastAPI + Uvicorn
- Configuration: environment variables and .env file
- External Integrations: enabled per environment
- Validation: pytest + e2e demo script

## 3. Repository Structure

```txt
legal-document-analyser/
  src/ or orchestrator/
  tests/
  infra/
  requirements.txt
  demo_e2e.py
```

## 4. Prerequisites

- Python 3.10+
- pip 23+
- Git
- Optional cloud credentials for enabled connectors

## 5. Local Setup

1. Clone repository

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

4. Configure environment

```bash
cp .env.example .env 2>/dev/null || true
```

## 6. Run the Service

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Service endpoints:
- API docs: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## 7. Validation and Test Flow

1. Syntax validation

```bash
python3 -m compileall -q .
```

2. Unit/integration tests

```bash
pytest -q
```

3. End-to-end demo

```bash
python demo_e2e.py
```

## 8. Troubleshooting

- Import or module errors:
  - Ensure .venv is active
  - Reinstall dependencies
- Port already in use:
  - Change --port value
- Cloud connector failures:
  - Validate credentials and service endpoints in .env

## 9. Production Readiness Checklist

- [ ] Environment variables externalized
- [ ] Secrets not committed
- [ ] Logging and tracing enabled
- [ ] Test suite green in CI
- [ ] Health checks configured in deployment

## 10. License

See LICENSE in this repository.
