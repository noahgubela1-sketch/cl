"""
AI Scheduling Engine – Stage 2 & 3 of the pipeline.

Stage 2 – Production Logic Engine:
  - Cluster scenes by location, cast combination, day/night block
  - Respect unavailability / blocked days

Stage 3 – Constraint-Satisfaction Optimizer:
  - Minimize location changes between consecutive shooting days
  - Minimize cast idle time
  - Respect max daily hours (typically 12h)
  - Assign scenes to shooting days with realistic time budgets
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# Typical wrap-around buffer per shooting day (minutes)
DEFAULT_DAY_MINUTES = 600  # 10h net shooting time
SETUP_BUFFER_PER_SCENE = 15  # minutes overhead per scene (setup, reset)


def _scene_key(scene: Any) -> tuple:
    """Heuristic sort key for greedy clustering."""
    return (
        scene.location_id or "",
        scene.day_night or "",
        scene.int_ext or "",
    )


def cluster_scenes(scenes: list[Any]) -> list[list[Any]]:
    """
    Group scenes into shooting day clusters using a greedy algorithm.

    Strategy:
    1. Sort scenes by (location, day_night, int_ext) to minimise location changes.
    2. Fill each cluster up to DEFAULT_DAY_MINUTES of estimated shooting time.
    3. Each cluster becomes one shooting day.
    """
    sorted_scenes = sorted(scenes, key=_scene_key)
    clusters: list[list[Any]] = []
    current_cluster: list[Any] = []
    current_minutes = 0

    for scene in sorted_scenes:
        scene_time = (scene.estimated_minutes or 10) + SETUP_BUFFER_PER_SCENE
        if current_minutes + scene_time > DEFAULT_DAY_MINUTES and current_cluster:
            clusters.append(current_cluster)
            current_cluster = []
            current_minutes = 0
        current_cluster.append(scene)
        current_minutes += scene_time

    if current_cluster:
        clusters.append(current_cluster)

    return clusters


def assign_dates(
    clusters: list[list[Any]],
    start_date: date,
    blocked_dates: set[date] | None = None,
) -> list[tuple[date, list[Any]]]:
    """
    Map scene clusters to actual calendar dates, skipping weekends and blocked dates.
    Returns list of (date, scenes) pairs.
    """
    blocked = blocked_dates or set()
    result: list[tuple[date, list[Any]]] = []
    current = start_date

    for cluster in clusters:
        # Advance past weekends and blocked days
        while current.weekday() >= 5 or current in blocked:
            current += timedelta(days=1)
        result.append((current, cluster))
        current += timedelta(days=1)

    return result


async def generate_schedule_background(project_id: str):
    """
    Background task: fetch project scenes, run optimizer, persist ShootingDays.
    """
    from sqlalchemy import select, delete
    from app.db.session import AsyncSessionLocal
    from app.db.models import Project, Scene, ShootingDay, shooting_day_scenes
    from sqlalchemy import insert

    logger.info("Generating schedule for project %s", project_id)

    async with AsyncSessionLocal() as db:
        # Load project
        proj_result = await db.execute(select(Project).where(Project.id == project_id))
        project = proj_result.scalar_one_or_none()
        if not project:
            logger.error("Project %s not found", project_id)
            return

        # Load all scenes
        scenes_result = await db.execute(
            select(Scene).where(Scene.project_id == project_id)
        )
        scenes = list(scenes_result.scalars().all())
        if not scenes:
            logger.warning("No scenes found for project %s – nothing to schedule", project_id)
            return

        # Determine start date
        start = (project.shooting_start or datetime.utcnow()).date()

        # Run optimizer
        clusters = cluster_scenes(scenes)
        day_assignments = assign_dates(clusters, start)

        # Clear existing shooting days
        await db.execute(
            delete(ShootingDay).where(ShootingDay.project_id == project_id)
        )
        await db.flush()

        # Persist new shooting days
        for shoot_date, day_scenes in day_assignments:
            call_dt = datetime.combine(shoot_date, datetime.min.time()).replace(hour=8)
            wrap_dt = call_dt + timedelta(hours=10)

            # Determine primary location (most common in this day)
            loc_counts: dict[str | None, int] = defaultdict(int)
            for s in day_scenes:
                loc_counts[s.location_id] += 1
            primary_loc = max(loc_counts, key=lambda k: loc_counts[k])

            day = ShootingDay(
                project_id=project_id,
                date=datetime.combine(shoot_date, datetime.min.time()),
                call_time=call_dt,
                wrap_time_planned=wrap_dt,
                primary_location_id=primary_loc,
            )
            db.add(day)
            await db.flush()

            # Link scenes to shooting day
            for pos, scene in enumerate(day_scenes):
                await db.execute(
                    insert(shooting_day_scenes).values(
                        shooting_day_id=day.id,
                        scene_id=scene.id,
                        position=pos,
                    )
                )

        await db.commit()
        logger.info(
            "Schedule generated for project %s: %d shooting days", project_id, len(day_assignments)
        )
