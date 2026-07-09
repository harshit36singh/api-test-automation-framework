# API Testing Automation Framework

A Python + FastAPI based framework for automating REST API validation and improving backend reliability. It pairs a small sample FastAPI service (auth + CRUD) with a reusable pytest automation layer, so the testing patterns here can be lifted into any FastAPI/REST project.

## What's included

- **Sample service** (`app/`) — JWT-based auth (register/login) and a CRUD `items` resource, with structured error responses (`error_code` + `message`) via centralized exception handlers.
- **Reusable API client** (`tests/utils/api_client.py`) — wraps raw HTTP calls behind intent-revealing methods (`register_and_login`, `create_item`, etc.) so tests read like workflows, not request plumbing.
- **Shared fixtures** (`tests/conftest.py`) — isolated in-memory DB reset per test, a pre-registered user, and an authenticated client.
- **Shared assertions** (`tests/utils/assertions.py`) — consistent checks for error-response shape and resource schemas.
- **Test suites**:
  - `tests/test_auth.py` — registration, login, token validation (positive + negative)
  - `tests/test_items_crud.py` — full CRUD lifecycle, ownership checks, validation errors (positive + negative)
- **CI** (`.github/workflows/tests.yml`) — runs the suite on every push/PR via GitHub Actions.

## Setup

```bash
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn app.main:app --reload
```

## Running the tests

```bash
pytest -v
```

Run only positive or negative scenarios:

```bash
pytest -m positive
pytest -m negative
```

## Design notes

- Errors are returned as `{"error_code": "...", "message": "..."}` for every failure path (validation, auth, not-found, forbidden), so tests can assert on error codes rather than parsing prose.
- The data layer (`app/database.py`) is an in-memory store behind a small interface, keeping tests fast and hermetic — no external DB required to run the suite.
- The `APIClient` wrapper centralizes auth-header handling and multi-step workflows (e.g. register-then-login) so adding new test cases doesn't mean re-deriving request boilerplate.
