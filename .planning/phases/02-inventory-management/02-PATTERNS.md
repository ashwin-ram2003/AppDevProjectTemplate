# Phase 2: Inventory Management - Pattern Map

**Mapped:** 2026-09-15
**Files analyzed:** 9 (backend: 4 modify; frontend: 5 modify/create)
**Analogs found:** structural-only / 9 — this is a blank-slate scaffold; no working logic exists anywhere in the repo. Every "analog" below is the stub file's own naming/module-wiring convention, not a functional pattern to copy behavior from.

## Important Caveat

This codebase has **no implemented logic to pattern-match against**. All four `server/*.py` files are function signatures with `pass` bodies and docstrings describing the *old* HaaS schema (superseded by `02-CONTEXT.md`'s D-01..D-11). All `client/src/**/*.js` files are 0 bytes. `client/` has no `package.json` — React tooling is not installed. There is no test suite, no auth middleware, no error-handling convention, no validation convention anywhere in the repo to extract.

Given this, "patterns" below are **structural/naming conventions only** (module wiring, docstring-schema style, route registration style) that the planner should have new/rewritten files follow for consistency — not behavior to copy. Where CONTEXT.md's schema decisions (D-01..D-11) conflict with a stub's existing docstring, CONTEXT.md wins; the stub docstring must be rewritten, not extended.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `server/hardwareDatabase.py` (rewrite → e.g. `inventoryDatabase.py` logic) | model/service (DB access module) | CRUD | itself (stub) | structural-only, no logic |
| `server/projectsDatabase.py` (extend, household doc) | model/service (DB access module) | CRUD | itself (stub) | structural-only, no logic |
| `server/app.py` (wire up inventory routes) | route/controller (Flask routes) | request-response | itself (stub) | structural-only, no logic |
| `server/usersDatabase.py` (unchanged, reference only) | model/service | CRUD | itself (stub) | reference — Track A owns this |
| `client/src/components/Checkout.js` | component | request-response | itself (0 bytes) | none — empty file |
| `client/src/components/Project.js` | component | request-response | itself (0 bytes) | none — empty file |
| `client/src/pages/MyUserPortal.js` | component/page | request-response | itself (0 bytes) | none — empty file |
| `client/src/App.js` | component (root) | request-response | itself (0 bytes) | none — empty file |
| `client/package.json` (new) | config | — | none exists | none — must be created from scratch |

## Pattern Assignments

### `server/hardwareDatabase.py` → inventory/item-batch DB module

**Analog:** itself, structural convention only (`server/hardwareDatabase.py:1-37`)

**Module wiring convention** (lines 1-2):
```python
# Import necessary libraries and modules
from pymongo import MongoClient
```
Every DB module imports `MongoClient` directly (no ORM/ODM), takes `client` as first arg of every function (dependency injection of the Mongo connection rather than a module-level global), e.g.:
```python
def createHardwareSet(client, hwSetName, initCapacity):
    pass
```
New inventory functions (e.g. `createBatch`, `reserveItem`, `consumeItem`, `getItemsByLocation`) should follow this same `(client, ...)` first-arg signature convention for consistency with `usersDatabase.py` and `projectsDatabase.py`.

**Docstring-as-schema convention** (lines 4-11): each DB module documents its Mongo document shape as a Python-dict-style comment block above the functions. This must be **rewritten**, not extended, per CONTEXT.md D-01/D-03/D-09-11 — old shape (`{'hwName', 'capacity', 'availability'}`) is flat and superseded. New docstring should reflect the batch-nested shape: item → location → `batches[]` (each batch: `quantity`, `purchaseDate`, `bestByDate`), with `capacity`/`availability` as derived sums, not stored fields.

**No error handling, no validation pattern exists** — `pass` bodies only. Planner/implementer must design these fresh; there is nothing in-repo to copy.

---

### `server/projectsDatabase.py` → household document (item quantity ops)

**Analog:** itself, structural convention only (`server/projectsDatabase.py:1-46`)

**Cross-module import convention** (line 4):
```python
import hardwareDB
```
`projectsDatabase.py` imports the sibling DB module by its Flask-app-facing alias name (`hardwareDB`, not `hardwareDatabase`) — confirms `server/app.py` imports modules under short aliases (see below). New inventory-batch logic co-located in this file (per ROADMAP.md's coordination point — Track B owns item-quantity updates within the household document) should follow the same `def fn(client, projectId, ...)` first-two-args convention seen in `checkOutHW`/`checkInHW` (lines 37-45):
```python
def checkOutHW(client, projectId, hwSetName, qty, userId):
    pass

def checkInHW(client, projectId, hwSetName, qty, userId):
    pass
```
These two are the closest naming precedent for D-04's "reserve" and "consume" actions (analogous to checkout/checkin) and D-08's "release reservation" action — new functions like `reserveItem(client, projectId, itemName, location, qty, userId)`, `consumeItem(client, projectId, itemName, location, qty)`, `releaseReservation(client, projectId, reservationId, userId)` should mirror this signature shape.

**Docstring must be rewritten** (lines 6-15): old `hwSets: {HW1: 0, HW2: 10, ...}` flat map is superseded by CONTEXT.md's nested item→location→batches model; must show reserve metadata (D-05: reserving user id/name attached per reserved quantity, not enforced) and batch array shape.

---

### `server/app.py` → inventory routes

**Analog:** itself, structural convention only (`server/app.py:1-197`)

**Module import/alias convention** (lines 6-9):
```python
import usersDB
import projectsDB
import hardwareDB
```
Note: imported under short aliases distinct from filenames (`usersDatabase.py` → `usersDB`). Any renamed/new inventory module should be imported the same way, e.g. `import hardwareDB` (if `hardwareDatabase.py` is repurposed for inventory) or a new alias if renamed.

**Route registration convention** (lines 115-193, e.g. `get_all_hw_names`, `check_out`, `check_in`, `/api/inventory`):
```python
@app.route('/check_out', methods=['POST'])
def check_out():
    # Extract data from request
    # Connect to MongoDB
    # Attempt to check out the hardware using the projectsDB module
    # Close the MongoDB connection
    # Return a JSON response
    return jsonify({})
```
Every route follows this 5-step comment scaffold (extract → connect → delegate to DB module → close connection → jsonify response), no try/except, no auth decorator, no input validation anywhere. This is the only structural convention in the file — new routes for reserve/consume/restock/get-inventory-by-location should follow the same comment scaffold and `jsonify({})` response shape for consistency, but the actual connect/close/error-handling logic must be authored fresh (none exists to copy). `/api/inventory` (GET, line 184) and `/check_out`/`/check_in` (POST, lines 142-167) are the closest existing route-name precedents for new inventory endpoints (view-by-location, reserve, consume, restock).

---

### Frontend files (`Checkout.js`, `Project.js`, `MyUserPortal.js`, `App.js`, etc.)

**No analog exists.** All are 0-byte files. `client/` has no `package.json`, no React/npm dependency installed, no component ever written in this repo. The planner should treat frontend Phase 2 work as greenfield: file names (`Checkout.js`, `Project.js`) hint at the *intended* original HaaS purpose (checkout/checkin UI, project/resource view) that should be reframed per CONTEXT.md onto food items/locations, but there is zero code, styling, or state-management convention to extract. `client/src/pages/MyLoginPage.js`, `MyRegistrationPage.js`, `ForgotMyPassword.js`, `MyUserPortal.js` are also all empty — Track A's auth UI is equally unimplemented, so no reusable auth-UI pattern exists either.

## Shared Patterns

### DB module function signature (backend only)
**Source:** `server/hardwareDatabase.py`, `server/projectsDatabase.py`, `server/usersDatabase.py` (all stubs, consistent across all three)
**Apply to:** all new/rewritten inventory DB functions
```python
def functionName(client, <ids/params>, ...):
    pass
```
First positional arg is always the Mongo `client`, injected by the caller (route handler) rather than imported as a module-level singleton.

### Flask route scaffold (backend only)
**Source:** `server/app.py:18-193`, every route uniformly
**Apply to:** all new inventory routes
```python
@app.route('/route_name', methods=['POST'])
def route_name():
    # Extract data from request
    # Connect to MongoDB
    # Attempt to <action> using the <module>DB module
    # Close the MongoDB connection
    # Return a JSON response
    return jsonify({})
```
No auth guard, no try/except, no validation library present anywhere — these must be designed from scratch by the phase's plans (not inherited).

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `client/package.json` | config | — | Does not exist; React tooling never installed in `client/` |
| `client/src/components/Checkout.js` | component | request-response | 0 bytes, no analog in repo |
| `client/src/components/Project.js` | component | request-response | 0 bytes, no analog in repo |
| `client/src/pages/MyUserPortal.js` | component/page | request-response | 0 bytes, no analog in repo |
| `client/src/App.js` | component (root) | request-response | 0 bytes, no analog in repo |
| Any error-handling/validation/auth-middleware module | middleware | — | Does not exist anywhere in `server/` |
| Any test file | test | — | No test directory or framework configured in repo |

## Metadata

**Analog search scope:** `server/`, `client/src/` (entire repo — only 14 tracked files total under these paths)
**Files scanned:** 14 (all tracked files in `server/` and `client/`)
**Pattern extraction date:** 2026-09-15
