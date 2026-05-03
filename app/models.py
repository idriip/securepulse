from pydantic import BaseModel
from typing import Optional, List


class HealthResponse(BaseModel):
    status: str
    timestamp: str


class CVEDetail(BaseModel):
    id: str
    description: str
    severity: str
    base_score: Optional[float] = None
    published: str
    references: List[str] = []


class CVEResponse(BaseModel):
    total_results: int
    returned: int
    timestamp: str
    cves: List[CVEDetail]