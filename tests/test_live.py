"""
Live HTTP Verification Script
Validates running FastAPI backend and Frontend HTTP server.
"""

import urllib.request
import json


def test_live_servers():
    def get(url):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read()

    # 1. Backend /health
    st, data = get("http://127.0.0.1:8000/health")
    assert st == 200
    res = json.loads(data.decode("utf-8"))
    assert res["status"] == "healthy"
    print(" Backend /health verified:", res)

    # 2. Backend /docs
    st, data = get("http://127.0.0.1:8000/docs")
    assert st == 200
    print(" Backend /docs verified (Swagger HTML available)")

    # 3. Backend /analytics/summary
    st, data = get("http://127.0.0.1:8000/analytics/summary")
    assert st == 200
    summary = json.loads(data.decode("utf-8"))
    assert summary["total_requests"] > 0
    print(" Backend /analytics/summary verified:", summary)

    # 4. Backend /hotspots
    st, data = get("http://127.0.0.1:8000/hotspots")
    assert st == 200
    hotspots = json.loads(data.decode("utf-8"))
    assert len(hotspots) > 0
    print(f" Backend /hotspots verified: {len(hotspots)} hotspots loaded. Top: {hotspots[0]['location']} (CNI: {hotspots[0]['civic_need_index']})")

    # 5. Frontend /index.html
    st, data = get("http://127.0.0.1:5500/index.html")
    assert st == 200
    assert b"CivicIntel AI" in data
    print(" Frontend /index.html verified")

    # 6. Frontend /citizen.html
    st, data = get("http://127.0.0.1:5500/citizen.html")
    assert st == 200
    assert b"Submit a Civic Issue" in data
    print(" Frontend /citizen.html verified")

    # 7. Frontend /dashboard.html
    st, data = get("http://127.0.0.1:5500/dashboard.html")
    assert st == 200
    assert b"Development Intelligence Overview" in data
    print(" Frontend /dashboard.html verified")


if __name__ == "__main__":
    test_live_servers()
    print("\n End-to-end live server verification successful!")
