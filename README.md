# Legal Document Analyser

**Project 6, Chapter 20 — Prompt to Production by Maneesh Kumar**

An AI-powered legal document analysis service that extracts clauses, detects obligations, identifies risks, and compares terms across multiple contracts. Built with FastAPI, Azure OpenAI, and Azure AI Search.

---

## Key Innovation: Two-Level Hierarchical Chunking

Standard RAG systems chunk documents into uniform blocks, which causes legal documents to lose structural context (a paragraph about "liability" may appear in multiple sections with very different meanings).

This project solves that problem with a **two-level hierarchical chunking strategy**:

- **Level 1 — Section Summaries (~1200 chars):** The document is split on formal legal headers (`ARTICLE`, `SECTION`, `CLAUSE`, `SCHEDULE`). Each section produces a summary chunk that carries full structural context.
- **Level 2 — Paragraph Chunks (~400 chars):** Each section is further split into fine-grained paragraph chunks, linked back to their parent section via `parent_id`.

### Two-Level Retrieval Flow

```
User Query: "What is the liability cap?"
        |
        v
+-------+--------+
|  Embed Query   |  (Azure OpenAI text-embedding-3-large)
+-------+--------+
        |
        v
+-------+--------------------+
|  Level 1: Search           |
|  chunk_type = section_summary  |
|  Hybrid: keyword + vector  |
|  Returns top section IDs   |
+-------+--------------------+
        |
        v
+-------+--------------------+
|  Level 2: Search           |
|  chunk_type = paragraph    |
|  Filter: parent_id IN      |
|   [matched section IDs]    |
|  Returns precise text      |
+-------+--------------------+
        |
        v
+-------+--------+
|  LLM Analysis  |  (Azure OpenAI GPT-4o)
|  Clause extract|
|  Risk identify |
+-------+--------+
        |
        v
  Structured JSON Response
```

This two-level approach ensures that:
1. Broad section context is always available to narrow the search space
2. Precise paragraph text is retrieved for LLM analysis
3. Parent-child relationships allow the LLM to understand clause hierarchy

---

## Architecture

```
legal-document-analyser/
├── src/
│   ├── main.py                  # FastAPI app and API routes
│   ├── config.py                # Pydantic Settings (Azure credentials)
│   ├── models.py                # Pydantic request/response models
│   ├── hierarchical_chunker.py  # Two-level document chunker
│   ├── document_processor.py   # Text extraction (PDF + Markdown)
│   ├── retriever.py             # Two-level Azure AI Search retriever
│   ├── analyser.py              # Clause, obligation, risk extraction
│   └── comparator.py           # Cross-contract comparison
├── indexer/
│   ├── index_documents.py       # Indexes contracts into Azure AI Search
│   └── sample_contracts/
│       ├── service_agreement.md # Sample Service Level Agreement
│       └── nda_template.md      # Sample NDA
├── tests/
│   └── test_chunker.py          # Unit tests for hierarchical chunker
├── infra/
│   ├── Dockerfile               # Container image definition
│   └── azure-deploy.sh          # Azure Container Apps deployment script
├── .env.example                 # Environment variable template
└── requirements.txt
```

---

## API Endpoints

### POST /api/v1/analyse

Extract clauses, obligations, and risks from a contract.

**Request:**
```json
{
  "query": "What are the payment terms and late payment penalties?",
  "contract_id": "service-agreement"
}
```

**Response:**
```json
{
  "query": "What are the payment terms and late payment penalties?",
  "contract_id": "service-agreement",
  "clauses": [
    {
      "reference": "3.1",
      "clause_type": "payment",
      "party": "Client",
      "content": "Client shall pay Provider £15,000 per month within 30 days of invoice.",
      "deadline": "30 days from invoice date",
      "penalty": "1.5% per month interest on overdue amounts"
    }
  ],
  "obligations": [
    {
      "party": "Client",
      "action": "Pay monthly retainer of £15,000",
      "deadline": "Within 30 days of invoice",
      "condition": null
    }
  ],
  "risks": [
    {
      "category": "financial",
      "description": "Late payment interest at 1.5% per month could accumulate significantly",
      "severity": "medium",
      "mitigation": "Set up automated payment reminders and direct debit"
    }
  ]
}
```

---

### POST /api/v1/compare

Compare a specific clause type across multiple contracts.

**Request:**
```json
{
  "contract_ids": ["service-agreement", "nda-template"],
  "clause_type": "confidentiality"
}
```

**Response:**
```json
{
  "contract_ids": ["service-agreement", "nda-template"],
  "clause_type": "confidentiality",
  "comparison": {
    "service-agreement": "5-year confidentiality obligation; standard NDA provisions apply; exclusions for public domain and prior knowledge.",
    "nda-template": "5-year obligation per disclosure; need-to-know basis; reasonable care standard; return/destruction on termination."
  },
  "differences": [
    "The NDA template includes explicit return/destruction obligations; the service agreement does not.",
    "The NDA template contains detailed exclusion categories; the service agreement is less explicit."
  ],
  "recommendation": "Consider adopting the NDA template's explicit return/destruction clause into the service agreement for stronger data protection."
}
```

---

### POST /api/v1/extract-obligations

Extract all obligations and risk areas from a specific contract.

**Request:**
```json
{
  "contract_id": "service-agreement"
}
```

**Response:**
```json
{
  "contract_id": "service-agreement",
  "obligations": [
    {
      "party": "Provider",
      "action": "Achieve 99.5% monthly uptime for all production systems",
      "deadline": "Measured on rolling 30-day basis",
      "condition": "Excluding scheduled maintenance windows"
    },
    {
      "party": "Client",
      "action": "Pay monthly retainer of £15,000",
      "deadline": "Within 30 days of invoice",
      "condition": null
    }
  ],
  "risks": [
    {
      "category": "financial",
      "description": "Liability cap limited to 12 months fees; may be insufficient for large data breaches",
      "severity": "high",
      "mitigation": "Negotiate higher cap or obtain cyber insurance"
    }
  ],
  "total_obligations": 2,
  "total_risks": 1
}
```

---

### GET /health

```json
{
  "status": "healthy",
  "service": "legal-document-analyser",
  "version": "1.0.0"
}
```

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- Azure subscription with:
  - Azure OpenAI (GPT-4o and text-embedding-3-large deployments)
  - Azure AI Search (Standard tier or higher for vector search)
  - Azure Document Intelligence (optional, for PDF extraction)

### 1. Clone and install

```bash
cd legal-document-analyser
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

### 3. Index sample contracts

```bash
python indexer/index_documents.py
```

This will:
- Create (or update) the Azure AI Search index with vector and hierarchical fields
- Chunk the sample contracts using the two-level hierarchical chunker
- Embed each chunk with text-embedding-3-large
- Upload all chunks to the search index

### 4. Start the API server

```bash
uvicorn src.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 5. Run tests

```bash
pytest tests/ -v
```

The unit tests for the hierarchical chunker run without any Azure credentials.

---

## Sample curl Commands

### Analyse a contract

```bash
curl -X POST http://localhost:8000/api/v1/analyse \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the liability cap?", "contract_id": "service-agreement"}'
```

### Compare confidentiality clauses

```bash
curl -X POST http://localhost:8000/api/v1/compare \
  -H "Content-Type: application/json" \
  -d '{"contract_ids": ["service-agreement", "nda-template"], "clause_type": "confidentiality"}'
```

### Extract all obligations

```bash
curl -X POST http://localhost:8000/api/v1/extract-obligations \
  -H "Content-Type: application/json" \
  -d '{"contract_id": "service-agreement"}'
```

---

## Docker Deployment

```bash
docker build -f infra/Dockerfile -t legal-document-analyser:latest .
docker run -p 8000:8000 --env-file .env legal-document-analyser:latest
```

## Azure Container Apps Deployment

```bash
chmod +x infra/azure-deploy.sh
./infra/azure-deploy.sh
```

---

## Environment Variables Reference

| Variable | Description | Default |
|---|---|---|
| AZURE_OPENAI_ENDPOINT | Azure OpenAI resource endpoint | required |
| AZURE_OPENAI_API_KEY | Azure OpenAI API key | required |
| AZURE_OPENAI_API_VERSION | API version | 2024-02-01 |
| AZURE_OPENAI_DEPLOYMENT | GPT model deployment name | gpt-4o |
| AZURE_OPENAI_EMBEDDING_DEPLOYMENT | Embedding model deployment name | text-embedding-3-large |
| AZURE_SEARCH_ENDPOINT | Azure AI Search endpoint | required |
| AZURE_SEARCH_API_KEY | Azure AI Search admin key | required |
| AZURE_SEARCH_INDEX_NAME | Name of the search index | legal-documents |
| AZURE_DOC_INTELLIGENCE_ENDPOINT | Azure Document Intelligence endpoint | optional |
| AZURE_DOC_INTELLIGENCE_KEY | Azure Document Intelligence key | optional |
| LOG_LEVEL | Logging level | INFO |

---

## Book Reference

This project is **Project 6** from **Chapter 20** of:

> **Prompt to Production** by Maneesh Kumar
>
> A practical guide to building production-grade agentic AI systems with Azure OpenAI, RAG, and multi-agent orchestration.

The chapter demonstrates how hierarchical document chunking solves the context-loss problem in legal RAG systems, and how two-level retrieval (section summaries + paragraph detail) produces more accurate clause extraction than flat chunking approaches.
