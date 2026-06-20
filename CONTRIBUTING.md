# Contributing to NHL API PyNest

Thank you for your interest in contributing! The following guidelines help keep the codebase consistent and the review process smooth.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branching Strategy](#branching-strategy)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Code Standards](#code-standards)
- [Reporting Bugs](#reporting-bugs)

---

## Code of Conduct

This project follows our [Code of Conduct](./CODE_OF_CONDUCT.md). By participating you agree to uphold its standards.

---

## Getting Started

1. **Fork** the repository and clone your fork locally.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template and fill in your own values:
   ```bash
   cp .env.sample .env
   ```
5. Start the development server:
   ```bash
   python main.py
   ```

---

## Development Workflow

| Command | Purpose |
|---------|---------|
| `python main.py` | Start the API server (creates tables + auto-seeds on first run) |
| `uvicorn "main:http_server" --reload` | Start with hot-reload enabled |
| `curl http://127.0.0.1:8000/docs` | Open the Swagger UI in a browser |

---

## Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready, protected |
| `feature/<name>` | New features |
| `fix/<name>` | Bug fixes |
| `chore/<name>` | Tooling, deps, docs |

Branch off `main`, keep branches short-lived.

---

## Commit Messages

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <short description>

[optional body]
[optional footer]
```

**Types**: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`

**Examples**:
```
feat(teams): add conference and division filter to list endpoint
fix(repository): add db.merge to prevent DetachedInstanceError on update
chore(deps): pin pynest-api to 0.3.x in requirements.txt
```

---

## Pull Request Process

1. Ensure your branch is up to date with `main`.
2. Run a quick sanity check — start the server and hit `/docs` to confirm the app still boots.
3. Fill in the pull request template completely.
4. Request a review from at least one maintainer.
5. Squash commits before merging if the PR history is noisy.

---

## Code Standards

- **Type hints everywhere** — annotate all function parameters and return types.
- **Pydantic models for I/O** — never pass raw `dict` objects as request or response bodies.
- **Repository pattern** — all database access goes through `TeamRepository`; service code must not import SQLAlchemy sessions directly.
- **Session-per-operation** — open a `with self.session_factory() as db:` block for each repository method; do not hold sessions open across calls.
- **No bare `except`** — catch specific exceptions and re-raise as `HTTPException` with a meaningful status code and detail message.
- **No secrets in code** — use environment variables loaded from `.env` only.

---

## Reporting Bugs

Please open a GitHub Issue using the bug report template. Include:

- Python version (`python --version`)
- Steps to reproduce
- Expected vs actual behaviour
- Relevant log output (sanitised — no passwords or tokens)

For security vulnerabilities, see [SECURITY.md](./SECURITY.md).
