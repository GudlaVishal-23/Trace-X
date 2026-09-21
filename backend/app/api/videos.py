import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from backend.app.database import get_db
from backend.app.models import VehicleEvent, Watchlist, Alert, Camera
from backend.app.api.ws import ws_manager
from backend.app.services.anpr import assess_image_quality, enhance_plate_crop, fuse_multiframe_reads

router = APIRouter(prefix="/videos", tags=["Sample Videos ANPR Verification"])

SAMPLE_VIDEOS_CATALOG = [
    {
        "id": "vid_dl_01",
        "title": "New Delhi - Connaught Place Traffic Stream",
        "city": "New Delhi",
        "camera_id": "CAM_DL_01",
        "camera_name": "New Delhi Connaught Place North",
        "road_id": "RD_CONNAUGHT_CIRCUS",
        "filename": "5009674-hd_1920_1080_25fps.mp4",
        "video_url": "/sample_videos/5009674-hd_1920_1080_25fps.mp4",
        "detected_plate": "DL9CAB5561",
        "vehicle_type": "car",
        "vehicle_make": "Maruti Suzuki",
        "vehicle_model": "Alto",
        "vehicle_color": "silver",
        "speed_kmh": 42.5,
        "quality_score": 62.2,
        "blur_score": 0.53,
        "observation_status": "CONFIRMED",
        "confidence": 0.98,
        "watchlist_target": True,
        "annotated_url": "/static/evidence/annotated_DL9CAB5561.jpg",
        "vehicle_url": "/static/evidence/test_v_DL9CAB5561.jpg",
        "plate_url": "/static/evidence/test_p_DL9CAB5561.jpg",
        "notes": "Frontal angle daylight capture. High sharpness, zero perspective skew."
    },
    {
        "id": "vid_mh_01",
        "title": "Mumbai - Western Express Arterial Corridor",
        "city": "Mumbai",
        "camera_id": "CAM_MH_01",
        "camera_name": "Mumbai Western Express Corridor",
        "road_id": "RD_WESTERN_EXPRESS",
        "filename": "13020050_3840_2160_30fps.mp4",
        "video_url": "/sample_videos/13020050_3840_2160_30fps.mp4",
        "detected_plate": "MH08AP3746",
        "vehicle_type": "truck",
        "vehicle_make": "Tata",
        "vehicle_model": "Intra V30",
        "vehicle_color": "white",
        "speed_kmh": 0.0,
        "quality_score": 40.8,
        "blur_score": 0.01,
        "observation_status": "CONFIRMED",
        "confidence": 0.94,
        "watchlist_target": True,
        "annotated_url": "/static/evidence/annotated_MH08AP3746.jpg",
        "vehicle_url": "/static/evidence/test_v_MH08AP3746.jpg",
        "plate_url": "/static/evidence/test_p_MH08AP3746.jpg",
        "notes": "Commercial transport vehicle with yellow license plate under flyover shadow."
    },
    {
        "id": "vid_wb_01",
        "title": "Kolkata - Central Transit Junction",
        "city": "Kolkata",
        "camera_id": "CAM_WB_01",
        "camera_name": "Kolkata Central Transit Circle",
        "road_id": "RD_KOLKATA_MG_WAY",
        "filename": "13926703_3840_2160_24fps.mp4",
        "video_url": "/sample_videos/13926703_3840_2160_24fps.mp4",
        "detected_plate": "WB04G5786",
        "vehicle_type": "auto_rickshaw",
        "vehicle_make": "Bajaj",
        "vehicle_model": "RE Compact",
        "vehicle_color": "green",
        "speed_kmh": 26.0,
        "quality_score": 59.5,
        "blur_score": 0.04,
        "observation_status": "CONFIRMED",
        "confidence": 0.92,
        "watchlist_target": False,
        "annotated_url": "/static/evidence/annotated_WB04G5786.jpg",
        "vehicle_url": "/static/evidence/test_v_WB04G5786.jpg",
        "plate_url": "/static/evidence/test_p_WB04G5786.jpg",
        "notes": "Two-line commercial auto-rickshaw plate, high contrast green/yellow body."
    },
    {
        "id": "vid_mp_01",
        "title": "Bhopal - National Highway Elevated Section",
        "city": "Bhopal",
        "camera_id": "CAM_MP_01",
        "camera_name": "Bhopal National Highway Flyover",
        "road_id": "RD_BHOPAL_EXPRESS",
        "filename": "14571138_3840_2160_60fps.mp4",
        "video_url": "/sample_videos/14571138_3840_2160_60fps.mp4",
        "detected_plate": "MP04CC6099",
        "vehicle_type": "car",
        "vehicle_make": "Maruti Suzuki",
        "vehicle_model": "WagonR",
        "vehicle_color": "white",
        "speed_kmh": 54.0,
        "quality_score": 90.0,
        "blur_score": 0.81,
        "observation_status": "CONFIRMED",
        "confidence": 0.96,
        "watchlist_target": False,
        "annotated_url": "/static/evidence/annotated_MP04CY8591.jpg",
        "vehicle_url": "/static/evidence/test_v_MP04CY8591.jpg",
        "plate_url": "/static/evidence/test_p_MP04CY8591.jpg",
        "notes": "Fast 60fps arterial highway stream. Crisp daylight edge clarity."
    },
    {
        "id": "vid_hyd_02",
        "title": "Hyderabad - Cyberabad High-Speed Delivery Corridor",
        "city": "Hyderabad",
        "camera_id": "CAM_HYD_02",
        "camera_name": "Cyberabad Hitec City Corridor",
        "road_id": "RD_HITEC_MAIN",
        "filename": "5614377-hd_1920_1080_25fps.mp4",
        "video_url": "/sample_videos/5614377-hd_1920_1080_25fps.mp4",
        "detected_plate": "TS09ZOMATO",
        "vehicle_type": "motorcycle",
        "vehicle_make": "Hero",
        "vehicle_model": "Splendor Plus",
        "vehicle_color": "red",
        "speed_kmh": 38.0,
        "quality_score": 56.7,
        "blur_score": 0.09,
        "observation_status": "PROBABLE",
        "confidence": 0.82,
        "watchlist_target": False,
        "annotated_url": "/static/evidence/annotated_TS09ZOMATO.jpg",
        "vehicle_url": "/static/evidence/test_v_TS09ZOMATO.jpg",
        "plate_url": "/static/evidence/test_p_TS09ZOMATO.jpg",
        "notes": "Stress test: High motion blur, dynamic foreground rider with CLAHE enhancement applied."
    }
]

@router.get("/catalog")
def get_sample_videos_catalog():
    """Returns the catalog of uploaded real-world sample videos with perception telemetry."""
    return {"status": "success", "count": len(SAMPLE_VIDEOS_CATALOG), "videos": SAMPLE_VIDEOS_CATALOG}

@router.post("/{video_id}/ingest")
async def ingest_sample_video_event(video_id: str, db: Session = Depends(get_db)):
    """
    Simulates real-time edge ANPR ingestion from the specified sample video into the TRACE-X database.
    Checks watchlists, creates alerts, and broadcasts live WebSockets.
    """
    video_item = next((v for v in SAMPLE_VIDEOS_CATALOG if v["id"] == video_id), None)
    if not video_item:
        raise HTTPException(status_code=404, detail="Video ID not found in sample catalog")

    # Camera record
    cam = db.query(Camera).filter(Camera.camera_id == video_item["camera_id"]).first()
    lat = cam.latitude if cam else 17.4435
    lon = cam.longitude if cam else 78.4682

    event_id = f"EVT_LIVE_{int(datetime.now().timestamp())}_{video_item['detected_plate'][:4]}"
    now = datetime.now(timezone.utc)

    # Create VehicleEvent record
    event = VehicleEvent(
        event_id=event_id,
        camera_id=video_item["camera_id"],
        timestamp=now,
        plate_text=video_item["detected_plate"],
        plate_confidence=video_item["confidence"],
        observation_status=video_item["observation_status"],
        vehicle_type=video_item["vehicle_type"],
        vehicle_color=video_item["vehicle_color"],
        vehicle_make=video_item["vehicle_make"],
        vehicle_model=video_item["vehicle_model"],
        direction="forward",
        latitude=lat,
        longitude=lon,
        road_id=video_item["road_id"],
        image_quality_score=video_item["quality_score"],
        detection_confidence=video_item["confidence"],
        thumbnail_url=video_item["annotated_url"]
    )
    db.add(event)

    # Check Watchlist for real-time alert trigger
    watchlist_entry = db.query(Watchlist).filter(
        Watchlist.plate_text == video_item["detected_plate"],
        Watchlist.status == "ACTIVE"
    ).first()

    alert_created = None
    if watchlist_entry:
        alert = Alert(
            alert_type="WATCHLIST_MATCH",
            plate_text=video_item["detected_plate"],
            camera_id=video_item["camera_id"],
            timestamp=now,
            confidence=video_item["confidence"],
            reason=f"[LIVE VIDEO STREAM DETECT] Match confirmed from {video_item['title']}. Priority: {watchlist_entry.priority}. Case Ref: {watchlist_entry.case_reference}",
            status="NEW",
            case_file_id=watchlist_entry.case_reference,
            officer_notes=watchlist_entry.notes
        )
        db.add(alert)
        alert_created = {
            "alert_type": "WATCHLIST_MATCH",
            "plate_text": video_item["detected_plate"],
            "category": watchlist_entry.category,
            "priority": watchlist_entry.priority,
            "camera_id": video_item["camera_id"],
            "camera_name": video_item["camera_name"],
            "notes": watchlist_entry.notes
        }

    db.commit()

    # Broadcast Live WebSocket Events
    event_payload = {
        "type": "NEW_EVENT",
        "data": {
            "event_id": event_id,
            "camera_id": video_item["camera_id"],
            "plate_text": video_item["detected_plate"],
            "vehicle_type": video_item["vehicle_type"],
            "vehicle_color": video_item["vehicle_color"],
            "timestamp": now.isoformat(),
            "quality_score": video_item["quality_score"],
            "thumbnail_url": video_item["annotated_url"],
            "observation_status": video_item["observation_status"]
        }
    }
    await ws_manager.broadcast_event(event_payload)

    if alert_created:
        alert_payload = {
            "type": "CRITICAL_ALERT",
            "data": alert_created
        }
        await ws_manager.broadcast_alert(alert_payload)

    return {
        "status": "success",
        "message": f"Edge ANPR event ingested from {video_item['title']}",
        "event_id": event_id,
        "plate_text": video_item["detected_plate"],
        "watchlist_hit": alert_created is not None,
        "alert": alert_created,
        "telemetry": {
            "quality_score": video_item["quality_score"],
            "blur_score": video_item["blur_score"],
            "speed_kmh": video_item["speed_kmh"],
            "vehicle": f"{video_item['vehicle_color'].title()} {video_item['vehicle_make']} {video_item['vehicle_model']}"
        }
    }
