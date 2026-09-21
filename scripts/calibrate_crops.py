import sys
import os
sys.path.insert(0, os.getcwd())
import cv2
import numpy as np

# Let's inspect frame 50% for each video and check crops
items = [
    {
        "video": "5009674-hd_1920_1080_25fps.mp4",
        "pct": 0.50, # 10.5s
        "plate": "DL9CAB5561",
        "vehicle_bbox": (0.265, 0.43, 0.17, 0.27),
        "plate_bbox": (0.325, 0.633, 0.057, 0.026)
    },
    {
        "video": "13020050_3840_2160_30fps.mp4",
        "pct": 0.50, # 8.0s
        "plate": "MH08AP3746",
        "vehicle_bbox": (0.68, 0.23, 0.20, 0.38),
        "plate_bbox": (0.795, 0.490, 0.045, 0.025)
    },
    {
        "video": "13926703_3840_2160_24fps.mp4",
        "pct": 0.50, # 5.2s
        "plate": "WB04G5786",
        "vehicle_bbox": (0.47, 0.40, 0.20, 0.48),
        "plate_bbox": (0.53, 0.58, 0.035, 0.035)
    },
    {
        "video": "14571138_3840_2160_60fps.mp4",
        "pct": 0.50, # 5.0s
        "plate": "MP04CY8591",
        "vehicle_bbox": (0.07, 0.64, 0.075, 0.14),
        "plate_bbox": (0.093, 0.732, 0.027, 0.018)
    },
    {
        "video": "5614377-hd_1920_1080_25fps.mp4",
        "pct": 0.50, # 3.5s
        "plate": "TS09ZOMATO",
        "vehicle_bbox": (0.13, 0.0, 0.58, 0.95),
        "plate_bbox": (0.42, 0.90, 0.25, 0.09)
    }
]

out_dir = os.path.join(os.getcwd(), "backend", "app", "static", "evidence")
os.makedirs(out_dir, exist_ok=True)

for item in items:
    v_path = os.path.join("sample videos", item["video"])
    cap = cv2.VideoCapture(v_path)
    fc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    target = int(fc * item["pct"])
    cap.set(cv2.CAP_PROP_POS_FRAMES, target)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        continue
    h, w = frame.shape[:2]
    vx, vy, vw, vh = [int(v) for v in (item["vehicle_bbox"][0]*w, item["vehicle_bbox"][1]*h, item["vehicle_bbox"][2]*w, item["vehicle_bbox"][3]*h)]
    px, py, pw, ph = [int(p) for p in (item["plate_bbox"][0]*w, item["plate_bbox"][1]*h, item["plate_bbox"][2]*w, item["plate_bbox"][3]*h)]

    vcrop = frame[vy:vy+vh, vx:vx+vw]
    pcrop = frame[py:py+ph, px:px+pw]

    cv2.imwrite(os.path.join(out_dir, f"test_v_{item['plate']}.jpg"), vcrop)
    cv2.imwrite(os.path.join(out_dir, f"test_p_{item['plate']}.jpg"), pcrop)
    print(f"Saved crops for {item['plate']} - V: {vcrop.shape}, P: {pcrop.shape}", flush=True)
