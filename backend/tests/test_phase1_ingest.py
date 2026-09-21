import os
import time
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models import IngestJob, JobDetection, JobTrack, VehicleEvent, Camera

def test_phase1_ingest_pipeline():
    with TestClient(app) as client:
        # 1. Verify /scan route serves Scan Theatre UI
        res = client.get("/scan")
        assert res.status_code == 200
        assert "Live Scan Theatre" in res.text
        print("[PASS] /scan serves Scan Theatre UI successfully")

        # 2. Pick a test video
        sample_video_path = os.path.join(os.getcwd(), "scratch", "sample_test_3s.mp4")
        if not os.path.exists(sample_video_path):
            sample_video_path = os.path.join(os.getcwd(), "sample videos", "5009674-hd_1920_1080_25fps.mp4")
        assert os.path.exists(sample_video_path), f"Sample video missing at {sample_video_path}"

        # Ensure a camera node exists
        cam_id = "CAM_DL_01"
        db = SessionLocal()
        cam = db.query(Camera).filter(Camera.camera_id == cam_id).first()
        if not cam:
            cam = Camera(camera_id=cam_id, name="Delhi Connaught Place", latitude=28.6328, longitude=77.2197, road_id="RD_CONNAUGHT_CIRCUS")
            db.add(cam)
            db.commit()
        db.close()

        # 3. Test Video Upload endpoint (POST /api/ingest/upload)
        with open(sample_video_path, "rb") as f:
            upload_res = client.post(
                "/api/ingest/upload",
                data={"camera_id": cam_id},
                files={"file": ("delhi_sample.mp4", f, "video/mp4")}
            )
        assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
        data = upload_res.json()
        assert "job_id" in data
        job_id = data["job_id"]
        assert data["status"] == "QUEUED"
        print(f"[PASS] /api/ingest/upload accepted video, assigned job_id: {job_id}")

        # 4. Test GET /api/ingest/jobs
        res = client.get("/api/ingest/jobs")
        assert res.status_code == 200
        jobs = res.json()
        assert any(j["job_id"] == job_id for j in jobs)
        print(f"[PASS] /api/ingest/jobs listed current job ({len(jobs)} total jobs)")

        # 5. Test HTTP Range streaming on original video (GET /api/ingest/jobs/{job_id}/video)
        range_res = client.get(
            f"/api/ingest/jobs/{job_id}/video",
            headers={"Range": "bytes=0-1024"}
        )
        assert range_res.status_code == 206
        assert "bytes 0-1024/" in range_res.headers.get("Content-Range", "")
        assert len(range_res.content) == 1025
        print("[PASS] /api/ingest/jobs/{job_id}/video supports HTTP Range seeking (206 Partial Content)")

        # 6. Test WebSocket event connection
        with client.websocket_connect(f"/ws/ingest/{job_id}") as ws:
            ws.send_text("ping")
            pong = ws.receive_json()
            assert pong.get("type") in ["pong", "progress", "detection"]
            print("[PASS] /ws/ingest/{job_id} WebSocket stream connected and active")

        # 7. Wait briefly for worker to complete or process frames
        max_wait = 25
        start_wait = time.time()
        final_job = None
        while time.time() - start_wait < max_wait:
            j_res = client.get(f"/api/ingest/jobs/{job_id}")
            assert j_res.status_code == 200
            final_job = j_res.json()
            if final_job["status"] in ["DONE", "FAILED"]:
                break
            time.sleep(1.0)

        print(f"[STATUS] Job completed with status: {final_job['status']} (done_frames={final_job['done_frames']}/{final_job['total_frames']})")
        assert final_job["status"] == "DONE"
        assert final_job["done_frames"] > 0

        # 8. Test GET /api/ingest/jobs/{job_id}/detections
        det_res = client.get(f"/api/ingest/jobs/{job_id}/detections")
        assert det_res.status_code == 200
        dets = det_res.json()
        assert len(dets) > 0
        print(f"[PASS] /api/ingest/jobs/{job_id}/detections returned {len(dets)} frame detections")

        # 9. Test GET /api/ingest/jobs/{job_id}/tracks
        track_res = client.get(f"/api/ingest/jobs/{job_id}/tracks")
        assert track_res.status_code == 200
        tracks = track_res.json()
        assert len(tracks) > 0
        print(f"[PASS] /api/ingest/jobs/{job_id}/tracks returned {len(tracks)} fused tracks (Bayesian consensus)")

        # 10. Verify Annotated Video Stream with Range Support
        ann_res = client.get(
            f"/api/ingest/jobs/{job_id}/annotated",
            headers={"Range": "bytes=0-2048"}
        )
        assert ann_res.status_code in [200, 206]
        print("[PASS] /api/ingest/jobs/{job_id}/annotated streams annotated MP4")

        # 11. Verify Materialization into vehicle_events (Section 1.5)
        db = SessionLocal()
        materialized = db.query(VehicleEvent).filter(VehicleEvent.camera_id == cam_id).all()
        assert len(materialized) > 0
        print(f"[PASS] Materialized {len(materialized)} ANPR vehicle events into main events table for trajectory reconstruction")
        db.close()

if __name__ == "__main__":
    test_phase1_ingest_pipeline()
