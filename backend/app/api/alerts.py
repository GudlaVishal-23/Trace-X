from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Alert, Watchlist
from backend.app.schemas import AlertResponse, AlertAcknowledge, WatchlistCreate, WatchlistResponse

router = APIRouter(prefix="/alerts", tags=["Alerts & Watchlist Operations"])

@router.get("", response_model=List[AlertResponse])
def list_alerts(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    return query.order_by(Alert.timestamp.desc()).all()

@router.post("/watchlist", response_model=WatchlistResponse, status_code=201)
def add_to_watchlist(payload: WatchlistCreate, db: Session = Depends(get_db)):
    clean_plate = payload.plate_text.upper().replace(" ", "")
    existing = db.query(Watchlist).filter(Watchlist.plate_text == clean_plate).first()
    if existing:
        existing.category = payload.category
        existing.priority = payload.priority
        existing.notes = payload.notes
        existing.status = "ACTIVE"
        db.commit()
        db.refresh(existing)
        return existing

    item = Watchlist(**payload.model_dump())
    item.plate_text = clean_plate
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/watchlist", response_model=List[WatchlistResponse])
def get_watchlist(db: Session = Depends(get_db)):
    return db.query(Watchlist).all()

@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: int, payload: AlertAcknowledge, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = payload.action
    alert.officer_notes = payload.officer_notes
    alert.case_file_id = payload.case_file_id
    alert.acknowledged_by = "Duty Officer"
    db.commit()
    db.refresh(alert)
    return alert
