from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import logging
from datetime import datetime, timezone
from app.models import CVEResponse, CVEDetail, HealthResponse
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SecurePulse starting up...")
    yield
    logger.info("SecurePulse shutting down...")


app = FastAPI(
    title="SecurePulse",
    description="A DevSecOps-hardened CVE vulnerability feed API powered by the NVD.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Liveness probe endpoint for Kubernetes."""
    return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc).isoformat())


@app.get("/cves", response_model=CVEResponse, tags=["Vulnerabilities"])
async def get_recent_cves(
    keyword: str = Query(None, description="Filter CVEs by keyword (e.g. 'nginx', 'apache')"),
    severity: str = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
):
    """
    Fetch recent CVEs from the NVD (National Vulnerability Database).
    Optionally filter by keyword and/or severity.
    """
    params = {"resultsPerPage": limit}

    if keyword:
        params["keywordSearch"] = keyword
    if severity:
        valid = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if severity.upper() not in valid:
            raise HTTPException(status_code=400, detail=f"Invalid severity. Must be one of: {valid}")
        params["cvssV3Severity"] = severity.upper()

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(NVD_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="NVD API timed out. Try again shortly.")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"NVD API error: {e.response.status_code}")

    vulnerabilities = data.get("vulnerabilities", [])
    results = []

    for item in vulnerabilities:
        cve = item.get("cve", {})
        cve_id = cve.get("id", "N/A")
        descriptions = cve.get("descriptions", [])
        description = next(
            (d["value"] for d in descriptions if d.get("lang") == "en"), "No description available."
        )

        metrics = cve.get("metrics", {})
        cvss_v3 = metrics.get("cvssMetricV31", metrics.get("cvssMetricV30", []))
        base_score = None
        severity_level = "UNKNOWN"

        if cvss_v3:
            cvss_data = cvss_v3[0].get("cvssData", {})
            base_score = cvss_data.get("baseScore")
            severity_level = cvss_data.get("baseSeverity", "UNKNOWN")

        published = cve.get("published", "")
        references = [r.get("url", "") for r in cve.get("references", [])[:3]]

        results.append(CVEDetail(
            id=cve_id,
            description=description[:500],
            severity=severity_level,
            base_score=base_score,
            published=published,
            references=references,
        ))

    return CVEResponse(
        total_results=data.get("totalResults", 0),
        returned=len(results),
        timestamp=datetime.now(timezone.utc).isoformat(),
        cves=results,
    )


@app.get("/cves/{cve_id}", response_model=CVEDetail, tags=["Vulnerabilities"])
async def get_cve_by_id(cve_id: str):
    """
    Fetch a specific CVE by its ID (e.g. CVE-2024-12345).
    """
    params = {"cveId": cve_id.upper()}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(NVD_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="NVD API timed out.")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"NVD API error: {e.response.status_code}")

    vulnerabilities = data.get("vulnerabilities", [])
    if not vulnerabilities:
        raise HTTPException(status_code=404, detail=f"CVE '{cve_id}' not found.")

    cve = vulnerabilities[0].get("cve", {})
    descriptions = cve.get("descriptions", [])
    description = next(
        (d["value"] for d in descriptions if d.get("lang") == "en"), "No description available."
    )

    metrics = cve.get("metrics", {})
    cvss_v3 = metrics.get("cvssMetricV31", metrics.get("cvssMetricV30", []))
    base_score = None
    severity_level = "UNKNOWN"

    if cvss_v3:
        cvss_data = cvss_v3[0].get("cvssData", {})
        base_score = cvss_data.get("baseScore")
        severity_level = cvss_data.get("baseSeverity", "UNKNOWN")

    references = [r.get("url", "") for r in cve.get("references", [])[:3]]

    return CVEDetail(
        id=cve.get("id", cve_id),
        description=description[:500],
        severity=severity_level,
        base_score=base_score,
        published=cve.get("published", ""),
        references=references,
    )