from typing import Optional, List, Dict
from pydantic import BaseModel, Field
import uuid

class DocumentChunkModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    section: str
    page_number: Optional[int] = None
    chunk_type: str  # "section_summary" or "paragraph"
    parent_id: Optional[str] = None
    contract_id: str
    document_title: str

class ClauseExtraction(BaseModel):
    reference: str
    clause_type: str
    party: str
    content: str
    deadline: Optional[str] = None
    penalty: Optional[str] = None

class Obligation(BaseModel):
    party: str
    action: str
    deadline: Optional[str] = None
    condition: Optional[str] = None

class RiskArea(BaseModel):
    category: str
    description: str
    severity: str  # high, medium, low
    mitigation: Optional[str] = None

class ContractAnalysis(BaseModel):
    contract_id: str
    clauses: List[ClauseExtraction] = Field(default_factory=list)
    obligations: List[Obligation] = Field(default_factory=list)
    risks: List[RiskArea] = Field(default_factory=list)
    summary: str = ""

class ComparisonResult(BaseModel):
    contract_ids: List[str]
    clause_type: str
    comparison: Dict[str, str] = Field(default_factory=dict)
    differences: List[str] = Field(default_factory=list)
    recommendation: str = ""

class AnalyseRequest(BaseModel):
    query: str = Field(..., min_length=5)
    contract_id: Optional[str] = None

class CompareRequest(BaseModel):
    contract_ids: List[str] = Field(..., min_length=2)
    clause_type: str = Field(default="liability")

class ObligationRequest(BaseModel):
    contract_id: str
