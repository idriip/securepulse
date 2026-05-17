from fastapi import APIRouter, Query
from app.models import CVEDetail, CVEResponse
from app.services.nvd import fetch_cves, fetch_cve_by_id

router = APIRouter(tags=["Vulnerabilities"])


@router.get("/cves", response_model=CVEResponse)
async def get_recent_cves(
    keyword: str = Query(None, description="Filter by keyword (e.g. 'nginx', 'apache')"),
    severity: str = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
):
    """
    Fetch recent CVEs from the NVD (National Vulnerability Database).
    Optionally filter by keyword and/or severity.
    """
    return await fetch_cves(keyword=keyword, severity=severity, limit=limit)


@router.get("/cves/{cve_id}", response_model=CVEDetail)
async def get_cve_by_id(cve_id: str):
    """
    Fetch a specific CVE by its ID (e.g. CVE-2024-12345).
    """
    return await fetch_cve_by_id(cve_id)