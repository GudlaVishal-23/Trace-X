from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import VehicleEvent, Camera
from backend.app.schemas import TrajectoryHistoryResponse
from backend.app.services.trajectory import solve_trajectory

router = APIRouter(prefix="/vehicles", tags=["Vehicle Trajectory Search"])

@router.get("/{plate}/history", response_model=TrajectoryHistoryResponse)
@router.get("/{plate}/trajectory", response_model=TrajectoryHistoryResponse)
def get_vehicle_trajectory(
    plate: str,
    include_gaps: bool = Query(True, description="Include interpolated camera gaps"),
    db: Session = Depends(get_db)
):
    # Fetch all events matching this plate (exact or fuzzy normalized)
    clean_plate = plate.upper().replace(" ", "").replace("-", "")
    events = db.query(VehicleEvent).filter(
        VehicleEvent.plate_text.ilike(f"%{clean_plate}%")
    ).order_by(VehicleEvent.timestamp.asc()).all()

    if not events:
        raise HTTPException(status_code=404, detail=f"No vehicle observations found for plate: {plate}")

    # Identify any offline cameras to support camera gap bridging
    offline_cameras = [c.camera_id for c in db.query(Camera).filter(Camera.status == "offline").all()]

    # Convert SQLAlchemy models to dicts for graph solver
    obs_list = []
    for e in events:
        obs_list.append({
            "event_id": e.event_id,
            "camera_id": e.camera_id,
            "timestamp": e.timestamp,
            "plate_text": e.plate_text,
            "plate_confidence": e.plate_confidence,
            "observation_status": e.observation_status,
            "vehicle_type": e.vehicle_type,
            "vehicle_color": e.vehicle_color,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "image_quality_score": e.image_quality_score,
            "thumbnail_url": e.thumbnail_url
        })

    trajectory = solve_trajectory(obs_list, offline_cameras if include_gaps else None)
    return trajectory
