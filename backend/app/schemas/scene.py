"""Pydantic schemas for Scene endpoints."""

from pydantic import BaseModel


class SceneOut(BaseModel):
    id: str
    project_id: str
    scene_number: str
    heading: str | None
    description: str | None
    day_night: str | None
    int_ext: str | None
    estimated_minutes: int | None
    page_count: float | None
    priority: int
    location_id: str | None
    notes: str | None

    model_config = {"from_attributes": True}


class SceneUpdate(BaseModel):
    scene_number: str | None = None
    heading: str | None = None
    description: str | None = None
    day_night: str | None = None
    int_ext: str | None = None
    estimated_minutes: int | None = None
    page_count: float | None = None
    priority: int | None = None
    location_id: str | None = None
    notes: str | None = None
