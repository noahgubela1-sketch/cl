"""Live set-tracking routes + WebSocket endpoint."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_current_user
from app.db.models import ShootingDay, TrackingEvent, TrackingEventType, User
from app.db.session import get_db
from app.services.tracking.realtime import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


class TrackingEventIn:
    def __init__(
        self,
        shooting_day_id: str,
        event_type: str,
        scene_id: str | None = None,
        delta_minutes: int | None = None,
        notes: str | None = None,
    ):
        self.shooting_day_id = shooting_day_id
        self.event_type = event_type
        self.scene_id = scene_id
        self.delta_minutes = delta_minutes
        self.notes = notes


@router.post("/events", status_code=status.HTTP_201_CREATED)
async def log_tracking_event(
    shooting_day_id: str,
    event_type: str,
    scene_id: str | None = None,
    delta_minutes: int | None = None,
    notes: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate event type
    try:
        evt_type = TrackingEventType(event_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown event type: {event_type}")

    event = TrackingEvent(
        id=str(uuid.uuid4()),
        shooting_day_id=shooting_day_id,
        scene_id=scene_id,
        event_type=evt_type,
        timestamp=datetime.utcnow(),
        delta_minutes=delta_minutes,
        notes=notes,
    )
    db.add(event)
    await db.flush()

    # Broadcast to all connected clients for this shooting day
    await manager.broadcast(
        shooting_day_id,
        {
            "event_id": event.id,
            "event_type": event_type,
            "scene_id": scene_id,
            "delta_minutes": delta_minutes,
            "timestamp": event.timestamp.isoformat(),
        },
    )
    return {"event_id": event.id}


@router.get("/events/{shooting_day_id}")
async def get_day_events(
    shooting_day_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(TrackingEvent)
        .where(TrackingEvent.shooting_day_id == shooting_day_id)
        .order_by(TrackingEvent.timestamp)
    )
    events = result.scalars().all()
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "scene_id": e.scene_id,
            "timestamp": e.timestamp,
            "delta_minutes": e.delta_minutes,
            "notes": e.notes,
        }
        for e in events
    ]


@router.websocket("/ws/{shooting_day_id}")
async def websocket_tracking(websocket: WebSocket, shooting_day_id: str):
    """Real-time WebSocket feed for a shooting day."""
    await manager.connect(shooting_day_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # keep connection alive (ping/pong)
    except WebSocketDisconnect:
        manager.disconnect(shooting_day_id, websocket)
