# Roadmap: HaaS Resource Manager PoC (Group 2 Monday)

## Overview

This roadmap delivers the assignment's generic Hardware-as-a-Service (HaaS) PoC by completing the
existing Flask/MongoDB/React scaffold (routes and DB modules are stubbed but not implemented;
client pages/components are still named generically after the assignment's "project"/"hardware
set" template). Work is organized into **four parallel tracks**, one per developer (the team
confirmed 4 developers), following the codebase's existing module seams rather than a sequential
build order:

> **Domain note (mid-project pivot, 2026-09-28):** an earlier iteration of this roadmap reframed
> "hardware set" as household food-item stock (pantry/fridge/freezer locations, freshness rules,
> purchase batches). That reframing has been reverted — this roadmap and the codebase now
> implement the assignment's generic hardware-resource domain directly (named hardware sets,
> flat capacity/availability, request/checkout/checkin). Phase numbers and wave structure below
> are unchanged from the food-domain era; only the domain nouns are.
>
> **Track rescope note (2026-09-28, same day, second pass):** Track D's workload was rebalanced —
> it now owns a comprehensive test suite wired into an early CI pipeline (not batched at the end)
> and a second stretch feature (password reset, moved from Track C) — and the former Track E (UI
> Design) was folded entirely into Track D, which is now **Quality Assurance & Deployment**: test
> design and UI/UX are both QA disciplines, alongside deployment. Track E is retired; the team is
> back to a clean 4 tracks for 4 developers, no dual duty. Track C's remaining stretch feature
> (arbitrary hardware sets) was also narrowed to the part not already covered by Track B's base
> data model — see Phase 3's rescope note below.

- **Track A — Account & Project Management**: everything in `usersDatabase.py` plus
  the project-CRUD/membership half of `projectsDatabase.py`, and the
  `MyLoginPage` / `MyRegistrationPage` / project-list parts of the frontend.
- **Track B — Hardware Resource Management**: everything in `hardwareDatabase.py`
  plus the request/checkout/checkin half of `projectsDatabase.py`,
  and the resource-status/capacity-availability parts of the frontend.
- **Track C — Data Integration & API**: eliminating hard-coded data everywhere and
  hardening the REST API layer so it only fully resolves once Tracks A and B have landed. Track
  C's *infrastructure* sub-tasks (Mongo Atlas provisioning, API response conventions) can start on
  day one in parallel with Tracks A and B; only the final integration/verification sub-tasks are
  gated on A and B substantially landing. Track C owns one promoted stretch feature (explicit
  hardware-set-type management) as its own committed Phase 2 scope, since only 3 of the 4 tracks
  can own one of the 3 real Phase 2 rubric items.
- **Track D — Quality Assurance & Deployment**: a comprehensive PyTest suite for the core backend
  routes wired into an early CI/CD pipeline (GitHub Actions, set up in the project's first days —
  real standalone work, not late scaffolding), deploying the app to a public cloud URL, a second
  promoted stretch feature (password reset), and — since the former Track E folded in here — all
  UI/UX design and polish work across the app. Track D's infra/design sub-tasks (CI pipeline,
  deployment config skeleton, early design-token/layout work against whichever track's UI exists)
  can start on day one in parallel with the other tracks; only the final integration/verification/
  deploy sub-tasks are gated on Tracks A, B, and C substantially landing.

**Explicit coordination point (resolved):** Track A owns project CRUD and membership
(`server/projectsDatabase.py` — create project, join project, look up a user's projects).
Track B owns hardware-set quantity updates and lives in a **separate collection**, not embedded in
the project document — a one-way architecture decision made during Track B's 02-01 execution
checkpoint specifically to avoid the write-contention/merge-conflict risk this coordination point
originally flagged. Hardware sets reference their project by ID; Track A and Track B no longer
write to the same document at all.

## Phases

**Track Ordering:** Tracks A, B, C, and D run in parallel (one per developer, split along existing
module seams) rather than a strict numeric sequence — see the coordination point above and each
track's "Depends on" line for the one place they touch.

> **Note on "Phase N" below:** The `Phase N` numbers in this section's headings are GSD's own
> internal phase-tracking IDs (required by the planning tooling to parse this file) — they are
> **not** the assignment's Phase 1/Phase 2 grading milestones, and they don't align with them
> 1:1 (e.g. GSD's "Phase 2" is Track B, whose own rubric ownership spans both the assignment's
> Phase 1 *and* Phase 2 — see each track's Rubric ownership line in `WORK-ITEMS.md`). Treat
> **Track A/B/C/D** as the real work-breakdown label everywhere in this project; the `Phase N`
> prefix here exists solely so `/gsd-discuss-phase`, `/gsd-plan-phase`, etc. can locate each
> track's section.

- [ ] **Phase 1 (Track A): Account & Project Management** - Users can securely register, log in, stay signed in, and create or join a project
- [x] **Phase 2 (Track B): Hardware Resource Management** - Users can view hardware-set status, request units, check units out, and check units back in (completed 2026-09-22)
- [ ] **Phase 3 (Track C): Data Integration & API** - The app runs entirely on live MongoDB/REST data, and Track C's own promoted stretch feature (explicit hardware-set-type management) is delivered
- [ ] **Phase 4 (Track D): Quality Assurance & Deployment** - A comprehensive test suite runs in CI on every PR, the app is reachable via a public URL, and password reset is delivered
- [x] **Phase 5 (Track D): UI Design** - Hardware-resource UI is visually coherent and phone-usable, with a documented component contract for Track A/C to wire into (completed 2026-09-24; folded from the retired Track E into Track D 2026-09-28)

## Phase Details

### Phase 1 (Track A): Account & Project Management

**Goal**: A project member can securely create an account, log in, stay logged in, and create or join a project to manage shared hardware resources within.
**Depends on**: Nothing (first track — can start immediately in parallel with Track B and Track C's infra sub-tasks)
**Requirements**: ACCT-01, ACCT-02, ACCT-03, ACCT-04, PROJ-01, PROJ-02, PROJ-03
**Success Criteria** (what must be TRUE):

  1. A new user can register via the "New User" sign-up form and immediately log in with those same credentials.
  2. Userid and password are never stored or transmitted in plaintext (encrypted at rest and in transit).
  3. A logged-in user remains logged in while navigating between pages within the app (session persists).
  4. A user can create a new project by supplying a name, description, and projectID.
  5. A user can join an existing project by entering its projectID, and can see the list of every project they belong to.

**Plans**: TBD
**UI hint**: yes

Plans:

- [ ] 01-01: TBD

### Phase 2 (Track B): Hardware Resource Management

**Goal**: Within a project, a member can see what hardware sets are on hand and request, check out, or check in units without ever over-committing what's available.
**Depends on**: Track A only for cross-track integration testing (hardware sets reference a projectId but live in their own collection, not `projectsDatabase.py`'s document — see the resolved coordination point above). Development can proceed in parallel using seeded/test project data.
**Requirements**: RES-01, RES-02, RES-03, RES-04, RES-05
**Success Criteria** (what must be TRUE):

  1. A user can view all hardware sets in a project's inventory, each showing capacity (total units) and availability (units not yet requested or checked out).
  2. A user can check in a hardware set — adding units to its capacity/availability.
  3. A user can request/claim units of a hardware set for themselves without removing them from shared availability.
  4. A user can check out units of a hardware set, and the action is rejected if it would exceed what's currently available.
  5. A project can define any number of named hardware sets, not limited to a fixed pair.

**Plans**: 4 plans
**UI hint**: yes

Plans:
**Wave 1**

- [x] 02-01-PLAN.md — Tracer: check in one hardware set and see it in the resource view (RES-01, RES-02)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 02-02-PLAN.md — (superseded — was location-specific freshness rules, dropped in the domain revert; hardware sets carry no freshness concept)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 02-03-PLAN.md — Hardware-set identity across checkins and per-set detail (RES-01, RES-02)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 02-04-PLAN.md — Request, release, and checkout with the overbooking guard (RES-03, RES-04)

### Phase 3 (Track C): Data Integration & API

**Goal**: The full application runs against a live MongoDB-backed REST API with zero hard-coded data anywhere, and Track C's own promoted stretch feature (explicit hardware-set-type management) is delivered as its Phase 2 scope.
**Depends on**: Track A and Track B for final integration and verification (needs both feature sets substantially implemented to confirm no hard-coded data remains and exercise the full REST surface). Infra sub-tasks (MongoDB Atlas provisioning, API response conventions) can start on day one in parallel with Track A and Track B.
**Requirements**: DATA-01, DATA-02, DATA-03, STRETCH-02
**Success Criteria** (what must be TRUE):

  1. All user, project, and hardware-set data lives in MongoDB collections, and every CRUD operation for each goes through a REST endpoint (no other data path exists).
  2. Every page in the app (login, project portal/list, hardware-resource view, request/checkout/checkin) renders its data — capacity, availability, project list, hardware-set details — from a live REST API call, with no hard-coded or mock values remaining in any component.
  3. A project member can explicitly create, rename, or deactivate a hardware-set *type* for their project (not just have one appear implicitly the first time someone checks something in under a new name) — this is real, distinct scope beyond the base data model, which already accepts any number of named sets automatically.

**Rescope note (2026-09-28):** the base hardware-set data model built in Track B already supports an arbitrary number of named sets per project (RES-05) — sets are created implicitly on first checkin under a new name. STRETCH-02 originally described that same capability and has been reframed to the distinct remaining gap: *explicit* hardware-set-type management (create/rename/deactivate a type without needing to check something in first). STRETCH-01 (password reset) moved to Track D — see Phase 4's rescope note.

**Plans**: TBD
**UI hint**: yes

Plans:

- [ ] 03-01: TBD

### Phase 4 (Track D): Quality Assurance & Deployment

**Goal**: The PoC is reachable by the instructor/TAs via a public URL, is backed by a comprehensive, deliberately-designed automated test suite wired into a CI pipeline that runs on every PR from early in the project, and Track D delivers its own promoted stretch feature (password reset) as standalone work that doesn't wait on deploy readiness. (This phase covers testing and deployment specifically; UI/UX design work — also now Track D's, after the Track E fold — is tracked separately in Phases 5/6, not duplicated here.)
**Depends on**: Track A, Track B, and Track C for final integration, verification, and deploy — but this now gates only the *last* mile (the actual public deploy and the final end-to-end route tests), not Track D's whole workload. CI/CD pipeline setup is real Day-1-onward work: CI can run against whatever routes exist at any point, growing to cover the full route surface as the comprehensive test suite is written. The password-reset stretch feature can start once Track A's login/session flow exists (early-to-mid project, not end-loaded).
**Requirements**: OPS-01, OPS-02, STRETCH-01
**Success Criteria** (what must be TRUE):

  1. A CI pipeline (GitHub Actions) runs the backend test suite and the client build on every pull request, set up in the first days of the project — not as a late add-on — so every track gets fast feedback on its own PRs from day one.
  2. A comprehensive, deliberately-designed PyTest suite exists and passes for the core backend routes (login, create project, join project, request, checkout, checkin) — written as a discrete piece of work, not scattered incremental additions — and runs automatically in CI on every PR.
  3. A user who forgot their password can reset it via the existing Forgot Password flow and regain access to their project's hardware resources.
  4. The deployed app is reachable at a public URL, and the instructor/TAs can complete the full account → project → request/checkout/checkin flow against the hosted instance.

**Rescope note (2026-09-28, two passes):** Track D was originally backloaded — its only Day-1 work was thin pipeline/harness scaffolding, with the bulk of its real work (meaningful tests, actual deploy) gated on every other track finishing. First pass: made CI/CD setup genuine early standalone work and moved the password-reset stretch feature here from Track C. Second pass: replaced the "write tests incrementally, paired with each track" framing with a real discrete deliverable — a comprehensive test suite designed as its own piece of work and wired into CI — and dropped a no-op item ("keep generic naming" is an implementation discipline, not a deliverable, so it was removed rather than tracked as a task). Track D is now **Quality Assurance & Deployment**, having also absorbed the former Track E (UI Design, see Phases 5/6) — test design and UI/UX are both QA disciplines.

**Plans**: TBD
**UI hint**: no

Plans:

- [ ] 04-01: TBD

### Phase 5 (Track D): UI Design

**Fold note (2026-09-28):** executed under the former Track E, owned by Aaron Phan as dual duty alongside Track B. Track E has since been folded entirely into Track D (now Quality Assurance & Deployment) — see the roadmap Overview's track rescope note. This phase's history and shipped artifacts are unchanged; only its go-forward ownership label is.

**Goal**: Track B's hardware-resource UI is visually coherent and usable on a phone, and Track A/Track C have a documented component contract to wire their own UI into instead of touching presentation internals.
**Depends on**: Track B (all design work operates on Track B's already-built components). Not gated on Track A or Track C landing first — the harness items are written *for* those tracks to consume later, not blocked on them existing yet.
**Requirements**: None from REQUIREMENTS.md — additive quality work, not tied to a stakeholder need or system requirement. Board items use `DESIGN` in place of a requirement ID.
**Owner**: Track D (folded from Track E 2026-09-28; executed by Aaron Phan under the original Track E ownership).
**Success Criteria** (what must be TRUE):

  1. The hardware-resource view has clear visual grouping and spacing — not bare HTML tables — and is usable on a phone-width screen.
  2. Status/availability indicators use consistent color coding a project member can recognize without reading the label text.
  3. The top-level resource-view component's session-identity props (`projectId`, `userId`, `userName`) are documented as a contract at one call site, so Track A can wire in real session data without touching component internals.
  4. Every presentational component's data-only prop contract (no internal fetch, no hard-coded fallback) is documented, so Track C can audit DATA-01/DATA-03 against it directly.
  5. A small shared set of style tokens (spacing/color/typography) exists and is documented for Track A and Track C's own UI to adopt.

**Plans**: 2/2 plans executed
**UI hint**: yes

Plans:
**Wave 1**

- [x] 05-01-PLAN.md — Design tokens, shelf-card resource layout, and the phone-width breakpoint (DESIGN)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 05-02-PLAN.md — JSDoc prop contracts on every component and the canonical 05-DESIGN.md (DESIGN)

## Progress

**Execution Order:**
Track A and Track B execute in parallel (independent tracks, one coordination point on `projectsDatabase.py`'s project document). Track C's and Track D's infra sub-tasks start alongside them; Track C's integration/verification sub-tasks and Track D's integration/verification/deploy sub-tasks complete last, after Track A, Track B, and (for Track D) Track C substantially land. Track D's design work (Phases 5/6, folded from the former Track E) starts once Track B's UI exists to design against; its harness items are consumed by Track A/Track C whenever those tracks build their own UI. Track D's QA/deploy work (Phase 4) and its design work (Phases 5/6) proceed independently — one developer, two kinds of quality work, not a strict sequence between them.

| Track | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| A. Account & Project Management | 0/TBD | Not started | - |
| B. Hardware Resource Management | 4/4 | Complete | 2026-09-22 |
| C. Data Integration & API | 0/TBD | Not started | - |
| D. Quality Assurance & Deployment (Phase 4) | 0/TBD | Not started | - |
| D. UI Design (Phase 5, folded from Track E) | 2/2 | Complete | 2026-09-24 |
| D. Dashboard Redesign (Phase 6, folded from Track E) | 0/TBD | In progress (domain pivot in flight) | - |

### Phase 6 (Track D): Dashboard Redesign

**Fold note (2026-09-28):** originally planned/partially executed under the former Track E, Aaron Phan dual duty. Track E has since been folded entirely into Track D (Quality Assurance & Deployment) — see the roadmap Overview's track rescope note. Whoever executes this phase's remaining plans going forward does so as Track D's design work, not as a separate dual-duty role.

**Goal**: The hardware-resource UI is rebuilt as a genuine dashboard — a distinct visual language (warm neutral palette, serif/sans type pairing, soft-shadow rounded surfaces) applied to a real dashboard information architecture (a single filterable data table of hardware sets, centered modal dialogs for Check-In and set-detail actions) — not a token-only polish pass over Phase 5's per-set card-list layout.
**Depends on**: Phase 5 (Track D: UI Design, folded from Track E). The underlying data contract, component prop shapes, and fetch/mutation behavior documented in `05-DESIGN.md` must not change — the top-level view component still fetches the same way and takes the same props — but the presentational markup (card sections, inline check-in form, inline card-expansion) is deliberately replaced, not just re-skinned. This phase supersedes Phase 5's "hairline borders, no shadow, no gradient" elevation rule and its original palette with the new direction; 05-DESIGN.md's data-layer contract sections remain authoritative, its visual-token sections do not.
**Requirements**: None from REQUIREMENTS.md — additive quality work, same as Phase 5. Board items use `DESIGN` in place of a requirement ID.
**Owner**: Track D (folded from Track E 2026-09-28).
**Domain-pivot note (2026-09-28):** this phase was originally designed and partially executed against the food-inventory domain (per-location card board, botanical/organic-serif palette named for a kitchen aesthetic). Following the project's revert to the generic HaaS domain, this phase's remaining work is being re-scoped in parallel: the underlying dashboard structure (single filterable table + centered modals, chosen after rejecting a Kanban-style card-board layout per `ux-heuristics-review`) is domain-agnostic and carries forward; the visual palette stays as a generic warm/neutral design language (no longer named or framed around a kitchen/pantry aesthetic); all remaining content (column headers, copy, filter dimensions) is generalized to hardware sets — no Location column/filter (hardware sets have no location dimension in the generic domain), Item → Hardware Set, Consume/Reserve/Release → Checkout/Request/Release.
**Success Criteria** (what must be TRUE):

  1. The app has a clear, consistent visual point of view (warm neutral background, a small deliberate accent palette, a serif/sans type pairing, heavily rounded soft-shadow surfaces, pill-shaped controls) applied across every screen state, not just the happy-path table.
  2. The hardware-resource list is a single data table (Hardware Set/Capacity/Available columns) — no location filter/column, since the generic domain has no location dimension.
  3. Clicking a table row opens a centered modal dialog showing that hardware set's detail and Checkout/Request/Release controls; a "+ Check In" header action opens the check-in form in the same centered-modal pattern. Both modals share one consistent chrome (rounded corners, soft shadow, dimmed backdrop, explicit × close button, backdrop-click-to-close) — no sidebar/drawer pattern.
  4. Every UI state a user can actually hit is designed, not just functionally present: loading, error/retry, and empty states are visually intentional and match the rest of the system.
  5. The underlying data contract matches the reverted generic backend: capacity/availability per named hardware set, no location/freshness/batch fields. WCAG AA contrast is maintained under the new palette.
  6. A follow-up 6-pillar UI audit scores meaningfully higher than Phase 5's 19/24, with Experience Design and Visuals specifically improved.

**Plans**: 3 plans (in progress — re-scoping to the generic domain in parallel with this roadmap update; see Track B/server and client rework)

Plans:
**Wave 1**

- [~] 06-01-PLAN.md — Dashboard tracer: tokens, the flattened hardware-set table, and the shared modal chrome (DESIGN) — tracer task committed against the food-inventory domain, being re-scoped to the generic domain
- [ ] 06-02-PLAN.md — The palette proven against WCAG AA, the designed loading/error/empty states, and phone width (DESIGN)
- [ ] 06-03-PLAN.md — Prop contracts for the new components and the 05-DESIGN.md supersession (DESIGN)

---
*Roadmap created: 2026-09-14*
*Last updated: 2026-09-28 — reverted the food-inventory domain reframing back to the assignment's generic HaaS/hardware-resource domain; then rescoped Track D (comprehensive test suite wired into early CI, second stretch feature) and folded the former Track E (UI Design, Phases 5/6) entirely into it as "Quality Assurance & Deployment" — phase numbers and wave structure unchanged, track count back to a clean 4-for-4 with no dual duty*
*Granularity: standard | Phase ID convention: sequential*
