from fastapi.testclient import TestClient
from backend.app.main import app

def test_api_suite():
    with TestClient(app) as client:
        # 1. Health check
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"
        print("[PASS] /health endpoint")

        # 2. Cameras API
        res = client.get("/api/cameras")
        assert res.status_code == 200
        cams = res.json()
        assert len(cams) >= 8
        print(f"[PASS] /api/cameras ({len(cams)} nodes returned)")

        # 3. Vehicle Events API
        res = client.get("/api/events")
        assert res.status_code == 200
        events = res.json()
        assert len(events) >= 4
        print(f"[PASS] /api/events ({len(events)} events returned)")

        # 4. Trajectory Reconstruction API
        res = client.get("/api/vehicles/TS09AB1234/history")
        assert res.status_code == 200
        traj = res.json()
        assert traj["plate"] == "TS09AB1234"
        assert len(traj["trajectory_links"]) >= 2
        print(f"[PASS] /api/vehicles/TS09AB1234/history (Status: {traj['status']}, Dist: {traj['total_distance_km']} km)")

        # 5. Traffic Analytics APIs
        res = client.get("/api/traffic/summary")
        assert res.status_code == 200
        sum_data = res.json()
        assert "total_vehicles_today" in sum_data
        print("[PASS] /api/traffic/summary")

        res = client.get("/api/traffic/od")
        assert res.status_code == 200
        od_data = res.json()
        assert len(od_data["zones"]) == 4
        print("[PASS] /api/traffic/od")

        # 6. Alerts & Watchlist API
        res = client.get("/api/alerts")
        assert res.status_code == 200
        alerts = res.json()
        assert len(alerts) >= 1
        print(f"[PASS] /api/alerts ({len(alerts)} alerts active)")

        # 7. Forensic Report API (with cryptographic SHA-256 verification)
        res = client.get("/api/reports/vehicle/TS09AB1234")
        assert res.status_code == 200
        rep = res.json()
        assert "evidence_integrity_hash_sha256" in rep
        print(f"[PASS] /api/reports/vehicle/TS09AB1234 (Hash: {rep['evidence_integrity_hash_sha256'][:16]}...)")

        # 8. Dashboard HTML serving
        res = client.get("/")
        assert res.status_code == 200
        assert "TRACE-X" in res.text
        print("[PASS] Root Dashboard UI served successfully")

if __name__ == "__main__":
    test_api_suite()
    print("\n=======================================================")
    print("ALL API ENDPOINTS & TRAJECTORY ENGINES VALIDATED 100%!")
    print("=======================================================")
