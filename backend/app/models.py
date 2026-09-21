from datetime import datetime, timezone
from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(32), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    road_id = Column(String(64), index=True)
    direction = Column(String(32), default="unknown")
    camera_type = Column(String(32), default="ANPR")
    status = Column(String(16), default="online", index=True) # online, offline, degraded
    quality_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    events = relationship("VehicleEvent", back_populates="camera")
    alerts = relationship("Alert", back_populates="camera")

class VehicleEvent(Base):
    __tablename__ = "vehicle_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(64), unique=True, index=True, nullable=False)
    camera_id = Column(String(32), ForeignKey("cameras.camera_id"), index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    plate_text = Column(String(16), index=True, nullable=True)
    plate_confidence = Column(Float, default=0.0)
    observation_status = Column(String(16), nullable=False) # CONFIRMED, PROBABLE, UNREADABLE
    vehicle_type = Column(String(32), index=True)           # car, motorcycle, bus, truck, auto_rickshaw
    vehicle_color = Column(String(32))
    vehicle_make = Column(String(64))
    vehicle_model = Column(String(64))
    direction = Column(String(32))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    road_id = Column(String(64))
    image_quality_score = Column(Float, default=0.0)
    detection_confidence = Column(Float, default=0.0)
    reid_embedding_id = Column(String(64), nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    camera = relationship("Camera", back_populates="events")

class Trajectory(Base):
    __tablename__ = "trajectories"

    id = Column(Integer, primary_key=True, index=True)
    trajectory_id = Column(String(64), unique=True, index=True, nullable=False)
    plate_text = Column(String(16), index=True, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    overall_confidence = Column(Float, nullable=False)
    status = Column(String(16), default="CONFIRMED") # CONFIRMED, PROBABLE, INCOMPLETE
    total_distance_km = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    links = relationship("TrajectoryLink", back_populates="trajectory", cascade="all, delete-orphan")

class TrajectoryLink(Base):
    __tablename__ = "trajectory_links"

    id = Column(Integer, primary_key=True, index=True)
    trajectory_id = Column(String(64), ForeignKey("trajectories.trajectory_id"), index=True)
    from_event_id = Column(String(64), ForeignKey("vehicle_events.event_id"))
    to_event_id = Column(String(64), ForeignKey("vehicle_events.event_id"))
    match_score = Column(Float, nullable=False)
    link_type = Column(String(16), nullable=False) # CONFIRMED, PROBABLE, CAMERA_GAP
    distance_km = Column(Float, nullable=False)
    travel_time_sec = Column(Integer, nullable=False)
    implied_speed_kmh = Column(Float, nullable=False)
    reason = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trajectory = relationship("Trajectory", back_populates="links")

class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    plate_text = Column(String(16), unique=True, index=True, nullable=False)
    category = Column(String(32), nullable=False) # STOLEN, SUSPECT, VIP, TRAFFIC_VIOLATOR
    priority = Column(String(16), default="HIGH") # CRITICAL, HIGH, MEDIUM
    case_reference = Column(String(64))
    notes = Column(Text)
    status = Column(String(16), default="ACTIVE", index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(32), nullable=False) # WATCHLIST_MATCH, ROUTE_ANOMALY, CLONED_PLATE, CONGESTION
    plate_text = Column(String(16), index=True)
    camera_id = Column(String(32), ForeignKey("cameras.camera_id"), index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(16), default="NEW", index=True) # NEW, ACKNOWLEDGED, DISMISSED, RESOLVED
    case_file_id = Column(String(64))
    officer_notes = Column(Text)
    acknowledged_by = Column(String(64))
    # Phase 4 Operator Confirmation Gate
    review_state = Column(String(16), default="PENDING", index=True) # PENDING, CONFIRMED, REJECTED
    reviewed_by = Column(String(64), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reject_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    camera = relationship("Camera", back_populates="alerts")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    role = Column(String(32), default="OFFICER") # ADMIN, OFFICER, ANALYST
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    officer_id = Column(String(64), nullable=True, index=True)
    role = Column(String(32), nullable=True)
    action = Column(String(64), nullable=False) # SEARCH_PLATE, EXPORT_REPORT, ACK_ALERT
    target = Column(String(128), nullable=True)
    case_ref = Column(String(64), nullable=True, index=True) # Mandatory FIR / Case reference
    justification = Column(Text, nullable=True)
    ip = Column(String(64), nullable=True)
    prev_hash = Column(String(64), nullable=True)
    row_hash = Column(String(64), nullable=True)
    resource = Column(String(128), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    details = Column(JSON, nullable=True)

# Phase 1: Video Ingestion & Live Scan Theatre Models
class IngestJob(Base):
    __tablename__ = "ingest_jobs"

    job_id = Column(String(64), primary_key=True, index=True) # uuid4
    filename = Column(String(256), nullable=False)
    camera_id = Column(String(32), ForeignKey("cameras.camera_id"), nullable=False, index=True)
    status = Column(String(24), default="QUEUED", index=True) # QUEUED, PROBING, PROCESSING, DONE, FAILED
    total_frames = Column(Integer, default=0)
    done_frames = Column(Integer, default=0)
    fps = Column(Float, default=0.0)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    duration_s = Column(Float, default=0.0)
    started_at = Column(String(64), nullable=True)
    finished_at = Column(String(64), nullable=True)
    error = Column(Text, nullable=True)
    stats_json = Column(Text, nullable=True) # JSON summary blob

    detections = relationship("JobDetection", back_populates="job", cascade="all, delete-orphan")
    tracks = relationship("JobTrack", back_populates="job", cascade="all, delete-orphan")

class JobDetection(Base):
    __tablename__ = "job_detections"

    det_id = Column(String(64), primary_key=True, index=True)
    job_id = Column(String(64), ForeignKey("ingest_jobs.job_id"), nullable=False, index=True)
    frame_idx = Column(Integer, nullable=False, index=True)
    video_ts = Column(Float, nullable=False)
    track_id = Column(Integer, nullable=True, index=True)
    bbox_json = Column(Text, nullable=False) # [x1, y1, x2, y2]
    plate_bbox_json = Column(Text, nullable=True)
    vehicle_class = Column(String(32), nullable=True)
    color = Column(String(32), nullable=True)
    plate_raw = Column(String(32), nullable=True)
    plate_conf = Column(Float, default=0.0)
    blur_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    crop_path = Column(Text, nullable=True)
    plate_crop_path = Column(Text, nullable=True)
    clahe_crop_path = Column(Text, nullable=True)
    embedding = Column(Text, nullable=True) # Base64 or BLOB for Phase 2 ReID

    job = relationship("IngestJob", back_populates="detections")

class JobTrack(Base):
    __tablename__ = "job_tracks"

    job_id = Column(String(64), ForeignKey("ingest_jobs.job_id"), primary_key=True)
    track_id = Column(Integer, primary_key=True)
    first_frame = Column(Integer, nullable=True)
    last_frame = Column(Integer, nullable=True)
    n_frames = Column(Integer, default=0)
    fused_plate = Column(String(32), nullable=True, index=True)
    fused_conf = Column(Float, default=0.0)
    vehicle_class = Column(String(32), nullable=True)
    color = Column(String(32), nullable=True)
    best_det_id = Column(String(64), nullable=True)
    watchlist_hit = Column(String(64), nullable=True) # NULL | Category

    job = relationship("IngestJob", back_populates="tracks")
