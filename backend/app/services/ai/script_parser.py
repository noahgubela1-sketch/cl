"""
Script Parsing Service – Stage 1 of the AI pipeline.

Uses an LLM to extract structured scene data from screenplay formats:
  PDF, Final Draft (FDX), Fountain, Celtx

Returns a list of ParsedScene objects that are then stored in the DB.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from typing import Literal

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

DayNightType = Literal["day", "night", "dusk", "dawn"]
IntExtType = Literal["interior", "exterior"]


@dataclass
class ParsedScene:
    scene_number: str
    heading: str
    description: str
    day_night: DayNightType | None
    int_ext: IntExtType | None
    estimated_minutes: int
    page_count: float
    cast_names: list[str] = field(default_factory=list)
    location_name: str | None = None
    notes: str = ""


SYSTEM_PROMPT = """You are an expert screenplay analyst for a film production scheduling system.
Given a screenplay excerpt, extract all scenes as structured JSON.

For each scene return:
- scene_number: string (e.g. "1", "14A")
- heading: the full slugline (e.g. "INT. OFFICE - DAY")
- description: 1-2 sentence summary of what happens
- day_night: "day" | "night" | "dusk" | "dawn" | null
- int_ext: "interior" | "exterior" | null
- location_name: name of the location (extracted from slugline)
- cast_names: list of character names appearing in this scene
- estimated_minutes: estimated shoot time in minutes (typical: 2-15 min per page, 1 page ≈ 1 min)
- page_count: number of pages (in eighths, e.g. 1.375 = 11/8 pages)

Return only valid JSON: { "scenes": [ ... ] }"""


async def parse_script_text(script_text: str) -> list[ParsedScene]:
    """Send script text to LLM and parse the structured response."""
    # Chunk large scripts to stay within context window
    chunks = _chunk_script(script_text, max_chars=40_000)
    all_scenes: list[ParsedScene] = []

    for i, chunk in enumerate(chunks):
        logger.info("Parsing script chunk %d/%d", i + 1, len(chunks))
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": chunk},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        for s in data.get("scenes", []):
            all_scenes.append(ParsedScene(**{k: s.get(k) for k in ParsedScene.__dataclass_fields__}))

    return all_scenes


def extract_text_from_pdf(path: str) -> str:
    """Extract raw text from a PDF screenplay."""
    import pdfplumber

    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n".join(pages)


def extract_text_from_fdx(path: str) -> str:
    """Extract text from Final Draft .fdx (XML) format."""
    import xml.etree.ElementTree as ET

    tree = ET.parse(path)
    root = tree.getroot()
    paragraphs = []
    for elem in root.iter():
        if elem.text:
            paragraphs.append(elem.text.strip())
    return "\n".join(p for p in paragraphs if p)


def extract_text_from_fountain(path: str) -> str:
    """Return raw .fountain file content (plain text)."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def _chunk_script(text: str, max_chars: int = 40_000) -> list[str]:
    """Split large scripts into overlapping chunks at scene boundaries."""
    # Split at INT./EXT. scene headings
    scene_pattern = re.compile(r"(?m)^(INT\.|EXT\.|I/E\.)", re.IGNORECASE)
    splits = [m.start() for m in scene_pattern.finditer(text)]

    if not splits:
        return [text]

    chunks = []
    start = 0
    for split in splits[1:]:
        if split - start > max_chars:
            chunks.append(text[start:split])
            start = split
    chunks.append(text[start:])
    return chunks


async def parse_script_background(script_id: str, path: str, fmt: str, project_id: str):
    """Background task: parse script and persist scenes to DB."""
    from app.db.session import AsyncSessionLocal
    from app.db.models import CastMember, Location, Scene, Script
    from sqlalchemy import select

    logger.info("Starting background parse for script %s (format=%s)", script_id, fmt)

    # 1. Extract text
    try:
        if fmt == "pdf":
            text = extract_text_from_pdf(path)
        elif fmt == "fdx":
            text = extract_text_from_fdx(path)
        else:  # fountain / celtx (plain text)
            text = extract_text_from_fountain(path)
    except Exception as exc:
        logger.error("Text extraction failed for %s: %s", script_id, exc)
        return

    # 2. LLM parse
    try:
        parsed_scenes = await parse_script_text(text)
    except Exception as exc:
        logger.error("LLM parsing failed for %s: %s", script_id, exc)
        return

    # 3. Persist to DB
    async with AsyncSessionLocal() as db:
        location_cache: dict[str, str] = {}  # name -> id
        cast_cache: dict[str, str] = {}       # name -> id

        for ps in parsed_scenes:
            # Upsert location
            loc_id: str | None = None
            if ps.location_name:
                if ps.location_name not in location_cache:
                    result = await db.execute(
                        select(Location).where(
                            Location.project_id == project_id,
                            Location.name == ps.location_name,
                        )
                    )
                    loc = result.scalar_one_or_none()
                    if not loc:
                        loc = Location(id=str(uuid.uuid4()), project_id=project_id, name=ps.location_name)
                        db.add(loc)
                        await db.flush()
                    location_cache[ps.location_name] = loc.id
                loc_id = location_cache[ps.location_name]

            # Create scene
            scene = Scene(
                id=str(uuid.uuid4()),
                project_id=project_id,
                location_id=loc_id,
                scene_number=ps.scene_number,
                heading=ps.heading,
                description=ps.description,
                day_night=ps.day_night,
                int_ext=ps.int_ext,
                estimated_minutes=ps.estimated_minutes,
                page_count=ps.page_count,
                notes=ps.notes,
            )
            db.add(scene)
            await db.flush()

            # Upsert cast members and associate
            for cast_name in ps.cast_names:
                if cast_name not in cast_cache:
                    result = await db.execute(
                        select(CastMember).where(
                            CastMember.project_id == project_id,
                            CastMember.name == cast_name,
                        )
                    )
                    cm = result.scalar_one_or_none()
                    if not cm:
                        cm = CastMember(
                            id=str(uuid.uuid4()),
                            project_id=project_id,
                            name=cast_name,
                            role_name=cast_name,
                        )
                        db.add(cm)
                        await db.flush()
                    cast_cache[cast_name] = cm.id

                # Link scene ↔ cast (raw insert to avoid loading full relationship)
                from app.db.models import scene_cast
                from sqlalchemy import insert
                await db.execute(
                    insert(scene_cast).values(scene_id=scene.id, cast_member_id=cast_cache[cast_name])
                )

        # Mark script as parsed
        result = await db.execute(select(Script).where(Script.id == script_id))
        script = result.scalar_one_or_none()
        if script:
            script.parsed = True

        await db.commit()
        logger.info("Script %s parsed: %d scenes persisted", script_id, len(parsed_scenes))
