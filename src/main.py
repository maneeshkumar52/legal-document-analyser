"""FastAPI entry point for the Legal Document Analyser."""
import logging, sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import structlog

structlog.configure(
    processors=[structlog.processors.add_log_level, structlog.processors.TimeStamper(fmt="iso"), structlog.processors.JSONRenderer()],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger(__name__)

from src.models import AnalyseRequest, CompareRequest, ObligationRequest
from src.analyser import ContractAnalyser
from src.comparator import ContractComparator

analyser: ContractAnalyser = None
comparator: ContractComparator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global analyser, comparator
    analyser = ContractAnalyser()
    comparator = ContractComparator()
    logger.info("legal_document_analyser_starting")
    yield


app = FastAPI(
    title="Legal Document Analyser",
    description="AI-powered contract analysis with hierarchical chunking — Project 6, Chapter 20, Prompt to Production",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "legal-document-analyser", "version": "1.0.0"}


@app.post("/api/v1/analyse")
async def analyse_contract(request: AnalyseRequest) -> dict:
    """Extract clauses, obligations, and risks from a contract."""
    try:
        clauses = await analyser.extract_clauses(request.query, request.contract_id)
        obligations = await analyser.detect_obligations(request.contract_id or "all") if request.contract_id else []
        risks = await analyser.identify_risks(request.contract_id or "all") if request.contract_id else []
        return {
            "query": request.query,
            "contract_id": request.contract_id,
            "clauses": [c.model_dump() for c in clauses],
            "obligations": [o.model_dump() for o in obligations],
            "risks": [r.model_dump() for r in risks],
        }
    except Exception as exc:
        logger.error("analyse_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/v1/compare")
async def compare_contracts(request: CompareRequest) -> dict:
    """Compare a specific clause type across multiple contracts."""
    try:
        result = await comparator.compare_terms(request.contract_ids, request.clause_type)
        return result.model_dump()
    except Exception as exc:
        logger.error("compare_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/v1/extract-obligations")
async def extract_obligations(request: ObligationRequest) -> dict:
    """Extract all obligations from a specific contract."""
    try:
        obligations = await analyser.detect_obligations(request.contract_id)
        risks = await analyser.identify_risks(request.contract_id)
        return {
            "contract_id": request.contract_id,
            "obligations": [o.model_dump() for o in obligations],
            "risks": [r.model_dump() for r in risks],
            "total_obligations": len(obligations),
            "total_risks": len(risks),
        }
    except Exception as exc:
        logger.error("obligations_error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))
