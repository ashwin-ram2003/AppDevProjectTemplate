# Testing (TD-09)

Two suites, both run by CI on every pull request (`.github/workflows/ci.yml`).

| Suite | Where | Run it | What it uses |
|-------|-------|--------|--------------|
| Backend | `server/tests/` | `cd server && pytest --cov` | PyTest + mongomock (no real database needed) |
| Client | `client/src/__tests__/` | `cd client && npm test` | Vitest + Testing Library |

Backend coverage is 95% (lines + branches). `pytest --cov` fails below the floor in `server/.coveragerc` (85%), and so does CI.

First-time setup for the backend: `pip install -r requirements.txt -r requirements-dev.txt`.

## Backend files

| File | Owner | What it proves |
|------|-------|----------------|
| `test_api_contract.py` | Track D | Every hardware route has the same front door: missing or empty `projectId`/`userId` is a 400, a non-member or unknown project is a 403, malformed JSON is a 400 (not a crash), and no `MONGODB_URI` is a JSON 503. Every rejection is also checked to have written nothing. |
| `test_request_ownership.py` | Track D | Only the person who made a request can release it. A teammate gets `not_your_reservation`, an outsider gets `not_a_project_member`, and a double release can't go negative. |
| `test_client_serving.py` | Track D | The deployed app (TD-08): `/healthz` works without a database, the built client is served, page routes fall back to `index.html`, and unknown `/api/...` paths stay JSON 404s. |
| `test_route_smoke.py` | Track D | Sends every registered route an empty request; nothing may answer 5xx. New routes are picked up automatically. |
| `test_adversarial_hardware.py` | Track B | Race conditions, bad quantities and names, project isolation, sorting, overflow. |
| `test_checkout.py`, `test_request.py`, `test_hardware_tracer.py`, `test_type_validation.py` | Track B | Hardware-set features and injection guards. |
| `test_auth_routes.py`, `test_users_database.py`, `test_password_security.py` | Track A | Sign-up, sign-in, bcrypt hashing (SR3). |

## Adding a route

1. Add it to `ROUTES` in `test_api_contract.py`. That alone gives it the missing-field, non-member, malformed-JSON and no-database checks.
2. Write its feature tests in a file named for what the route lets a user do.
3. For anything that writes, assert on what's actually stored, not just the status code.
