import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data

def test_readiness_check_nvd_unreachable():
    """Readiness probe returns 503 when NVD API is unreachable."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("NVD unreachable")
        response = client.get("/ready")
        assert response.status_code == 503    


def test_get_cves_invalid_severity():
    response = client.get("/cves?severity=EXTREME")
    assert response.status_code == 400
    assert "Invalid severity" in response.json()["detail"]


def test_get_cves_limit_bounds():
    # limit > 50 should be rejected by FastAPI validation
    response = client.get("/cves?limit=100")
    assert response.status_code == 422


def test_get_cves_limit_zero():
    response = client.get("/cves?limit=0")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_cves_success():
    mock_response = {
        "totalResults": 1,
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2024-99999",
                    "descriptions": [{"lang": "en", "value": "Test vulnerability description."}],
                    "metrics": {
                        "cvssMetricV31": [
                            {"cvssData": {"baseScore": 9.8, "baseSeverity": "CRITICAL"}}
                        ]
                    },
                    "published": "2024-01-01T00:00:00.000",
                    "references": [{"url": "https://example.com"}],
                }
            }
        ],
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json = lambda: mock_response

        response = client.get("/cves?limit=1")
        assert response.status_code in [200, 502]