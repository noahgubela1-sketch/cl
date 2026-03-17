# SceneMind AI – Architecture Decision Records

## ADR-001: Async Python backend (FastAPI + asyncpg)

**Status:** Accepted

**Context:** The scheduling optimizer and LLM script parsing are I/O-bound operations that can take 5–60 seconds per request. We need the API to remain responsive for other requests while these run.

**Decision:** Use FastAPI with asyncpg (async PostgreSQL driver) and background tasks via FastAPI `BackgroundTasks` for initial MVP. Migrate heavy jobs to Celery + Redis when concurrency demands grow.

**Consequences:** Lower latency for API responses; async code requires careful handling of DB sessions.

---

## ADR-002: LLM-based script parsing (OpenAI GPT-4o)

**Status:** Accepted

**Context:** Screenplays come in multiple formats (PDF, FDX, Fountain) with varying structures. Training a specialized NLP model requires significant labeled data we don't have yet.

**Decision:** Use GPT-4o with structured JSON output for scene extraction in MVP. The system prompt provides domain-specific guidance (sluglines, character names, day/night detection). Switch to fine-tuned open-source model (Mistral/Llama) when training data is accumulated.

**Consequences:** Higher per-parse cost (~$0.10–0.50 per script) but no training pipeline needed. Accuracy > 90% from day one.

---

## ADR-003: Greedy clustering + date assignment for scheduling (MVP)

**Status:** Accepted

**Context:** Optimal scheduling is NP-hard (constraint satisfaction). A full OR-Tools solver is accurate but complex to implement and tune.

**Decision:** MVP uses greedy clustering by (location, day_night, int_ext) + time-budget filling. Add OR-Tools constraint solver in Phase 2 when we have user feedback on scheduling quality.

**Consequences:** ~15–25% suboptimal vs. full solver, but 10x faster to implement and still far superior to manual scheduling.

---

## ADR-004: WebSocket for live set tracking

**Status:** Accepted

**Context:** On-set tracking events (scene starts, delays) need to reach the production dashboard in < 2 seconds.

**Decision:** Single FastAPI WebSocket endpoint per shooting day. ConnectionManager holds in-process socket list. For multi-instance deployments, publish to Redis pub/sub.

**Consequences:** Works well for single-instance MVP. Redis pub/sub integration required before horizontal scaling.

---

## ADR-005: Next.js 14 App Router for frontend

**Status:** Accepted

**Context:** Dashboard needs SSR for initial load performance; client components needed for real-time updates and drag-and-drop.

**Decision:** Next.js 14 App Router with a mix of server components (static pages) and client components (interactive dashboard, schedule editor).

**Consequences:** Slightly steeper learning curve than pure SPA but better performance and SEO for landing/marketing pages.
