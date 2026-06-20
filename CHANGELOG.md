# Changelog

All notable changes to NHL API PyNest are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-06-20

### Added
- **PyNest module architecture**: `AppModule` → `TeamModule` with explicit `useFactory` DI wiring for `TeamService` and `TeamRepository`.
- **`TeamController`**: REST endpoints — `GET /teams/`, `GET /teams/{id}`, `POST /teams/`, `PUT /teams/{id}`, `DELETE /teams/{id}`, `POST /teams/populate`, `POST /teams/truncate`.
- **Conference and division filtering**: `GET /teams/` accepts optional `?conference=` and `?division=` query parameters using case-insensitive `ilike` matching.
- **`TeamService`**: Business logic layer with duplicate-name guard on `add_team` and 404 handling on `get_team` / `modify_team` / `remove_team`.
- **`TeamRepository`**: Synchronous SQLAlchemy session-per-operation pattern with `db.merge()` for safe update and delete of detached instances.
- **`TeamEntity`**: SQLAlchemy ORM model mapped to the `teams` table; `state` and `stadium` columns set to `nullable=True`.
- **SQLite database**: File-based storage via `sqlite:///./national_hockey_league.db`; synchronous `create_engine` with `check_same_thread=False`.
- **Auto-seed on startup**: `main.py` checks whether the `teams` table is empty and populates it from `nhl_teams.json` if so — no manual step required.
- **`nhl_teams.json` fixture**: 30 NHL teams as of the 2016 season, covering all conferences and divisions.
- **FastAPI Swagger UI**: Interactive docs auto-generated at `/docs`; ReDoc at `/redoc`.
- **`python-dotenv` support**: `DATABASE_URL` loaded from `.env` with a sensible default.

### Fixed
- Replaced `sqlite+aiosqlite://` driver (async) with `sqlite:///` (sync) to eliminate `greenlet` errors when running inside Uvicorn's event loop.
- Added `nullable=True` to `state` and `stadium` columns to allow teams without a US state or a known arena name.
- Switched PyNest service registration to `useFactory` pattern to resolve `TeamService` dependency injection correctly.
- Added `db.merge(db_team)` in `update_team` and `delete_team` to prevent `DetachedInstanceError` on objects loaded in a prior session context.
