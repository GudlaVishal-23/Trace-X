import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'tracex.db'}")
SECRET_KEY = os.getenv("JWT_SECRET", "sih2026-tracex-secret-key-32chars")
CAMERA_SPEED_LIMIT_KMH = float(os.getenv("MAX_SPEED_KMH", "160.0"))
MIN_PLATE_CONFIDENCE = float(os.getenv("MIN_PLATE_CONFIDENCE", "0.50"))
CONFIRMED_PLATE_CONFIDENCE = float(os.getenv("CONFIRMED_PLATE_CONFIDENCE", "0.85"))
