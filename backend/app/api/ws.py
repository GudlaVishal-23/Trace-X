from typing import List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger("tracex.ws")

router = APIRouter(tags=["WebSockets"])

class ConnectionManager:
    def __init__(self):
        self.event_connections: List[WebSocket] = []
        self.alert_connections: List[WebSocket] = []

    async def connect_events(self, websocket: WebSocket):
        await websocket.accept()
        self.event_connections.append(websocket)
        logger.info(f"WebSocket client connected to events stream. Total: {len(self.event_connections)}")

    def disconnect_events(self, websocket: WebSocket):
        if websocket in self.event_connections:
            self.event_connections.remove(websocket)

    async def connect_alerts(self, websocket: WebSocket):
        await websocket.accept()
        self.alert_connections.append(websocket)
        logger.info(f"WebSocket client connected to alerts stream. Total: {len(self.alert_connections)}")

    def disconnect_alerts(self, websocket: WebSocket):
        if websocket in self.alert_connections:
            self.alert_connections.remove(websocket)

    async def broadcast_event(self, data: Dict[str, Any]):
        dead_connections = []
        for connection in self.event_connections:
            try:
                await connection.send_json(data)
            except Exception:
                dead_connections.append(connection)
        for dead in dead_connections:
            self.disconnect_events(dead)

    async def broadcast_alert(self, data: Dict[str, Any]):
        dead_connections = []
        for connection in self.alert_connections:
            try:
                await connection.send_json(data)
            except Exception:
                dead_connections.append(connection)
        for dead in dead_connections:
            self.disconnect_alerts(dead)

ws_manager = ConnectionManager()

@router.websocket("/ws/events")
async def websocket_events_endpoint(websocket: WebSocket):
    await ws_manager.connect_events(websocket)
    try:
        while True:
            # Keep-alive heartbeat listener
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_events(websocket)
    except Exception:
        ws_manager.disconnect_events(websocket)

@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    await ws_manager.connect_alerts(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_alerts(websocket)
    except Exception:
        ws_manager.disconnect_alerts(websocket)
