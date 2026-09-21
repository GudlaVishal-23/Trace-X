import os
import uuid
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from backend.app.database import get_db, SessionLocal
from backend.app.models import IngestJob, JobDetection, JobTrack, Camera
from backend.app.ingest.video_worker import run_video_worker, JOB_SUBSCRIBERS, get_event_buffer

logger = logging.getLogger("tracex.ingest_router")

router = APIRouter(prefix="/ingest", tags=["Video Ingestion & Scan Theatre"])
ws_router = APIRouter(tags=["Video Ingestion WebSocket"])

# ThreadPoolExecutor owned by backend (Section 1.2: max_workers=2)
ingest_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="tracex_ingest")

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
MAX_FILE_SIZE = 500 * 1024 * 1024 # 500 MB

def range_streamer(file_path: str, start: int, length: int, chunk_size: int = 64 * 1024):
    """Yields chunks of a file within a byte range for HTTP 206 streaming."""
    with open(file_path, "rb") as f:
        f.seek(start)
        remaining = length
        while remaining > 0:
            bytes_to_read = min(remaining, chunk_size)
            data = f.read(bytes_to_read)
            if not data:
                break
            remaining -= len(data)
            yield data

def build_range_response(file_path: str, request: Request, content_type: str = "video/mp4"):
    """Handles HTTP Range requests enabling seeking in Chrome and Safari video players."""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested video artifact not found")

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("Range")

    if not range_header:
        # Full file streaming
        return StreamingResponse(
            range_streamer(file_path, 0, file_size),
            status_code=200,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
                "Content-Type": content_type
            }
        )

    # Parse Range: bytes=start-end
    try:
        range_value = range_header.strip().split("=")[1]
        parts = range_value.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
        end = min(end, file_size - 1)
        length = end - start + 1

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(length),
            "Content-Type": content_type
        }
        return StreamingResponse(range_streamer(file_path, start, length), status_code=206, headers=headers)
    except Exception as e:
        logger.error(f"Range parsing error: {e}")
        return StreamingResponse(
            range_streamer(file_path, 0, file_size),
            status_code=200,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
                "Content-Type": content_type
            }
        )

import shutil

@router.post("/upload")
async def upload_video(
    file: Optional[UploadFile] = File(None),
    preset_filename: Optional[str] = Form(None),
    camera_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Accepts video upload or server preset filename + camera_id.
    Validates file extension and size (<= 500 MB).
    Saves file to data/uploads/{job_id}{ext} and queues async worker.
    """
    if not file and not preset_filename:
        raise HTTPException(status_code=400, detail="Either video file or preset_filename must be provided")

    # Verify camera exists
    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera node {camera_id} not registered in topology")

    job_id = str(uuid.uuid4())
    upload_dir = os.path.join(os.getcwd(), "data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    if preset_filename:
        filename = preset_filename
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        src_candidates = [
            os.path.join(os.getcwd(), "sample videos", preset_filename),
            os.path.join(os.getcwd(), "scratch", preset_filename)
        ]
        src_path = next((p for p in src_candidates if os.path.exists(p)), None)
        if not src_path:
            raise HTTPException(status_code=404, detail=f"Preset {preset_filename} not found on server")
        saved_video_path = os.path.join(upload_dir, f"{job_id}{ext}")
        shutil.copyfile(src_path, saved_video_path)
    else:
        filename = file.filename or "traffic_capture.mp4"
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported format {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

        saved_video_path = os.path.join(upload_dir, f"{job_id}{ext}")
        total_bytes = 0
        with open(saved_video_path, "wb") as dest:
            while True:
                chunk = await file.read(1024 * 1024) # 1 MB chunks
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE:
                    dest.close()
                    if os.path.exists(saved_video_path):
                        os.remove(saved_video_path)
                    raise HTTPException(status_code=413, detail=f"Video exceeds maximum allowed size of 500 MB")
                dest.write(chunk)

    # Create job in database
    job = IngestJob(
        job_id=job_id,
        filename=filename,
        camera_id=camera_id,
        status="QUEUED"
    )
    db.add(job)
    db.commit()

    # Dispatch to background ThreadPoolExecutor without blocking request
    ingest_pool.submit(run_video_worker, job_id, saved_video_path, camera_id)

    return {
        "job_id": job_id,
        "filename": filename,
        "camera_id": camera_id,
        "status": "QUEUED",
        "message": "Video queued for frame-by-frame edge analysis and tracking"
    }

@router.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    """Returns recent ingestion jobs."""
    jobs = db.query(IngestJob).order_by(IngestJob.started_at.desc()).limit(20).all()
    res = []
    for j in jobs:
        stats = json.loads(j.stats_json) if j.stats_json else {}
        res.append({
            "job_id": j.job_id,
            "filename": j.filename,
            "camera_id": j.camera_id,
            "status": j.status,
            "total_frames": j.total_frames,
            "done_frames": j.done_frames,
            "fps": j.fps,
            "duration_s": j.duration_s,
            "started_at": j.started_at,
            "finished_at": j.finished_at,
            "error": j.error,
            "stats": stats
        })
    return res

@router.get("/jobs/{job_id}")
def get_job_detail(job_id: str, db: Session = Depends(get_db)):
    """Returns status, frame counters, and summary statistics for a specific job."""
    job = db.query(IngestJob).filter(IngestJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Ingest job not found")

    n_dets = db.query(JobDetection).filter(JobDetection.job_id == job_id).count()
    n_tracks = db.query(JobTrack).filter(JobTrack.job_id == job_id).count()
    stats = json.loads(job.stats_json) if job.stats_json else {}

    return {
        "job_id": job.job_id,
        "filename": job.filename,
        "camera_id": job.camera_id,
        "status": job.status,
        "total_frames": job.total_frames,
        "done_frames": job.done_frames,
        "fps": job.fps,
        "width": job.width,
        "height": job.height,
        "duration_s": job.duration_s,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
        "error": job.error,
        "detections_count": n_dets,
        "tracks_count": n_tracks,
        "stats": stats
    }

@router.get("/jobs/{job_id}/detections")
def get_job_detections(job_id: str, since_frame: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    """Returns paginated detections for a job with optional ?since_frame= filter."""
    dets = db.query(JobDetection).filter(
        JobDetection.job_id == job_id,
        JobDetection.frame_idx >= since_frame
    ).order_by(JobDetection.frame_idx.asc()).limit(limit).all()

    return [{
        "det_id": d.det_id,
        "frame_idx": d.frame_idx,
        "video_ts": d.video_ts,
        "track_id": d.track_id,
        "bbox": json.loads(d.bbox_json) if d.bbox_json else [],
        "plate_bbox": json.loads(d.plate_bbox_json) if d.plate_bbox_json else [],
        "vehicle_class": d.vehicle_class,
        "color": d.color,
        "plate_raw": d.plate_raw,
        "plate_conf": d.plate_conf,
        "blur_score": d.blur_score,
        "quality_score": d.quality_score,
        "crop_path": d.crop_path,
        "plate_crop_path": d.plate_crop_path,
        "clahe_crop_path": d.clahe_crop_path
    } for d in dets]

@router.get("/jobs/{job_id}/tracks")
def get_job_tracks(job_id: str, db: Session = Depends(get_db)):
    """Returns fused per-vehicle results with Bayesian consensus plate predictions."""
    tracks = db.query(JobTrack).filter(JobTrack.job_id == job_id).all()
    return [{
        "job_id": t.job_id,
        "track_id": t.track_id,
        "first_frame": t.first_frame,
        "last_frame": t.last_frame,
        "n_frames": t.n_frames,
        "fused_plate": t.fused_plate,
        "fused_conf": t.fused_conf,
        "vehicle_class": t.vehicle_class,
        "color": t.color,
        "best_det_id": t.best_det_id,
        "watchlist_hit": t.watchlist_hit
    } for t in tracks]

@router.get("/jobs/{job_id}/video")
def stream_original_video(job_id: str, request: Request, db: Session = Depends(get_db)):
    """Streams original uploaded video with HTTP Range header support."""
    job = db.query(IngestJob).filter(IngestJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Ingest job not found")

    upload_dir = os.path.join(os.getcwd(), "data", "uploads")
    # Search for job file with any extension
    target_path = None
    for ext in ALLOWED_EXTENSIONS:
        candidate = os.path.join(upload_dir, f"{job_id}{ext}")
        if os.path.exists(candidate):
            target_path = candidate
            break

    if not target_path:
        raise HTTPException(status_code=404, detail="Original video file not found")

    return build_range_response(target_path, request)

@router.get("/jobs/{job_id}/annotated")
def stream_annotated_video(job_id: str, request: Request, db: Session = Depends(get_db)):
    """Streams annotated MP4 with bounding boxes, HUD, and Range support."""
    annotated_dir = os.path.join(os.getcwd(), "data", "uploads", "annotated")
    annotated_path = os.path.join(annotated_dir, f"{job_id}_annotated.mp4")

    if not os.path.exists(annotated_path):
        raise HTTPException(status_code=404, detail="Annotated video not yet ready or processing")

    return build_range_response(annotated_path, request)

@ws_router.websocket("/ws/ingest/{job_id}")
async def websocket_ingest_stream(websocket: WebSocket, job_id: str):
    """
    WebSocket live event stream for scan theatre.
    Replays buffered events (deque maxlen 2000) so late-connecting clients catch up instantly.
    """
    await websocket.accept()
    if job_id not in JOB_SUBSCRIBERS:
        JOB_SUBSCRIBERS[job_id] = []
    JOB_SUBSCRIBERS[job_id].append(websocket)

    # Replay buffer to catch up
    buf = get_event_buffer(job_id)
    for evt in list(buf):
        try:
            await websocket.send_text(json.dumps(evt))
        except Exception:
            break

    try:
        while True:
            # Keep-alive loop
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        pass
    finally:
        if job_id in JOB_SUBSCRIBERS and websocket in JOB_SUBSCRIBERS[job_id]:
            JOB_SUBSCRIBERS[job_id].remove(websocket)
