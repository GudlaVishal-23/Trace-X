import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.database import engine, Base, SessionLocal
from backend.app.models import Camera, Watchlist, VehicleEvent, Alert
from backend.app.api import cameras, events, vehicles, traffic, alerts, reports, ws, videos
from backend.app.routers import ingest
from backend.app.services.queue import ingestion_queue
from datetime import datetime, timezone, timedelta

# Auto-seed sample data if tables are empty
def seed_initial_data():
    db = SessionLocal()
    try:
        if db.query(Camera).count() == 0:
            sample_cams = [
                Camera(camera_id="C101", name="Begumpet Flyover Northbound", latitude=17.4435, longitude=78.4682, road_id="RD_BEGUMPET_MAIN", direction="north", status="online", quality_score=0.96),
                Camera(camera_id="C107", name="Secunderabad Station Jct", latitude=17.4320, longitude=78.4550, road_id="RD_SECUNDERABAD_ARTERIAL", direction="north", status="online", quality_score=0.65),
                Camera(camera_id="C112", name="Paradise Circle Southbound", latitude=17.4410, longitude=78.4870, road_id="RD_PARADISE_CORRIDOR", direction="east", status="offline", quality_score=0.00),
                Camera(camera_id="C115", name="Panjagutta Central Circle", latitude=17.4285, longitude=78.4510, road_id="RD_PANJAGUTTA_MAIN", direction="south", status="online", quality_score=0.92),
                Camera(camera_id="C118", name="Secretariat Gateway West", latitude=17.4110, longitude=78.4710, road_id="RD_LAKDIKAPUL_LINK", direction="south", status="online", quality_score=0.94),
                Camera(camera_id="C123", name="Mehdipatnam Express Interchange", latitude=17.3915, longitude=78.4410, road_id="RD_PVNR_EXPRESSWAY", direction="south", status="online", quality_score=0.95),
                Camera(camera_id="C130", name="Hitec City Cyber Towers Jct", latitude=17.4504, longitude=78.3808, road_id="RD_MADHAPUR_FLYOVER", direction="west", status="online", quality_score=0.91),
                Camera(camera_id="C135", name="Gachibowli Stadium Gateway", latitude=17.4401, longitude=78.3489, road_id="RD_GACHIBOWLI_MAIN", direction="west", status="online", quality_score=0.89)
            ]
            db.add_all(sample_cams)

        if db.query(Watchlist).count() == 0:
            sample_watchlist = [
                Watchlist(plate_text="DL9CAB5561", category="SUSPECT", priority="CRITICAL", case_reference="FIR-2026-DEL-8812", notes="Commercial cab wanted in interstate cargo theft probe. High-risk flight vector."),
                Watchlist(plate_text="MH08AP3746", category="STOLEN_VEHICLE", priority="CRITICAL", case_reference="FIR-2026-MUM-4419", notes="Stolen white hatchback reported at Marine Drive; cross-corridor evasion alert."),
                Watchlist(plate_text="WB04G5786", category="TRAFFIC_VIOLATOR", priority="HIGH", case_reference="ECHALLAN-2026-KOL-902", notes="Kolkata luxury sedan clocked exceeding corridor limit by 52 km/h; expired permit."),
                Watchlist(plate_text="MP04CY8591", category="SUSPECT", priority="HIGH", case_reference="CRIME-2026-MP-3011", notes="Bhopal commercial transit van wanted in cash transport robbery evasion."),
                Watchlist(plate_text="TS09ZOMATO", category="STOLEN_VEHICLE", priority="CRITICAL", case_reference="FIR-2026-HYD-7704", notes="Rapid delivery two-wheeler stolen during active dispatch; suspected cloned livery."),
                Watchlist(plate_text="TS09AB1234", category="STOLEN_VEHICLE", priority="CRITICAL", case_reference="FIR-2026-HYD-4091", notes="Black Yamaha R15 stolen from metro station; fleeing south."),
                Watchlist(plate_text="DL01CA9999", category="SUSPECT", priority="HIGH", case_reference="CRIME-2026-DEL-102", notes="White Toyota Fortuner wanted in commercial burglary investigation."),
                Watchlist(plate_text="MH12XY7788", category="TRAFFIC_VIOLATOR", priority="MEDIUM", case_reference="ECHALLAN-88902", notes="Repeated dangerous driving and reckless lane cut-offs.")
            ]
            db.add_all(sample_watchlist)

        if db.query(VehicleEvent).count() <= 4:
            t0 = datetime.now(timezone.utc) - timedelta(minutes=35)
            target_events = [
                VehicleEvent(event_id="EVT_001", camera_id="C101", timestamp=t0, plate_text="TS09AB1234", plate_confidence=0.96, observation_status="CONFIRMED", vehicle_type="motorcycle", vehicle_color="black", vehicle_make="Yamaha", vehicle_model="R15", direction="north", latitude=17.4435, longitude=78.4682, road_id="RD_BEGUMPET_MAIN", image_quality_score=95.0, detection_confidence=0.96),
                VehicleEvent(event_id="EVT_002", camera_id="C107", timestamp=t0 + timedelta(minutes=6), plate_text="TS09A?1234", plate_confidence=0.61, observation_status="PROBABLE", vehicle_type="motorcycle", vehicle_color="black", vehicle_make="Yamaha", vehicle_model="R15", direction="north", latitude=17.4320, longitude=78.4550, road_id="RD_SECUNDERABAD_ARTERIAL", image_quality_score=62.0, detection_confidence=0.88),
                VehicleEvent(event_id="EVT_003", camera_id="C115", timestamp=t0 + timedelta(minutes=15), plate_text="TS09AB1234", plate_confidence=0.94, observation_status="CONFIRMED", vehicle_type="motorcycle", vehicle_color="black", vehicle_make="Yamaha", vehicle_model="R15", direction="south", latitude=17.4285, longitude=78.4510, road_id="RD_PANJAGUTTA_MAIN", image_quality_score=92.0, detection_confidence=0.94),
                VehicleEvent(event_id="EVT_004", camera_id="C123", timestamp=t0 + timedelta(minutes=24), plate_text="TS09AB1234", plate_confidence=0.95, observation_status="CONFIRMED", vehicle_type="motorcycle", vehicle_color="black", vehicle_make="Yamaha", vehicle_model="R15", direction="south", latitude=17.3915, longitude=78.4410, road_id="RD_PVNR_EXPRESSWAY", image_quality_score=94.0, detection_confidence=0.95),

                # Presets for DL01CA9999 (White Toyota Fortuner)
                VehicleEvent(event_id="EVT_005", camera_id="C135", timestamp=t0 + timedelta(minutes=5), plate_text="DL01CA9999", plate_confidence=0.97, observation_status="CONFIRMED", vehicle_type="suv", vehicle_color="white", vehicle_make="Toyota", vehicle_model="Fortuner", direction="west", latitude=17.4401, longitude=78.3489, road_id="RD_GACHIBOWLI_MAIN", image_quality_score=96.0, detection_confidence=0.97),
                VehicleEvent(event_id="EVT_006", camera_id="C130", timestamp=t0 + timedelta(minutes=18), plate_text="DL01CA9999", plate_confidence=0.93, observation_status="CONFIRMED", vehicle_type="suv", vehicle_color="white", vehicle_make="Toyota", vehicle_model="Fortuner", direction="east", latitude=17.4504, longitude=78.3808, road_id="RD_MADHAPUR_FLYOVER", image_quality_score=91.0, detection_confidence=0.93),

                # Presets for MH12XY7788 (Grey Swift Reckless Violator)
                VehicleEvent(event_id="EVT_007", camera_id="C101", timestamp=t0 + timedelta(minutes=8), plate_text="MH12XY7788", plate_confidence=0.92, observation_status="CONFIRMED", vehicle_type="car", vehicle_color="grey", vehicle_make="Maruti Suzuki", vehicle_model="Swift", direction="south", latitude=17.4435, longitude=78.4682, road_id="RD_BEGUMPET_MAIN", image_quality_score=89.0, detection_confidence=0.92),
                VehicleEvent(event_id="EVT_008", camera_id="C118", timestamp=t0 + timedelta(minutes=22), plate_text="MH12XY7788", plate_confidence=0.95, observation_status="CONFIRMED", vehicle_type="car", vehicle_color="grey", vehicle_make="Maruti Suzuki", vehicle_model="Swift", direction="south", latitude=17.4110, longitude=78.4710, road_id="RD_LAKDIKAPUL_LINK", image_quality_score=93.0, detection_confidence=0.95)
            ]
            for ev in target_events:
                if not db.query(VehicleEvent).filter(VehicleEvent.event_id == ev.event_id).first():
                    db.add(ev)

            # Seed Operational Alerts for real vehicles & targets
            alerts_data = [
                Alert(alert_type="WATCHLIST_MATCH", plate_text="DL9CAB5561", camera_id="C101", timestamp=t0 + timedelta(minutes=31), confidence=0.98, reason="CRITICAL HOTLIST MATCH: Delhi commercial cab (DL9CAB5561) detected at C101 (Begumpet Main). Matched interstate cargo theft FIR-2026-DEL-8812.", status="NEW"),
                Alert(alert_type="STOLEN_VEHICLE", plate_text="MH08AP3746", camera_id="C115", timestamp=t0 + timedelta(minutes=27), confidence=0.96, reason="STOLEN VEHICLE ALERT: Maharashtra hatchback (MH08AP3746) spotted at C115 (Panjagutta Circle). Rapid interception vector active.", status="NEW"),
                Alert(alert_type="RECKLESS_SPEED", plate_text="WB04G5786", camera_id="C123", timestamp=t0 + timedelta(minutes=23), confidence=0.94, reason="SPEED VIOLATION: Clocked at 118 km/h in 60 km/h zone on PVNR Expressway corridor (C123). Expired commercial permit.", status="NEW"),
                Alert(alert_type="ROUTE_ANOMALY", plate_text="MP04CY8591", camera_id="C130", timestamp=t0 + timedelta(minutes=19), confidence=0.93, reason="ROUTE ANOMALY & HOTLIST: Bhopal transit van (MP04CY8591) taking erratic feeder detour near Cyber Towers (C130).", status="NEW"),
                Alert(alert_type="STOLEN_VEHICLE", plate_text="TS09ZOMATO", camera_id="C107", timestamp=t0 + timedelta(minutes=14), confidence=0.97, reason="HOTLIST INTERCEPT: Red delivery two-wheeler (TS09ZOMATO) detected at C107 (Secunderabad Station). Stolen courier bike alert.", status="NEW"),
                Alert(alert_type="STOLEN_VEHICLE", plate_text="TS09AB1234", camera_id="C123", timestamp=t0 + timedelta(minutes=24), confidence=0.95, reason="CRITICAL HOTLIST: Stolen Black Yamaha R15 detected at C123 (PVNR Expressway Southbound).", status="NEW"),
                Alert(alert_type="SUSPECT_EVASION", plate_text="DL01CA9999", camera_id="C130", timestamp=t0 + timedelta(minutes=18), confidence=0.93, reason="HIGH PRIORITY: White Fortuner wanted in commercial burglary detected at C130 (Cyber Towers).", status="NEW"),
                Alert(alert_type="RECKLESS_SPEED", plate_text="MH12XY7788", camera_id="C118", timestamp=t0 + timedelta(minutes=22), confidence=0.95, reason="SPEED VIOLATION: Clocked at 114 km/h in 60 km/h zone on Lakdikapul arterial corridor.", status="NEW")
            ]
            for a in alerts_data:
                if not db.query(Alert).filter(Alert.plate_text == a.plate_text).first():
                    db.add(a)

        db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Capture the running event loop for thread worker WebSocket dispatch
    import asyncio
    from backend.app.ingest import video_worker
    video_worker.MAIN_EVENT_LOOP = asyncio.get_running_loop()

    # Create tables automatically on startup
    Base.metadata.create_all(bind=engine)
    seed_initial_data()
    await ingestion_queue.start_worker()
    yield
    await ingestion_queue.stop_worker()

app = FastAPI(
    title="TRACE-X Intelligence API",
    description="City-Wide AI Engine for Multi-Camera ANPR Trajectory Tracking & Urban Traffic Analytics (SIH26127)",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(cameras.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(vehicles.router, prefix="/api")
app.include_router(traffic.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(ws.router, prefix="/api")
app.include_router(videos.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(ingest.ws_router)

# Mount Static Files & Web Dashboard
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

SAMPLE_VIDEOS_DIR = Path(os.getcwd()) / "sample videos"
if SAMPLE_VIDEOS_DIR.exists():
    app.mount("/sample_videos", StaticFiles(directory=SAMPLE_VIDEOS_DIR), name="sample_videos")

UPLOADS_DIR = Path(os.getcwd()) / "data" / "uploads"
if UPLOADS_DIR.exists():
    app.mount("/data/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

@app.get("/")
def serve_dashboard():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"status": "online", "message": "TRACE-X API is active. Open /docs for Swagger specifications."}

@app.get("/style.css")
def serve_style():
    style_path = STATIC_DIR / "style.css"
    if style_path.exists():
        return FileResponse(style_path, media_type="text/css")
    return {"status": "error"}

@app.get("/app.js")
def serve_app_js():
    js_path = STATIC_DIR / "app.js"
    if js_path.exists():
        return FileResponse(js_path, media_type="application/javascript")
    return {"status": "error"}

@app.get("/scan")
def serve_scan_theatre():
    scan_path = STATIC_DIR / "scan.html"
    if scan_path.exists():
        response = FileResponse(scan_path)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return {"status": "error", "message": "Scan theatre UI not found"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "tracex-intelligence-engine"}
