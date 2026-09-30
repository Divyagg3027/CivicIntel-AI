# CivicIntel AI

> **An AI-powered multilingual civic intelligence platform that transforms citizen requests into geographically aggregated development insights and identifies areas with higher unmet civic needs.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-4479A1.svg)](https://www.mysql.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-199900.svg)](https://leafletjs.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384.svg)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

---

## 1. Project Title

**CivicIntel AI**  
*Turning Citizen Voices into Development Intelligence*

---

## 2. One-Line Description

An AI-powered multilingual civic intelligence platform that transforms citizen requests into geographically aggregated development insights and identifies areas with higher unmet civic needs.

---

## 3. Problem Statement

Municipal corporations and public planning authorities manage vast urban and rural jurisdictions, receiving thousands of citizen grievances, petitions, and maintenance calls every month. However, standard grievance portals suffer from major systemic bottlenecks:

* **Unstructured and Fragmented Grievances:** Citizens express issues in conversational, informal text without standard categorization, making programmatic sorting unreliable.
* **Multilingual Communication Barriers:** In diverse states and metropolitan regions, citizens submit complaints in regional languages (Tamil, Hindi, Telugu, Malayalam, Kannada, etc.). Traditional portals often route non-English requests through manual translation queues, causing triage delays.
* **Isolated Ticketing Mentality:** Existing grievance systems treat citizen complaints as transactional, isolated tickets ("fix a pothole", "clear one drain"). They fail to aggregate individual reports to identify underlying systemic infrastructure failures.
* **Disconnection from Macro Baselines:** A high volume of complaints from an affluent locality with strong infrastructure is frequently prioritized over severe distress from an under-funded, high-density neighborhood simply because the former files more tickets. Individual requests are rarely correlated with local population density, existing municipal infrastructure coverage, or past capital investment allocations.
* **Prioritization Paralysis:** Policymakers lack transparent, data-grounded metrics to determine which municipal zones are critical development hotspots requiring immediate capital allocation versus areas that simply need routine maintenance.

---

## 4. Proposed Solution

**CivicIntel AI** re-engineers civic grievance management into an autonomous development intelligence system. Instead of treating complaints as isolated tickets, CivicIntel AI:

1. **Accepts Citizen Requests:** Ingests unstructured citizen grievances via a user-friendly public portal.
2. **Supports Multilingual Input:** Automatically detects and processes submissions in multiple Indian languages (Tamil, Hindi, Telugu, Malayalam, Kannada) and English without requiring manual translation.
3. **Extracts Structured Telemetry:** Leverages a local, zero-API-cost NLP engine to analyze civic category, severity level, affected population count, target location, and recommended development project type.
4. **Persists Data in MySQL:** Stores validated, indexed records in a relational MySQL database configured with `utf8mb4` encoding to preserve native regional scripts.
5. **Aggregates Civic Needs Geographically:** Groups individual requests by municipality, town, or ward to reveal localized distress patterns.
6. **Correlates with Macro Baselines:** Combines citizen request volume and severity with local demographic baselines (population counts), infrastructure coverage scores (0–100 across 8 core sectors), and historical capital investment data.
7. **Calculates the Civic Need Index (CNI):** Computes a mathematical indicator bounded between 0 and 100 that balances demand intensity, severity, infrastructure deficit, and capital investment mitigation.
8. **Identifies Tier 1 and Tier 2 Hotspots:** Automatically classifies geographical zones into actionable priority tiers (`Tier 1 Priority Hotspot`, `Tier 2 Priority Need`, and `Monitoring Tier`).
9. **Delivers a Policymaker Dashboard:** Visualizes geospatial clusters on an interactive OpenStreetMap GIS map, displays real-time analytical charts, provides multi-criteria filtering, and generates grounded analytical intelligence narratives.

---

## 5. Key Features

### Implemented in the Current Application:

* **Multilingual Citizen Input:** Accepts unstructured citizen inputs written in English, Tamil (தமிழ்), Hindi (हिन्दी), Telugu (తెలుగు), Malayalam (മലയാളം), or Kannada (ಕನ್ನಡ).
* **Text/Voice-Ready Citizen Interface:** Features an intuitive citizen reporting form equipped with quick-select location chips and browser-based voice dictation via the Web Speech API (allowing citizens to speak their concerns in supported browsers).
* **AI/NLP-Based Request Classification:** Built-in rule-based and script-analyzing NLP pipeline classifying complaints across 10 municipal categories (*Water, Roads, Electricity, Healthcare, Education, Sanitation, Waste Management, Public Transport, Housing, Other*) with zero external API dependencies.
* **Severity Analysis:** Evaluates urgency and critical risk keywords to classify grievances into *High*, *Medium*, or *Low* severity.
* **Affected Population Extraction:** Context-aware regex engine that extracts affected citizen numbers (*e.g., "500 people", "around 300 families", "500 மக்கள்"*) while intelligently filtering out ward numbers, bus routes, and calendar dates.
* **MySQL Persistence:** Relational database storage using SQLAlchemy ORM and PyMySQL, tracking requests, timestamps, geocoded coordinates, and analytical metadata.
* **Geographic Aggregation:** Real-time SQL grouping of grievances by location to compute cumulative request volume, total affected residents, and dominant civic stressors.
* **Civic Need Index (0–100):** A transparent, bounded mathematical metric synthesizing request rate per capita, affected population impact, average severity, baseline infrastructure gap, and capital investment relief.
* **Tier 1 & Tier 2 Hotspot Identification:** Automated classification of municipal zones into *Tier 1 Priority Hotspots* ($\ge 70$), *Tier 2 Priority Need Zones* ($40 - 69.9$), and *Monitoring Zones* ($< 40$).
* **Interactive Leaflet Map:** OpenStreetMap GIS geospatial visualization featuring color-coded circular hotspot clusters (Red for Tier 1, Amber for Tier 2, Green for Monitoring) with dynamic radiuses scaled by need intensity.
* **Real-Time Dashboard Charts:** Rich Chart.js visualizations including:
  * Category distribution doughnut chart
  * Severity proportion pie chart
  * Language distribution bar chart
  * Top locations horizontal bar chart
  * Multi-metric comparative bar chart (Reported Need Score vs Infrastructure Baseline vs Capital Investment)
* **Search and Filtering:** Live multi-criteria filtering across search keywords, civic categories, severity tiers, detected languages, and geographical locations.
* **AI-Generated Grounded Explanations:** Automated generation of concise, factually grounded intelligence summaries for every hotspot (with built-in support for optional Google Gemini 1.5 Flash connectivity when an API key is provided).

### Distinguishing Implemented vs. Future Scope:
> **Note on Voice Processing:** The current application implements browser-based speech recognition through the client-side Web Speech API (`webkitSpeechRecognition` / `SpeechRecognition`) for immediate voice-to-text dictation into the form. Server-side audio recording ingestion, native `.wav`/`.mp3` upload processing, and advanced server-side speech models (e.g., Whisper) are designated as **Future Scope**.

---

## 6. System Architecture

### End-to-End Information Flow:

```text
               Citizen Request (Web / Voice Dictation)
                                  ↓
                       Multilingual NLP Engine
               (Script Detection & Keyword Scoring)
                                  ↓
                       Structured Civic Request
          (Category, Severity, Affected Count, Coordinates)
                                  ↓
                        MySQL Database Storage
                   (`citizen_requests` Table)
                                  ↓
                        Geographic Aggregation
                  (Group by Location / Municipality)
                                  ↓
          Cross-Domain Correlation with Macro Datasets
          - Population Baseline (`population_data`)
          - Infrastructure Readiness Scores (`infrastructure_data`)
          - Capital Investment Records (`investment_data`)
                                  ↓
                   Civic Need Index (CNI) Engine
          [0–100 Score combining Demand, Severity, Deficit & Relief]
                                  ↓
                          Hotspot Detection
          [Tier 1 (>=70) | Tier 2 (40-69.9) | Monitoring (<40)]
                                  ↓
                        Policymaker Dashboard
          [Leaflet GIS Map + Chart.js Analytics + AI Dossier]
```

### Architectural Tiers:

1. **Presentation Layer (Frontend):**
   * Responsive HTML5/CSS3 interface styled with a municipal blue design system.
   * Citizen Reporting Portal (`citizen.html`) with instant structured feedback card.
   * Executive Policymaker Dashboard (`dashboard.html`) displaying KPI counters, GIS maps, comparative charts, filterable tables, and modal intelligence dossiers.
   * Landing Page (`index.html`) illustrating the methodology and civic workflow.
2. **API & Orchestration Layer (Backend):**
   * Built on **FastAPI** with asynchronous request handling and Pydantic schemas.
   * REST routers partitioned into `requests.py`, `analytics.py`, and `hotspots.py`.
   * Cross-Origin Resource Sharing (CORS) middleware enabling seamless frontend communication.
3. **Core Services Layer:**
   * `language_service.py`: Unicode script range detector identifying language without external network calls.
   * `analysis_service.py`: Weighted multilingual lexicon matching, severity analyzer, and context-aware regex numbers extraction.
   * `hotspot_service.py`: Multi-source aggregator and mathematical Civic Need Index calculator.
   * `insight_service.py`: Grounded analytical narrative generator (deterministic rule-based by default, with optional external Gemini LLM hook).
4. **Data Persistence Layer:**
   * **MySQL 8.0+** relational database managed via **SQLAlchemy 2.0** ORM.
   * Normalized schemas with indexing on locations, categories, severities, and timestamps.
   * Pre-ping connection pooling ensuring persistent, auto-reconnecting sessions.

---

## 7. Technology Stack

CivicIntel AI utilizes a focused, robust, and verified modern open-source technology stack:

| Layer | Technology | Version | Purpose in CivicIntel AI |
|---|---|---|---|
| **Backend Framework** | **FastAPI** | `>= 0.110.0` | Asynchronous REST API, routing, request validation, and OpenAPI documentation |
| **ASGI Server** | **Uvicorn** | `>= 0.28.0` | High-performance ASGI production web server |
| **Data Validation** | **Pydantic V2** | `>= 2.6.0` | Request and response data parsing, schema enforcement, and type safety |
| **ORM / Database Layer** | **SQLAlchemy** | `>= 2.0.28` | Object-Relational Mapping, query compilation, and session lifecycle management |
| **Database Driver** | **PyMySQL** | `>= 1.1.0` | Pure-Python MySQL database client |
| **Configuration** | **python-dotenv** | `>= 1.0.1` | Environment variable management from `.env` file |
| **HTTP Client** | **HTTPX** | `>= 0.27.0` | Asynchronous HTTP client for optional external Gemini LLM integration and testing |
| **Database Engine** | **MySQL Server** | `>= 8.0` | Primary relational datastore configured with `utf8mb4` charset |
| **GIS Mapping** | **Leaflet.js** | `1.9.4` | Interactive mobile-friendly GIS mapping with custom circle markers and popups |
| **Map Cartography** | **OpenStreetMap** | Standard Tiles | Free, open-access tile layer for geographic visualization |
| **Data Visualization** | **Chart.js** | `4.4.1` | Responsive charts (Doughnut, Bar, Horizontal Bar, Pie, Grouped Comparison) |
| **Client-side Speech** | **Web Speech API** | Native Browser | Client-side voice dictation in supported browsers (Chrome, Edge) |
| **Frontend Foundation** | **HTML5 / CSS3 / Vanilla JS** | Modern Standards | Lightweight, framework-free, highly responsive user interface |
| **Testing Suite** | **Pytest** | `>= 8.0.0` | Comprehensive unit, API integration, and live server testing suite |

---

## 8. Project Structure

```text
CivicIntel-AI/
├── backend/
│   ├── main.py                  # FastAPI application entrypoint, CORS & router mounting
│   ├── database.py              # SQLAlchemy engine, session maker & declarative Base
│   ├── models.py                # Database models (CitizenRequest, PopulationData, InfrastructureData, etc.)
│   ├── schemas.py               # Pydantic schemas for API validation & serializing responses
│   ├── requirements.txt         # Backend Python dependencies
│   ├── test_db.py               # Standalone script to verify MySQL connectivity
│   ├── .env.example             # Template configuration file for environment variables
│   ├── .env                     # Local environment configuration (ignored by git)
│   │
│   ├── routers/
│   │   ├── requests.py          # Routes for submitting, retrieving, filtering, and re-analyzing requests
│   │   ├── analytics.py         # Routes for KPI summaries, category/language/location statistics & comparisons
│   │   └── hotspots.py          # Routes for hotspot listings, rankings, and deep-dive dossiers
│   │
│   └── services/
│       ├── analysis_service.py  # Core NLP engine: category scoring, severity detection, population extraction
│       ├── language_service.py  # Zero-dependency language detection via Unicode script code points
│       ├── hotspot_service.py   # Civic Need Index (CNI) aggregation engine & database upserts
│       └── insight_service.py   # Analytical narrative generator (deterministic rule-based + optional Gemini LLM)
│
├── frontend/
│   ├── index.html               # Platform landing page & interactive pipeline overview
│   ├── citizen.html             # Citizen reporting portal (multilingual text input + voice dictation)
│   ├── dashboard.html           # Policymaker intelligence dashboard with Leaflet GIS map & charts
│   ├── script.js                # Shared frontend utilities
│   ├── style.css                # Base stylesheet
│   │
│   ├── css/
│   │   └── style.css            # Comprehensive municipal UI theme, responsive grid & card styles
│   │
│   └── js/
│       ├── api.js               # Centralized HTTP API client for backend communication
│       ├── citizen.js           # Form handling, validation & Web Speech API dictation logic
│       ├── dashboard.js         # Dashboard controller, KPI synchronization, filters & modal handlers
│       ├── charts.js            # Chart.js visualization configurations and rendering functions
│       └── map.js               # Leaflet.js interactive map module, pin styling & popup logic
│
├── data/
│   ├── population.csv           # Baseline population datasets for demonstration cities
│   ├── infrastructure.csv       # Baseline infrastructure readiness scores (0-100) across 8 civic sectors
│   └── investment.csv           # Baseline municipal capital allocation and project counts
│
├── scripts/
│   └── seed_data.py             # Idempotent database seeding script for demo data & sample requests
│
├── tests/
│   ├── test_analysis.py         # Unit tests for NLP engine, script detection & regex parsing
│   ├── test_requests.py         # Integration tests for request ingestion, validation & filtering
│   ├── test_analytics.py        # Integration tests for analytics KPIs, comparisons & hotspots
│   └── test_live.py             # Live HTTP server verification test (backend :8000 & frontend :5500)
│
├── .gitignore                   # Git exclusion rules (.env, venv, caches, logs)
└── README.md                    # Project documentation
```

---

## 9. Installation and Setup

Follow these beginner-friendly, step-by-step instructions to set up and run CivicIntel AI locally.

### Prerequisites

* **Python 3.10+** (Tested on Python 3.10 – 3.14)
* **MySQL Server 8.0+** (running locally on port `3306`)
* **Git** installed on your system
* A modern web browser (Google Chrome or Microsoft Edge recommended for voice dictation support)

---

### Step 1: Clone the Repository & Navigate to Project

```bash
git clone https://github.com/YourOrg/CivicIntel-AI.git
cd CivicIntel-AI
```

---

### Step 2: Python Environment Setup

Create and activate an isolated Python virtual environment:

**On Windows (PowerShell):**
```powershell
python -m venv backend\venv
.\backend\venv\Scripts\activate
```

**On Linux / macOS:**
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
```

---

### Step 3: Install Backend Dependencies

With the virtual environment activated, install all required dependencies:

```bash
pip install -r backend/requirements.txt
```

---

### Step 4: MySQL Database Setup

1. Start your local MySQL server service if it is not already running.
2. Open your MySQL client (Command Line, MySQL Workbench, or phpMyAdmin) and create the database with UTF-8 support:

```sql
CREATE DATABASE IF NOT EXISTS civicintel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

### Step 5: Configure Environment Variables

Create a `.env` file inside the `backend/` directory by copying the provided `.env.example`:

**On Windows (PowerShell):**
```powershell
Copy-Item backend\.env.example backend\.env
```

**On Linux / macOS:**
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your actual MySQL credentials:

```env
# Database Connection String
# Format: mysql+pymysql://<USERNAME>:<PASSWORD>@localhost:3306/civicintel
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/civicintel

# Optional External AI/LLM Integration
# If left empty, CivicIntel AI operates autonomously using high-accuracy local rule-based NLP
EXTERNAL_LLM_API_KEY=
EXTERNAL_LLM_PROVIDER=
```

Verify your database connectivity using the test script:
```bash
python backend/test_db.py
```
*(Should output: `✅ MySQL connection successful!`)*

---

### Step 6: Seed Demonstration Datasets

Populate the database with baseline demographic counts, sector infrastructure scores, capital investments, and representative multilingual citizen reports:

```bash
python scripts/seed_data.py
```

---

### Step 7: Start the FastAPI Backend

Run the FastAPI backend server using Uvicorn on port `8000`:

```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

* **API Base URL:** `http://127.0.0.1:8000`
* **Health Check:** `http://127.0.0.1:8000/health`
* **Interactive Swagger UI:** `http://127.0.0.1:8000/docs`
* **Alternative ReDoc UI:** `http://127.0.0.1:8000/redoc`

---

### Step 8: Start the Frontend Application

Open a **new terminal window**, navigate to the `frontend/` folder, and serve it via Python's built-in HTTP server on port `5500`:

```bash
cd frontend
python -m http.server 5500
```

---

### Step 9: Open the Application in Your Browser

Open your web browser and access the application pages:

* **Landing Page:** [http://127.0.0.1:5500/index.html](http://127.0.0.1:5500/index.html)
* **Citizen Reporting Portal:** [http://127.0.0.1:5500/citizen.html](http://127.0.0.1:5500/citizen.html)
* **Policymaker Intelligence Dashboard:** [http://127.0.0.1:5500/dashboard.html](http://127.0.0.1:5500/dashboard.html)

---

### Running Automated Tests

To execute the test suite across unit and integration checks:

```powershell
& .\backend\venv\Scripts\pytest.exe tests -v
```
*(All 22 test cases will run and pass).*

---

## 10. Database Architecture

CivicIntel AI utilizes **MySQL 8.0+** with the `utf8mb4` character set and `utf8mb4_unicode_ci` collation. This configuration ensures native storage and searching of regional South Asian scripts (Tamil, Devanagari/Hindi, Telugu, Kannada, Malayalam).

### Main Purpose of Storing Citizen Requests:

* **Auditability & Traceability:** Provides a permanent, unalterable historical log of community issues reported across time.
* **Geospatial Aggregation:** Enables high-speed SQL grouping and window operations across municipalities, wards, and GPS coordinates.
* **Time-Series Intelligence:** Allows urban planners to track whether community distress in a specific area is escalating, persisting, or declining following municipal intervention.
* **Algorithmic Input:** Feeds live count, severity, and population parameters directly into the Civic Need Index computation.

### Schema Overview:

```
+---------------------------------------------------------------------------------------------------+
|                                        MYSQL DATABASE SCHEMA                                      |
+---------------------------------------------------------------------------------------------------+
|  1. citizen_requests      | Ingested grievances, NLP category, severity, affected count, coords   |
|  2. population_data       | Baseline municipality census populations (demographic normalizer)     |
|  3. infrastructure_data   | Sector readiness scores (0-100), availability & capacity metrics      |
|  4. investment_data       | Past public capital expenditure amounts & project counts per sector   |
|  5. hotspot_analysis      | Cached Civic Need Index, rankings, dominant categories & explanations |
+---------------------------------------------------------------------------------------------------+
```

#### Detailed Table Specifications:

1. **`citizen_requests`**
   * `id` (`INT`, Primary Key, Auto-increment)
   * `request_text` (`TEXT`, Nullable: No) — Original raw submission.
   * `location` (`VARCHAR(255)`, Indexed) — City, town, or ward name.
   * `latitude` / `longitude` (`FLOAT`) — Resolved geographic coordinates.
   * `language` (`VARCHAR(50)`, Indexed) — Detected language (*English, Tamil, Hindi, etc.*).
   * `category` (`VARCHAR(100)`, Indexed) — Classified civic category (*Water, Roads, etc.*).
   * `severity` (`VARCHAR(50)`, Indexed) — Urgency level (*High, Medium, Low*).
   * `affected_people` (`INT`) — Contextually extracted resident count.
   * `status` (`VARCHAR(50)`) — Processing status (default: `"Analyzed"`).
   * `detected_need` (`VARCHAR(255)`) — Actionable municipal project recommendation.
   * `created_at` (`DATETIME`, Indexed) — Submission timestamp.

2. **`population_data`**
   * `id` (`INT`, Primary Key)
   * `location` (`VARCHAR(255)`, Unique, Indexed)
   * `population` (`INT`, Nullable: No) — Baseline urban population.

3. **`infrastructure_data`**
   * `id` (`INT`, Primary Key)
   * `location` (`VARCHAR(255)`, Indexed)
   * `category` (`VARCHAR(100)`, Indexed) — Sector name.
   * `infrastructure_score` (`FLOAT`) — Readiness score ($0.0 - 100.0$).
   * `availability` (`VARCHAR(50)`) — Status (*High, Moderate, Limited, Low*).
   * `capacity` (`VARCHAR(100)`) — Capacity load metric.

4. **`investment_data`**
   * `id` (`INT`, Primary Key)
   * `location` (`VARCHAR(255)`, Indexed)
   * `category` (`VARCHAR(100)`, Indexed)
   * `investment_amount` (`FLOAT`) — Capital budget allocated in INR.
   * `project_count` (`INT`) — Count of sanctioned public works.
   * `year` (`INT`) — Fiscal budget year.

5. **`hotspot_analysis`**
   * `id` (`INT`, Primary Key)
   * `location` (`VARCHAR(255)`, Unique, Indexed)
   * `civic_need_index` (`FLOAT`) — Computed CNI score ($0.0 - 100.0$).
   * `request_count` (`INT`) — Aggregated complaint volume.
   * `affected_people` (`INT`) — Cumulative affected cohort.
   * `severity_score` (`FLOAT`) — Calculated severity weight component.
   * `infrastructure_gap` (`FLOAT`) — Baseline infrastructure deficit ($100 - \text{Score}$).
   * `investment_context` (`FLOAT`) — Total recorded investment.
   * `dominant_category` (`VARCHAR(100)`) — Primary civic stressor.
   * `explanation` (`TEXT`) — Generated intelligence narrative.
   * `calculated_at` (`DATETIME`) — Index computation timestamp.

---

## 11. Backend API Reference

All backend endpoints are prefixed by their respective resource routers and can be interactively explored via Swagger UI at `http://127.0.0.1:8000/docs`.

### System & Health Endpoints

| HTTP Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root service metadata, platform tagline, version, and documentation links. |
| `GET` | `/health` | System health check verifying application responsiveness and operational state. |

### Citizen Request Endpoints (`/requests`)

| HTTP Method | Endpoint | Description |
|---|---|---|
| `POST` | `/requests` | **Ingest Request:** Accepts unstructured problem text and location, runs real-time multilingual NLP classification (language, category, severity, affected count, coordinates), stores record in MySQL, and returns structured intelligence. |
| `GET` | `/requests` | **Filter Requests:** Retrieves stored citizen requests with optional query parameters: `search` (text search), `category`, `severity`, `language`, `location`, `status`, `limit`, and `offset`. |
| `GET` | `/requests/{request_id}` | **Single Request Profile:** Fetches the full structured record and classification details for a specific request ID. |
| `POST` | `/requests/{request_id}/analyze` | **Re-analyze Request:** Re-runs the central NLP and classification pipeline on an existing request record and updates the database. |

### Civic Analytics Endpoints (`/analytics`)

| HTTP Method | Endpoint | Description |
|---|---|---|
| `GET` | `/analytics/summary` | Returns high-level summary KPIs derived from live database records: total requests, high/medium/low severity counts, aggregate affected population, and active hotspot count ($\text{CNI} \ge 60$). |
| `GET` | `/analytics/categories` | Returns request counts and relative percentages grouped across all civic categories. |
| `GET` | `/analytics/languages` | Returns request counts and percentages broken down by detected language. |
| `GET` | `/analytics/locations` | Returns aggregated request volumes, cumulative affected population, and dominant category grouped by location. |
| `GET` | `/analytics/comparison` | **Comparative Intelligence:** Returns sector-by-sector comparative metrics contrasting Reported Need Score ($0-100$) vs Baseline Infrastructure Readiness Score ($0-100$) vs Public Capital Investment Score ($0-100$). |

### Hotspot Intelligence Endpoints (`/hotspots`)

| HTTP Method | Endpoint | Description |
|---|---|---|
| `GET` | `/hotspots` | **Ranked Hotspots:** Triggers the multi-source aggregation engine, calculates the Civic Need Index ($0-100$) for every evaluated location, updates the `hotspot_analysis` table, and returns ranked hotspots sorted descending by need score. |
| `GET` | `/hotspots/{location}` | **Location Dossier:** Returns the complete intelligence profile, CNI breakdown, dominant civic stressor, and AI-grounded narrative explanation for a specific location. |

---

## 12. Civic Need Index (CNI) Methodology

The **Civic Need Index (CNI)** is a deterministic, transparent analytical indicator designed to identify municipal areas where citizen distress coincides with acute physical infrastructure deficits and historical under-investment.

Unlike black-box models, CNI is fully auditable, mathematically bounded between **$0.0$** and **$100.0$**, and directly grounded in empirical municipal variables.

### Complete Formula

$$\text{CNI} = \text{clamp}\Big(I_{req} + I_{pop} + I_{sev} + I_{inf} - I_{inv},\; 0.0,\; 100.0\Big)$$

### Mathematical Components:

#### 1. Request Intensity Component ($I_{req} \in [0, 25]$)
Measures the volume of incoming citizen reports normalized against the local population baseline to prevent large cities from overwhelming smaller towns:
$$\text{req\_rate} = \left(\frac{\text{request\_count}}{\text{population}}\right) \times 10{,}000$$
$$I_{req} = \min\Big(25.0,\; (\text{req\_rate} \times 2.5) + \min(12.0,\; \text{request\_count} \times 0.8)\Big)$$
*(If $\text{request\_count} = 0$, $I_{req} = 0.0$)*

#### 2. Affected Population Impact Component ($I_{pop} \in [0, 25]$)
Gauges the cumulative human scale of the reported problem, combining linear population ratio with a logarithmic dampener for large community distress:
$$\text{pop\_ratio} = \frac{\text{affected\_people}}{\max(\text{population},\; 1)}$$
$$\text{log\_factor} = \log_{10}\big(\max(\text{affected\_people},\; 1)\big) \times 3.0$$
$$I_{pop} = \min\Big(25.0,\; (\text{pop\_ratio} \times 150.0) + \text{log\_factor}\Big)$$
*(If $\text{affected\_people} = 0$, $I_{pop} = 0.0$)*

#### 3. Severity Score Component ($I_{sev} \in [0, 20]$)
Calculates the weighted average hazard level of grievances filed for that location:
$$\text{severity\_sum} = \sum_{\text{requests}} \begin{cases} 1.0 & \text{if High Severity} \\ 0.5 & \text{if Medium Severity} \\ 0.2 & \text{if Low Severity} \end{cases}$$
$$\text{avg\_sev} = \frac{\text{severity\_sum}}{\text{request\_count}}$$
$$I_{sev} = \text{avg\_sev} \times 20.0$$
*(If $\text{request\_count} = 0$, $I_{sev} = 5.0$ as a neutral baseline)*

#### 4. Infrastructure Baseline Deficit Component ($I_{inf} \in [0, 20]$)
Reflects the gap in existing municipal physical infrastructure (water networks, roads, sanitation, etc.):
$$\text{infra\_gap} = \max\Big(0.0,\; 100.0 - \text{avg\_infrastructure\_score}\Big)$$
$$I_{inf} = \left(\frac{\text{infra\_gap}}{100.0}\right) \times 20.0$$

#### 5. Investment Mitigation Discount ($I_{inv} \in [0, 10]$)
Accounts for recent public capital expenditures already allocated to that location. High recent per-capita investment discounts immediate unaddressed urgency:
$$\text{inv\_per\_capita} = \frac{\text{total\_investment}}{\max(\text{population},\; 1)}$$
$$I_{inv} = \min\Big(10.0,\; \left(\frac{\text{inv\_per\_capita}}{100.0}\right) \times 4.0\Big)$$

---

### Hotspot Priority Tier Classification:

| Priority Tier | CNI Range | Map Indicator | Operational Meaning & Recommended Policy Action |
|---|---|---|---|
| **Tier 1 Priority Hotspot** | **$70.0 - 100.0$** | 🔴 **Red Pin** | **Critical Urgency:** High citizen distress coinciding with acute infrastructure deficits and low recent investment. Immediate cross-departmental capital and operational intervention recommended. |
| **Tier 2 Priority Need** | **$40.0 - 69.9$** | 🟠 **Amber Pin** | **Moderate-to-High Need:** Recognizable infrastructure capacity constraints or recurring localized grievances. Targeted capital allocation advised in upcoming budget cycle. |
| **Monitoring Tier** | **$0.0 - 39.9$** | 🟢 **Green Pin** | **Stable Baseline:** Adequate physical infrastructure with predominantly routine or localized issues. Ongoing standard municipal maintenance and periodic surveillance sufficient. |

---

## 13. End-to-End Demonstration Workflow

```text
Step 1: Citizen Submission
   │  Citizen opens `citizen.html`, selects location "Nagercoil", and types:
   │  "குடிநீர் விநியோகம் முற்றிலும் இல்லை. சுமார் 500 மக்கள் பாதிக்கப்பட்டுள்ளனர்."
   │  (Or clicks 🎙️ to dictate via Web Speech API)
   ▼
Step 2: Real-Time AI/NLP Extraction
   │  FastAPI `/requests` endpoint executes central analysis:
   │  - Language: Tamil
   │  - Category: Water
   │  - Severity: High ("முற்றிலும் இல்லை")
   │  - Affected Population: 500
   │  - Recommended Need: Drinking Water Infrastructure
   ▼
Step 3: Relational Persistence
   │  Validated record is stored in MySQL `citizen_requests` table with timestamp and coordinates.
   │  Citizen sees immediate structured confirmation on the portal.
   ▼
Step 4: Policymaker Opens Dashboard
   │  Administrator loads `dashboard.html`.
   │  Frontend parallelly queries `/analytics/summary`, `/analytics/categories`, and `/hotspots`.
   ▼
Step 5: Geospatial Aggregation & CNI Computation
   │  `hotspot_service.py` aggregates all requests for Nagercoil.
   │  Cross-references population (224,849), infrastructure baseline (38.5 / 100), and capital investment.
   │  Computes CNI = 72.4 / 100.
   │  Classifies Nagercoil as a **Tier 1 Priority Hotspot**.
   ▼
Step 6: Map & Chart Visualization
   │  Leaflet map renders a pulsating Red marker on Nagercoil.
   │  Comparative chart displays high Citizen Need Score against low Infrastructure Score.
   ▼
Step 7: Deep-Dive Intelligence Inspection
   │  Administrator clicks "Inspect Intelligence".
   │  Modal opens displaying grounded explanation:
   │  "Nagercoil is identified as a Priority Tier 1 Hotspot with a Civic Need Index of 72.4/100...
   │   The primary civic stressor is Water... Immediate cross-departmental intervention recommended."
```

---

## 14. Future Scope

The following features represent viable extensions and production roadmap enhancements that are **NOT** currently implemented in the prototype:

1. **Production Government Data Connectors:** Integration with official state municipal data exchanges, national open data portals (e.g., data.gov.in), and real-time Census/NIC APIs.
2. **Omnichannel Messaging Bot (WhatsApp / Telegram / SMS):** Two-way chatbot integration via WhatsApp Business API or Twilio, enabling citizens in low-bandwidth regions to submit grievances and receive automated status updates via chat.
3. **Server-Side Audio & Speech Pipeline:** Dedicated server-side audio ingestion capable of accepting raw voice note recordings (`.ogg`, `.mp3`), performing noise suppression, and executing regional speech-to-text via fine-tuned Whisper models.
4. **Expanded Dialect & Regional Language Support:** Expansion beyond the current 6 languages to support all 22 official scheduled languages of India, including regional dialectal slang and code-mixed transliteration (e.g., "Tanglish", "Hinglish").
5. **Real-Time IoT & SCADA Telemetry:** Automated ingestion of physical telemetry streams (smart water flow meters, electrical grid transformer sensors, and ultrasonic smart waste bin monitors) to validate citizen grievances against real sensor readings.
6. **Satellite & Geospatial GIS Layers:** Overlaying high-resolution satellite imagery (ISRO Bhuvan / Copernicus Sentinel) for automated pothole detection, flood inundation modeling, and urban vegetation loss analysis.
7. **Predictive Civic Planning & Budget Allocation:** Machine learning models that forecast seasonal infrastructure failure risks (e.g., monsoon drainage overflow) and automatically generate optimized capital expenditure allocations for municipal budget committees.

---

## 15. Security and Best Practices

* **Environment Variable Isolation:** Database credentials and third-party API keys are strictly configured through `backend/.env`. Sensitive files are excluded from Git tracking via `.gitignore`. Never commit credentials to version control.
* **SQL Injection Prevention:** All database operations utilize SQLAlchemy ORM with parameterized queries, eliminating SQL injection vulnerabilities.
* **Input Validation & Sanitization:** Incoming payloads are strictly validated by Pydantic schemas (`schemas.py`), enforcing string length bounds and proper data typing.
* **CORS Hardening for Production:** The prototype enables `allow_origins=["*"]` to simplify local dual-port evaluation (`8000` and `5500`). For production deployment, CORS must be restricted to verified municipal domain origins.
* **Authentication & Role-Based Access Control (RBAC):** In an enterprise deployment, administrative endpoints (`/analytics/*`, `/hotspots/*`) should be secured behind OAuth2 / JWT authentication, reserving citizen submission routes for public access.

---

## 16. Hackathon Innovation Summary

**CivicIntel AI** transforms how municipal administrations perceive citizen complaints. 

By shifting from a **reactive, isolated ticketing mindset** to an **autonomous, geographically aggregated intelligence model**, CivicIntel AI bridges the gap between grassroots citizen grievances and strategic public development budgeting. It empowers citizens to voice their concerns in their native language—via text or voice dictation—while providing policymakers with an explainable, data-backed compass to direct public capital where human need and infrastructure deficits are greatest.

---

*CivicIntel AI &bull; Turning Citizen Voices into Development Intelligence*
