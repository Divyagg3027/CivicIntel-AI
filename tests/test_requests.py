"""
Automated Integration Tests for Citizen Requests API
Tests:
- POST /requests: Validation, AI Analysis, DB persistence
- GET /requests: Retrieval, search, category filter, severity filter, language filter
- GET /requests/{id}: Single request lookup
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "CivicIntel AI"}


def test_create_citizen_request():
    payload = {
        "request_text": "There is no drinking water in our village. Around 500 people are affected.",
        "location": "Nagercoil"
    }
    response = client.post("/requests", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "request" in data
    req = data["request"]
    assert req["location"] == "Nagercoil"
    assert req["category"] == "Water"
    assert req["severity"] == "High"
    assert req["affected_people"] == 500
    assert req["detected_need"] == "Drinking Water Infrastructure"
    assert req["status"] == "Analyzed"
    assert req["id"] is not None


def test_create_multilingual_tamil_request():
    payload = {
        "request_text": "எங்கள் பகுதியில் குடிநீர் இல்லை. 500 மக்கள் பாதிக்கப்பட்டுள்ளனர்.",
        "location": "Madurai"
    }
    response = client.post("/requests", json=payload)
    assert response.status_code == 201
    req = response.json()["request"]
    assert req["language"] == "Tamil"
    assert req["category"] == "Water"
    assert req["severity"] == "High"
    assert req["affected_people"] == 500


def test_create_invalid_request():
    # Empty text
    response = client.post("/requests", json={"request_text": "", "location": "Chennai"})
    assert response.status_code == 422 or response.status_code == 400

    # Short location
    response = client.post("/requests", json={"request_text": "Valid problem description here", "location": "C"})
    assert response.status_code == 422 or response.status_code == 400


def test_get_requests_with_filters():
    # Fetch all
    res_all = client.get("/requests")
    assert res_all.status_code == 200
    assert isinstance(res_all.json(), list)
    assert len(res_all.json()) > 0

    # Filter by category Water
    res_water = client.get("/requests?category=Water")
    assert res_water.status_code == 200
    for item in res_water.json():
        assert item["category"] == "Water"

    # Filter by severity High
    res_high = client.get("/requests?severity=High")
    assert res_high.status_code == 200
    for item in res_high.json():
        assert item["severity"] == "High"

    # Search filter
    res_search = client.get("/requests?search=pothole")
    assert res_search.status_code == 200
    for item in res_search.json():
        assert "pothole" in item["request_text"].lower()


def test_get_single_request():
    # First get an existing request id
    res_all = client.get("/requests?limit=1")
    assert res_all.status_code == 200
    req_id = res_all.json()[0]["id"]

    res_single = client.get(f"/requests/{req_id}")
    assert res_single.status_code == 200
    assert res_single.json()["id"] == req_id
