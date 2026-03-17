"""SceneMind AI – FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, projects, scripts, schedules, tracking, export
from app.core.config import settings
from app.db.session import engine
from app.db import models  # noqa: F401 – ensure models are registered


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown – close DB connections etc.
    await engine.dispose()


app = FastAPI(
    title="SceneMind AI",
    description="AI-powered film production scheduling platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(scripts.router, prefix="/api/v1/scripts", tags=["scripts"])
app.include_router(schedules.router, prefix="/api/v1/schedules", tags=["schedules"])
app.include_router(tracking.router, prefix="/api/v1/tracking", tags=["tracking"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])


@app.get("/health", tags=["meta"])
async def health_check():
    return {"status": "ok", "version": app.version}
