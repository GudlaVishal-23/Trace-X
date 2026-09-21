# TRACE-X: Technology Stack & Architectural Decision Records (ADR)

**Document Code:** TECH-STACK-01  
**Target Environment:** Prototype to Production Deployment  
**Standard Architecture:** Event-Driven Microservices Layer over PostGIS  

---

## 1. Complete Technology Matrix

| Layer | Component / Technology | Chosen Library / Tool | Primary Rationale & Justification |
| :--- | :--- | :--- | :--- |
| **Edge / Ingestion** | Video Stream Handler | **OpenCV 4.9 (C++ / Python bindings)** | Low-latency RTSP/file decoding, hardware acceleration via CUDA/VAAPI, matrix manipulation. |
| **Object Detection** | Vehicle & Plate Detection | **Ultralytics YOLOv8 / YOLO11** | Superior mAP/speed frontier, native ONNX export, robust anchor-free detection head. |
| **OCR & Recognition** | Text & Plate Reading | **PaddleOCR v4 / CRNN + CTC** | Outperforms Tesseract on low-contrast text; robust recognition of alphanumeric plate fonts. |
| **Deep Metric Learning** | Vehicle Re-Identification | **TorchVision / Torchreid (OSNet)** | Generates compact 512-dim visual embeddings resilient to viewpoint variations. |
| **Backend Framework** | High-Throughput REST API | **FastAPI (Python 3.10+)** | Async ASGI runtime (`asyncio` + `uvicorn`), automatic OpenAPI spec generation, Pydantic v2 data validation. |
| **Database Engine** | Relational & Geospatial | **PostgreSQL 16 + PostGIS 3.4** | Native spatial indexes (`GIST`), spatial topology functions (`ST_Distance`, `ST_MakeLine`, `ST_DWithin`). |
| **Frontend Framework** | Command Center UI | **React 18 + Vite** | Fast HMR build pipeline, component reusability, virtual DOM performance for high-frequency updates. |
| **GIS Mapping Canvas** | Map & Spatial Visualizer | **Leaflet 1.9 + React-Leaflet + OSM** | Free, open-source, tile-server independent, lightweight polygon and breadcrumb polyline rendering. |
| **Charts & Analytics** | Data Visualization | **Recharts & Chart.js** | Canvas/SVG charting for hourly flow, modal distribution, and Origin-Destination matrices. |
| **Containerization** | Orchestration & Deploy | **Docker & Docker Compose** | Reproducible builds across developer laptops, cloud VMs, and edge hardware. |

---

## 2. Architectural Decision Records (ADR)

### ADR-01: PostgreSQL + PostGIS vs. NoSQL (MongoDB)
- **Context:** The system must store vehicle events with GPS coordinates, timestamps, and plate strings, while performing high-speed spatial proximity searches and route graph lookups.
- **Decision:** Use **PostgreSQL 16 with the PostGIS extension**.
- **Rationale:**
  - PostGIS provides true spatial indexing (`GIST` R-Tree), allowing queries like `ST_DWithin(geom, ST_MakePoint(lon, lat), 500)` to execute in $< 5 \text{ ms}$.
  - Strict ACID guarantees prevent phantom records in police watchlist and audit logging tables.
  - Relational joins cleanly express `trajectory_links` connecting `vehicle_events` to `cameras`.
- **Consequences:** Slightly more upfront schema discipline required compared to schema-less document stores.

### ADR-02: Event-First Architecture vs. Continuous Video Archiving
- **Context:** Storing 1080p video from 100 cameras 24/7 requires $> 15 \text{ TB}$ of storage per week, which creates severe bandwidth, storage, and legal liabilities.
- **Decision:** **Extract and persist structured `VehicleEvent` records (~1.2 KB each)**; retain raw footage only at existing municipal NVR endpoints according to external policy.
- **Rationale:**
  - 1 million vehicle events require only $\sim 1.2 \text{ GB}$ of database storage.
  - Search queries across millions of events execute in sub-seconds using B-Tree and GIST indexes.
  - Aligns with India's **Digital Personal Data Protection (DPDP) Act 2023** by practicing strict data minimization.

### ADR-03: PaddleOCR / CRNN vs. Tesseract OCR
- **Context:** License plates on Indian roads are frequently damaged, non-standard, dusty, and captured at acute perspective angles.
- **Decision:** Use **PaddleOCR / Lightweight CRNN (Convolutional Recurrent Neural Network) with CTC loss**.
- **Rationale:**
  - Tesseract performs poorly on single-line scene text with complex backgrounds, yielding $< 65\%$ accuracy on raw crops.
  - PaddleOCR uses a deep text detection (DBNet) + recognition (SVTR/CRNN) pipeline that achieves $> 92\%$ accuracy on distorted alphanumeric strings.

### ADR-04: Leaflet + OpenStreetMap vs. Mapbox / Google Maps API
- **Context:** The GIS dashboard must render city maps, camera markers, colored trajectory vectors, and density heatmaps.
- **Decision:** **Leaflet with OpenStreetMap CartoDB Dark Matter tiles**.
- **Rationale:**
  - Zero API cost and zero rate limits during hackathon demos and high-frequency operational testing.
  - Sleek dark theme tiles perfectly match command center aesthetic guidelines.
  - Full offline capability using cached tile packages.

---

## 3. Production-Scale Extension Components

When moving from the SIH prototype to full city-scale deployment (1,000+ cameras):

```text
[Camera Edge Nodes] 
         │ (Vehicle Events via MQTT / gRPC)
         ▼
[Apache Kafka Cluster] ── (Topic: vehicle.events.raw)
         │
         ├───► [Apache Flink / Spark Streaming] ──► [Real-Time Congestion & Anomaly Detector]
         │
         ├───► [Event Ingestion Worker Pool] ──► [PostgreSQL 16 + Citus / PostGIS Cluster]
         │
         └───► [Redis In-Memory Cache] ──► [Active 10-Min Watchlist & Trajectory Lookups]
```

1. **Apache Kafka:** Decouples high-frequency camera ingestion from database writes.
2. **Redis 7:** In-memory caching for active watchlist plates and hot trajectory edges ($< 2 \text{ ms}$ lookup).
3. **MinIO / AWS S3:** Object storage for authorized evidence thumbnails and forensic PDF journey reports.
4. **Kubernetes (K8s):** Horizontal auto-scaling of worker pods based on queue length.

---

## 4. Hardware Sizing & Specifications

### 4.1 Prototype Demonstration Setup (Single Laptop/Desktop)
- **CPU:** Intel Core i5/i7 (11th Gen+) or AMD Ryzen 5/7 (6+ cores).
- **RAM:** 16 GB DDR4/DDR5.
- **GPU:** Optional; NVIDIA GTX 1650 / RTX 3050 (4 GB VRAM) provides real-time multi-stream demo.
- **Storage:** 20 GB free SSD space.

### 4.2 City Command Center Pilot (100 Cameras)
- **Inference Server:** 2x Dell PowerEdge R750 with 2x NVIDIA RTX A4000 (16 GB VRAM each).
- **Database Server:** 32-core AMD EPYC, 64 GB RAM, NVMe RAID-10 storage.
- **Throughput:** Capable of processing 150 frames/second across 100 cameras using 5 FPS intelligent frame sampling.
