# Legal Document Analyser

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

Contract intelligence platform for clause extraction, obligation detection, risk identification, and cross-contract comparison — powered by Azure OpenAI and Azure AI Search with hierarchical document chunking.

## Architecture

```
Legal Documents (PDF/DOCX)
        │
        ▼
┌─────────────────────────────────────┐
│  Document Intelligence (OCR/Parse)  │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  HierarchicalChunker                │
│  (Section-level + paragraph-level)  │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  Azure AI Search (Vector Index)     │
│  text-embedding-3-large             │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│  FastAPI Service (:8000)            │
│                                     │
│  /analyse  → ContractAnalyser       │──► Clause + obligation + risk extraction
│  /compare  → Comparator            │──► Cross-contract diff + recommendations
│  /query    → TwoLevelRetriever     │──► Hybrid search (vector + keyword)
└─────────────────────────────────────┘
```

## Key Features

- **Clause Extraction** — Identifies liability, payment, termination, confidentiality, IP, and warranty clauses with structured metadata
- **Obligation Detection** — Extracts party obligations with deadlines and conditions
- **Risk Identification** — LLM-powered risk analysis with severity scoring
- **Cross-Contract Comparison** — Side-by-side clause diff across multiple contracts with recommendations
- **Hierarchical Chunking** — Two-level chunking (section summaries + paragraphs) for better retrieval precision
- **Two-Level Retrieval** — Combines section-level and paragraph-level search for context-aware answers
- **Document Intelligence** — Azure Form Recognizer for OCR and structured document parsing

## Step-by-Step Flow

### Step 1: Document Ingestion
Run `indexer/index_documents.py` to process contracts from `indexer/sample_contracts/`. Azure Document Intelligence extracts text and structure.

### Step 2: Hierarchical Chunking
`HierarchicalChunker` splits documents into section-level summaries and paragraph-level chunks, preserving parent-child relationships via `parent_id`.

### Step 3: Vector Indexing
Chunks are embedded with `text-embedding-3-large` and indexed in Azure AI Search with metadata (contract_id, section, page_number, chunk_type).

### Step 4: Analysis Request
Client sends a contract ID or query to the FastAPI endpoints. `TwoLevelRetriever` fetches relevant chunks using hybrid search.

### Step 5: LLM Analysis
`ContractAnalyser` sends retrieved context to GPT-4o with specialized prompts for clause extraction, obligation detection, or risk identification.

### Step 6: Cross-Contract Comparison
`Comparator` retrieves matching clause types across contracts and generates structured comparison reports with recommendations.

## Repository Structure

```
legal-document-analyser/
├── src/
│   ├── main.py                  # FastAPI app entry point
│   ├── analyser.py              # ContractAnalyser — clause, obligation, risk extraction
│   ├── comparator.py            # Cross-contract comparison engine
│   ├── retriever.py             # TwoLevelRetriever — hybrid vector + keyword search
│   ├── hierarchical_chunker.py  # Section + paragraph chunking
│   ├── document_processor.py    # Document Intelligence integration
│   ├── models.py                # Pydantic models
│   └── config.py                # Environment-driven settings
├── indexer/
│   ├── index_documents.py       # Batch document indexing pipeline
│   └── sample_contracts/        # Sample legal documents
├── tests/
│   └── test_chunker.py
├── infra/
│   ├── Dockerfile
│   └── azure-deploy.sh
├── demo_e2e.py
├── requirements.txt
└── .env.example
```

## Quick Start

```bash
git clone https://github.com/maneeshkumar52/legal-document-analyser.git
cd legal-document-analyser
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Configure Azure credentials
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configuration

| Variable | Description |
|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment (gpt-4o) |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding model (text-embedding-3-large) |
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search endpoint |
| `AZURE_SEARCH_INDEX_NAME` | Index name (legal-documents) |
| `AZURE_DOC_INTELLIGENCE_ENDPOINT` | Document Intelligence endpoint |

## Testing

```bash
pytest -q                    # Unit tests
python demo_e2e.py           # End-to-end demo
```

## License

MIT
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
