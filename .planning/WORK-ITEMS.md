# HaaS Resource Manager — Feature Board & Initial Work Items (R1-2)

**Board (visual):** https://claude.ai/code/artifact/f0a9abd4-7299-49bd-87c5-e400d61a4fcc

This is the source-of-truth for the Phase 1 rubric item R1-2 ("All Features on a board. Initial work items — user stories, technical debt, or research items — created for features"). If the team also maintains a GitHub Projects board, import these cards there and keep it as the canonical issue-tracker-adjacent board (kept **separate** from the bug/issue tracker per the assignment's General Requirements).

Each user story is ≤3 sentences per the Mountain Goat Software convention referenced in the assignment.

**Domain note (2026-09-28):** this board previously reframed the assignment's generic hardware-resource domain as a household food-inventory tracker (pantry/fridge/freezer, freshness, purchase batches). That reframing has been reverted; every story below now targets the assignment's own generic HaaS domain — named hardware sets, capacity/availability, request/checkout/checkin.

## Legend

- **User story** — an observable thing a project member can do
- **Technical debt** — engineering work with no direct user-facing story (implementation, infra, security)
- **Research item** — a spike/backlog item beyond this PoC's committed scope, explicitly **not committed**
- **Sub-story** — a separately demonstrable behavior of a parent story, numbered with its parent's ID plus a letter (e.g. `US-07a`)

---

## 1. Account & Authentication — Track A

**Goal:** A user can create a secure account and stay signed in while using the app.

**Rubric ownership:** R1-1 (Project Plan) · R2-2 (live user/project data, no hard-coding)

| ID | Type | Title | Story / Description | Req | Phase |
|----|------|-------|----------------------|-----|-------|
| TD-DOC-A | Technical debt | Define Track A scope, schema, and initial stories | Define the account/project data model (userid/password fields, project document shape with name/description/projectID) and write Track A's initial user stories (US-01..US-05) for the feature board. | ACCT/PROJ | 1 |
| US-R1-A | User story | Document the project plan | As the instructor, I want a documented project plan covering team members, sprint velocity, collaboration tools, and implementation methodology so I can assess how the team is organized and working together. | R1-1 | 1 |
| US-01 | User story | Sign up | As a new user, I want to create an account with a userid and password so I can access my project's hardware resources. | ACCT-02 | 2 |
| US-02 | User story | Sign in | As a returning user, I want to sign in with my credentials so I can resume managing my project's hardware resources. | ACCT-01 | 2 |
| TD-01 | Technical debt | Encrypt credentials | Add password hashing (e.g. bcrypt) in `usersDatabase.py` — currently a stub with no security logic. | ACCT-03 | 2 |
| TD-02 | Technical debt | Persist session | Implement session/token handling so login state survives page navigation — not implemented in the scaffold. | ACCT-04 | 2 |

## 2. Project Management — Track A

**Goal:** A user can create or join the shared project space their hardware resources live in.

**Part of:** Track A — see Rubric ownership in section 1.

| ID | Type | Title | Story / Description | Req | Phase |
|----|------|-------|----------------------|-----|-------|
| US-03 | User story | Create a project | As a user, I want to create a new project with a name, description, and ID so my team shares one set of hardware resources. | PROJ-01 | 2 |
| US-04 | User story | Join a project | As a user, I want to join an existing project using its ID so I see the same hardware resources as my teammates. | PROJ-02 | 2 |
| US-05 | User story | View my projects | As a user, I want to see every project I belong to so I can switch between them if I'm part of more than one. | PROJ-03 | 2 |
| TD-03 | Technical debt | Project hardware-set schema | Agree on and define the project's hardware-set shape (capacity/availability per named set, keyed by project) before Hardware Resource Management work starts writing to it. **Coordination point between Track A and Track B.** | PROJ-01 | 2 |

## 3. Hardware Resource Management — Track B

**Goal:** A project member can see what hardware sets are on hand and move units through request → checkout, or check new units in.

**Rubric ownership:** R1-2 (Feature board) · R2-1 (hardware resources in DB + API)

**Schema note:** Track B's hardware-set shape: each set is keyed by project + name (e.g. "HWSet1"), holding a running `capacity` (total units ever checked in) and `available` (units not currently checked out). No location, no freshness, no per-checkin batch history — a project can define any number of named sets.

| ID | Type | Title | Story / Description | Req | Phase |
|----|------|-------|----------------------|-----|-------|
| TD-DOC-B | Technical debt | Define Track B scope, schema, and initial stories | Define the hardware-set schema — sets keyed by project + name, each holding a capacity and availability count — and write Track B's initial user stories for the feature board. Delivered as `02-CONTEXT.md` plus the four phase plans `02-01` through `02-04`. | RES | 1 |
| US-R1-B | User story | Publish the feature board | As the instructor, I want to see every planned feature captured as user stories, technical debt, or research items on a shared board so I can verify the team has scoped its work before implementation begins. | R1-2 | 1 |
| US-06 | User story | View hardware set status | As a project member, I want to see every named hardware set with its capacity and availability so I know what's on hand at a glance. Availability is what nobody has requested or checked out yet; capacity is the total units the project owns. A project with no hardware sets defined says so plainly rather than showing a blank space. | RES-01 | 2 |
| US-07 | User story | Check in a hardware set | As a project member, I want to add units to a named hardware set's capacity and availability so the system reflects what the project physically has. Checking in a set that doesn't exist yet creates it. | RES-02 | 2 |
| US-08 | User story | Request a hardware set | As a project member, I want to claim units of a hardware set under my name so my teammates know I'm planning to use them. Claiming is a heads-up, not a hold — it never removes the units from the shared availability count and never stops anyone else from checking them out. | RES-03 | 2 |
| US-08a | User story | Release a request I made | As a project member, I want to take back a request I made once I no longer need it, so the hardware set stops showing as spoken for. Only the person who made a request can release it. | RES-03 | 2 |
| US-08b | User story | See who requested what | As a project member, I want to see which teammate has requested a quantity of a hardware set and how much, so I can decide for myself whether to check it out anyway or leave it for them. | RES-03 | 2 |
| US-09 | User story | Check out a hardware set | As a project member, I want to check out units of a hardware set so its available count stays accurate. I can do this at any time without requesting it first. | RES-04 | 2 |
| TD-04 | Technical debt | Overbooking guard | Reject a checkout that would take more units than the hardware set has available, leaving the set completely unchanged when it does — no partial deduction. The guard applies to checkout only; a request is never rejected, because a request was never a real hold on the hardware. | RES-04 | 2 |
| TD-04a | Technical debt | Concurrent checkouts | Make two simultaneous checkouts of the same hardware set unable to drive its availability below zero: apply each checkout with a conditional update pinned to the exact counts that were read, and have the losing writer re-check the guard before retrying. | RES-04 | 2 |
| TD-11 | Technical debt | Bootstrap the React client | Stand up the React application — `package.json`, build tooling, entry HTML, and root component — since `client/` currently has no package manifest and every source file is empty. **Cross-track coordination point: Track B creates this shell first because its resource view needs it; Tracks A, C, and D build into the same shell rather than creating a second one.** | — | 2 |
| TD-12 | Technical debt | Make the Flask app runnable | Fix `server/app.py`'s three module imports, which name modules that do not exist and stop the app from starting at all, and add the `requirements.txt` and virtual environment the repository currently lacks. Replace the placeholder connection-string literal with an environment-variable read — the credential half of this overlaps Track C's TD-07, which owns provisioning. | — | 2 |

## 4. Data Integration & API — Track C

**Goal:** Everything on screen comes from a live database through a real API — nothing is hard-coded.

**Rubric ownership:** R1-4 (Tool choice & approach) · Stretch Feature (US-14) in place of a numbered R2 item

**Rescope note (2026-09-28):** US-13 (password reset) moved to Track D so Track D has standalone feature work spread through the project instead of only infra/testing/deploy. US-14's scope was narrowed to the part not already covered by Track B's base data model — see its row below.

| ID | Type | Title | Story / Description | Req | Phase |
|----|------|-------|----------------------|-----|-------|
| TD-DOC-C | Technical debt | Define Track C scope, schema, and initial stories | Define the REST API surface and deployment/test plan covering DATA-01..03 and OPS-01..02, and write Track C's initial user stories (US-11..US-12) for the feature board. | DATA/OPS | 1 |
| US-R1-C | User story | Document tool choice & approach | As the instructor, I want a written explanation of the team's chosen tech stack and technical approach so I can evaluate whether the decisions fit the project's needs. | R1-4 | 1 |
| US-11 | User story | Always-live data | As a project member, I want everything I see to reflect the real shared database, never sample data, so I can trust the app for real use. | DATA-03 | 2 |
| TD-05 | Technical debt | Wire REST endpoints | Implement the stubbed Flask routes in `app.py` against real DB module logic — routes currently exist but do nothing. | DATA-02 | 2 |
| TD-06 | Technical debt | Remove hard-coded frontend data | Replace placeholder/sample values in React components with live API calls. | DATA-01 | 2 |
| TD-07 | Technical debt | Provision MongoDB Atlas | Stand up a MongoDB Atlas cluster and connection config via environment variables — no secrets committed to the repo. | DATA-01 | 2 |
| US-14 | User story | Manage hardware-set types explicitly | As a project member, I want to create, rename, or deactivate a hardware-set type for my project directly, without needing to check something in first, so hardware-set definitions aren't just a side effect of a checkin. (The base model already supports any number of named sets, created implicitly on first checkin — this story is the explicit-management gap beyond that.) | STRETCH-02 | 2 |

## 5. Deployment & Quality — Track D

**Goal:** The PoC is reachable by the instructor/TAs, its core flows are covered by automated tests written incrementally as each track's routes land, CI runs on every PR from early in the project, and Track D delivers its own promoted stretch feature (password reset) as standalone work.

**Rubric ownership:** R1-3 (High-level sketch) · R2-3 (Cloud deployment) · Stretch Feature (US-13) as additional work

**Rescope note (2026-09-28):** Track D was originally backloaded — thin Day-1 scaffolding, then idle until every other track finished enough to write real tests and deploy. Rescoped: CI/CD setup (TD-16) is genuine early standalone work; the test-harness item (TD-09) is now explicitly incremental/paired rather than one end-of-project batch; and Track D picks up US-13 (moved from Track C) as a real feature it can build mid-project once Track A's login exists.

| ID | Type | Title | Story / Description | Req | Phase |
|----|------|-------|----------------------|-----|-------|
| TD-DOC-D | Technical debt | Define Track D scope, schema, and initial stories | Define the deployment pipeline and test-coverage plan covering OPS-01/OPS-02, and write Track D's initial user stories (US-12) for the feature board. | OPS | 1 |
| US-R1-D | User story | Sketch the application architecture | As the instructor, I want a high-level sketch of the application's architecture and user flow so I can quickly understand the system's design before reviewing the code. | R1-3 | 1 |
| TD-16 | Technical debt | Set up CI/CD early | Stand up a GitHub Actions workflow that runs the backend PyTest suite and the client build on every pull request, done in the first days of the project — not scaffolding for later, but real Day-1 infrastructure every track gets fast PR feedback from immediately. | OPS-02 | 1 |
| US-12 | User story | Reachable, gradeable app | As an instructor or TA, I want to open a public URL and walk through the full account → project → request/checkout/checkin flow so I can grade the working PoC. | OPS-01 | 2 |
| TD-08 | Technical debt | Deployment pipeline | Set up cloud hosting and deploy config so the app is reachable via a stable public URL. | OPS-01 | 2 |
| TD-09 | Technical debt | Incremental backend test coverage | Write PyTest coverage for each backend route as its owning track ships it — pairing with Track A on login/project routes, Track B on request/checkout/checkin, Track C on the REST surface — rather than one batched pass after every route already exists. CI (TD-16) runs the growing suite on every PR throughout. | OPS-02 | 2 |
| TD-10 | Technical debt | Keep generic domain naming | The scaffold's original "project"/"hardware set" language is the domain itself now — as implementation lands, keep code and UI naming aligned to it (reverted from an earlier food-domain renaming pass). | — | 2 |
| US-13 | User story | Reset a forgotten password | As a user who forgot their password, I want to reset it via the existing Forgot Password flow so I can regain access to my project's hardware resources without contacting an admin. | STRETCH-01 | 2 |

## 6. UI Design — Track E

**Goal:** The app looks and works like one coherent product, not four developers' separately-styled screens — and each functional track gets a documented, prop-based contract to wire its real data into instead of touching presentation internals.

**Owner:** Aaron Phan, dual duty alongside Track B (Hardware Resource Management). Not a PDF rubric-owning track — no `Req` line maps to a stakeholder need or system requirement; this is additive quality work.

**Scope note:** Design stories start with Track B's UI, since it's the only track with a real screen to critique. As Track A and Track C build their own UI (login/project pages; stretch-feature UI), Track E's harness items (TD-13/TD-14/TD-15 below) are what those tracks wire into — add further Track E design stories once that UI exists, rather than designing speculatively against code that isn't written yet.

| ID | Type | Title | Story / Description | Req | Phase |
|----|------|-------|----------------------|-----|-------|
| US-15 | User story | Clean, scannable resource layout | As a project member, I want the hardware-resource view laid out with clear visual grouping and spacing instead of bare HTML tables, so I can scan what's on hand without hunting through rows. | DESIGN | 2 |
| US-16 | User story | Status cues readable at a glance | As a project member, I want availability/status indicators to use consistent color coding I can recognize instantly, not just read, so I know a set's state without stopping to read every label. | DESIGN | 2 |
| US-17 | User story | Usable resource view on a phone | As a project member checking hardware status from my phone, I want the resource view and its checkin/request/checkout controls to work on a small screen, so I don't need a laptop to use the app day-to-day. | DESIGN | 2 |
| TD-13 | Technical debt | Document the session-identity harness for Track A | Define and document the exact prop contract (`projectId`, `userId`, `userName`) the top-level resource-view component and its children expect — currently hardcoded as constants in `client/src/App.js` — so Track A can wire in real login/session data (ACCT-04) by replacing three values at one call site instead of tracing through component internals. | DESIGN | 2 |
| TD-14 | Technical debt | Document the live-data contract for Track C's audit | Confirm and document that every presentational component receives all displayed data via props only, with no internal fetch or hard-coded fallback, so Track C can audit DATA-01/DATA-03 (no hard-coded data) against a documented contract instead of re-reading component internals. | DESIGN | 2 |
| TD-15 | Technical debt | Shared design tokens for cross-track UI consistency | Extract a small shared set of style tokens (spacing scale, color palette, typography) from Track B's `client/src/App.css` into a reusable base other tracks' UI can adopt, so Track A's login/project pages and Track C's stretch-feature UI (password reset, arbitrary hardware sets) look like one app instead of three. | DESIGN | 2 |

## Future Vision — Research Backlog (not scheduled, v2)

Beyond this PoC's committed scope — each needs sensors, ML modeling, or third-party integrations no semester project can fund. Kept visible so the team can spike opportunistically without risking rubric-critical time.

| ID | Type | Title | Description | Req |
|----|------|-------|--------------|-----|
| R-01 | Research | RFID / barcode auto-capture | Spike whether RFID tags or barcode scans can auto-detect hardware entering or leaving storage. | CAP-01 |
| R-02 | Research | Sensor-based checkout/checkin detection | Spike automatic detection of checkout/checkin events without manual logging. | CAP-02 |
| R-03 | Research | Usage analytics | Research surfacing which hardware sets are checked out most, and forecasting low-availability windows. | INT-01 |
| R-04 | Research | Per-user behavior learning | Research learning individual usage patterns to improve availability forecasting. | INT-02 |
| R-05 | Research | Low-availability alerts & reorder suggestions | Research alerting and automated procurement suggestions when a hardware set runs low. | PLAN-01 |
| R-06 | Research | Overdue-checkout reminders | Research checkout-duration reminders and overdue-return notifications. | PLAN-02 |

---

**Totals:** 6 committed features · 18 user stories (3 with sub-stories) · 21 technical debt items (16 Phase 2 + 5 Phase 1 scope/schema/stories/CI items) · 6 research items · 19/19 v1 requirements covered (Track E's items are additive quality work, not mapped to a stakeholder requirement).

**4 tracks, 4 developers:** Track A, Track B, Track C, and Track D each own exactly one Phase 1 rubric item (US-R1-A/B/C/D → R1-1/R1-2/R1-4/R1-3 respectively) plus either one Phase 2 rubric item or, for Track C, a promoted stretch-feature scope (US-14) in place of a numbered R2 item. Track D additionally carries a second stretch feature (US-13, moved from Track C 2026-09-28) alongside its own R2-3, plus early CI/CD ownership (TD-16) and incremental (not batched) test-writing (TD-09) — a workload rebalance so its developer has substantive, continuous work across the whole project instead of being idle until every other track finishes.

**Plus Track E (UI Design), dual duty:** Aaron Phan owns Track E alongside Track B. Track E isn't a rubric-owning track — it's cross-cutting design/polish work, starting with Track B's UI (the only screen that exists) and leaving documented component contracts (TD-13/TD-14/TD-15) for Track A and Track C to wire their real data into once their own UI lands.

**Out of scope reminder:** The Project Plan (team members, sprint cadence, collaboration tools, methodology, toolchain — R1-1) is now represented on this board via US-R1-A, owned by Track A.

---
*Board created: 2026-09-14*
*Last updated: 2026-09-28 — reverted food-inventory domain stories back to the assignment's generic hardware-resource domain, then rescoped Track D (added CI/CD as Day-1 work, made test-writing incremental, moved the password-reset stretch feature from Track C) so its developer isn't idle for most of the project*
