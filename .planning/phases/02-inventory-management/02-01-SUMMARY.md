---
phase: 02-inventory-management
plan: 01
subsystem: api
tags: [flask, pymongo, mongomock, vite, react, inventory]

# Dependency graph
requires: []
provides:
  - "Items collection document shape (householdId, location, itemKey, itemName, batches[], reservations, capacity, reservedQuantity, availability-derived)"
  - "GET /api/inventory and POST /api/inventory/restock REST contract"
  - "assertHouseholdMember trust-boundary guard in projectsDatabase.py"
  - "itemIdentity.normalizeItemName (D-03 normalization half)"
  - "Working Python (.venv) and Node (Vite) toolchains, .gitignore"
  - "React app shell (index.js, App.js, index.css, App.css) and InventoryView/RestockForm components"
affects: [02-02-freshness, 02-03-item-identity-matching, 02-04-reserve-consume, track-a-auth, track-c-deploy, track-d-testing]

# Actuals (#2632)
actuals:
  tokens: 23981
  tasks: 4
  commits: 3

# Tech tracking
tech-stack:
  added: [flask==3.0.3, pymongo==4.8.0, pytest==8.3.2, mongomock==4.1.2, python-dotenv==1.0.1, react@18, react-dom@18, vite@5, "@vitejs/plugin-react@4"]
  patterns:
    - "DB modules take (client, ...) as first arg (dependency-injected Mongo connection)"
    - "Flask routes follow extract -> connect -> delegate -> close -> respond scaffold, with a try/finally around client.close()"
    - "Exceptions (InvalidInventoryInput/NotAHouseholdMemberError/ItemNotFoundError) map to HTTP status in app.py, never leak past the route"
    - "React source files stay .js (not .jsx); vite.config.js explicitly overrides esbuild's default exclude to still JSX-transform them"

key-files:
  created:
    - server/itemIdentity.py
    - server/requirements.txt
    - server/tests/conftest.py
    - server/tests/test_inventory_tracer.py
    - client/package.json
    - client/vite.config.js
    - client/index.html
    - client/src/api/inventory.js
    - client/src/components/RestockForm.js
    - .gitignore
  modified:
    - server/hardwareDatabase.py
    - server/projectsDatabase.py
    - server/app.py
    - server/usersDatabase.py
    - client/src/index.js
    - client/src/index.css
    - client/src/App.js
    - client/src/App.css
    - client/src/components/Project.js

key-decisions:
  - "Package legitimacy (Task 1 checkpoint): all 9 packages (flask, pymongo, pytest, mongomock, python-dotenv, react, react-dom, vite, @vitejs/plugin-react) approved by the coordinator; Vite confirmed as the client build tool over create-react-app."
  - "Storage shape (Task 2 checkpoint): household inventory lives in a separate `Items` collection keyed by householdId+location+itemKey, NOT embedded in the household document. Chosen to remove Track A/Track B write contention and make the overbooking guard a single conditional update. ROADMAP.md's 'inventory lives in the household document' wording is now stale and should be corrected by the orchestrator."
  - "itemName (display spelling) is set only on insert ($setOnInsert) so the first-seen spelling of an itemKey persists across later restocks with different casing/whitespace, per D-03."

patterns-established:
  - "Item/batch document shape and /api/inventory REST contract are now load-bearing for plans 02-02, 02-03, 02-04 and Tracks A/C/D — do not redefine, only extend."
  - "Vite JSX-in-.js gotcha: Vite's built-in esbuild plugin defaults `exclude` to /\\.js$/ regardless of `include`; any future .js-based Vite config in this repo must carry the same `esbuild: { loader: 'jsx', include, exclude: [] }` override."

requirements-completed: [INV-01, INV-02]

coverage:
  - id: D1
    description: "A household member can restock a food item with quantity/purchase date/best-by date and it appears in the inventory view without restarting anything (INV-02, D-01)"
    requirement: "INV-02"
    verification:
      - kind: unit
        ref: "server/tests/test_inventory_tracer.py#test_restock_then_read_shows_item_under_pantry"
        status: pass
      - kind: integration
        ref: "live Flask dev server over real HTTP (manual smoke test, not committed as a test file): POST /api/inventory/restock then GET /api/inventory"
        status: pass
    human_judgment: false
  - id: D2
    description: "Inventory view groups items under Pantry/Fridge/Freezer and shows capacity and availability (INV-01)"
    requirement: "INV-01"
    verification:
      - kind: unit
        ref: "server/tests/test_inventory_tracer.py#test_restock_then_read_shows_item_under_pantry"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every number on the inventory screen comes from the live API response; no item/quantity/location literal is written into React source (R2-1)"
    verification:
      - kind: other
        ref: "grep -c \"itemName: '\" client/src/components/Project.js (count 0) + grep -c fetchInventory (count 2)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Each restock appends a new batch rather than overwriting; capacity is the sum of batch quantities (D-01)"
    requirement: "INV-02"
    verification:
      - kind: unit
        ref: "server/tests/test_inventory_tracer.py#test_second_restock_of_normalized_name_merges_into_one_item_with_two_batches"
        status: pass
    human_judgment: false
  - id: D5
    description: "A request for inventory belonging to a household the caller is not a member of is rejected with 403 and no inventory data"
    verification:
      - kind: unit
        ref: "server/tests/test_inventory_tracer.py#test_non_member_get_is_rejected_with_403_and_no_inventory"
        status: pass
    human_judgment: false
  - id: D6
    description: "A household with no items returns all three location groups present and empty; UI renders an explicit empty-state message per empty location"
    requirement: "INV-01"
    verification:
      - kind: unit
        ref: "server/tests/test_inventory_tracer.py#test_empty_household_returns_all_three_location_keys_empty"
        status: pass
    human_judgment: true
    rationale: "Backend empty-groups behavior is unit-tested and passes. The React empty-state message ('Nothing stored here yet.') was code-reviewed but not confirmed rendering in a running browser -- Task 4's <human-check> browser click-through was deferred to end-of-phase per HUMAN_VERIFY_MODE=end-of-phase (logged in .planning/WINDOWS.md as an unrun-verify entry)."
  - id: D7
    description: "Items within a location are returned in deterministic, repeatable order (soonest bestByDate first, itemKey ascending tie-break)"
    verification:
      - kind: unit
        ref: "server/tests/test_inventory_tracer.py#test_two_consecutive_gets_of_unchanged_data_return_identical_ordering"
        status: pass
    human_judgment: false
  - id: D8
    description: "Same normalized item name merges within a location; the same name in a different location stays a separate item (D-03 adjacency half)"
    verification:
      - kind: unit
        ref: "server/tests/test_inventory_tracer.py#test_same_name_different_location_is_a_separate_item"
        status: pass
    human_judgment: false
  - id: D9
    description: "Restock with quantity < 1, blank item name, unknown location, or missing purchase date is rejected with 400 and writes no batch"
    requirement: "INV-02"
    verification:
      - kind: unit
        ref: "server/tests/test_inventory_tracer.py#test_restock_with_quantity_zero_is_rejected_and_writes_nothing (+3 sibling tests for negative quantity, blank name, unknown location, missing purchase date)"
        status: pass
    human_judgment: false
  - id: D10
    description: "Batches within an item are ordered bestByDate ascending (Pantry/Fridge) / purchaseDate ascending (Freezer), createdAt tie-break"
    requirement: "INV-02"
    verification:
      - kind: unit
        ref: "server/tests/test_inventory_tracer.py#test_batches_within_pantry_item_ordered_by_best_by_date_ascending, #test_batches_within_freezer_item_ordered_by_purchase_date_ascending"
        status: pass
    human_judgment: false
  - id: D11
    description: "No literal MongoDB connection string remains in tracked source; MONGODB_URI is read from the environment and raises when unset"
    verification:
      - kind: other
        ref: "grep -c MONGODB_URI server/app.py (5) + grep -c your_mongodb_connection_string_here server/app.py (0)"
        status: pass
    human_judgment: false
  - id: D12
    description: "A person can restock an item in the browser and watch it appear in the inventory view with correct capacity/availability, nothing hard-coded"
    verification: []
    human_judgment: true
    rationale: "Requires an actual browser session against the running dev server (npm run dev + server/.venv/bin/python server/app.py). The production build succeeds and a live HTTP smoke test against the real Flask server confirmed the exact request/response cycle the UI depends on, but the browser click-through itself was not run interactively -- deferred to end-of-phase per HUMAN_VERIFY_MODE=end-of-phase."

duration: ~20min (active work across two sessions, separated by two blocking-human checkpoints)
completed: 2026-09-16
status: complete
---

# Phase 2 Plan 1: Inventory Tracer Summary

**End-to-end restock-and-read tracer: Flask + pymongo + mongomock backend with a separate `Items` collection, and a Vite/React client rendering live inventory — the item/batch document shape and REST contract the rest of the phase builds on.**

## Performance

- **Duration:** ~20 min of active tool-call work (session paused at two blocking-human checkpoints between Task 2 and Task 3; wall-clock spans two sessions)
- **Tasks:** 4/4 complete (2 checkpoints resolved by coordinator, 2 build tasks executed)
- **Files modified/created:** 22 (excluding generated `client/package-lock.json`)

## Accomplishments
- Fixed the repo's broken module aliasing (`server/app.py`'s bare `import usersDB`/`projectsDB`/`hardwareDB` never resolved) so the Flask app can start at all
- Rewrote `server/hardwareDatabase.py` around a separate `Items` collection: `addBatch` (validated, always-append batches) and `getItemsByLocation` (grouped, sorted, JSON-serializable)
- Extended `server/projectsDatabase.py` with the Track B section: `assertHouseholdMember`, `restockItem`, `getHouseholdInventory`, leaving Track A's `queryProject`/`createProject`/`addUser`/`updateUsage` untouched
- Wired `GET /api/inventory` and `POST /api/inventory/restock` in `server/app.py`, with `getMongoClient()` reading `MONGODB_URI` from the environment (no default connection string)
- 13 passing pytest tests covering the tracer path plus every boundary in the plan's must_haves: batch merging, location separation, empty household, 403 membership guard, 400 input validation x4, deterministic item ordering, and batch-level date ordering for both Pantry and Freezer
- Bootstrapped the client's first-ever `package.json`/Vite toolchain; built `InventoryView` (`client/src/components/Project.js`) and `RestockForm` rendering live API data only, with an explicit per-location empty state
- Production build (`npm run build`) succeeds and emits `client/dist/index.html`
- Live smoke test: ran the real Flask dev server (not just the test client) over actual HTTP and confirmed GET/POST/403 behavior end-to-end

## Task Commits

Each task was committed atomically:

1. **Task 1: Verify package legitimacy before any install** - checkpoint, resolved by coordinator (approved all 9 packages + Vite choice), no commit
2. **Task 2: Choose where household inventory is stored** - checkpoint, resolved by coordinator (separate `Items` collection), no commit
3. **Task 3: End-to-end restock and read — Flask, pymongo, one path** - `859a194` (feat)
4. **Task 4: The same path in the browser — React shell and live inventory view** - `6baabb3` (feat)
5. **Follow-up: explicit batch-ordering test coverage** - `fc0fa75` (test)

## Files Created/Modified
- `server/itemIdentity.py` - `normalizeItemName` (D-03 normalization half)
- `server/hardwareDatabase.py` - rewritten: Items collection, `addBatch`, `getItemsByLocation`, sort/derive logic
- `server/projectsDatabase.py` - extended: `assertHouseholdMember`, `restockItem`, `getHouseholdInventory`
- `server/app.py` - fixed imports, `getMongoClient()`, `/api/inventory` + `/api/inventory/restock` routes, deleted 3 superseded stub routes
- `server/usersDatabase.py` - one-line blocking-bug fix (`import projectsDB` -> `import projectsDatabase as projectsDB`)
- `server/requirements.txt`, `server/.venv/` - Python toolchain
- `server/tests/conftest.py`, `server/tests/test_inventory_tracer.py` - 13 passing tests
- `.gitignore` - repository's first ignore file
- `client/package.json`, `client/vite.config.js`, `client/index.html` - Vite + React toolchain
- `client/src/index.js`, `client/src/App.js`, `client/src/index.css`, `client/src/App.css` - app shell
- `client/src/api/inventory.js` - `fetchInventory`, `restockItem`
- `client/src/components/Project.js` - `InventoryView`
- `client/src/components/RestockForm.js` - `RestockForm`
- Deleted: `client/public/index.html` (tracked 0-byte file superseded by `client/index.html`)

## Decisions Made
- **Storage shape:** separate `Items` collection, not embedded in the household document (coordinator decision on Task 2's checkpoint). ROADMAP.md's original "inventory lives in the household document" wording is now stale.
- **Package legitimacy:** all 9 proposed packages approved as-is (coordinator decision on Task 1's checkpoint); Vite confirmed over create-react-app.
- **Display name provenance:** `itemName` is set only via `$setOnInsert`, so the first-seen spelling of a normalized itemKey is what's displayed on every later restock, per D-03.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed broken import in Track A's `usersDatabase.py`**
- **Found during:** Task 3, first pytest run (`ModuleNotFoundError: No module named 'projectsDB'`)
- **Issue:** `usersDatabase.py` (not in this plan's files_modified list, owned by Track A) had a bare `import projectsDB` that cannot resolve — no such module exists, only `projectsDatabase.py`. This transitively blocked `server/app.py` from importing at all, since `app.py` imports `usersDatabase`.
- **Fix:** Changed the import to `import projectsDatabase as projectsDB`, the same aliasing convention already used elsewhere in the codebase.
- **Files modified:** `server/usersDatabase.py` (one line)
- **Verification:** `server/tests/test_inventory_tracer.py` collects and runs.
- **Committed in:** `859a194` (Task 3 commit)

**2. [Rule 3 - Blocking] Fixed Vite's silent JSX-in-.js exclusion**
- **Found during:** Task 4, `npm run build` (`Failed to parse source for import analysis... If you are using JSX, make sure to name the file with the .jsx or .tsx extension`)
- **Issue:** The plan's files_modified list keeps React source at `.js` (not `.jsx`). Vite's built-in esbuild transform plugin defaults its `exclude` option to `/\.js$/` whenever it isn't explicitly set, which silently overrides any custom `include` regex and skips JSX stripping for every `.js` file during the production build (dev server's HMR path happens to route through `@vitejs/plugin-react`'s Babel transform instead, so this gotcha is build-only).
- **Fix:** Added `esbuild: { loader: 'jsx', include: /src\/.*\.js$/, exclude: [] }` to `client/vite.config.js`, explicitly overriding the default exclude.
- **Files modified:** `client/vite.config.js`
- **Verification:** `npm run build` succeeds and emits `client/dist/index.html`.
- **Committed in:** `6baabb3` (Task 4 commit)

**3. [Rule 2 - Missing coverage] Added explicit batch-ordering tests**
- **Found during:** post-Task-4 self-review against the plan's `must_haves.truths`
- **Issue:** The must_haves truth "batches ordered bestByDate ascending for Pantry/Fridge, purchaseDate ascending for Freezer, createdAt tie-break" was implemented (`_batchSortKey` in `hardwareDatabase.py`) but not directly asserted by any test with mixed out-of-order dates — the existing two-batch test only checked aggregate capacity, not per-batch order.
- **Fix:** Added `test_batches_within_pantry_item_ordered_by_best_by_date_ascending` and `test_batches_within_freezer_item_ordered_by_purchase_date_ascending`, each restocking three batches out of chronological order and asserting the GET response returns them sorted.
- **Files modified:** `server/tests/test_inventory_tracer.py`
- **Verification:** all 13 tests pass.
- **Committed in:** `fc0fa75`

---

**Total deviations:** 3 auto-fixed (2 blocking, 1 missing test coverage)
**Impact on plan:** All three were necessary for correctness/completeness; none changed the plan's document shape, REST contract, or scope.

## Issues Encountered
- Task 4's `<verify>` block includes a `<human-check>` requiring a running backend + frontend and manual browser interaction. Per `HUMAN_VERIFY_MODE=end-of-phase` (the project's configured default) and `AUTO_CHAIN=false`/`AUTO_CFG=false`, this was not run interactively during this plan's execution. As a substitute, a live smoke test ran the actual Flask dev server (not the Flask test client) over real HTTP and confirmed GET empty inventory (200), POST restock (201), GET after restock (200, correct item/capacity), and GET by a non-member (403) all behave as the plan specifies. Both the deferred human-check and a documentation of this substitute evidence are logged in `.planning/WINDOWS.md`.

## Known Stubs
- `client/src/App.js` hardcodes `HOUSEHOLD_ID = 'H1'` and `USER_ID = 'alice'` rather than sourcing them from a login/session flow, because Track A's auth/session layer (ACCT-04) has not landed yet. This is not inventory data (no item names/quantities/totals are hardcoded — the prohibition this plan enforces), it is session identity input that Track A is explicitly responsible for wiring in later, per this plan's own cross-track coordination notice and the T-02-01 threat-register mitigation note. Logged in `.planning/WINDOWS.md` as a stub entry for visibility.

## Threat Flags

None beyond what the plan's own `<threat_model>` already covers (T-02-01, T-02-04, T-02-05, T-02-SC) — no new network endpoints, auth paths, or trust-boundary-crossing surface was introduced beyond what the plan specified.

## User Setup Required

None for local development — `server/.venv` and `client/node_modules` are both installed and gitignored. **Before running the server**, a `server/.env` file (or exported shell variable) must set `MONGODB_URI` — there is no default connection string, and `getMongoClient()` raises `RuntimeError` with instructions if it is unset. Track C's Atlas provisioning (TD-07) will supply the real connection string; `mongomock` is used for all tests so no live database is required to develop or test this phase.

## Next Phase Readiness
- The item/batch document shape and the `/api/inventory` + `/api/inventory/restock` REST contract are settled and load-bearing for plans 02-02 (freshness), 02-03 (substring/prefix item matching), and 02-04 (reserve/consume) — none of them should redefine these, only extend.
- `itemIdentity.py` is ready for plan 02-03 to extend with substring/prefix matching alongside the normalization already here.
- The deferred browser click-through (`<human-check>` in Task 4) and the hardcoded `HOUSEHOLD_ID`/`USER_ID` in `App.js` are both logged in `.planning/WINDOWS.md` for end-of-phase/ship-gate visibility.
- Blocker for Track A: ROADMAP.md's "inventory lives in the household document" wording is now stale per the Task 2 storage-shape decision and should be corrected during this phase's STATE.md/ROADMAP.md update pass (owned by the orchestrator, not this plan).

---
*Phase: 02-inventory-management*
*Completed: 2026-09-16*

## Self-Check: PASSED

All 20 claimed files verified present on disk (including `.planning/WINDOWS.md`), `client/public/index.html` confirmed deleted, and all 3 claimed commit hashes (`859a194`, `6baabb3`, `fc0fa75`) confirmed present in git log.
