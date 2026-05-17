import httpx
from fastapi import HTTPException
from app.models import CVEDetail, CVEResponse
from datetime import datetime, timezone

NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def _parse_cve(cve: dict) -> CVEDetail:
    cve_id = cve.get("id", "N/A")
    descriptions = cve.get("descriptions", [])
    description = next(
        (d["value"] for d in descriptions if d.get("lang") == "en"),
        "No description available."
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
        id=cve_id,
        description=description[:500],
        severity=severity_level,
        base_score=base_score,
        published=cve.get("published", ""),
        references=references,
    )


async def fetch_cves(keyword=None, severity=None, limit=10) -> CVEResponse:
    params = {"resultsPerPage": limit}
    if keyword:
        params["keywordSearch"] = keyword
    if severity:
        valid = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if severity.upper() not in valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity. Must be one of: {valid}"
            )
        params["cvssV3Severity"] = severity.upper()
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
    results = [_parse_cve(item.get("cve", {})) for item in vulnerabilities]
    return CVEResponse(
        total_results=data.get("totalResults", 0),
        returned=len(results),
        timestamp=datetime.now(timezone.utc).isoformat(),
        cves=results,
    )


async def fetch_cve_by_id(cve_id: str) -> CVEDetail:
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
    return _parse_cve(vulnerabilities[0].get("cve", {}))
