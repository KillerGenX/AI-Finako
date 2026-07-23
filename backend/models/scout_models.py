from pydantic import BaseModel
from typing import List, Optional

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
