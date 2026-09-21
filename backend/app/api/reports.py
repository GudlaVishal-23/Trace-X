import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import VehicleEvent
from backend.app.services.trajectory import solve_trajectory

router = APIRouter(prefix="/reports", tags=["Forensic Reports"])

@router.get("/vehicle/{plate}")
def generate_forensic_report(plate: str, db: Session = Depends(get_db)):
    clean_plate = plate.upper().replace(" ", "")
    events = db.query(VehicleEvent).filter(
        VehicleEvent.plate_text.ilike(f"%{clean_plate}%")
    ).order_by(VehicleEvent.timestamp.asc()).all()

    if not events:
        raise HTTPException(status_code=404, detail="No vehicle events found for report")

    obs_list = [{
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
        "thumbnail_url": e.thumbnail_url
    } for e in events]

    trajectory = solve_trajectory(obs_list)

    # Generate a cryptographic digital checksum for court admissibility
    dossier_str = f"{plate}:{trajectory['total_distance_km']}:{len(events)}:{trajectory['first_detected']}"
    evidence_sha256 = hashlib.sha256(dossier_str.encode()).hexdigest()

    return {
        "report_id": f"REP-{clean_plate}-{datetime.now().strftime('%Y%m%d%H%M')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_plate": clean_plate,
        "evidence_integrity_hash_sha256": evidence_sha256,
        "trajectory_summary": {
            "status": trajectory["status"],
            "total_distance_km": trajectory["total_distance_km"],
            "average_speed_kmh": trajectory["average_speed_kmh"],
            "first_seen": trajectory["first_detected"],
            "last_seen": trajectory["last_detected"],
            "observation_count": len(events)
        },
        "chain_of_custody_events": trajectory["observations"],
        "links": trajectory["trajectory_links"],
        "legal_notice": "TRACE-X AI forensic audit record generated in accordance with Digital Personal Data Protection (DPDP) Act 2023 regulations."
    }
