# Contributing to SceneMind AI

## Development setup

1. Fork the repository and clone it locally.
2. Create a feature branch: `git checkout -b feat/your-feature-name`
3. Follow the quick-start guide in the [README](../README.md).

## Commit convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add drag-and-drop schedule editor
fix: correct day-of-week skipping in optimizer
chore: bump FastAPI to 0.112
docs: update API reference with export endpoints
test: add optimizer edge cases for blocked dates
```

## Branch strategy

| Branch | Purpose |
|---|---|
| `main` | Production-ready, protected |
| `dev` | Integration branch |
| `feat/*` | New features |
| `fix/*` | Bug fixes |
| `chore/*` | Maintenance |

## Pull requests

- Target `dev` (not `main`) for all PRs.
- Include a short description of the change.
- Add or update tests for new functionality.
- Ensure `ruff` and `tsc --noEmit` pass before opening a PR.

## Code style

**Backend:** `ruff` for linting, `black` for formatting.

```bash
cd backend
ruff check .
black .
```

**Frontend:** ESLint + TypeScript strict mode.

```bash
cd frontend
pnpm lint
pnpm type-check
```
