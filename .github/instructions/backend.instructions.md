---
description: Backend-only guidance for Flask API, services, storage, and Python workflows in this repository.
applyTo: "backend/**"
---

# Backend Guidelines

## Build And Test
- Run backend tests: `cd backend && uv run pytest`

## Architecture
- Backend is a Flask app with an application factory in `backend/app/__init__.py` and startup entry in `backend/run.py`.
- API routes live under `backend/app/api` and are split by domain: graph, simulation, report.
- Business logic lives in `backend/app/services`.
- Storage abstractions and implementations live in `backend/app/storage`.
- Data models live in `backend/app/models` and use dataclasses with explicit serialization helpers.

## Conventions
- Keep route handlers thin. Put non-trivial logic in service classes.
- Access graph storage through Flask app extensions (`current_app.extensions['neo4j_storage']`) instead of global singletons.
- Preserve API response shape used across routes: `{"success": bool, "data": ..., "error": ...}`.
- Prefer existing retry helpers in `backend/app/utils/retry.py` for transient external failures.
- Use module loggers from `backend/app/utils/logger.py` (`get_logger(__name__)`) instead of ad-hoc logging.

## Environment And Pitfalls
- `.env` is expected at the repository root, not inside `backend`.
- For local runs, service URLs typically use `localhost`; inside Docker Compose, use container service names.
- Ollama models must be available before simulation/report workflows are run.
- Python compatibility is currently constrained by CAMEL dependencies (target Python 3.11 in this repo).

## Key Reference Files
- Commands: `backend/pyproject.toml`
- App setup: `backend/run.py`, `backend/app/__init__.py`, `backend/app/config.py`
- API patterns: `backend/app/api/graph.py`
- Service patterns: `backend/app/services/oasis_profile_generator.py`
- Storage patterns: `backend/app/storage/neo4j_storage.py`