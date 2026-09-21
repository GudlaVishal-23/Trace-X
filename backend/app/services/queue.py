import asyncio
import hmac
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.app.database import SessionLocal
from backend.app.models import VehicleEvent, Watchlist, Alert
from backend.app.api.ws import ws_manager

logger = logging.getLogger("tracex.queue")

# Shared HMAC secret for edge-to-server payload verification
HMAC_SECRET = b"sih2026_tracex_edge_secret_key"

class IngestionQueue:
    def __init__(self, maxsize: int = 10000):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
        self.worker_task: Optional[asyncio.Task] = None
        self.running: bool = False
        self._watchlist_cache: set = set()
        self._last_cache_refresh: float = 0

    def verify_signature(self, payload: Dict[str, Any], signature: Optional[str]) -> bool:
        if not signature:
            return True # Allow unsigned in local/dev mode
        canonical = json.dumps(payload, sort_keys=True).encode("utf-8")
        expected = hmac.new(HMAC_SECRET, canonical, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    async def enqueue(self, event_data: Dict[str, Any], signature: Optional[str] = None) -> bool:
        if not self.verify_signature(event_data, signature):
            logger.warning("Rejected event: Invalid HMAC signature")
            return False
        try:
            self.queue.put_nowait(event_data)
            return True
        except asyncio.QueueFull:
            logger.error("Ingestion queue full! Dropping event to prevent backpressure explosion.")
            return False

    async def start_worker(self):
        self.running = True
        self.worker_task = asyncio.create_task(self._process_queue())
        logger.info("Asynchronous ingestion worker pipeline started.")

    async def stop_worker(self):
        self.running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Asynchronous ingestion worker pipeline stopped.")

    def _get_active_watchlist(self, db) -> Dict[str, Watchlist]:
        # Fast query for active target plates
        targets = db.query(Watchlist).filter(Watchlist.status == "ACTIVE").all()
        return {t.plate_text.upper().replace(" ", "").replace("-", ""): t for t in targets}

    async def _process_queue(self):
        batch = []
        batch_size = 20
        flush_interval = 0.2 # seconds

        while self.running:
            try:
                try:
                    event = await asyncio.wait_for(self.queue.get(), timeout=flush_interval)
                    batch.append(event)
                    self.queue.task_done()
                except asyncio.TimeoutError:
                    pass

                # If batch is full or timeout occurred with items
                if batch:
                    await self._persist_batch(batch)
                    batch = []

            except asyncio.CancelledError:
                if batch:
                    await self._persist_batch(batch)
                break
            except Exception as e:
                logger.error(f"Error in ingestion worker loop: {e}", exc_info=True)
                await asyncio.sleep(0.5)

    async def _persist_batch(self, batch):
        db = SessionLocal()
        try:
            watchlist_map = self._get_active_watchlist(db)
            events_to_add = []
            alerts_to_add = []

            for item in batch:
                plate_clean = (item.get("plate_text") or "").upper().replace(" ", "").replace("-", "")
                
                # Check for Watchlist Hotlist Match
                is_target = plate_clean in watchlist_map
                matched_target = watchlist_map.get(plate_clean)

                ts = item.get("timestamp")
                if isinstance(ts, str):
                    try:
                        ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    except Exception:
                        ts = datetime.now(timezone.utc)
                elif not isinstance(ts, datetime):
                    ts = datetime.now(timezone.utc)

                event_obj = VehicleEvent(
                    event_id=item.get("event_id") or f"EVT_{int(datetime.now().timestamp()*1000)}",
                    camera_id=item.get("camera_id"),
                    timestamp=ts,
                    plate_text=item.get("plate_text"),
                    plate_confidence=float(item.get("plate_confidence", 0.95)),
                    observation_status=item.get("observation_status", "CONFIRMED"),
                    vehicle_type=item.get("vehicle_type", "car"),
                    vehicle_color=item.get("vehicle_color", "unknown"),
                    vehicle_make=item.get("vehicle_make", "unknown"),
                    vehicle_model=item.get("vehicle_model", "unknown"),
                    direction=item.get("direction", "unknown"),
                    latitude=float(item.get("latitude", 17.4435)),
                    longitude=float(item.get("longitude", 78.4682)),
                    road_id=item.get("road_id", "RD_UNKNOWN"),
                    image_quality_score=float(item.get("image_quality_score", 90.0)),
                    detection_confidence=float(item.get("detection_confidence", 0.95)),
                    reid_embedding_id=item.get("reid_embedding_id"),
                    thumbnail_url=item.get("thumbnail_url")
                )
                events_to_add.append(event_obj)

                # Generate alert if watchlist matched
                if is_target and matched_target:
                    alert_obj = Alert(
                        alert_type=matched_target.category,
                        plate_text=item.get("plate_text"),
                        camera_id=item.get("camera_id"),
                        timestamp=ts,
                        confidence=event_obj.plate_confidence,
                        reason=f"{matched_target.priority} HOTLIST: {matched_target.notes} (Case: {matched_target.case_reference})",
                        status="NEW"
                    )
                    alerts_to_add.append((alert_obj, {
                        "alert_type": alert_obj.alert_type,
                        "plate_text": alert_obj.plate_text,
                        "camera_id": alert_obj.camera_id,
                        "timestamp": alert_obj.timestamp.isoformat(),
                        "confidence": alert_obj.confidence,
                        "reason": alert_obj.reason,
                        "priority": matched_target.priority,
                        "case_reference": matched_target.case_reference
                    }))

            # DB persistence
            db.add_all(events_to_add)
            for alert_obj, _ in alerts_to_add:
                db.add(alert_obj)
            db.commit()

            # Real-time WebSocket broadcasts (non-blocking)
            for item in batch:
                asyncio.create_task(ws_manager.broadcast_event(item))
            for _, alert_dict in alerts_to_add:
                asyncio.create_task(ws_manager.broadcast_alert(alert_dict))

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to persist batch of {len(batch)} events: {e}", exc_info=True)
        finally:
            db.close()

ingestion_queue = IngestionQueue()
