#!/usr/bin/env python3
"""
TRACE-X Database Seeding & Mock Topology Generator
Generates realistic camera network topology, active watchlist items,
and urban road connections for the Smart India Hackathon 2026 prototype.
"""

import json
from datetime import datetime, timezone

# 1. SAMPLE CAMERA NETWORK (Hyderabad Urban Corridor)
SAMPLE_CAMERAS = [
    {
        "camera_id": "C101",
        "name": "Begumpet Flyover Northbound",
        "latitude": 17.4435,
        "longitude": 78.4682,
        "road_id": "RD_BEGUMPET_MAIN",
        "direction": "north",
        "camera_type": "ANPR",
        "status": "online",
        "quality_score": 0.96
    },
    {
        "camera_id": "C107",
        "name": "Secunderabad Station Jct",
        "latitude": 17.4320,
        "longitude": 78.4550,
        "road_id": "RD_SECUNDERABAD_ARTERIAL",
        "direction": "north",
        "camera_type": "ANPR",
        "status": "online",
        "quality_score": 0.65  # Simulates camera prone to glare/blur
    },
    {
        "camera_id": "C112",
        "name": "Paradise Circle Southbound",
        "latitude": 17.4410,
        "longitude": 78.4870,
        "road_id": "RD_PARADISE_CORRIDOR",
        "direction": "east",
        "camera_type": "ANPR",
        "status": "offline",  # Simulates offline camera gap
        "quality_score": 0.00
    },
    {
        "camera_id": "C115",
        "name": "Panjagutta Central Circle",
        "latitude": 17.4285,
        "longitude": 78.4510,
        "road_id": "RD_PANJAGUTTA_MAIN",
        "direction": "south",
        "camera_type": "ANPR",
        "status": "online",
        "quality_score": 0.92
    },
    {
        "camera_id": "C118",
        "name": "Secretariat Gateway West",
        "latitude": 17.4110,
        "longitude": 78.4710,
        "road_id": "RD_LAKDIKAPUL_LINK",
        "direction": "south",
        "camera_type": "ANPR",
        "status": "online",
        "quality_score": 0.94
    },
    {
        "camera_id": "C123",
        "name": "Mehdipatnam Express Interchange",
        "latitude": 17.3915,
        "longitude": 78.4410,
        "road_id": "RD_PVNR_EXPRESSWAY",
        "direction": "south",
        "camera_type": "ANPR",
        "status": "online",
        "quality_score": 0.95
    },
    {
        "camera_id": "C130",
        "name": "Hitec City Cyber Towers Jct",
        "latitude": 17.4504,
        "longitude": 78.3808,
        "road_id": "RD_MADHAPUR_FLYOVER",
        "direction": "west",
        "camera_type": "ANPR",
        "status": "online",
        "quality_score": 0.91
    },
    {
        "camera_id": "C135",
        "name": "Gachibowli Stadium Gateway",
        "latitude": 17.4401,
        "longitude": 78.3489,
        "road_id": "RD_GACHIBOWLI_MAIN",
        "direction": "west",
        "camera_type": "ANPR",
        "status": "online",
        "quality_score": 0.89
    }
]

# 2. ACTIVE POLICE WATCHLIST (Blacklisted Target Vehicles)
SAMPLE_WATCHLIST = [
    {
        "plate_text": "TS09AB1234",
        "category": "STOLEN_VEHICLE",
        "priority": "CRITICAL",
        "case_reference": "FIR-2026-HYD-4091",
        "notes": "Black Yamaha R15 motorcycle stolen from Panjagutta metro station; suspect fleeing towards PVNR expressway."
    },
    {
        "plate_text": "DL01CA9999",
        "category": "SUSPECT",
        "priority": "HIGH",
        "case_reference": "CRIME-2026-DEL-102",
        "notes": "White Toyota Fortuner wanted in commercial burglary investigation."
    },
    {
        "plate_text": "MH12XY7788",
        "category": "TRAFFIC_VIOLATOR",
        "priority": "MEDIUM",
        "case_reference": "ECHALLAN-88902",
        "notes": "Repeated overspeeding and reckless lane changes along arterial roads."
    }
]

# 3. ROAD NETWORK CONNECTIVITY GRAPH (Distance & Expected Transit Time)
SAMPLE_ROAD_SEGMENTS = [
    {"from_camera": "C101", "to_camera": "C107", "distance_km": 2.1, "speed_limit_kmh": 50},
    {"from_camera": "C107", "to_camera": "C112", "distance_km": 3.4, "speed_limit_kmh": 40},
    {"from_camera": "C112", "to_camera": "C115", "distance_km": 2.8, "speed_limit_kmh": 45},
    {"from_camera": "C107", "to_camera": "C115", "distance_km": 4.2, "speed_limit_kmh": 45}, # Bypass route if C112 is offline
    {"from_camera": "C115", "to_camera": "C118", "distance_km": 1.6, "speed_limit_kmh": 40},
    {"from_camera": "C118", "to_camera": "C123", "distance_km": 4.5, "speed_limit_kmh": 60}
]

def main():
    print("==================================================")
    print("TRACE-X: Topology & Seed Data Generator")
    print("==================================================")
    print(f"[+] Generating {len(SAMPLE_CAMERAS)} camera nodes across Hyderabad grid...")
    for cam in SAMPLE_CAMERAS:
        print(f"    - {cam['camera_id']}: {cam['name']} (Status: {cam['status']}, Quality: {cam['quality_score']})")

    print(f"\n[+] Registering {len(SAMPLE_WATCHLIST)} priority watchlist targets...")
    for w in SAMPLE_WATCHLIST:
        print(f"    - [{w['priority']}] {w['plate_text']} ({w['category']}) - Ref: {w['case_reference']}")

    print(f"\n[+] Calibrating {len(SAMPLE_ROAD_SEGMENTS)} arterial road graph segments...")
    for r in SAMPLE_ROAD_SEGMENTS:
        print(f"    - {r['from_camera']} -> {r['to_camera']} | Dist: {r['distance_km']} km | Max: {r['speed_limit_kmh']} km/h")

    # Export seed data to json
    output_path = "data/sample/seed_topology.json"
    import os
    os.makedirs("data/sample", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({
            "cameras": SAMPLE_CAMERAS,
            "watchlist": SAMPLE_WATCHLIST,
            "road_segments": SAMPLE_ROAD_SEGMENTS,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }, f, indent=2)

    print(f"\n[SUCCESS] Seed topology successfully exported to: {output_path}")

if __name__ == "__main__":
    main()
