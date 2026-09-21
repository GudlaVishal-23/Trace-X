# TRACE-X: End-to-End System Architecture Specification

**Document Code:** ARCH-SPEC-01  
**Architecture Pattern:** Event-Driven Microservices with Geospatial Intelligence Layer  
**Core Innovation:** Resilient Evidence Fusion with Zero Continuous Video Archiving  

---

## 1. Architectural Blueprint

TRACE-X decouples high-bandwidth computer vision perception from downstream search and analytical intelligence. Rather than ingesting and retaining petabytes of raw CCTV video, the platform operates as an **Edge-to-Event Translation Engine**.

```text
                                  MUNICIPAL CAMERA INFRASTRUCTURE
                     ┌───────────────────┬───────────────────┬───────────────────┐
                     ▼                   ▼                   ▼                   ▼
                [Camera C101]       [Camera C107]       [Camera C115]       [Camera C123]
               (Arterial North)     (Ring Road Jct)      (Flyover Exit)     (Sector Gate)
                     │                   │                   │                   │
                     └───────────────────┴─────────┬─────────┴───────────────────┘
                                                   │ RTSP / Video Stream
                                                   ▼
                                     ┌───────────────────────────┐
                                     │   VIDEO INGESTION LAYER   │
                                     │  Adaptive Frame Sampler   │
                                     └─────────────┬─────────────┘
                                                   │ Key Frames
                                                   ▼
                                     ┌───────────────────────────┐
                                     │   AI PERCEPTION PIPELINE  │
                                     │ • Vehicle Detector (YOLO) │
                                     │ • Plate Detector (YOLO)   │
                                     │ • Image Quality Screening │
                                     │ • Conditional Enhance     │
                                     │ • Multi-Frame OCR Fusion  │
                                     │ • Re-ID Feature Extractor │
                                     └─────────────┬─────────────┘
                                                   │ Structured JSON Event
                                                   ▼
                                     ┌───────────────────────────┐
                                     │ UNIFIED VEHICLE EVENT BUS │
                                     │  (FastAPI Event Ingestion)│
                                     └─────────────┬─────────────┘
                                                   │
                         ┌─────────────────────────┴─────────────────────────┐
                         ▼                                                   ▼
              ┌─────────────────────┐                             ┌─────────────────────┐
              │  POSTGRESQL 16 DB   │                             │ IN-MEMORY HOT CACHE │
              │   PostGIS Spatial   │                             │  Active Watchlists  │
              │  Vehicle Event Rows │                             │  Recent Tracklets   │
              └──────────┬──────────┘                             └──────────┬──────────┘
                         │                                                   │
       ┌─────────────────┼─────────────────────────┐                         │
       ▼                 ▼                         ▼                         ▼
┌──────────────┐  ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│  TRAJECTORY  │  │MACRO TRAFFIC │          │  WATCHLIST   │          │  AUDIT LOG   │
│ GRAPH ENGINE │  │FLOW ENGINE   │          │ ALERT ENGINE │          │ & COMPLIANCE │
└──────┬───────┘  └──────┬───────┘          └──────┬───────┘          └──────┬───────┘
       │                 │                         │                         │
       └─────────────────┴────────────┬────────────┴─────────────────────────┘
                                      │ REST API / WebSockets
                                      ▼
                      ┌───────────────────────────────┐
                      │    TRACE-X COMMAND CENTER     │
                      │  React 18 + Leaflet GIS UI    │
                      │ • Live Map with Status Pulse  │
                      │ • Single-Plate Trajectory View│
                      │ • Macro Heatmap & OD Matrix   │
                      │ • Instant Alert Drawer        │
                      └───────────────────────────────┘
```

---

## 2. The Core Storage Paradigm: Events vs. Video Duplication

One of the most fatal errors in surveillance platform architecture is designing around continuous video archiving. 

### 2.1 Comparative Analysis
| Attribute | Traditional Archiving Model | TRACE-X Event-Driven Model |
| :--- | :--- | :--- |
| **Data Ingested** | Continuous 1080p H.264 video streams. | Periodic keyframe crops during vehicle passage. |
| **Storage per Camera** | $\sim 20 \text{ GB}$ per day ($7.3 \text{ TB}$/year). | $\sim 10 \text{ MB}$ per day ($3.65 \text{ GB}$/year). |
| **City Scale (1,000 Cams)**| $\sim 7.3 \text{ Petabytes}$ per year. | $\sim 3.65 \text{ Terabytes}$ per year. |
| **Query Mechanism** | Manual scrubbing across video timelines. | Instantaneous indexed SQL & PostGIS queries. |
| **Query Latency** | Hours to days of operator inspection. | $< 800 \text{ ms}$ automated trajectory return. |
| **Data Governance** | High liability under DPDP Act 2023. | Full compliance via strict data minimization. |

### 2.2 Storage Boundary
TRACE-X records references back to the external CCTV/NVR system's timestamped channel rather than storing the video itself. It stores:
1. Structured tabular attributes (~1.2 KB).
2. Optional 15 KB JPEG plate crop & vehicle thumbnail for immediate forensic verification.

---

## 3. Normalized Vehicle Event Schema

Every observation on any camera produces an immutable event record:

```json
{
  "event_id": "evt_9f82b714",
  "camera_id": "C101",
  "timestamp": "2026-09-10T10:05:14+05:30",
  "plate_text": "TS09AB1234",
  "plate_confidence": 0.96,
  "observation_status": "CONFIRMED",
  "vehicle_type": "motorcycle",
  "vehicle_color": "black",
  "vehicle_make": "Yamaha",
  "vehicle_model": "R15",
  "direction": "north",
  "latitude": 17.412345,
  "longitude": 78.407123,
  "road_id": "RD_INNER_RING_04",
  "image_quality_score": 91.5,
  "blur_score": 0.88,
  "detection_confidence": 0.95,
  "reid_embedding_id": "emb_9f82b714",
  "thumbnail_url": "/static/crops/evt_9f82b714_crop.jpg"
}
```

---

## 4. Scalability Principles: From Prototype to 1,000+ Cameras

TRACE-X utilizes a 3-tier partitioning model:

1. **Temporal Partitioning (PostgreSQL Table Partitioning):**
   - The `vehicle_events` table is partitioned by month (`vehicle_events_2026_09`, `vehicle_events_2026_10`).
   - Old partitions can be moved to cold compressed tablespaces or archived.
2. **Spatial Partitioning:**
   - Spatial indexing via PostGIS `GIST (geom)` indexes. Queries bounded by geographic polygons or bounding boxes prune 95% of non-relevant table partitions.
3. **Candidate Pruning in Trajectory Solver:**
   - When connecting Camera $A$ to candidate Camera $B$, candidate generation filters out cameras that:
     - Are further than $d_{max} = v_{max} \times (t_B - t_A)$ away.
     - Require opposing travel direction on one-way arterial links.
     - Are disconnected in the road graph topology.

---

## 5. Camera Reliability & Self-Healing Resilience

Modern urban camera networks experience frequent outages due to power fluctuations, network dropouts, and physical damage. TRACE-X handles this through two mechanisms:

1. **Active Heartbeat & Health Monitoring:**
   - Every camera maintains a rolling 15-minute event counter.
   - If expected event volume drops to zero during daylight hours on a known active corridor, the camera is flagged as `OFFLINE / DEGRADED`.
2. **Camera Gap Trajectory Bridging:**
   - If a target vehicle was seen at $C_{101}$ at 10:05 and next seen at $C_{123}$ at 10:25, and intermediate camera $C_{107}$ is offline:
   - The trajectory solver recognizes the offline state of $C_{107}$.
   - It computes the shortest topological path between $C_{101}$ and $C_{123}$ via the road graph.
   - It marks the intermediate leg as `CAMERA GAP (Probable Continuation)` on the GIS map, warning the investigator of the missing camera without hallucinating a detection.
