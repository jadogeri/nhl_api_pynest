# Security Policy

## Supported Versions

| Version | Supported |
|---------|:---------:|
| 1.x (current) | ✅ |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

To report a security issue, email the maintainer directly:

> **Security contact**: see the [CONTRIBUTORS.md](./CONTRIBUTORS.md) file for the primary maintainer's contact.

Include the following in your report:

1. **Description** — a clear explanation of the vulnerability.
2. **Steps to reproduce** — a minimal, reproducible example.
3. **Impact** — what data or functionality could be compromised.
4. **Suggested fix** *(optional)* — if you have one.

You will receive an acknowledgement within **48 hours** and a full response within **7 days**.

## Security Measures in This Project

### Input Validation
- All request bodies are validated by **Pydantic models** before reaching service code.
- SQLAlchemy uses **parameterised queries** exclusively — raw string interpolation into SQL is not used anywhere in the codebase, preventing SQL injection.

### Database
- The SQLite database file is stored locally and is not exposed over the network.
- The `DATABASE_URL` is loaded from environment variables — never hardcoded.

### Transport Security
- In production, all traffic should be served over **HTTPS/TLS** via a reverse proxy (e.g. nginx, Caddy).
- The development server (`uvicorn --reload`) is intended for local use only.

### Logging
- The application does not log request bodies or sensitive field values.
- No credentials or tokens are logged at any log level.

## Dependency Auditing

Run the following to check for known vulnerabilities in installed packages:

```bash
pip audit
```

Dependencies are pinned in `requirements.txt` to prevent unintended upgrades. Review and update pins regularly.
