# TRACE-X | City-Wide AI Vehicle Intelligence & Traffic Analytics Engine

<div align="center">

![TRACE-X Banner](https://img.shields.io/badge/TRACE--X-SIH26127-F59E0B?style=for-the-badge&logo=shield&logoColor=white)
![Status](https://img.shields.io/badge/STATUS-PRODUCTION--READY%20PROTOTYPE-10B981?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-ByteTrack-3B82F6?style=for-the-badge&logo=opencv&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=leaflet&logoColor=white)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)

**An enterprise-grade, spatiotemporal multi-camera ANPR tracking and macro urban traffic analytics platform built for Smart India Hackathon 2026 (Problem Statement: SIH26127).**

[Live Command Center](http://127.0.0.1:8000) • [Live Scan Theatre](http://127.0.0.1:8000/scan) • [Swagger API Docs](http://127.0.0.1:8000/docs) • [System Specifications](./docs/) • [Changelog](./CHANGELOG.md)

</div>

---

## 🚦 1. Executive Summary & Core Philosophy

**TRACE-X** transforms disparate, city-wide CCTV and ANPR camera feeds into structured, actionable, and legally defensible vehicle intelligence. Designed specifically to resolve urban security blind spots and multi-camera handover gaps, TRACE-X delivers:

1. **Live Frame-by-Frame Video Ingestion & Perception (Scan Theatre)**: Evaluator uploads traffic feeds or selects presets to observe real-time bounding boxes, live Indian High Security Registration Plate (HSRP) detection, ByteTrack vehicle tracking, and Bayesian multi-frame consensus.
2. **Single-Plate Spatiotemporal Trajectory Solver**: Graph-based journey reconstruction that correlates vehicle observations across distributed cameras, enforces physical feasibility guards ($v \le 160\text{ km/h}$), bridges blind camera zones, and classifies confidence into `CONFIRMED`, `PROBABLE`, and `CAMERA_GAP`.
3. **Macro Urban Traffic Analytics & GIS Heatmaps**: Real-time arterial flow analysis, spatial density heatmaps across key urban junctions, corridor transit velocities, Deep CNN vehicle modal distribution (2-wheelers, cars, commercial, autos), and Origin-Destination (OD) commute matrices.
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
 │  CLAHE Contrast Enhancement ──> ByteTrack Multi-Object Tracking ──> Bayesian Consensus   │
 └───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                             │ JSON Event Payloads / WebSocket Stream
                                             ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────┐
 │                                BACKEND & ANALYTICS CORE                                  │
 │  ┌────────────────────────────────────────────────────────────────────────────────────┐ │
 │  │ FastAPI Asynchronous REST Engine (Python 3.10+)                                    │ │
 │  │  • /api/cameras     • /api/events      • /api/vehicles/{plate}/trajectory          │ │
 │  │  • /api/traffic     • /api/alerts      • /api/ingest/upload & /ws/ingest           │ │
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
 │         DATA & PERSISTENCE LAYER         │  │         COMMAND CENTER & THEATRE         │
 │  • PostgreSQL 16 + PostGIS Spatial DB    │  │  • Clean Modern SaaS Interface (v5.0)    │
 │  • SQLite Spatial Fallback Engine        │  │  • Warm Slate + Amber/Emerald Accents    │
 │  • Ingest Jobs, Detections, & Tracks     │  │  • 64px Icon Rail + Leaflet GIS Canvas   │
 │  • Local Metadata & Snapshot Store       │  │  • Live Scan Theatre with Canvas HUD     │
 └──────────────────────────────────────────┘  └──────────────────────────────────────────┘
```

---

## ⚡ 3. Key Capabilities & Feature Matrix

| Module | Features & Capabilities | Status |
| :--- | :--- | :--- |
| **Live Scan Theatre (`/scan`)** | Frame-by-frame video ingestion, YOLOv8 vehicle/plate bounding boxes, ByteTrack tracking, aspect-ratio letterbox compensation, live WebSocket streaming, and Bayesian consensus fusion drawer. | ✅ Production |
| **Live GIS Map** | Real-time Leaflet GIS canvas, strategic city camera nodes, live detection stream, Daylight Basemap Switcher (`Daylight OSM`, `Carto Voyager`, `World Street`). | ✅ Production |
| **Trajectory Tracking** | Spatiotemporal graph solver, physical velocity guard ($v \le 160\text{ km/h}$), camera gap interpolation, corridor polylines, 4 KPI metric cards, confidence scoring (`CONFIRMED`, `PROBABLE`, `CAMERA_GAP`). | ✅ Production |
| **Authentic HSRP Plate Badges** | Dual-layer Indian High Security Registration Plate rendering with blue `IND` wedge, Ashoka Chakra emblem, and yellow (commercial) / white (private) variants. | ✅ Production |
| **Traffic Analytics** | Macro KPIs (Vehicles Today, City Speed, Active Bottlenecks), peak commute indicators, CNN modal split distribution, Origin-Destination (OD) flow matrix. | ✅ Production |
| **Congestion Heatmap**| Real-time spatial traffic heatmap, 11 monitored junctions, 5 arterial corridor polylines colored by speed, interactive hotspot zoom (`Begumpet`, `Gachibowli`, `Secunderabad`, `PVNR Expressway`). | ✅ Production |
| **Watchlist & Alerts** | Real-time alert cards with CLAHE OCR plate crops, CCTV evidence lightbox, stolen vehicle hotlist table, and 1-click PCR Patrol Intercept dispatch system. | ✅ Production |
| **Forensic Dossier** | Chain-of-custody intelligence brief export with cryptographic SHA-256 verification hash for court-admissible evidence. | ✅ Production |

---

## 🎨 4. Design System & Theming

The interface adopts a **Soft, Clean, Premium Modern SaaS Architecture (v5.0)**:

- **Warm Slate Background (`#0F172A` / `#1E293B`)**: Layered surfaces designed to prevent eye fatigue during prolonged monitoring.
- **Warm Amber Accent (`#F59E0B`)**: High-contrast, non-aggressive primary accent for active navigation, highlighted plates, and key actions.
- **Emerald Success (`#10B981`)**: Trajectory confirmations, optimal speeds, and online node indicators.
- **Compact 64px Icon Rail**: Replaces bulky 256px sidebars to maximize GIS map and analytics real estate.
- **Modern Typography**: Clean `Inter` font for UI hierarchy with `JetBrains Mono` reserved for telemetry and HSRP registration plates.

---

## 🚀 5. Quickstart & Local Setup

### Prerequisites
- Python 3.10 or higher
- Git
- Modern web browser (Chrome, Edge, Firefox)

### Step 1: Clone Repository
```bash
git clone https://github.com/GudlaVishal-23/Trace-X.git
cd Trace-X
```

### Step 2: Create & Activate Virtual Environment
```bash
# Windows:
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS:
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
# Or core packages:
pip install fastapi uvicorn pydantic sqlalchemy httpx pillow opencv-python ultralytics supervision
```

### Step 4: Run Application
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

### Step 5: Access Web Interfaces
- **Command Center Dashboard:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Live Scan Theatre:** [http://127.0.0.1:8000/scan](http://127.0.0.1:8000/scan)
- **Interactive OpenAPI Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 6. Testing & Quality Assurance

### Automated Tests
Run the comprehensive integration and perception test suite:
```bash
python -m pytest backend/tests/test_api.py backend/tests/test_phase1_ingest.py -v
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
| `/api/ingest/upload` | `POST` | Upload video for live perception processing ($\le 500\text{ MB}$). |
| `/api/ingest/jobs` | `GET` | List all video ingestion jobs with progress telemetry. |
| `/api/ingest/jobs/{id}/tracks` | `GET` | Retrieve Bayesian consensus tracks and plate reads for a job. |
| `/ws/ingest/{job_id}` | `WebSocket` | Real-time live frame detection stream with bounding boxes. |
| `/api/cameras` | `GET` | Returns all operational camera nodes with coordinates, status, and telemetry. |
| `/api/events` | `GET` | Real-time vehicle detection event stream (supports plate & node filters). |
| `/api/vehicles/{plate}/trajectory` | `GET` | Reconstructs spatiotemporal journey with speed validation and gap bridging. |
| `/api/traffic/kpis` | `GET` | City-wide macro KPIs, vehicle modal distribution, and hourly volume trends. |
| `/api/traffic/heatmap` | `GET` | Spatial traffic density points (11 junctions) and arterial corridor speeds. |
| `/api/traffic/od` | `GET` | Origin-Destination movement matrix between key urban zones. |
| `/api/alerts` | `GET` | Active security notifications and blacklisted vehicle sightings. |
| `/api/alerts/watchlist` | `POST` | Register a new high-interest target plate with priority and notes. |

---

## 📁 8. Project Directory Structure

```
Trace-X/
├── .agents/                        # Agent workflows and TRACE-X domain skills
├── backend/                        # Backend Application Package
│   ├── app/
│   │   ├── api/                    # Modular FastAPI Route Handlers
│   │   │   ├── alerts.py           # Watchlist and alert dispatch routes
│   │   │   ├── cameras.py          # Camera metadata and status routes
│   │   │   ├── events.py           # Ingestion and event query routes
│   │   │   ├── traffic.py          # Macro analytics, heatmap, OD routes
│   │   │   ├── vehicles.py         # Trajectory search and dossier routes
│   │   │   └── videos.py           # Sample video catalog and presets
│   │   ├── ingest/                 # Video Perception & Ingestion Engine
│   │   │   └── video_worker.py     # YOLOv8, ByteTrack, CLAHE, & Bayesian voting
│   │   ├── services/               # Core Algorithmic Business Logic
│   │   │   ├── trajectory.py       # Spatiotemporal graph solver & speed guard
│   │   │   └── traffic.py          # Heatmap generation and corridor flow calculator
│   │   ├── static/                 # Modern Clean SaaS Web UI
│   │   │   ├── index.html          # Command Center dashboard (64px rail, Leaflet GIS)
│   │   │   ├── scan.html           # Live Scan Theatre (letterbox canvas HUD, WebSocket)
│   │   │   ├── style.css           # Clean Design System v5.0 (Warm Slate, Amber, Emerald)
│   │   │   └── app.js              # GIS map controller, real-time polling, timeline renderer
│   │   ├── database.py             # Database engine (PostGIS / SQLite fallback)
│   │   ├── models.py               # SQLAlchemy ORM models (Jobs, Detections, Tracks)
│   │   ├── schemas.py              # Pydantic validation schemas
│   │   └── main.py                 # FastAPI application root & seed data runner
│   └── tests/
│       ├── test_api.py             # Automated API unit & integration tests
│       └── test_phase1_ingest.py   # End-to-end video ingestion & tracking tests
├── data/                           # Data directory (SQLite db, uploads, seed topology)
├── docs/                           # Architectural Documentation & PRDs
├── sample videos/                  # Sample 4K/1080p traffic clips for demo
├── scripts/                        # Calibration and simulation scripts
├── AGENTS.md                       # Workspace memory & permanent instructions
├── CHANGELOG.md                    # Chronological record of all engineering changes
├── docker-compose.yml              # Production Docker stack (FastAPI, PostGIS, Redis)
└── README.md                       # Master project documentation
```

---

## ⚖️ 9. Domain Constraints & Legal Compliance

1. **Zero Continuous Video Duplication**: Feeds are processed transiently; only structured `VehicleEvent` records with cryptographic hashes are persisted.
2. **Physical Velocity Limit Enforcement**: Any multi-camera trajectory edge implying a speed exceeding $160\text{ km/h}$ is automatically pruned to eliminate false positive plate correlations.
3. **Multi-Camera Consensus**: High-confidence alerts require verification across multiple cameras or human-in-the-loop analyst confirmation.
4. **Data Privacy by Design**: All vehicle metadata adheres to role-based access control (RBAC), automated record expiration policies, and SHA-256 chain-of-custody logging.

---

<div align="center">

**TRACE-X Engine — Smart India Hackathon 2026**  
*City-Wide Multi-Camera Vehicle Intelligence & Traffic Flow Optimization*

</div>
