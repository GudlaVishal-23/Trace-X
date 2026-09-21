import sqlite3
import os

db_path = os.path.join(os.getcwd(), "data", "tracex.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

sample_cams = [
    ("CAM_DL_01", "New Delhi Connaught Place North", 28.6328, 77.2197, "RD_CONNAUGHT_CIRCUS", "south", "online", 0.96),
    ("CAM_MH_01", "Mumbai Western Express Corridor", 19.0760, 72.8777, "RD_WESTERN_EXPRESS", "north", "online", 0.94),
    ("CAM_WB_01", "Kolkata Central Transit Circle", 22.5726, 88.3639, "RD_KOLKATA_MG_WAY", "east", "online", 0.91),
    ("CAM_MP_01", "Bhopal National Highway Flyover", 23.2599, 77.4126, "RD_BHOPAL_EXPRESS", "south", "online", 0.95),
    ("CAM_HYD_02", "Cyberabad Hitec City Corridor", 17.4490, 78.3750, "RD_HITEC_MAIN", "west", "online", 0.90)
]

for cam in sample_cams:
    cur.execute("""
        INSERT OR REPLACE INTO cameras (camera_id, name, latitude, longitude, road_id, direction, status, quality_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, cam)

# Add DL9CAB5561 to watchlist
cur.execute("""
    INSERT OR REPLACE INTO watchlist (plate_text, category, priority, case_reference, notes)
    VALUES ('DL9CAB5561', 'SUSPECT', 'CRITICAL', 'FIR-2026-DL-8821', 'Silver Maruti Alto captured in New Delhi Connaught Place CCTV stream. Flagged for immediate field intercept.')
""")

# Add MH08AP3746 to watchlist as commercial permit check
cur.execute("""
    INSERT OR REPLACE INTO watchlist (plate_text, category, priority, case_reference, notes)
    VALUES ('MH08AP3746', 'COMMERCIAL_PERMIT', 'HIGH', 'CHALLAN-MH-4421', 'Tata Intra Mini-Truck with inter-state transit check.')
""")

conn.commit()
conn.close()
print("Sample video cameras and watchlist entries successfully registered in SQLite database.", flush=True)
