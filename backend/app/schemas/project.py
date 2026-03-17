"""Pydantic schemas for Project endpoints."""

from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    shooting_start: datetime | None = None
    shooting_end: datetime | None = None
    budget_cents: int | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    shooting_start: datetime | None = None
    shooting_end: datetime | None = None
    budget_cents: int | None = None
    status: str | None = None


class ProjectOut(BaseModel):
    id: str
    name: str
    description: str | None
    status: str
    shooting_start: datetime | None
    shooting_end: datetime | None
    budget_cents: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
