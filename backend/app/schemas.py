from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# --- CAMERA SCHEMAS ---
class CameraBase(BaseModel):
    camera_id: str
    name: str
    latitude: float
    longitude: float
    road_id: Optional[str] = None
    direction: Optional[str] = "unknown"
    camera_type: Optional[str] = "ANPR"
    status: Optional[str] = "online"
    quality_score: Optional[float] = 1.0

class CameraCreate(CameraBase):
    pass

class CameraResponse(CameraBase):
    id: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

# --- VEHICLE EVENT SCHEMAS ---
class VehicleEventBase(BaseModel):
    camera_id: str
    timestamp: Optional[datetime] = None
    plate_text: Optional[str] = None
    plate_confidence: float = 0.0
    observation_status: str = "CONFIRMED"
    vehicle_type: Optional[str] = "car"
    vehicle_color: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    direction: Optional[str] = None
    latitude: float
    longitude: float
    road_id: Optional[str] = None
    image_quality_score: float = 0.0
    detection_confidence: float = 0.0
    thumbnail_url: Optional[str] = None

class VehicleEventCreate(VehicleEventBase):
    event_id: Optional[str] = None

class VehicleEventResponse(VehicleEventBase):
    id: int
    event_id: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- TRAJECTORY SCHEMAS ---
class TrajectoryLinkItem(BaseModel):
    from_camera: str
    to_camera: str
    link_type: str # CONFIRMED, PROBABLE, CAMERA_GAP
    distance_km: float
    travel_time_sec: int
    implied_speed_kmh: float
    match_score: float
    reason: str

class TrajectoryHistoryResponse(BaseModel):
    plate: str
    first_detected: Optional[datetime] = None
    last_detected: Optional[datetime] = None
    overall_confidence: float
    status: str
    total_distance_km: float
    average_speed_kmh: float
    observations: List[Dict[str, Any]]
    trajectory_links: List[TrajectoryLinkItem]

# --- WATCHLIST & ALERT SCHEMAS ---
class WatchlistCreate(BaseModel):
    plate_text: str
    category: str
    priority: Optional[str] = "HIGH"
    case_reference: Optional[str] = None
    notes: Optional[str] = None

class WatchlistResponse(WatchlistCreate):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class AlertAcknowledge(BaseModel):
    action: str # CONFIRMED, DISMISSED, RESOLVED
    officer_notes: Optional[str] = None
    case_file_id: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    alert_type: str
    plate_text: Optional[str]
    camera_id: Optional[str]
    timestamp: datetime
    confidence: float
    reason: str
    status: str
    case_file_id: Optional[str]
    officer_notes: Optional[str]
    acknowledged_by: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

# --- TRAFFIC ANALYTICS SCHEMAS ---
class TrafficSummaryResponse(BaseModel):
    total_vehicles_today: int
    average_city_speed_kmh: float
    active_bottlenecks: int
    peak_hour: str
    modal_distribution: Dict[str, int]
