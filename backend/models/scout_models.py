from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str

class BuyingSignal(BaseModel):
    signal_type: str
    description: str
    evidence_url: Optional[str] = None

class OpportunityEvaluation(BaseModel):
    score: int
    reasoning: str
    next_action: str
    status: str = "discovered"

class ScoutResult(BaseModel):
    company_name: str
    domain: str
    industry: str
    description: str
    signals: List[BuyingSignal]
    evaluation: OpportunityEvaluation

class ScoutListResult(BaseModel):
    results: List[ScoutResult]

class OpportunityUpdate(BaseModel):
    status: str
    reasoning: Optional[str] = None
    next_action: Optional[str] = None
