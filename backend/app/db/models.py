"""SQLAlchemy ORM models – core domain entities for SceneMind AI."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    Column,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.session import Base


# ── Helpers ──────────────────────────────────────────────────────────────────

def _uuid():
    return str(uuid.uuid4())


# ── Many-to-many association tables ──────────────────────────────────────────

scene_cast = Table(
    "scene_cast",
    Base.metadata,
    Column("scene_id", ForeignKey("scenes.id"), primary_key=True),
    Column("cast_member_id", ForeignKey("cast_members.id"), primary_key=True),
)

shooting_day_scenes = Table(
    "shooting_day_scenes",
    Base.metadata,
    Column("shooting_day_id", ForeignKey("shooting_days.id"), primary_key=True),
    Column("scene_id", ForeignKey("scenes.id"), primary_key=True),
    Column("position", Integer, default=0),
)


# ── Enums ─────────────────────────────────────────────────────────────────────

class DayNight(str, enum.Enum):
    day = "day"
    night = "night"
    dusk = "dusk"
    dawn = "dawn"


class InteriorExterior(str, enum.Enum):
    interior = "interior"
    exterior = "exterior"


class ProjectStatus(str, enum.Enum):
    pre_production = "pre_production"
    shooting = "shooting"
    post_production = "post_production"
    completed = "completed"


class TrackingEventType(str, enum.Enum):
    scene_start = "scene_start"
    scene_end = "scene_end"
    setup_start = "setup_start"
    setup_end = "setup_end"
    break_start = "break_start"
    break_end = "break_end"
    technical_delay = "technical_delay"
    weather_delay = "weather_delay"
    day_wrap = "day_wrap"


# ── Core models ───────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    projects: Mapped[list["Project"]] = relationship(back_populates="owner")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.pre_production
    )
    shooting_start: Mapped[datetime | None] = mapped_column(DateTime)
    shooting_end: Mapped[datetime | None] = mapped_column(DateTime)
    budget_cents: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User"] = relationship(back_populates="projects")
    scenes: Mapped[list["Scene"]] = relationship(back_populates="project")
    cast_members: Mapped[list["CastMember"]] = relationship(back_populates="project")
    locations: Mapped[list["Location"]] = relationship(back_populates="project")
    shooting_days: Mapped[list["ShootingDay"]] = relationship(back_populates="project")
    scripts: Mapped[list["Script"]] = relationship(back_populates="project")


class Script(Base):
    __tablename__ = "scripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    filename: Mapped[str] = mapped_column(String(500))
    storage_path: Mapped[str] = mapped_column(String(1000))
    file_format: Mapped[str] = mapped_column(String(20))  # pdf | fdx | fountain | celtx
    parsed: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="scripts")


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(Text)
    daily_cost_cents: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)

    project: Mapped["Project"] = relationship(back_populates="locations")
    scenes: Mapped[list["Scene"]] = relationship(back_populates="location")


class CastMember(Base):
    __tablename__ = "cast_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(255))
    role_name: Mapped[str] = mapped_column(String(255))
    daily_rate_cents: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)

    project: Mapped["Project"] = relationship(back_populates="cast_members")
    scenes: Mapped[list["Scene"]] = relationship(
        secondary=scene_cast, back_populates="cast_members"
    )


class Scene(Base):
    __tablename__ = "scenes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"))

    scene_number: Mapped[str] = mapped_column(String(20))  # e.g. "14A"
    heading: Mapped[str | None] = mapped_column(Text)       # slugline from script
    description: Mapped[str | None] = mapped_column(Text)
    day_night: Mapped[DayNight | None] = mapped_column(Enum(DayNight))
    int_ext: Mapped[InteriorExterior | None] = mapped_column(Enum(InteriorExterior))
    estimated_minutes: Mapped[int | None] = mapped_column(Integer)
    page_count: Mapped[float | None] = mapped_column(Float)  # eighths of a page
    priority: Mapped[int] = mapped_column(Integer, default=5)  # 1 (low) – 10 (high)
    notes: Mapped[str | None] = mapped_column(Text)

    project: Mapped["Project"] = relationship(back_populates="scenes")
    location: Mapped["Location | None"] = relationship(back_populates="scenes")
    cast_members: Mapped[list["CastMember"]] = relationship(
        secondary=scene_cast, back_populates="scenes"
    )
    shooting_days: Mapped[list["ShootingDay"]] = relationship(
        secondary=shooting_day_scenes, back_populates="scenes"
    )
    tracking_events: Mapped[list["TrackingEvent"]] = relationship(back_populates="scene")


class ShootingDay(Base):
    __tablename__ = "shooting_days"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    date: Mapped[datetime] = mapped_column(DateTime)
    call_time: Mapped[datetime | None] = mapped_column(DateTime)
    wrap_time_planned: Mapped[datetime | None] = mapped_column(DateTime)
    wrap_time_actual: Mapped[datetime | None] = mapped_column(DateTime)
    primary_location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"))
    notes: Mapped[str | None] = mapped_column(Text)

    project: Mapped["Project"] = relationship(back_populates="shooting_days")
    scenes: Mapped[list["Scene"]] = relationship(
        secondary=shooting_day_scenes, back_populates="shooting_days"
    )
    tracking_events: Mapped[list["TrackingEvent"]] = relationship(
        back_populates="shooting_day"
    )


class TrackingEvent(Base):
    __tablename__ = "tracking_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    shooting_day_id: Mapped[str] = mapped_column(ForeignKey("shooting_days.id"))
    scene_id: Mapped[str | None] = mapped_column(ForeignKey("scenes.id"))
    event_type: Mapped[TrackingEventType] = mapped_column(Enum(TrackingEventType))
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    delta_minutes: Mapped[int | None] = mapped_column(Integer)  # deviation from plan
    notes: Mapped[str | None] = mapped_column(Text)

    shooting_day: Mapped["ShootingDay"] = relationship(back_populates="tracking_events")
    scene: Mapped["Scene | None"] = relationship(back_populates="tracking_events")
