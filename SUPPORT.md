# Support

## How to Get Help

### Documentation

Start with the project [README.md](./README.md) — it covers installation, configuration, all API routes, the auto-seeding flow, and lessons learned from known bugs.

The auto-generated **Swagger UI** at `http://127.0.0.1:8000/docs` is the fastest way to explore and test every endpoint interactively without writing a single line of client code.

### Bug Reports & Feature Requests

Use GitHub Issues:

- **Bug report** — describe the problem, steps to reproduce, and the expected outcome.
- **Feature request** — explain the use case and why the feature would be valuable.

> Please search existing issues before opening a new one.

### Security Vulnerabilities

**Do not open a public issue for security problems.** See [SECURITY.md](./SECURITY.md) for the responsible disclosure process.

---

## Common Questions

#### The server crashes immediately on startup with a `greenlet` error

Your `DATABASE_URL` is set to an async driver (`sqlite+aiosqlite://`). Change it to the synchronous driver:

```
DATABASE_URL="sqlite:///./national_hockey_league.db"
```

The repository uses a synchronous `sessionmaker` — mixing it with an async driver causes the `greenlet` runtime error.

#### Teams are not appearing after I call `POST /teams/populate`

Confirm that `nhl_teams.json` exists in the **project root** (the same directory as `main.py`). The service looks for the file using a relative path. If you start the server from a different working directory, the file will not be found.

#### I get a `DetachedInstanceError` when updating or deleting a team

This means a `TeamEntity` object was loaded in one SQLAlchemy session and then used after that session closed. Make sure you are calling `db.merge(db_team)` at the start of any `update_team` or `delete_team` repository method to re-attach the instance.

#### `PUT /teams/{team_id}` is not changing the record

Verify that the request body only includes the fields you want to change. The update uses `model_dump(exclude_unset=True)`, so fields that are absent from the body are left unchanged. Sending an empty body `{}` will result in no changes being applied.

#### The Swagger UI is not loading

Ensure the server is running (`python main.py`) and that nothing else is bound to port 8000. Try accessing `http://127.0.0.1:8000/docs` directly in your browser rather than via a proxy.

---

## Contact

See [CONTRIBUTORS.md](./CONTRIBUTORS.md) for maintainer contact information.
