# SceneMind AI

**AI-powered SaaS platform for automated film production scheduling.**

SceneMind AI automates the entire planning process for film productions and optimizes it in real-time during shooting. The platform consists of two tightly integrated modules:

- **Module 1 – AI Scheduling Engine**: Automated creation of optimized shooting schedules from scripts, cast lists, and production data. Reduces planning effort from 1–3 days to under 30 minutes.
- **Module 2 – Live Production Monitor**: Real-time tracking on set with automatic schedule adjustment, crew notifications, and production dashboard.

---

## Architecture

```
scenemind-ai/
├── backend/          # Python FastAPI – AI services, scheduling engine, REST + WebSocket API
├── frontend/         # Next.js – Web app for pre-production planning & dashboard
├── mobile/           # React Native – Set tracking app (iOS + Android)
├── infra/            # Docker, docker-compose, deployment configs
└── docs/             # Architecture decisions, API specs, onboarding
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python 3.11, FastAPI, Uvicorn |
| AI / NLP | LangChain, OpenAI / local LLM, spaCy |
| Scheduling | Custom constraint-satisfaction + genetic optimizer |
| Database | PostgreSQL 15, SQLAlchemy 2, Alembic |
| Realtime | WebSocket (FastAPI native) |
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Mobile | React Native (Expo) |
| Auth | Supabase Auth / JWT |
| Cache | Redis |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions |

## Quick Start (Local Development)

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- `pnpm` (frontend)

### 1. Clone & configure environment

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

Fill in the required values (see each `.env.example`).

### 2. Start all services with Docker Compose

```bash
docker compose up -d
```

Services:
- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 3. Run backend standalone (development)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### 4. Run frontend standalone (development)

```bash
cd frontend
pnpm install
pnpm dev
```

---

## Key Features

### AI Scheduling Engine (Pre-Production)
- Script parsing (PDF, FDX, Fountain, Celtx) via NLP
- Automatic scene breakdown with location, cast, day/night, interior/exterior detection
- Constraint-satisfaction + genetic scheduling optimizer
- Export: PDF, Excel, Movie Magic, iCal, Google Calendar

### Live Production Monitor (On-Set)
- Real-time scene time-tracking by 1st AD / set runner
- Automatic schedule re-optimization on delay
- Push notifications to full crew
- Production dashboard: planned vs. actual, overtime forecasts, budget risk

---

## Project Roadmap

| Phase | Timeline | Focus |
|---|---|---|
| Foundation | Month 1–6 | Script parsing, core scheduler, web app, PDF export |
| Production-Ready | Month 7–12 | Mobile set app, live tracking, drag-and-drop editor |
| Intelligence | Month 13–18 | Auto script breakdown, AI budget planning, callsheet gen |
| Ecosystem | Month 19–24 | 3rd-party API, location AI, crew management, enterprise SSO |

---

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

## License

Proprietary – All rights reserved. SceneMind AI GmbH.
