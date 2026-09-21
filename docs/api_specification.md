# TRACE-X: Backend REST API Specification

**Document Code:** API-SPEC-01  
**Base URL:** `http://localhost:8000/api`  
**Standard:** OpenAPI 3.1 / JSON API  
**Authentication:** Bearer JWT Token in `Authorization` header  

---

## 1. Camera Management Endpoints

### 1.1 List All Monitored Cameras
- **Endpoint:** `GET /api/cameras`
- **Query Parameters:**
  - `status` (optional, string): `online` | `offline` | `degraded`
  - `road_id` (optional, string): Filter by road corridor
  - `zone` (optional, string): Filter by municipal zone (e.g. `Zone_North`)
- **Response `200 OK`:**
```json
[
  {
    "camera_id": "C101",
    "name": "Begumpet Junction Northbound",
    "latitude": 17.4435,
    "longitude": 78.4682,
    "road_id": "RD_BEGUMPET_MAIN",
    "direction": "north",
    "status": "online",
    "quality_score": 0.94,
    "last_heartbeat": "2026-09-10T10:30:00Z"
  }
]
```

### 1.2 Get Camera Details
- **Endpoint:** `GET /api/cameras/{camera_id}`
- **Response `200 OK`:** Detailed camera metadata, streaming URI, installation specs, and 24-hour event count.

### 1.3 Register New Camera
- **Endpoint:** `POST /api/cameras`
- **Request Body:**
```json
{
  "camera_id": "C135",
  "name": "Outer Ring Road Exit 8",
  "latitude": 17.4120,
  "longitude": 78.3450,
  "road_id": "RD_ORR_E08",
  "direction": "south",
  "stream_url": "rtsp://admin:pass@192.168.1.135:554/live"
}
```

---

## 2. Vehicle Event Ingestion & Query Endpoints

### 2.1 Query Vehicle Events
- **Endpoint:** `GET /api/events`
- **Query Parameters:**
  - `plate` (optional, string): License plate filter (supports partial match)
  - `camera_id` (optional, string): Filter by observing camera
  - `start_time` (optional, ISO 8601): Start timestamp filter
  - `end_time` (optional, ISO 8601): End timestamp filter
  - `vehicle_type` (optional, string): `car` | `motorcycle` | `bus` | `truck` | `auto_rickshaw`
  - `min_confidence` (optional, float): Minimum plate confidence threshold (e.g. `0.75`)
  - `limit` (optional, int, default: 50): Number of records per page
  - `offset` (optional, int, default: 0): Pagination offset
- **Response `200 OK`:** Array of `VehicleEvent` records and total count.

### 2.2 Ingest Vehicle Event (Edge Ingestion)
- **Endpoint:** `POST /api/events`
- **Request Body:**
```json
{
  "camera_id": "C101",
  "timestamp": "2026-09-10T10:05:14+05:30",
  "plate_text": "TS09AB1234",
  "plate_confidence": 0.96,
  "vehicle_type": "motorcycle",
  "vehicle_color": "black",
  "vehicle_make": "Yamaha",
  "vehicle_model": "R15",
  "direction": "north",
  "image_quality_score": 91.5,
  "detection_confidence": 0.95,
  "reid_embedding": [0.034, -0.112, 0.089, "...512 floats..."],
  "crop_base64": "...optional..."
}
```

---

## 3. Vehicle Search & Trajectory Reconstruction Endpoints

### 3.1 Historical Trajectory Reconstruction
- **Endpoint:** `GET /api/vehicles/{plate}/history`
- **Query Parameters:**
  - `start_time` (optional, ISO 8601)
  - `end_time` (optional, ISO 8601)
  - `include_gaps` (optional, bool, default: `true`): Include interpolated camera gaps
- **Response `200 OK`:**
```json
{
  "plate": "TS09AB1234",
  "first_detected": "2026-09-10T10:05:00Z",
  "last_detected": "2026-09-10T10:25:00Z",
  "overall_confidence": 0.92,
  "status": "CONFIRMED",
  "total_distance_km": 8.4,
  "average_speed_kmh": 25.2,
  "observations": [
    {
      "event_id": "evt_001",
      "camera_id": "C101",
      "timestamp": "2026-09-10T10:05:00Z",
      "latitude": 17.4435,
      "longitude": 78.4682,
      "plate_text": "TS09AB1234",
      "confidence": 0.96,
      "vehicle_color": "black"
    },
    {
      "event_id": "evt_002",
      "camera_id": "C107",
      "timestamp": "2026-09-10T10:11:00Z",
      "latitude": 17.4320,
      "longitude": 78.4550,
      "plate_text": "TS09A?1234",
      "confidence": 0.61,
      "vehicle_color": "black"
    }
  ],
  "trajectory_links": [
    {
      "from_camera": "C101",
      "to_camera": "C107",
      "link_type": "CONFIRMED",
      "distance_km": 2.1,
      "travel_time_sec": 360,
      "implied_speed_kmh": 21.0,
      "match_score": 0.91,
      "reason": "High plate similarity + compatible travel time"
    },
    {
      "from_camera": "C107",
      "to_camera": "C123",
      "link_type": "CAMERA_GAP",
      "distance_km": 6.3,
      "travel_time_sec": 840,
      "implied_speed_kmh": 27.0,
      "match_score": 0.74,
      "reason": "Camera C115 offline along arterial; path bridged via shortest road path"
    }
  ]
}
```

---

## 4. Macro Traffic Analytics Endpoints

### 4.1 Traffic Summary KPIs
- **Endpoint:** `GET /api/traffic/summary`
- **Response `200 OK`:**
```json
{
  "total_vehicles_today": 248910,
  "average_city_speed_kmh": 34.8,
  "active_bottlenecks": 5,
  "peak_hour": "09:00 - 10:00",
  "modal_distribution": {
    "car": 89600,
    "motorcycle": 104540,
    "auto_rickshaw": 29870,
    "bus": 12450,
    "truck": 12450
  }
}
```

### 4.2 City Congestion Heatmap
- **Endpoint:** `GET /api/traffic/heatmap`
- **Response `200 OK`:** GeoJSON `FeatureCollection` of road segments with properties `congestion_level` (`LOW`, `MODERATE`, `SEVERE`), `current_speed_kmh`, and `volume_per_hour`.

### 4.3 Origin-Destination Matrix
- **Endpoint:** `GET /api/traffic/od`
- **Query Parameters:** `date` (YYYY-MM-DD), `time_bucket` (`morning_peak`, `evening_peak`, `all_day`)
- **Response `200 OK`:** Matrix of trips between municipal zones (Zone A, B, C, D).

---

## 5. Watchlist & Alerts Endpoints

### 5.1 List Active Alerts
- **Endpoint:** `GET /api/alerts`
- **Query Parameters:** `status` (`NEW`, `ACKNOWLEDGED`, `RESOLVED`), `priority` (`CRITICAL`, `HIGH`, `MEDIUM`)

### 5.2 Add Vehicle to Watchlist
- **Endpoint:** `POST /api/alerts/watchlist`
- **Request Body:**
```json
{
  "plate_text": "TS09AB1234",
  "category": "STOLEN_VEHICLE",
  "priority": "CRITICAL",
  "case_reference": "FIR-2026-HYD-4091",
  "notes": "Suspect involved in commercial burglary; armed"
}
```

### 5.3 Acknowledge Alert (Human-in-the-Loop)
- **Endpoint:** `PATCH /api/alerts/{alert_id}/acknowledge`
- **Request Body:**
```json
{
  "action": "CONFIRMED",
  "officer_notes": "Unit 4 dispatched to Begumpet junction for interception",
  "case_file_id": "FIR-2026-HYD-4091"
}
```

---

## 6. Forensic Reports Endpoints

### 6.1 Generate Vehicle Journey Dossier
- **Endpoint:** `GET /api/reports/vehicle/{plate}`
- **Query Parameters:** `format` (`json` | `pdf`), `start_time`, `end_time`
- **Response:** PDF binary download or structured JSON forensic audit dossier including cryptographic SHA-256 hash.
