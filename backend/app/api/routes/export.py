"""Export routes – PDF, Excel, iCal."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_current_user
from app.db.models import Project, User
from app.db.session import get_db
from app.services.scheduling.exporter import (
    export_schedule_pdf,
    export_schedule_xlsx,
    export_schedule_ical,
)

router = APIRouter()


@router.get("/{project_id}/pdf")
async def export_pdf(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _assert_ownership(project_id, current_user.id, db)
    pdf_bytes = await export_schedule_pdf(project_id, db)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=schedule_{project_id}.pdf"},
    )


@router.get("/{project_id}/xlsx")
async def export_xlsx(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _assert_ownership(project_id, current_user.id, db)
    xlsx_bytes = await export_schedule_xlsx(project_id, db)
    return StreamingResponse(
        iter([xlsx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=schedule_{project_id}.xlsx"},
    )


@router.get("/{project_id}/ical")
async def export_ical(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _assert_ownership(project_id, current_user.id, db)
    ical_text = await export_schedule_ical(project_id, db)
    return StreamingResponse(
        iter([ical_text.encode()]),
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=schedule_{project_id}.ics"},
    )


async def _assert_ownership(project_id: str, owner_id: str, db: AsyncSession):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == owner_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
