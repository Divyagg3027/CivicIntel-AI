# CivicIntel AI — Architecture Documentation

> This document describes the **actual, current implementation** of CivicIntel AI.  
> Every component shown below exists in the codebase and was verified by direct file inspection.

---

## Architecture Diagram

A presentation-ready 1560×860 vector diagram is saved at [`architecture_diagram.svg`](./architecture_diagram.svg).  
Open it in any browser or import it directly into a slide deck.

---

## System Overview

CivicIntel AI is a six-layer pipeline. Unstructured multilingual citizen text flows through an NLP service into a FastAPI backend, is persisted in MySQL, is aggregated into a Civic Need Index, and is visualised on a policymaker dashboard.

```
┌──────────────┐   HTTP POST    ┌──────────────────┐   calls   ┌───────────────────┐
│  1. CITIZEN  │ ─────────────▶ │  2. FASTAPI API  │ ────────▶ │  3. NLP SERVICES  │
│     INPUT    │                │     :8000        │           │   (pure Python)   │
└──────────────┘                └──────────────────┘           └─────────┬─────────┘
                                        │                                │ returns dict
                                        │ SQLAlchemy ORM                 │
                                        ▼                                ▼
                                ┌──────────────────┐     ┌──────────────────────────┐
                                │  4. MYSQL 8.0+   │────▶│  5. CIVIC INTELLIGENCE   │
                                │   5 tables       │     │  CNI 0-100 · Tiers       │
                                └──────────────────┘     └────────────┬─────────────┘
                                                                       │ JSON
                                                                       ▼
                                                          ┌─────────────────────────┐
                                                          │  6. POLICYMAKER DASH.   │
                                                          │  dashboard.html :5500   │
                                                          └─────────────────────────┘
                                                                       │ GET /hotspots
                                                                       │ GET /analytics/*
                                                                       └──────────────▶ API
```

---

## Layer 1 — Citizen Input

### Files
- `frontend/index.html` — Landing page  
- `frontend/citizen.html` — Reporting portal  
- `frontend/js/citizen.js` — Form logic  
- `frontend/js/api.js` — Centralised HTTP client  

### What is implemented

**Text input**  
A `<textarea>` validated to ≥ 3 characters. A location `<input>` validated to ≥ 2 characters. Eight quick-select city chips auto-fill the location field:  
*Nagercoil, Coimbatore, Madurai, Chennai, Tirunelveli, Salem, Trichy, Thoothukudi.*

**Voice dictation (browser-side only)**  
`window.SpeechRecognition` / `window.webkitSpeechRecognition` with `lang="en-IN"`. When the 🎙 button is pressed, interim transcripts are appended to the textarea.  
**No audio file is uploaded to the server. There is no server-side speech processing.**

**Instant result card**  
After a successful `POST /requests`, `citizen.js` renders the returned JSON fields inline:  
`category`, `severity`, `affected_people`, `language`, `detected_need`, `status`, `location`.

**Dashboard frontend**  
`dashboard.html` loads `map.js`, `charts.js`, `dashboard.js` to query all API endpoints in parallel and render the policymaker view.

---

## Layer 2 — FastAPI Backend

### Files
- `backend/main.py` — Application entry point  
- `backend/schemas.py` — Pydantic V2 models  
- `backend/routers/requests.py`  
- `backend/routers/analytics.py`  
- `backend/routers/hotspots.py`  

### Runtime
```
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
CORS: `allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]`.  
Swagger UI: `http://127.0.0.1:8000/docs`  
ReDoc: `http://127.0.0.1:8000/redoc`

### All Implemented Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service metadata (name, version, links) |
| `GET` | `/health` | Health check — returns `{"status":"healthy"}` |
| `POST` | `/requests` | Submit citizen request; runs NLP analysis; stores in MySQL; returns structured record |
| `GET` | `/requests` | List requests; query params: `search`, `category`, `severity`, `language`, `location`, `status`, `limit`, `offset` |
| `GET` | `/requests/{id}` | Fetch single citizen request by integer ID |
| `POST` | `/requests/{id}/analyze` | Re-run NLP analysis on an existing stored request |
| `GET` | `/analytics/summary` | KPI totals: total requests, high/medium/low severity counts, total affected people, hotspot count (CNI ≥ 60) |
| `GET` | `/analytics/categories` | Request counts + percentages grouped by category |
| `GET` | `/analytics/languages` | Request counts + percentages grouped by detected language |
| `GET` | `/analytics/locations` | Request counts, affected people, dominant category grouped by location |
| `GET` | `/analytics/comparison` | Per-sector: `reported_need_score` vs `infrastructure_score` vs `investment_score` |
| `GET` | `/hotspots` | Trigger aggregation engine; return all locations ranked by CNI descending |
| `GET` | `/hotspots/{location}` | Return full intelligence dossier for one location |

### Pydantic Schemas (`schemas.py`)
- `CitizenRequestCreate` — input: `request_text`, `location`  
- `CitizenRequestOut` — output: all model fields  
- `CitizenRequestCreateResponse` — wraps message + CitizenRequestOut  
- `SummaryAnalytics`, `CategoryItem`, `LanguageItem`, `LocationItem`, `HotspotResponse`

---

## Layer 3 — NLP Services

### Files
- `backend/services/language_service.py`  
- `backend/services/analysis_service.py`  
- `backend/services/hotspot_service.py`  
- `backend/services/insight_service.py`  

### `language_service.py` — `detect_language(text) → str`
Counts characters whose Unicode code point falls within a script block:

| Language | Unicode Range |
|----------|---------------|
| Tamil | `0x0B80 – 0x0BFF` |
| Hindi (Devanagari) | `0x0900 – 0x097F` |
| Telugu | `0x0C00 – 0x0C7F` |
| Malayalam | `0x0D00 – 0x0D7F` |
| Kannada | `0x0C80 – 0x0CFF` |
| English | Latin A–Z fallback |

Returns the language with the highest character count. No external libraries or API calls.

### `analysis_service.py` — `analyze_request_data(text, location) → dict`

**`detect_category(text)`**  
Weighted keyword scoring across 10 categories. Each keyword has an integer weight; the category with the highest total score wins.  
Categories: `Water`, `Roads`, `Electricity`, `Healthcare`, `Education`, `Sanitation`, `Waste Management`, `Public Transport`, `Housing`, `Other`.  
Keywords exist for all six supported languages.

**`detect_severity(text) → "High" | "Medium" | "Low"`**  
Sums weights for HIGH_SEVERITY_KEYWORDS and MEDIUM_SEVERITY_KEYWORDS.  
Rule: `high_score ≥ 3` → High; `high_score > 0 or medium_score ≥ 2` → Medium; else Low.

**`extract_affected_people(text) → int`**  
Regex patterns matching numbers followed by community nouns (`people`, `families`, `residents`, `மக்கள்`, `குடும்பங்கள்`, `लोग`, `మంది`, etc.).  
Pre-masks `ward N`, `bus N`, `year NNNN` patterns before matching.  
Returns 0 if no match; caps result at 5,000,000.

**`get_coordinates(location) → (lat, lng)`**  
Dictionary lookup against 8 known demo city names.  
Returns `(10.7905, 78.7047)` (Tamil Nadu centroid) for unknown locations.

**`DEVELOPMENT_NEEDS` mapping**  
Translates detected category into a human-readable project type (e.g. `Water` → `"Drinking Water Infrastructure"`).

### `hotspot_service.py` — `calculate_hotspots(db) → list`

1. SQL `GROUP BY location` on `citizen_requests` — produces `request_count`, `total_affected`, `severity_sum` (using CASE weighting: High=1.0, Medium=0.5, Low=0.2).  
2. Joins `population_data`, `infrastructure_data`, `investment_data`.  
3. Computes Civic Need Index for every location (details in Layer 5).  
4. Calls `generate_hotspot_insight(...)` per location.  
5. Upserts result into `hotspot_analysis` table.  
6. Returns list sorted descending by CNI.

### `insight_service.py` — `generate_hotspot_insight(...) → str`

Primary path — `_generate_deterministic_insight()`:  
Template-based narrative using severity description, infrastructure gap description, investment description, urgency tier label, and recommendation sentence.  
No external calls, no model weights, fully reproducible.

Optional path — `_call_external_llm()`:  
Called only if env var `EXTERNAL_LLM_API_KEY` is non-empty.  
Posts a structured prompt to `generativelanguage.googleapis.com` (Gemini 1.5 Flash endpoint).  
Falls back to deterministic on any exception or non-200 response.

---

## Layer 4 — MySQL Database

### Files
- `backend/database.py` — Engine + session factory  
- `backend/models.py` — SQLAlchemy ORM models  
- `data/population.csv`, `data/infrastructure.csv`, `data/investment.csv` — Seed data  
- `scripts/seed_data.py` — Idempotent seeder  

### Connection
```python
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:PASSWORD@localhost/civicintel")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
```
Charset: `utf8mb4` / collation `utf8mb4_unicode_ci` (set at database creation).

### Tables

**`citizen_requests`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | INT PK | Auto-increment |
| `request_text` | TEXT | Raw submission |
| `location` | VARCHAR(255) | Indexed |
| `latitude` | FLOAT | From `get_coordinates()` |
| `longitude` | FLOAT | From `get_coordinates()` |
| `language` | VARCHAR(50) | Indexed |
| `category` | VARCHAR(100) | Indexed |
| `severity` | VARCHAR(50) | Indexed |
| `affected_people` | INT | Default 0 |
| `status` | VARCHAR(50) | Default "Analyzed" |
| `detected_need` | VARCHAR(255) | Mapped project type |
| `created_at` | DATETIME | Indexed |

**`population_data`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | INT PK | |
| `location` | VARCHAR(255) | UNIQUE, indexed |
| `population` | INT | |

Seeded from `data/population.csv`. 8 Tamil Nadu cities; range 224,849 – 7,088,000.

**`infrastructure_data`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | INT PK | |
| `location` | VARCHAR(255) | Indexed |
| `category` | VARCHAR(100) | Indexed |
| `infrastructure_score` | FLOAT | 0–100 |
| `availability` | VARCHAR(50) | |
| `capacity` | VARCHAR(100) | |

Seeded from `data/infrastructure.csv`. 8 locations × 8 sectors = 64 rows.

**`investment_data`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | INT PK | |
| `location` | VARCHAR(255) | Indexed |
| `category` | VARCHAR(100) | Indexed |
| `investment_amount` | FLOAT | INR |
| `project_count` | INT | |
| `year` | INT | |

Seeded from `data/investment.csv`.

**`hotspot_analysis`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | INT PK | |
| `location` | VARCHAR(255) | UNIQUE, indexed |
| `civic_need_index` | FLOAT | 0–100 |
| `request_count` | INT | |
| `affected_people` | INT | |
| `severity_score` | FLOAT | |
| `infrastructure_gap` | FLOAT | |
| `investment_context` | FLOAT | |
| `dominant_category` | VARCHAR(100) | |
| `explanation` | TEXT | AI narrative |
| `calculated_at` | DATETIME | |

Written on every `GET /hotspots` call via upsert (update-if-exists, insert otherwise).

---

## Layer 5 — Civic Intelligence Engine

Implemented entirely inside `hotspot_service.py`.

### Civic Need Index Formula

```
CNI = clamp( I_req + I_pop + I_sev + I_inf − I_inv,  0.0,  100.0 )
```

**Component 1 — Request Intensity `I_req` ∈ [0, 25]**
```python
req_rate = (request_count / population) * 10_000
I_req    = min(25.0, (req_rate * 2.5) + min(12.0, request_count * 0.8))
# 0.0 when request_count == 0
```

**Component 2 — Affected Population Impact `I_pop` ∈ [0, 25]**
```python
pop_ratio  = affected_people / max(population, 1)
log_factor = math.log10(max(affected_people, 1)) * 3.0
I_pop      = min(25.0, (pop_ratio * 150.0) + log_factor)
# 0.0 when affected_people == 0
```

**Component 3 — Severity Score `I_sev` ∈ [0, 20]**
```python
# severity_sum uses CASE: High=1.0, Medium=0.5, Low=0.2
avg_sev = severity_sum / request_count
I_sev   = avg_sev * 20.0
# 5.0 (neutral baseline) when request_count == 0
```

**Component 4 — Infrastructure Deficit `I_inf` ∈ [0, 20]**
```python
avg_infra_score = mean(infrastructure_scores for location)  # default 50.0
infra_gap       = max(0.0, 100.0 - avg_infra_score)
I_inf           = (infra_gap / 100.0) * 20.0
```

**Component 5 — Investment Mitigation `I_inv` ∈ [0, 10]**
```python
inv_per_capita = total_investment / max(population, 1)
I_inv          = min(10.0, (inv_per_capita / 100.0) * 4.0)
```

### Hotspot Tier Classification

| Tier | CNI Range | Map Colour | Narrative Label |
|------|-----------|------------|-----------------|
| Tier 1 Priority Hotspot | ≥ 70.0 | 🔴 Red | Immediate cross-departmental intervention |
| Tier 2 Priority Need | 40.0 – 69.9 | 🟠 Amber | Targeted capital allocation advised |
| Monitoring Tier | < 40.0 | 🟢 Green | Standard maintenance sufficient |

### Comparative Analytics (`/analytics/comparison`)

For each of 8 sectors (`Water`, `Roads`, `Electricity`, `Healthcare`, `Sanitation`, `Waste Management`, `Education`, `Public Transport`):

- **`reported_need_score`** — `min(100, (category_request_count / total_requests) * 250)`
- **`infrastructure_score`** — average `infrastructure_score` from `infrastructure_data`
- **`investment_score`** — `min(100, (total_investment / 200_000_000) * 100)`

---

## Layer 6 — Policymaker Dashboard

### Files
- `frontend/dashboard.html` — UI structure  
- `frontend/js/dashboard.js` — Controller, KPIs, filters, modals  
- `frontend/js/map.js` — Leaflet.js integration  
- `frontend/js/charts.js` — Chart.js rendering  
- `frontend/js/api.js` — HTTP client  
- `frontend/css/style.css` — Stylesheet  

Served at `http://127.0.0.1:5500/dashboard.html` via `python -m http.server 5500`.

### KPI Summary Cards
Four counters populated from `GET /analytics/summary`:  
Total Citizen Reports · High Severity Reports · Reported Affected Citizens · Active Hotspots (CNI ≥ 60).

### Leaflet.js GIS Map (`map.js`)
- OpenStreetMap tile layer  
- `L.circleMarker` per hotspot; radius = `min(18, max(9, CNI / 4.5))`  
- Fill colour: Red (Tier 1) · Amber (Tier 2) · Green (Monitoring)  
- Popup on click: location name, tier badge, CNI, request count, affected people, dominant category, "Inspect Intelligence" button  
- `map.fitBounds()` auto-zooms to all markers  

### Chart.js Analytics (`charts.js`)
Five rendered charts, all destroyed and re-created on data refresh:

| Chart | Type | Data source |
|-------|------|-------------|
| Category distribution | Doughnut | `/analytics/categories` |
| Severity breakdown | Pie | `/analytics/summary` |
| Language distribution | Bar | `/analytics/languages` |
| Top locations | Horizontal bar | `/analytics/locations` (top 8) |
| Need vs Infra vs Investment | Grouped bar | `/analytics/comparison` |

### Search & Filter Panel
Query params sent to `GET /requests`: `search`, `category`, `severity`, `language`, `location`.  
Table re-renders on each change without page reload.

### Hotspot Ranked Table
Columns: rank, location, CNI badge, request count, affected people, dominant category, infra gap, Inspect button.  
"Inspect Intelligence" triggers the dossier modal for that location.

### Intelligence Dossier Modal
Opens on map pin click or table "Inspect" click.  
Displays: location, tier badge, CNI score, request count, affected people, dominant category, infrastructure gap, investment amount, sector breakdown doughnut, full AI narrative explanation.

---

## Data Flow — Citizen Request to Dashboard

```
[Citizen types text + location in citizen.html]
              │
              ▼
POST /requests  {request_text, location}
              │
              ▼
[Pydantic validates input]
              │
              ▼
[analyze_request_data(text, location)]
    ├─ detect_language(text)         → language
    ├─ detect_category(text)         → category
    ├─ detect_severity(text)         → severity
    ├─ extract_affected_people(text) → affected_people
    ├─ DEVELOPMENT_NEEDS[category]   → detected_need
    └─ get_coordinates(location)     → latitude, longitude
              │
              ▼
[INSERT into citizen_requests] → MySQL
              │
              ▼
[Return CitizenRequestOut JSON]
              │
              ▼
[citizen.js renders result card]


[Policymaker opens dashboard.html]
              │
              ▼
[dashboard.js: Promise.all — parallel API calls]
    ├─ GET /analytics/summary   → KPI counters
    ├─ GET /analytics/categories → doughnut chart
    ├─ GET /analytics/languages  → bar chart
    ├─ GET /analytics/locations  → horizontal bar chart
    ├─ GET /analytics/comparison → grouped bar chart
    └─ GET /hotspots
              │
              ▼
[GET /hotspots triggers calculate_hotspots(db)]
    ├─ SQL GROUP BY location (citizen_requests)
    ├─ JOIN population_data
    ├─ JOIN infrastructure_data  (avg score per location)
    ├─ JOIN investment_data      (total investment per location)
    ├─ Compute CNI per location
    ├─ generate_hotspot_insight() per location
    ├─ UPSERT hotspot_analysis
    └─ Return sorted list
              │
              ▼
[dashboard.js renders map pins + hotspot table]
[map.js places colour-coded Leaflet markers]
[charts.js renders all 5 Chart.js visualisations]
```

---

## Testing

```
tests/test_analysis.py    — Unit tests: language detection, category, severity, population extraction
tests/test_requests.py    — Integration: POST/GET /requests, multilingual Tamil submission, filters
tests/test_analytics.py   — Integration: all /analytics/* and /hotspots endpoints
tests/test_live.py        — Live HTTP: verifies backend :8000 and frontend :5500 are running
```

Run with:
```powershell
& .\backend\venv\Scripts\pytest.exe tests -v
```
**Result: 22 / 22 tests pass.**

---

## File Index (Project Root)

```
CivicIntel-AI/
├── backend/
│   ├── main.py                         FastAPI app, CORS, router mounting
│   ├── database.py                     SQLAlchemy engine + session factory
│   ├── models.py                       5 ORM models
│   ├── schemas.py                      Pydantic V2 request/response schemas
│   ├── requirements.txt                fastapi uvicorn pydantic sqlalchemy pymysql python-dotenv httpx pytest
│   ├── test_db.py                      Standalone MySQL connectivity check
│   ├── .env.example                    Template: DATABASE_URL, EXTERNAL_LLM_API_KEY
│   ├── .env                            Local secrets (git-ignored)
│   ├── routers/
│   │   ├── requests.py                 POST+GET /requests, GET /requests/{id}, POST /requests/{id}/analyze
│   │   ├── analytics.py                GET /analytics/summary|categories|languages|locations|comparison
│   │   └── hotspots.py                 GET /hotspots, GET /hotspots/{location}
│   └── services/
│       ├── language_service.py         Unicode script detector
│       ├── analysis_service.py         Category, severity, population, geocoding
│       ├── hotspot_service.py          CNI aggregation engine, DB upsert
│       └── insight_service.py          Deterministic narrative + optional Gemini hook
├── frontend/
│   ├── index.html                      Landing page
│   ├── citizen.html                    Citizen reporting portal
│   ├── dashboard.html                  Policymaker intelligence dashboard
│   ├── css/style.css                   Complete UI stylesheet
│   └── js/
│       ├── api.js                      Centralised fetch wrapper
│       ├── citizen.js                  Form handler + Web Speech API
│       ├── dashboard.js                Dashboard controller + modals
│       ├── charts.js                   Chart.js 5-chart suite
│       └── map.js                      Leaflet.js GIS map
├── data/
│   ├── population.csv                  8 cities, synthetic baselines
│   ├── infrastructure.csv              8 cities × 8 sectors, scores 0-100
│   └── investment.csv                  Capital investment per city/sector/year
├── scripts/
│   └── seed_data.py                    Idempotent CSV→MySQL seeder
├── tests/
│   ├── test_analysis.py
│   ├── test_requests.py
│   ├── test_analytics.py
│   └── test_live.py
├── architecture_diagram.svg            16:9 vector diagram (this document's companion)
├── ARCHITECTURE.md                     This file
└── README.md                           Full project documentation
```
