# TRACE-X — Implementation Plan v2 (SIH26127)

> **Specification for Autonomous & Pair-Programming Implementation**  
> **Target System:** FastAPI backend, SQLite (`data/tracex.db`), YOLOv8 + LPRNet/PaddleOCR edge pipeline, vanilla-JS command center dashboard, Leaflet GIS map.  
> **Build Directive:** Build strictly in phase order. Each phase concludes with a runnable acceptance check.

---

## Build Order & Priority Matrix

| Phase | Description | Estimated Effort | Core Evaluator Value |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Video Upload + Live Scan Theatre** | 3–4 days | **Highest Demo Value** (Live scanning, ByteTrack, WebSocket, annotated video playback) |
| **Phase 3** | **Accuracy Benchmark & Ground Truth** | 2 days | Real precision/recall/F1, CER, blur quartile breakdown, ablation study |
| **Phase 4** | **Trust, Audit & Legal Defensibility** | 2 days | Officer confirmation before dispatch, audit log with mandatory case_ref, cryptographic hash chain, RBAC |
| **Phase 7** | **Hygiene & CI/CD** | 0.5 day | Pytest clean pass (`pyproject.toml`), fix plate contradiction, offline demo mode, architecture docs |
| **Phase 2** | **Appearance Re-Identification (ReID)** | 2 days | Plate-free search graceful degradation (`osnet_x0_25` / MobileNetV3) |
| **Phase 5** | **Differentiators (Convoy, Markov, Gov Adapters)** | 3 days | Convoy/tailing detection, learned route prediction, edge store-forward, VAHAN/CCTNS mock adapters |
| **Phase 6** | **Performance & Scale Benchmarks** | 1 day | Hardware FPS, latency budget, 10k queue load test, SQLite write ceiling, scale migration slide |

> **Critical Triad:** If time is constrained, prioritize **Phase 1, Phase 3, and Phase 4**. These close the three primary vulnerabilities an evaluation panel probes: *Is it real? Is it accurate? Can it be abused?*

---

## PHASE 1 — Video Upload + Live Scan Theatre (Highest Demo Value)

**Goal:** Evaluator uploads any traffic video $\rightarrow$ watches detection happen frame-by-frame with overlays $\rightarrow$ gets a structured result set that feeds the rest of the system and materializes onto the live map.

### 1.1 Database Schema Extensions (`data/tracex.db`)

```sql
CREATE TABLE IF NOT EXISTS ingest_jobs (
  job_id        TEXT PRIMARY KEY,      -- uuid4
  filename      TEXT NOT NULL,
  camera_id     TEXT NOT NULL,         -- Evaluator selects from /api/cameras
  status        TEXT NOT NULL,         -- QUEUED | PROBING | PROCESSING | DONE | FAILED
  total_frames  INTEGER DEFAULT 0,
  done_frames   INTEGER DEFAULT 0,
  fps           REAL,
  width         INTEGER,
  height        INTEGER,
  duration_s    REAL,
  started_at    TEXT,
  finished_at   TEXT,
  error         TEXT,
  stats_json    TEXT                   -- Summary JSON blob
);

CREATE TABLE IF NOT EXISTS job_detections (
  det_id          TEXT PRIMARY KEY,
  job_id          TEXT NOT NULL REFERENCES ingest_jobs(job_id),
  frame_idx       INTEGER NOT NULL,
  video_ts        REAL NOT NULL,         -- Elapsed seconds into video
  track_id        INTEGER,               -- ByteTrack ID
  bbox_json       TEXT NOT NULL,         -- [x1, y1, x2, y2] absolute pixels
  plate_bbox_json TEXT,
  vehicle_class   TEXT,
  color           TEXT,
  plate_raw       TEXT,
  plate_conf      REAL,
  blur_score      REAL,
  quality_score   REAL,
  crop_path       TEXT,
  plate_crop_path TEXT,
  clahe_crop_path TEXT,
  embedding       BLOB                   -- float32 ReID vector (Phase 2)
);

CREATE TABLE IF NOT EXISTS job_tracks (
  job_id        TEXT NOT NULL,
  track_id      INTEGER NOT NULL,
  first_frame   INTEGER,
  last_frame    INTEGER,
  n_frames      INTEGER,
  fused_plate   TEXT,                  -- Bayesian consensus result
  fused_conf    REAL,
  vehicle_class TEXT,
  color         TEXT,
  best_det_id   TEXT,
  watchlist_hit TEXT,                  -- NULL | Category
  PRIMARY KEY (job_id, track_id)
);
```

### 1.2 Backend Implementation Files

#### `backend/app/ingest/video_worker.py`
```python
def process_video(job_id: str, path: str, camera_id: str):
    cap = cv2.VideoCapture(path)
    # Probe fps, total_frames, dimensions -> update ingest_jobs (status=PROCESSING)
    stride = max(1, round(fps / TARGET_FPS))     # TARGET_FPS = 8
    tracker = ByteTrack()                         # supervision.ByteTrack
    for frame_idx, frame in frames:
        if frame_idx % stride: 
            continue
        dets = yolo(frame, classes=["car", "motorcycle", "bus", "truck"], conf=0.35)
        tracks = tracker.update(dets)
        for t in tracks:
            crop = frame[t.bbox]
            plate_box = plate_detector(crop)
            if plate_box:
                pcrop = crop[plate_box]
                blur  = laplacian_var(pcrop)
                img   = clahe(pcrop) if blur < 100 else pcrop
                text, conf = ocr(img)
            color = dominant_color_hsv(crop)
            # Write job_detections row + save 4 forensic image artifacts
            emit_event(job_id, {...})             # Broadcast to WebSocket
    for each track: 
        fused = bayesian_vote(dets_of_track)      # Reuse Section 2.4 formula
        # Write job_tracks; check watchlist; if hit -> emit ALERT event
    # Write annotated MP4 (H.264 compatible)
    # Materialize ANPR events into main events table
    # status = DONE
```
- Managed via `ThreadPoolExecutor(max_workers=2)` owned by FastAPI lifespan (non-blocking).

#### `backend/app/routers/ingest.py`
| Route | Method | Purpose |
| :--- | :--- | :--- |
| `/api/ingest/upload` | POST (multipart) | Accepts video file + `camera_id`; validates ext in `.mp4,.avi,.mov,.mkv`, size $\le 500\text{ MB}$; writes to `data/uploads/{job_id}{ext}`; dispatches to thread pool; returns `{job_id}` |
| `/api/ingest/jobs` | GET | List recent ingest jobs with progress telemetry |
| `/api/ingest/jobs/{job_id}` | GET | Job metadata, status, and summary statistics |
| `/api/ingest/jobs/{job_id}/detections` | GET | Paginated detections with `?since_frame=` parameter |
| `/api/ingest/jobs/{job_id}/tracks` | GET | Fused per-vehicle tracking consensus |
| `/api/ingest/jobs/{job_id}/video` | GET | Streams original video with HTTP Range header support |
| `/api/ingest/jobs/{job_id}/annotated` | GET | Streams annotated MP4 output |
| `/ws/ingest/{job_id}` | WebSocket | Real-time live frame/detection event stream |

*Note: HTTP Range header support is mandatory to enable smooth scrubbing in Chrome and Safari `<video>` elements.*

### 1.3 Annotated Video Output
- Write `data/uploads/{job_id}_annotated.mp4` using OpenCV `VideoWriter`.
- Fallback/Post-process with `ffmpeg -y -i raw.mp4 -c:v libx264 -pix_fmt yuv420p final.mp4` to ensure browser compatibility.
- Frame Annotations:
  - Vehicle bounding box (2px, color-coded by `track_id`).
  - Label bar: `#track_id · class · color`.
  - Plate bounding box in amber, with `PLATE · confidence` banner.
  - Corner HUD: `frame i/N · t=12.4s · tracks=7 · plates=4`.
  - Red flashing border + `⚠ WATCHLIST HIT` banner when a hotlist target triggers.
- Persist identical geometry in `bbox_json` so the client canvas can redraw overlays in real time.

### 1.4 WebSocket Protocol Specification
JSON envelopes sent over `/ws/ingest/{job_id}`:
```json
{"type": "progress", "done": 420, "total": 3000, "fps_proc": 11.3, "eta_s": 38}
{"type": "detection", "frame_idx": 418, "video_ts": 16.72, "track_id": 7, "bbox": [812, 430, 1044, 612], "plate_bbox": [880, 560, 980, 590], "plate_raw": "TS09AB1234", "plate_conf": 0.91, "blur": 142.0, "vehicle_class": "motorcycle", "color": "black", "crop_url": "/static/evidence/..."}
{"type": "fused", "track_id": 7, "plate": "TS09AB1234", "conf": 0.96, "n_frames": 14}
{"type": "alert", "plate": "TS09AB1234", "category": "STOLEN_VEHICLE", "priority": "CRITICAL"}
{"type": "done", "stats": {"tracks": 9, "plates_read": 6, "alerts": 1, "wall_s": 41.2}}
```
- Server maintains a `collections.deque(maxlen=2000)` buffer per job to replay missed events to late-joining clients.

### 1.5 Main Trajectory Pipeline Materialization
- For each track in `job_tracks` where `fused_conf >= 0.60`, insert a structured observation into the primary `vehicle_events` table using `ingest_jobs.camera_id` and timestamp `job.started_at + video_ts`.
- **Demo Choreography:** Evaluator uploads 3 clips of target vehicle `TS09AB1234` at Begumpet (`C101`), Secunderabad (`C107`), and Panjagutta (`C115`). Clicking *"Build Trajectory from Ingest Jobs"* renders the full cross-camera path directly onto the Live Map.

### 1.6 Scan Theatre UI (`backend/app/static/scan.html` & Command Center Tab)
- Split-screen theater:
  - Left: Video player with overlaid responsive `<canvas>` rendering bounding boxes in real time. Mode toggle: **LIVE** (canvas synced to WebSocket) vs **REVIEW** (canvas synced to `timeupdate` $\pm 60\text{ms}$).
  - Bottom: Processing progress bar, elapsed frames, processing FPS, and ETA countdown.
  - Right: Real-time detection card feed and fused track summaries. Clicking any detection card seeks video to `video_ts` and displays the 4-artifact forensic lightbox.
- Audio & Visual Triggers: Watchlist hits fire the tactical audio chirp and display high-visibility alerts.

**Acceptance Check:** Upload 40s 1080p clip $\rightarrow$ progress advances within 3s $\rightarrow \ge 1$ plate card appears $\rightarrow$ `job_tracks` populated $\rightarrow$ annotated video plays smoothly with Range requests $\rightarrow$ 3-clip trajectory reconstructs on map.

---

## PHASE 2 — Appearance Re-Identification (ReID)

**Goal:** Graceful degradation for muddy, obscured, angled, or missing plates.

### 2.1 ReID Embedding Module (`backend/app/perception/reid.py`)
- Load `osnet_x0_25` (via `torchreid`) or MobileNetV3 (`timm`) with classifier head stripped (~3 MB, CPU optimized).
- `embed(crop)` $\rightarrow$ $\mathbb{R}^{512}$ float32, L2-normalized vector. Batched inference (16 crops/pass).
- For each track, compute and store the mean embedding of the 3 sharpest crops as `BLOB` (`np.tobytes()`).

### 2.2 Re-weighted Multi-Signal Graph Link Solver
Update $S_{\text{link}}$:
$$S_{\text{link}} = 0.35 \cdot S_{\text{plate}} + 0.15 \cdot S_{\text{attr}} + 0.25 \cdot S_{\text{time}} + 0.25 \cdot S_{\text{reid}}$$
If plate text is missing on either node:
$$S_{\text{link}} = 0.55 \cdot S_{\text{reid}} + 0.30 \cdot S_{\text{time}} + 0.15 \cdot S_{\text{attr}}$$
*(Classification capped at `PROBABLE`, never `CONFIRMED` without plate consensus).*

### 2.3 Appearance Search Endpoint
- `POST /api/search/appearance`: Body `{det_id, threshold=0.75, time_window_min=30}`. Returns ranked matching vehicles across all cameras based on cosine distance.
- Add *"Find Similar Vehicles"* button on all detection cards.

---

## PHASE 3 — Accuracy Benchmarks & Empirical Ground Truth

**Goal:** Transform reported confidence metrics into rigorous empirical accuracy.

### 3.1 Ground Truth Dataset (`benchmarks/ground_truth.csv`)
- Minimum 200 hand-labeled frames across the 5 sample videos: `video_id, frame_idx, x1, y1, x2, y2, plate_text, vehicle_class, color`.

### 3.2 Automated Evaluation Runner (`benchmarks/run_benchmark.py`)
Generates `benchmarks/results.md` calculating:
1. **Detection Quality:** Precision, Recall, F1 @ IoU 0.5 (greedy Hungarian matching).
2. **Plate Recognition:** Character Error Rate ($\text{CER} = \frac{\text{Levenshtein}}{\text{len}(gt)}$) and exact-match accuracy rate.
3. **CLAHE Impact Breakdown:** Exact-match rate segmented by blur-score quartiles.
4. **Trajectory Link Quality:** Link Precision, Recall, and False-Link Rate.
5. **Threshold Sweep:** Empirical validation justifying `CONFIRMED` ($\ge 0.85$) vs `PROBABLE` ($0.60 - 0.85$) cutoffs.

### 3.3 Ablation Study (`benchmarks/ablation.py`)
- Evaluates link reconstruction F1 score with each term ($S_{\text{plate}}, S_{\text{attr}}, S_{\text{time}}, S_{\text{reid}}$) zeroed out to defend formula weights to judges.

---

## PHASE 4 — Trust, Audit & Legal Defensibility (DPDP Act 2023)

### 4.1 Operator Confirmation Gate
- Extend `alerts` schema:
```sql
ALTER TABLE alerts ADD COLUMN review_state TEXT DEFAULT 'PENDING'; -- PENDING | CONFIRMED | REJECTED
ALTER TABLE alerts ADD COLUMN reviewed_by TEXT;
ALTER TABLE alerts ADD COLUMN reviewed_at TEXT;
ALTER TABLE alerts ADD COLUMN reject_reason TEXT;
```
- Endpoint `POST /api/alerts/{id}/review` $\rightarrow$ `{decision, officer_id, reason}`.
- Alerts land in `PENDING` state (amber indicator) and cannot dispatch until confirmed. Rejected alerts populate a searchable false-positive log.

### 4.2 Query Audit Logging & Mandatory Case Reference
```sql
CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT,
  officer_id TEXT NOT NULL,
  role TEXT NOT NULL,
  action TEXT NOT NULL,
  target TEXT,
  case_ref TEXT NOT NULL,  -- Mandatory FIR / Investigation ID
  justification TEXT,
  ip TEXT,
  prev_hash TEXT,
  row_hash TEXT
);
```
- FastAPI middleware intercepts every plate search, history lookup, report export, and appearance query. Queries without a valid `case_ref` are rejected (HTTP 400).
- Dedicated `/audit` read-only log view in the command center.

### 4.3 Cryptographic Merkle Hash Chain
- Replace static checksums with an immutable append-only hash chain:
$$\text{row\_hash}_i = \text{SHA-256}\left(\text{row\_hash}_{i-1} \parallel \text{canonical\_json}(\text{payload}_i)\right)$$
- Genesis block: 64 zeros.
- Endpoint `GET /api/integrity/verify` returns `{valid: bool, rows_checked: int, first_break_at: Optional[int]}`.
- UI displays a live glowing `CHAIN INTACT` badge. Live tampering demo endpoint available.

### 4.4 Role-Based Access Control (RBAC)
- 3 Roles: `VIEWER` (traffic analytics only), `OFFICER` (search, inspect, review), `ADMIN` (watchlist management, retention purge).
- JWT auth with role claims and `@require_role(...)` FastAPI dependencies.

---

## PHASE 5 — Strategic Differentiators

### 5.1 Convoy & Tailing Vehicle Detection
- `GET /api/analysis/convoy/{plate}?window_s=120&min_cooccur=3`: SQL self-join finding companion plates appearing at $\ge 3$ consecutive cameras within $\pm 120\text{s}$.
- Displays companion vehicle panel and dashed convoy corridors on the map.

### 5.2 Learned Markov Route Prediction
- Computes transition matrix $P(\text{cam}_{j} \mid \text{cam}_{i})$ from historical observation transitions with Laplace smoothing and peak/off-peak time-of-day bucketing.
- Upgrades 60° geometric cone into ranked candidate corridors: e.g., `C123 — 71% — ETA 4.2 min`. Falls back to cone when observations $< 10$.

### 5.3 Edge Store-and-Forward Outbox
- Edge client writes telemetry to local SQLite outbox on network failure; replays in sequence with exponential backoff on reconnection. Server deduplicates on `event_uuid`.

### 5.4 National Agency Integration Adapters (`backend/app/integrations/`)
- Typed schemas and mock providers for **VAHAN** (vehicle registration), **CCTNS** (police criminal tracking), **eChallan** (traffic fines), and **DIAL 112** (emergency response dispatch), controlled via `INTEGRATION_MODE=mock|live`.

---

## PHASE 6 — Performance & Scale Benchmarks

### 6.1 Benchmark Metrics (`benchmarks/perf_test.py`)
- Edge processing FPS across 720p, 1080p, and 4K resolutions on test hardware.
- End-to-end latency budget breakdown (Capture $\rightarrow$ Detect $\rightarrow$ OCR $\rightarrow$ Ingest $\rightarrow$ Persist $\rightarrow$ Alert, p50/p95).
- Queue load testing driving `ingestion_queue` to 10k items with event-drop metrics under saturation.
- SQLite sustained write IOPS ceiling.

### 6.2 Scale Architecture Defense
- Clear documentation for 4,000+ camera urban deployments:
  - Transition path to PostgreSQL / TimescaleDB hypertables.
  - Apache Kafka / Redis Streams distributed message broker.
  - Horizontally scalable stateless worker containers.

---

## PHASE 7 — Repository Hygiene & Presentation Readiness

1. **Plate Inconsistency Resolution:** Standardize the Bhopal sample vehicle plate across all documentation, tests, and databases to `MP04CY8591` (or `MP04CC6099` based on video inspection).
2. **Native Pytest Execution:** Add `pyproject.toml` with `[tool.pytest.ini_options] pythonpath = ["."]`. Ensure `pytest -v` runs cleanly without manual sys.path hacks.
3. **CI Pipeline:** Create `.github/workflows/ci.yml` running linting and tests across Python 3.10 and 3.11.
4. **Offline Demo Mode (`DEMO_MODE=1`):** `python scripts/seed_demo.py` loads cached video job results and annotated clips so presentations execute flawlessly without network dependencies.
5. **Architectural Blueprint:** Maintain `docs/ARCHITECTURE.md` with complete tier diagrams, contracts, and migration maps.

---

## 8-Minute SIH Jury Demo Choreography

| Timestamp | Presentation Action | Key Narrative |
| :--- | :--- | :--- |
| **0:00 - 0:30** | Problem Framing | Traditional surveillance requires manual scrubbing across fragmented cameras; suspect vehicles escape into blind spots. |
| **0:30 - 2:00** | Live Video Upload & Scan Theatre | Upload real 1080p video. ByteTrack locks onto vehicles, CLAHE enhances blurred plates, Bayesian consensus fuses characters in real time. |
| **2:00 - 3:00** | Watchlist Alert & Officer Confirmation | Hotlist match triggers audio chirp. Alert appears as `PENDING`. Officer inspects 4-crop evidence lightbox and enters mandatory case reference to confirm dispatch. |
| **3:00 - 4:30** | Multi-Camera Trajectory Assembly | Evaluator uploads clips from 2 additional cameras. Click *"Build Trajectory"*. Road route draws on map with Panjagutta arterial corridor and offline camera gap bridging. |
| **4:30 - 5:30** | Markov Predictive Interception & Convoy | Engine projects high-probability escape routes with ETAs; convoy panel highlights a companion vehicle tailing the target. |
| **5:30 - 6:30** | Velocity Guard & Appearance ReID | Engine rejects cross-city anomaly ($6,902\text{ km/h}$). Demonstrates plate-free appearance search on an obscured vehicle crop. |
| **6:30 - 7:30** | Cryptographic Audit & DPDP Compliance | Show immutable hash chain (`CHAIN INTACT`). Demonstrate tampering detection. Show accuracy benchmark F1 curves and ablation matrix. |
| **7:30 - 8:00** | Scale Architecture & Q&A | Review 4,000-camera scale migration roadmap and answer evaluator questions. |
