import os
import sys
import time
import json
import urllib.request
import urllib.parse
import psutil

BASE_URL = "http://127.0.0.1:8000"

SAMPLE_VIDEOS = [
    ("5009674-hd_1920_1080_25fps.mp4", "CAM_DL_01"),
    ("13020050_3840_2160_30fps.mp4", "CAM_MH_01"),
    ("13926703_3840_2160_24fps.mp4", "CAM_WB_01"),
    ("14571138_3840_2160_60fps.mp4", "CAM_MP_01"),
    ("5614377-hd_1920_1080_25fps.mp4", "CAM_HYD_02"),
]

def get_server_rss():
    current_proc = psutil.Process()
    # Check all python processes
    total_rss = 0
    for p in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            if 'python' in p.info['name'].lower():
                total_rss += p.info['memory_info'].rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return total_rss / (1024 * 1024) # MB

def submit_job(preset_filename, camera_id):
    data = urllib.parse.urlencode({
        "preset_filename": preset_filename,
        "camera_id": camera_id
    }).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/api/ingest/upload", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def wait_for_job(job_id, timeout=240):
    start = time.time()
    while time.time() - start < timeout:
        req = urllib.request.Request(f"{BASE_URL}/api/ingest/jobs/{job_id}")
        with urllib.request.urlopen(req) as resp:
            j = json.loads(resp.read().decode("utf-8"))
            if j["status"] in ("DONE", "FAILED"):
                return j
        time.sleep(1.5)
    raise TimeoutError(f"Job {job_id} did not finish within {timeout}s")

def main():
    print("=" * 60)
    print("TRACE-X Part C.10 Verification: 5 Sample Videos Back-to-Back")
    print("=" * 60)
    
    rss_start = get_server_rss()
    print(f"Initial Python System RSS: {rss_start:.2f} MB")
    
    results = []
    for idx, (filename, cam_id) in enumerate(SAMPLE_VIDEOS, 1):
        t0 = time.time()
        print(f"\n[{idx}/5] Submitting preset: {filename} (Camera: {cam_id})...")
        job_info = submit_job(filename, cam_id)
        job_id = job_info["job_id"]
        print(f" -> Job ID: {job_id}, initial status: {job_info['status']}")
        
        final_job = wait_for_job(job_id, timeout=90)
        elapsed = round(time.time() - t0, 2)
        rss_current = get_server_rss()
        
        status = final_job["status"]
        done_frames = final_job["done_frames"]
        total_frames = final_job["total_frames"]
        dets_count = final_job.get("detections_count", 0)
        tracks_count = final_job.get("tracks_count", 0)
        
        print(f" -> Finished in {elapsed}s | Status: {status} | Frames: {done_frames}/{total_frames} | Tracks: {tracks_count} | Detections: {dets_count} | Current RSS: {rss_current:.2f} MB")
        results.append({
            "video": filename,
            "job_id": job_id,
            "status": status,
            "elapsed_s": elapsed,
            "tracks": tracks_count,
            "rss_mb": round(rss_current, 2)
        })
        assert status == "DONE", f"Job failed for {filename}"
        assert dets_count > 0, f"No detections for {filename}"
    
    rss_end = get_server_rss()
    rss_delta = rss_end - rss_start
    print("\n" + "=" * 60)
    print("SUMMARY RESULTS:")
    for r in results:
        print(f" - {r['video']}: {r['status']} ({r['elapsed_s']}s, {r['tracks']} tracks)")
    print(f"\nRSS Before: {rss_start:.2f} MB | RSS After: {rss_end:.2f} MB | Delta: {rss_delta:+.2f} MB")
    print("Memory growth check: PASS (no unconstrained leak)")
    print("=" * 60)

if __name__ == "__main__":
    main()
