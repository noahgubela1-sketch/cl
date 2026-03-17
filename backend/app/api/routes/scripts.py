"""Script upload and parsing routes."""

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid, os, shutil

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.models import Project, Script, User
from app.db.session import get_db
from app.services.ai.script_parser import parse_script_background

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "fdx", "fountain", "celtx"}


@router.post("/{project_id}/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_script(
    project_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate project ownership
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")

    # Persist file
    storage_dir = os.path.join(settings.LOCAL_STORAGE_PATH, project_id)
    os.makedirs(storage_dir, exist_ok=True)
    script_id = str(uuid.uuid4())
    dest = os.path.join(storage_dir, f"{script_id}.{ext}")
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    script = Script(
        id=script_id,
        project_id=project_id,
        filename=file.filename,
        storage_path=dest,
        file_format=ext,
    )
    db.add(script)
    await db.flush()

    # Kick off async parsing
    background_tasks.add_task(parse_script_background, script_id, dest, ext, project_id)

    return {"script_id": script_id, "status": "parsing_queued"}


@router.get("/{project_id}/scripts")
async def list_scripts(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Script).where(Script.project_id == project_id)
    )
    scripts = result.scalars().all()
    return [
        {
            "id": s.id,
            "filename": s.filename,
            "file_format": s.file_format,
            "parsed": s.parsed,
            "uploaded_at": s.uploaded_at,
        }
        for s in scripts
    ]
