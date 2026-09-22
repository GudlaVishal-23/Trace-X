import os
from pathlib import Path

# Project Roots - dynamically resolved, zero hardcoded paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
UPLOADS_DIR = DATA_DIR / "uploads"
CROPS_DIR = UPLOADS_DIR / "crops"
ANNOTATED_DIR = UPLOADS_DIR / "annotated"
SAMPLE_VIDEOS_DIR = Path(os.getenv("SAMPLE_VIDEOS_DIR", str(BASE_DIR / "sample videos")))
STATIC_DIR = Path(__file__).resolve().parent / "static"

# Database & Security
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'tracex.db'}")
SECRET_KEY = os.getenv("JWT_SECRET", "sih2026-tracex-secret-key-32chars")

# Business Domain Parameters
CAMERA_SPEED_LIMIT_KMH = float(os.getenv("MAX_SPEED_KMH", "160.0"))
MIN_PLATE_CONFIDENCE = float(os.getenv("MIN_PLATE_CONFIDENCE", "0.50"))
CONFIRMED_PLATE_CONFIDENCE = float(os.getenv("CONFIRMED_PLATE_CONFIDENCE", "0.85"))

# Video Ingestion & Processing Limits (Part D.3, D.6)
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "500"))
MAX_FILE_SIZE = MAX_UPLOAD_MB * 1024 * 1024
TARGET_PROCESS_FPS = int(os.getenv("TARGET_PROCESS_FPS", "8"))
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "2"))
JOB_TIMEOUT_SECONDS = int(os.getenv("JOB_TIMEOUT_SECONDS", "600"))
DEMO_MODE = os.getenv("DEMO_MODE", "0").lower() in ("1", "true", "yes")

# Model Paths
YOLO_WEIGHTS_PATH = Path(os.getenv("YOLO_WEIGHTS_PATH", str(BASE_DIR / "yolov8n.pt")))

