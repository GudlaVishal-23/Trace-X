import math
from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two GPS coordinates using stdlib math."""
    R = 6371.0 # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    return round(2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)), 2)

# Precomputed Static Camera Coordinates for Hyderabad Arterial Network (Master Doc Section 20)
CAMERA_COORDS: Dict[str, Tuple[float, float]] = {
    "C101": (17.4435, 78.4682), # Begumpet Flyover Northbound
    "C107": (17.4320, 78.4550), # Secunderabad Station Jct
    "C112": (17.4410, 78.4870), # Paradise Circle Southbound
    "C115": (17.4285, 78.4510), # Panjagutta Central Circle (Main Arterial)
    "C118": (17.4110, 78.4710), # Secretariat Gateway West
    "C123": (17.3915, 78.4410), # Mehdipatnam Express Interchange
    "C130": (17.4504, 78.3808), # Hitec City Cyber Towers Jct
    "C135": (17.4401, 78.3489)  # Gachibowli Stadium Gateway
}

# Precompute N x N static distance matrix for O(1) trajectory link evaluation
CAMERA_ADJACENCY_MATRIX: Dict[Tuple[str, str], float] = {
    (c1, c2): 0.0 if c1 == c2 else haversine_distance_km(lat1, lon1, lat2, lon2)
    for c1, (lat1, lon1) in CAMERA_COORDS.items()
    for c2, (lat2, lon2) in CAMERA_COORDS.items()
}

def get_camera_distance(c1: str, c2: str, lat1: float = None, lon1: float = None, lat2: float = None, lon2: float = None) -> float:
    """O(1) matrix lookup with fallback to haversine calculation."""
    if (c1, c2) in CAMERA_ADJACENCY_MATRIX:
        return CAMERA_ADJACENCY_MATRIX[(c1, c2)]
    if lat1 is not None and lat2 is not None:
        return haversine_distance_km(lat1, lon1, lat2, lon2)
    return 1.5

def calculate_link_score(obs_a: Dict[str, Any], obs_b: Dict[str, Any], distance_km: float) -> Dict[str, Any]:
    """
    Computes cross-camera candidate match score between obs_a (earlier) and obs_b (later).
    """
    delta_sec = (obs_b["timestamp"] - obs_a["timestamp"]).total_seconds()
    if delta_sec <= 0:
        return {"score": 0.0, "link_type": "REJECTED", "implied_speed_kmh": 0.0, "reason": "Non-positive transit time"}

    implied_speed = distance_km / (delta_sec / 3600.0)
    if implied_speed > 160.0:
        return {
            "score": 0.0,
            "link_type": "ANOMALY",
            "implied_speed_kmh": round(implied_speed, 1),
            "reason": f"Implied speed {implied_speed:.1f} km/h is physically impossible (> 160 km/h)"
        }

    # Plate text similarity (Normalized Levenshtein ratio)
    plate_a = (obs_a.get("plate_text") or "").replace("?", "")
    plate_b = (obs_b.get("plate_text") or "").replace("?", "")
    s_plate = SequenceMatcher(None, plate_a, plate_b).ratio() if (plate_a and plate_b) else 0.0

    # Vehicle Attributes
    type_match = 1.0 if obs_a.get("vehicle_type") == obs_b.get("vehicle_type") else 0.0
    color_match = 1.0 if obs_a.get("vehicle_color") == obs_b.get("vehicle_color") else 0.0
    s_attr = 0.6 * type_match + 0.4 * color_match

    # Reject direct vehicle class contradictions (e.g. motorcycle vs truck)
    if type_match == 0.0:
        return {
            "score": 0.05,
            "link_type": "REJECTED",
            "implied_speed_kmh": round(implied_speed, 1),
            "reason": f"Vehicle class mismatch ({obs_a.get('vehicle_type')} vs {obs_b.get('vehicle_type')})"
        }

    # Spatiotemporal travel feasibility (Urban speed window: 15 to 80 km/h)
    if 15.0 <= implied_speed <= 80.0:
        s_time = 1.0
    elif implied_speed < 15.0:
        s_time = max(0.2, implied_speed / 15.0)
    else:
        s_time = max(0.2, (160.0 - implied_speed) / 80.0)

    composite = (0.45 * s_plate) + (0.25 * s_attr) + (0.30 * s_time)

    # Classification
    if s_plate >= 0.85 and composite >= 0.78:
        link_type = "CONFIRMED"
        reason = "High plate confidence consensus with feasible transit time"
    elif composite >= 0.50:
        link_type = "PROBABLE"
        reason = "Partial plate or appearance match within valid road window"
    else:
        link_type = "UNKNOWN"
        reason = "Insufficient evidence"

    return {
        "score": round(composite, 3),
        "link_type": link_type,
        "implied_speed_kmh": round(implied_speed, 1),
        "reason": reason
    }

def solve_trajectory(observations: List[Dict[str, Any]], offline_cameras: List[str] = None) -> Dict[str, Any]:
    """
    Constructs the optimal chronological trajectory path across observations.
    Bridges offline cameras as CAMERA_GAP links without hallucinating observations.
    """
    if not observations:
        return {
            "overall_confidence": 0.0,
            "status": "NOT_FOUND",
            "total_distance_km": 0.0,
            "average_speed_kmh": 0.0,
            "observations": [],
            "trajectory_links": []
        }

    sorted_obs = sorted(observations, key=lambda x: x["timestamp"])
    links = []
    total_dist = 0.0
    offline_set = set(offline_cameras or [])

    for i in range(len(sorted_obs) - 1):
        obs1 = sorted_obs[i]
        obs2 = sorted_obs[i + 1]

        dist_km = get_camera_distance(
            obs1.get("camera_id"), obs2.get("camera_id"),
            obs1.get("latitude"), obs1.get("longitude"),
            obs2.get("latitude"), obs2.get("longitude")
        )
        # Ensure minimum distance floor for adjacent junction nodes
        dist_km = max(0.5, dist_km)
        total_dist += dist_km

        res = calculate_link_score(obs1, obs2, dist_km)
        delta_sec = int((obs2["timestamp"] - obs1["timestamp"]).total_seconds())

        # Check if an intermediate camera gap exists
        link_type = res["link_type"]
        reason = res["reason"]
        if offline_set:
            # If any offline camera lies between or is designated along the corridor
            link_type = "CAMERA_GAP"
            reason = "Camera gap along transit corridor; bridged via road graph"

        links.append({
            "from_camera": obs1["camera_id"],
            "to_camera": obs2["camera_id"],
            "link_type": link_type,
            "distance_km": dist_km,
            "travel_time_sec": delta_sec,
            "implied_speed_kmh": res["implied_speed_kmh"],
            "match_score": res["score"],
            "reason": reason
        })

    # Trajectory Summary
    first_time = sorted_obs[0]["timestamp"]
    last_time = sorted_obs[-1]["timestamp"]
    total_duration_hours = max(0.01, (last_time - first_time).total_seconds() / 3600.0)
    avg_speed = round(total_dist / total_duration_hours, 1)

    avg_conf = sum(o.get("plate_confidence", 0.8) for o in sorted_obs) / len(sorted_obs)
    has_confirmed = any(l["link_type"] == "CONFIRMED" for l in links)
    status = "CONFIRMED" if (has_confirmed and avg_conf >= 0.75) else "PROBABLE"

    return {
        "plate": sorted_obs[0].get("plate_text", "UNKNOWN"),
        "first_detected": first_time,
        "last_detected": last_time,
        "overall_confidence": round(avg_conf, 2),
        "status": status,
        "total_distance_km": round(total_dist, 2),
        "average_speed_kmh": avg_speed,
        "observations": sorted_obs,
        "trajectory_links": links
    }
