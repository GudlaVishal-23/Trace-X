import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, BackgroundTasks, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import VehicleEvent, Watchlist, Alert
from backend.app.schemas import VehicleEventResponse, VehicleEventCreate
from backend.app.api.ws import ws_manager
from backend.app.services.queue import ingestion_queue

router = APIRouter(prefix="/events", tags=["Vehicle Events"])

@router.get("", response_model=List[VehicleEventResponse])
def list_events(
    plate: Optional[str] = None,
    camera_id: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(VehicleEvent)
    if plate:
        query = query.filter(VehicleEvent.plate_text.ilike(f"%{plate}%"))
    if camera_id:
        query = query.filter(VehicleEvent.camera_id == camera_id)
    if vehicle_type:
        query = query.filter(VehicleEvent.vehicle_type == vehicle_type)
    return query.order_by(VehicleEvent.timestamp.desc()).offset(offset).limit(limit).all()

@router.post("", response_model=VehicleEventResponse, status_code=201)
async def ingest_event(
    payload: VehicleEventCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    event_dict = payload.model_dump()
    if not event_dict.get("event_id"):
        event_dict["event_id"] = f"evt_{uuid.uuid4().hex[:12]}"

    event = VehicleEvent(**event_dict)
    db.add(event)

    # Automated Watchlist Interception Check
    matched_alert = None
    if event.plate_text:
        match = db.query(Watchlist).filter(
            Watchlist.plate_text == event.plate_text,
            Watchlist.status == "ACTIVE"
        ).first()
        if match:
            alert = Alert(
                alert_type="WATCHLIST_MATCH",
                plate_text=event.plate_text,
                camera_id=event.camera_id,
                timestamp=event.timestamp or datetime.now(timezone.utc),
                confidence=event.plate_confidence,
                reason=f"Matched target on active police watchlist ({match.category}) - Ref: {match.case_reference}",
                status="NEW"
            )
            db.add(alert)
            matched_alert = {
                "alert_type": alert.alert_type,
                "plate_text": alert.plate_text,
                "camera_id": alert.camera_id,
                "timestamp": alert.timestamp.isoformat() if hasattr(alert.timestamp, "isoformat") else str(alert.timestamp),
                "confidence": alert.confidence,
                "reason": alert.reason,
                "priority": match.priority,
                "case_reference": match.case_reference
            }

    db.commit()
    db.refresh(event)

    # Real-time WebSocket Push Notification
    serialized_event = {
        "event_id": event.event_id,
        "camera_id": event.camera_id,
        "timestamp": event.timestamp.isoformat() if hasattr(event.timestamp, "isoformat") else str(event.timestamp),
        "plate_text": event.plate_text,
        "plate_confidence": event.plate_confidence,
        "observation_status": event.observation_status,
        "vehicle_type": event.vehicle_type,
        "vehicle_color": event.vehicle_color,
        "vehicle_make": event.vehicle_make,
        "vehicle_model": event.vehicle_model,
        "direction": event.direction,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "road_id": event.road_id,
        "image_quality_score": event.image_quality_score,
        "detection_confidence": event.detection_confidence
    }
    background_tasks.add_task(ws_manager.broadcast_event, serialized_event)
    if matched_alert:
        background_tasks.add_task(ws_manager.broadcast_alert, matched_alert)

    return event

@router.post("/async", status_code=202)
async def ingest_event_async(
    payload: VehicleEventCreate,
    x_signature: Optional[str] = Header(None, alias="X-Signature")
):
    event_dict = payload.model_dump()
    if not event_dict.get("event_id"):
        event_dict["event_id"] = f"evt_{uuid.uuid4().hex[:12]}"

    enqueued = await ingestion_queue.enqueue(event_dict, signature=x_signature)
    if not enqueued:
        return JSONResponse(status_code=400, content={"status": "rejected", "message": "Queue full or invalid signature"})
    return {"status": "enqueued", "event_id": event_dict["event_id"]}
