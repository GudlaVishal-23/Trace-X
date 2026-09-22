# TRACE-X | City-Wide AI Vehicle Intelligence & Traffic Analytics Engine

<div align="center">

![TRACE-X Banner](https://img.shields.io/badge/TRACE--X-SIH26127-FF6D00?style=for-the-badge&logo=shield&logoColor=white)
![Status](https://img.shields.io/badge/STATUS-PRODUCTION--READY%20PROTOTYPE-00E475?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostGIS](https://img.shields.io/badge/PostGIS-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=leaflet&logoColor=white)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)

**An enterprise-grade, spatiotemporal multi-camera ANPR tracking and macro traffic analytics platform built for Smart India Hackathon 2026 (Problem Statement: SIH26127).**

[Live Dashboard](http://127.0.0.1:8000) • [Swagger API Docs](http://127.0.0.1:8000/docs) • [System Specifications](./docs/) • [Changelog](./CHANGELOG.md)

</div>

---

## 🚦 1. Executive Summary & Core Philosophy

**TRACE-X** transforms disparate, city-wide CCTV and ANPR camera feeds into structured, actionable, and legally defensible vehicle intelligence. Designed specifically to resolve urban security blind spots and multi-camera handover gaps, TRACE-X delivers:

1. **High-Accuracy ANPR/OCR Ingestion**: Resilient edge-detection for real-world Indian road conditions (blur, low light, heavy rainfall, high-angle skews, dirt/obstruction, and standard/non-standard HSRP plates).
2. **Single-Plate Spatiotemporal Trajectory Solver**: Graph-based journey reconstruction that correlates vehicle observations across distributed cameras, enforces physical feasibility guards ($v \le 160\text{ km/h}$), bridges blind camera zones, and classifies confidence into `CONFIRMED`, `PROBABLE`, and `CAMERA_GAP`.
3. **Macro Urban Traffic Analytics & GIS Heatmaps**: Real-time arterial flow analysis, spatial density heatmaps, corridor transit velocities, Deep CNN vehicle modal distribution (2-wheelers, cars, commercial, autos), and Origin-Destination (OD) commute matrices.
4. **Active Intercept & Watchlist Dispatch**: Real-time stolen vehicle alerts, geofence violations, automated PCR patrol unit dispatch, and cryptographic SHA-256 forensic dossier generation.

```
                    TRACE-X OPERATIONAL PIPELINE
  ┌─────────────┐     ┌────────────────┐     ┌───────────────────┐     ┌────────────────┐
  │     SEE     │ ──> │    CONNECT     │ ──> │    UNDERSTAND     │ ──> │      ACT       │
  │ Robust ANPR │     │ Spatiotemporal │     │ City-Wide Traffic │     │ PCR Dispatch & │
  │ & Perception│     │ Trajectory ReID│     │ Flow & Heatmaps   │     │ Forensic Report│
  └─────────────┘     └────────────────┘     └───────────────────┘     └────────────────┘
```

---

## 📸 2. System Architecture

```
                                  TRACE-X ARCHITECTURE
 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │                                EDGE / INGESTION LAYER                                    │
 │  RTSP Feeds / Pre-recorded Streams ──> OpenCV Frame Grabber ──> YOLOv8 Vehicle & Plate  │
 │  PaddleOCR / CRNN Text Recognition ──> OSNet Re-ID Embeddings (512-d)                   │
 └───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                             │ JSON Event Payloads
                                             ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │                                BACKEND & ANALYTICS CORE                                  │
 │  ┌────────────────────────────────────────────────────────────────────────────────────┐ │
 │  │ FastAPI Asynchronous REST Engine (Python 3.10+)                                    │ │
 │  │  • /api/cameras     • /api/events      • /api/vehicles/{plate}/trajectory          │ │
 │  │  • /api/traffic     • /api/alerts      • /api/traffic/heatmap                      │ │
 │  └──────────────────────────────────┬─────────────────────────────────────────────────┘ │
 │                                     ▼                                                   │
 │  ┌───────────────────────────┐  ┌───────────────────────────┐  ┌──────────────────────┐ │
 │  │ Trajectory Graph Solver   │  │ Macro Traffic Engine      │  │ Watchlist & Security │ │
 │  │ - Physical Speed Guard    │  │ - 11 Spatial Heat Nodes   │  │ - Hotlist Matching   │ │
 │  │   (<160 km/h)             │  │ - 5 Arterial Corridors    │  │ - PCR Unit Dispatch  │ │
 │  │ - Multi-Camera Handover   │  │ - Origin-Destination (OD) │  │ - SHA-256 Forensic   │ │
 │  │ - Blind Gap Interpolation │  │ - Modal Split Statistics  │  │   Dossier Chain      │ │
 │  └───────────────────────────┘  └───────────────────────────┘  └──────────────────────┘ │
 └───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
 ┌──────────────────────────────────────────┐  ┌──────────────────────────────────────────┐
 │         DATA & PERSISTENCE LAYER         │  │         TACTICAL COMMAND CENTER          │
 │  • PostgreSQL 16 + PostGIS Spatial DB    │  │  • Stitch AI-Inspired Dark HUD Console   │
 │  • SQLite Spatial Fallback Engine        │  │  • Traffic Signal Theme (Orange/White/Grn│
 │  • Redis 7 In-Memory Hot Cache           │  │  • Daylight Leaflet Basemap Switcher     │
 │  • Local Metadata & Snapshot Store       │  │  • Authentic Indian HSRP Plate Renderer  │
 └──────────────────────────────────────────┘  └──────────────────────────────────────────┘
```

---

## ⚡ 3. Key Capabilities & Feature Matrix

| Module | Features & Capabilities | Status |
| :--- | :--- | :--- |
| **Live City Map** | Real-time Leaflet GIS canvas, 8 strategic Hyderabad cameras, pulsing radar halos, live detection stream (12+ events/sec), Daylight Basemap Switcher (`Daylight OSM`, `Carto Voyager`, `World Street`). | ✅ Production |
| **Trajectory Tracking** | Spatiotemporal graph solver, physical velocity guard ($v \le 160\text{ km/h}$), camera gap interpolation, corridor polylines, 4 KPI metric cards, confidence scoring (`CONFIRMED`, `PROBABLE`, `CAMERA_GAP`). | ✅ Production |
| **HSRP Generator** | Authentic Indian High Security Registration Plate rendering with blue `IND` wedge, Ashoka Chakra emblem, and yellow (commercial) / white (private) variants. | ✅ Production |
| **Traffic Analytics** | Macro KPIs (248,910+ vehicles, 34.8 km/h city avg), Peak commute indicator, CNN modal split distribution, Origin-Destination (OD) flow matrix. | ✅ Production |
| **Congestion Heatmap**| Real-time spatial traffic heatmap, 11 monitored junctions, 5 arterial corridor polylines colored by speed, interactive hotspot zoom (`Begumpet`, `Gachibowli`, `Secunderabad`, `PVNR Expressway`). | ✅ Production |
| **Watchlist & Alerts** | Real-time alert cards, stolen vehicle hotlist table, suspect registration modal, and 1-click PCR Patrol Intercept dispatch system. | ✅ Production |
| **Forensic Dossier** | Chain-of-custody intelligence brief export with cryptographic SHA-256 verification hash for court-admissible evidence. | ✅ Production |

---

## 🎨 4. Design System & Theming

Designed in accordance with the **Stitch AI Master Prompt** and the official **Traffic Signal / Indian Tricolor Palette**:

- **Signal Orange (`#FF6D00`)**: Primary accents, active navigation tabs, radar warning halos, critical alerts, and congested corridors ($<20\text{ km/h}$).
- **Signal Emerald Green (`#00E475`)**: Confirmed trajectory links, optimal traffic flow ($>40\text{ km/h}$), verified consensus badges, and online nodes.
- **Pure White (`#FFFFFF`)**: High-contrast typography, reflective camera marker cores, and private vehicle HSRP plates.
- **Obsidian Slate (`#080C16`, `#0F131D`)**: Ultra-deep, military-grade tactical command console shell.
- **Daylight Street Basemap**: Clean, daytime cartography powered by **OpenStreetMap** with zero watermarks and clear road hierarchies.

---

## 🚀 5. Quickstart & Local Setup

### Prerequisites
- Python 3.10 or higher
- Git
- Web browser (Chrome, Edge, Firefox)
- *(Optional)* Docker & Docker Compose

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/your-org/neura-track.git
cd "Neura Track"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install fastapi uvicorn pydantic sqlalchemy sqlite3 httpx pillow opencv-python
```

### Step 3: Configure Environment
Copy the configuration template:
```bash
cp .env.example .env
```

### Step 4: Run Application
Start the high-performance Uvicorn server:
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 5: Access Web Command Center
Open your browser and navigate to:
- **Command Dashboard:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive OpenAPI Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative Redoc API Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 6. Testing & Simulation

### Running Automated Integration Tests
Execute the comprehensive test suite validating all API endpoints, trajectory graph solvers, and traffic aggregations:
```bash
pytest backend/tests/test_api.py -v
```

### Running the Synthetic ANPR Pipeline Simulator
Simulate live vehicle feeds, edge OCR extractions, and spatiotemporal event injection:
```bash
python scripts/simulate_pipeline.py
```

---

## 🗺️ 7. API Reference Overview

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/cameras` | `GET` | Returns all operational camera nodes with coordinates, status, and telemetry. |
| `/api/cameras/{id}` | `GET` | Telemetry details and uptime stats for a single camera node. |
| `/api/events` | `GET` | Real-time vehicle detection event stream (supports plate & node filters). |
| `/api/events` | `POST` | Ingests a new vehicle detection event from an edge ANPR camera. |
| `/api/vehicles/{plate}/trajectory` | `GET` | Reconstructs spatiotemporal journey with speed validation and gap bridging. |
| `/api/traffic/kpis` | `GET` | City-wide macro KPIs, vehicle modal distribution, and hourly volume trends. |
| `/api/traffic/heatmap` | `GET` | Spatial traffic density points (11 junctions) and arterial corridor speeds. |
| `/api/traffic/od` | `GET` | Origin-Destination movement matrix between key urban zones. |
| `/api/alerts` | `GET` | Active security notifications and blacklisted vehicle sightings. |
| `/api/alerts/watchlist` | `GET` | List of target vehicles registered on the active police hotlist. |
| `/api/alerts/watchlist` | `POST` | Register a new high-interest target plate with priority and notes. |

---

## 📁 8. Project Directory Structure

```
c:\Neura Track/
├── .agents/                        # Agent workflows and domain intelligence skills
│   └── skills/trace-x-engine/      # TRACE-X domain skill (ANPR, trajectory, traffic)
├── backend/                        # Backend Application Package
│   ├── app/
│   │   ├── api/                    # Modular FastAPI Route Handlers
│   │   │   ├── alerts.py           # Watchlist and alert dispatch routes
│   │   │   ├── cameras.py          # Camera metadata and status routes
│   │   │   ├── events.py           # Ingestion and event query routes
│   │   │   ├── traffic.py          # Macro analytics, heatmap, OD routes
│   │   │   └── vehicles.py         # Trajectory search and dossier routes
│   │   ├── services/               # Core Algorithmic Business Logic
│   │   │   ├── trajectory.py       # Spatiotemporal graph solver & physical speed guard
│   │   │   └── traffic.py          # Heatmap generation and corridor flow calculator
│   │   ├── static/                 # Tactical Command Center Web UI
│   │   │   ├── index.html          # 4-workspace tactical command center console
│   │   │   ├── style.css           # Traffic signal design system (#FF6D00, #00E475, #080C16)
│   │   │   └── app.js              # Leaflet GIS controller, basemap switcher, real-time polling
│   │   ├── database.py             # Database engine (PostGIS / SQLite fallback)
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   ├── schemas.py              # Pydantic validation schemas
│   │   └── main.py                 # FastAPI application root & seed data runner
│   └── tests/
│       └── test_api.py             # Automated unit & integration tests
├── docs/                           # Engineering Specifications & Architectural Documentation
│   ├── prd.md                      # Product Requirements Document & Non-Functional SLOs
│   ├── ai_models_and_pipeline.md   # Computer Vision, OCR, and Re-ID specifications
│   ├── tech_stack.md               # Technology choices and justification
│   ├── architecture.md             # System architecture & distributed data pipeline
│   ├── database_schema.md          # PostGIS schema definitions and spatial indexing
│   ├── api_specification.md        # Comprehensive OpenAPI/Swagger specification
│   ├── testing_and_evaluation.md   # Testing protocols and evaluation benchmarks
│   └── stitch_ui_master_prompt.md  # Master prompt specification for Google Stitch AI
├── scripts/
│   └── simulate_pipeline.py        # Synthetic multi-camera ANPR event simulator
├── .env.example                    # Environment variable configuration template
├── AGENTS.md                       # Workspace memory & permanent instructions
├── CHANGELOG.md                    # Immutable chronological record of all engineering changes
├── docker-compose.yml              # Production Docker stack (FastAPI, PostGIS, Redis)
└── README.md                       # Master project documentation
```

---

## ⚖️ 9. Domain Constraints & Legal Compliance

1. **Zero Continuous Video Duplication**: Video feeds are processed strictly at the edge or transiently in memory; only lightweight, structured JSON events with cryptographic hashes are persisted.
2. **Physical Velocity Limit Enforcement**: Any multi-camera trajectory edge implying a speed exceeding $160\text{ km/h}$ is automatically pruned to eliminate false positive plate correlations.
3. **Multi-Camera Consensus**: High-confidence alerts require verification across multiple cameras or human-in-the-loop analyst confirmation.
4. **Data Privacy by Design**: All vehicle metadata adheres to role-based access control (RBAC), automated record expiration policies, and SHA-256 chain-of-custody logging.

---

<div align="center">

**TRACE-X Engine — Smart India Hackathon 2026**  
*City-Wide Multi-Camera Vehicle Intelligence & Traffic Flow Optimization*

</div>
