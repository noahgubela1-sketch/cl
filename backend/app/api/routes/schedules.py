"""Schedule generation and management routes."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_current_user
from app.db.models import Project, Scene, ShootingDay, User
from app.db.session import get_db
from app.schemas.scene import SceneOut, SceneUpdate
from app.services.scheduling.optimizer import generate_schedule_background

router = APIRouter()


@router.post("/{project_id}/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_schedule(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger AI schedule generation for a project."""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    background_tasks.add_task(generate_schedule_background, project_id)
    return {"status": "generation_queued", "project_id": project_id}


@router.get("/{project_id}/scenes", response_model=list[SceneOut])
async def list_scenes(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify ownership
    proj_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(Scene).where(Scene.project_id == project_id).order_by(Scene.scene_number)
    )
    return result.scalars().all()


@router.patch("/{project_id}/scenes/{scene_id}", response_model=SceneOut)
async def update_scene(
    project_id: str,
    scene_id: str,
    body: SceneUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Scene).where(Scene.id == scene_id, Scene.project_id == project_id)
    )
    scene = result.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(scene, field, value)
    await db.flush()
    return scene


@router.get("/{project_id}/shooting-days")
async def list_shooting_days(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ShootingDay)
        .where(ShootingDay.project_id == project_id)
        .order_by(ShootingDay.date)
    )
    days = result.scalars().all()
    return [
        {
            "id": d.id,
            "date": d.date,
            "call_time": d.call_time,
            "wrap_time_planned": d.wrap_time_planned,
            "primary_location_id": d.primary_location_id,
        }
        for d in days
    ]
