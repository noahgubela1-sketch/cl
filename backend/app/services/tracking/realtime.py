"""WebSocket connection manager for real-time set tracking."""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections grouped by shooting_day_id."""

    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, day_id: str, websocket: WebSocket):
        await websocket.accept()
        self._connections[day_id].append(websocket)
        logger.info("WS connected: day=%s total=%d", day_id, len(self._connections[day_id]))

    def disconnect(self, day_id: str, websocket: WebSocket):
        try:
            self._connections[day_id].remove(websocket)
        except ValueError:
            pass
        logger.info("WS disconnected: day=%s total=%d", day_id, len(self._connections[day_id]))

    async def broadcast(self, day_id: str, message: dict[str, Any]):
        """Send JSON message to all clients subscribed to a shooting day."""
        payload = json.dumps(message)
        dead: list[WebSocket] = []
        for ws in list(self._connections.get(day_id, [])):
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(day_id, ws)
