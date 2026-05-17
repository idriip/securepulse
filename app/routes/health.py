import httpx
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from app.models import HealthResponse

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Liveness probe — confirms the app process is running."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness probe — checks connectivity to NVD API."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://services.nvd.nist.gov/rest/json/cves/2.0",
                params={"resultsPerPage": 1}
            )
            response.raise_for_status()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="NVD API is unreachable — pod not ready"
        )
    return HealthResponse(
        status="ready",
        timestamp=datetime.now(timezone.utc).isoformat()
    )