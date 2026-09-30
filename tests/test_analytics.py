"""
Automated Integration Tests for Analytics & Hotspot Intelligence API
Tests:
- GET /analytics/summary
- GET /analytics/categories
- GET /analytics/languages
- GET /analytics/locations
- GET /analytics/comparison
- GET /hotspots
- GET /hotspots/{location}
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


def test_analytics_summary():
    response = client.get("/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "high_severity" in data
    assert "medium_severity" in data
    assert "low_severity" in data
    assert "total_affected_people" in data
    assert data["total_requests"] >= 0
    assert data["total_affected_people"] >= 0


def test_analytics_categories():
    response = client.get("/analytics/categories")
    assert response.status_code == 200
    cats = response.json()
    assert isinstance(cats, list)
    if len(cats) > 0:
        assert "category" in cats[0]
        assert "count" in cats[0]
        assert "percentage" in cats[0]


def test_analytics_languages():
    response = client.get("/analytics/languages")
    assert response.status_code == 200
    langs = response.json()
    assert isinstance(langs, list)
    if len(langs) > 0:
        assert "language" in langs[0]
        assert "count" in langs[0]
        assert "percentage" in langs[0]


def test_analytics_locations():
    response = client.get("/analytics/locations")
    assert response.status_code == 200
    locs = response.json()
    assert isinstance(locs, list)
    if len(locs) > 0:
        assert "location" in locs[0]
        assert "count" in locs[0]
        assert "affected_people" in locs[0]
        assert "dominant_category" in locs[0]


def test_infrastructure_comparison():
    response = client.get("/analytics/comparison")
    assert response.status_code == 200
    data = response.json()
    assert "disclaimer" in data
    assert "comparison" in data
    assert len(data["comparison"]) > 0
    first_item = data["comparison"][0]
    assert "reported_need_score" in first_item
    assert "infrastructure_score" in first_item
    assert "investment_score" in first_item


def test_hotspots_endpoint():
    response = client.get("/hotspots")
    assert response.status_code == 200
    hotspots = response.json()
    assert isinstance(hotspots, list)
    assert len(hotspots) > 0

    first = hotspots[0]
    assert "location" in first
    assert "civic_need_index" in first
    assert "request_count" in first
    assert "affected_people" in first
    assert "dominant_category" in first
    assert "explanation" in first
    assert 0.0 <= first["civic_need_index"] <= 100.0

    # Verify descending sort order
    for i in range(len(hotspots) - 1):
        assert hotspots[i]["civic_need_index"] >= hotspots[i+1]["civic_need_index"]


def test_hotspot_by_location():
    # Fetch a known hotspot location
    response = client.get("/hotspots/Nagercoil")
    assert response.status_code == 200
    data = response.json()
    assert data["location"].lower() == "nagercoil"
    assert "explanation" in data
    assert len(data["explanation"]) > 20
