---
name: trace-x-engine
description: Domain knowledge and operational workflows for developing, querying, simulating, and evaluating TRACE-X (Multi-Camera ANPR Trajectory Tracking & Urban Traffic Analytics).
---

# TRACE-X Engine: Agent Skill & Operational Manual

This skill provides operational workflows, architectural rules, code conventions, and simulation utilities for the **TRACE-X** platform (Smart India Hackathon Problem Statement **SIH26127**).

## 1. Core Principles to Uphold

1. **Zero Video Duplication:** Never write code that attempts to store continuous CCTV video in database records or local storage. Always generate and store structured `VehicleEvent` records.
2. **Never Hallucinate Plates:** If OCR confidence is $< 0.50$ or character evidence is ambiguous, assign `observation_status = "PARTIAL"` or `"UNREADABLE"`. Do not invent characters.
3. **Tri-Level Trajectory Classification:** Always classify cross-camera trajectory edges into:
   - `CONFIRMED`: High plate confidence ($\ge 0.85$) + feasible travel time + connected road link.
   - `PROBABLE`: Partial plate OR high Re-ID appearance match + spatiotemporal feasibility.
   - `CAMERA_GAP`: Missing camera link along an expected corridor; bridged via road graph without phantom detection.
4. **Physical Feasibility Guard:** Reject any trajectory candidate where implied speed:
   $$v_{implied} = \frac{\text{Distance}(C_i, C_j)}{t_j - t_i} > 160 \text{ km/h}$$
   If two identical plates appear at distant cameras simultaneously, trigger a `CLONED_PLATE_ANOMALY`.

---

## 2. Multi-Signal Trajectory Scoring Implementation

When implementing or modifying the trajectory engine, use the normalized scoring formula:

```python
def calculate_match_score(event_a: dict, event_b: dict, road_distance_km: float) -> dict:
    """
    Computes cross-camera match score between event_a (earlier) and event_b (later).
    """
    delta_t_sec = (event_b["timestamp"] - event_a["timestamp"]).total_seconds()
    if delta_t_sec <= 0:
        return {"score": 0.0, "status": "REJECTED", "reason": "Negative or zero travel time"}

    # 1. Physical Velocity Check
    implied_speed_kmh = (road_distance_km / (delta_t_sec / 3600.0))
    if implied_speed_kmh > 160.0:
        return {
            "score": 0.0,
            "status": "ANOMALY",
            "reason": f"Implied speed {implied_speed_kmh:.1f} km/h exceeds 160 km/h threshold"
        }

    # 2. Plate Similarity (Normalized Levenshtein)
    from difflib import SequenceMatcher
    plate_a = event_a.get("plate_text") or ""
    plate_b = event_b.get("plate_text") or ""
    s_plate = SequenceMatcher(None, plate_a, plate_b).ratio() if (plate_a and plate_b) else 0.0

    # 3. Vehicle Attributes (Class & Color)
    type_match = 1.0 if event_a.get("vehicle_type") == event_b.get("vehicle_type") else 0.0
    color_match = 1.0 if event_a.get("vehicle_color") == event_b.get("vehicle_color") else 0.0
    s_attr = 0.6 * type_match + 0.4 * color_match

    # 4. Travel Time Feasibility (Optimal speed window: 15 - 80 km/h)
    if 15.0 <= implied_speed_kmh <= 80.0:
        s_time = 1.0
    elif implied_speed_kmh < 15.0:
        s_time = max(0.2, implied_speed_kmh / 15.0)
    else:
        s_time = max(0.2, (160.0 - implied_speed_kmh) / 80.0)

    # 5. Composite Match Score
    composite_score = (0.45 * s_plate) + (0.25 * s_attr) + (0.30 * s_time)

    # Classification
    if s_plate >= 0.85 and composite_score >= 0.80:
        status = "CONFIRMED"
    elif composite_score >= 0.55:
        status = "PROBABLE"
    else:
        status = "UNKNOWN"

    return {
        "score": round(composite_score, 3),
        "status": status,
        "implied_speed_kmh": round(implied_speed_kmh, 1),
        "plate_sim": round(s_plate, 2),
        "attr_sim": round(s_attr, 2)
    }
```

---

## 3. PostGIS Query Patterns

### Find all vehicles within 500 meters of a coordinate in the last 15 minutes:
```sql
SELECT event_id, camera_id, plate_text, vehicle_type, vehicle_color, timestamp,
       ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(78.4682, 17.4435), 4326)::geography) AS distance_meters
FROM vehicle_events
WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(78.4682, 17.4435), 4326)::geography, 500)
  AND timestamp >= NOW() - INTERVAL '15 minutes'
ORDER BY timestamp DESC;
```

### Reconstruct Trajectory Links for a Target Plate:
```sql
SELECT l.from_event_id, l.to_event_id, l.link_type, l.distance_km, l.implied_speed_kmh, l.match_score, l.reason
FROM trajectory_links l
JOIN trajectories t ON l.trajectory_id = t.trajectory_id
WHERE t.plate_text = 'TS09AB1234'
ORDER BY l.id ASC;
```

---

## 4. Testing & Verification Commands

- To test database seeding:
  ```powershell
  python scripts/seed_database.py
  ```
- To test the perception & trajectory pipeline simulation:
  ```powershell
  python scripts/simulate_pipeline.py
  ```

---

## 5. Ponytail Engineering Integration & Minimalist Discipline

When the user asks to "use the ponytail plugin", "be lazy", or develop features with minimal code, follow the **Ponytail Senior Dev Ladder**:
1. **YAGNI First:** Question whether the module/wrapper needs to exist at all.
2. **Reuse Existing Patterns:** Check `scripts/` and `backend/` before writing new utilities.
3. **Standard Library Over Dependencies:** Use `math`, `difflib`, `datetime`, and `json` rather than heavy custom packages.
4. **Native Over App Code:** Push spatial calculations to PostGIS (`ST_DWithin`, `ST_Distance`) instead of processing large arrays in Python.
5. **Shortest Working Diff:** Always ship the minimal code that works reliably, with code first and at most 3 lines of summary.
6. **Available Ponytail Tools:**
   - Review code for over-engineering: `/ponytail-review`
   - Whole-codebase bloat audit: `/ponytail-audit`
   - Track shortcuts and deliberate simplifications: `/ponytail-debt`

