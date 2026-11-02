# Requirements: HaaS Resource Manager PoC (Group 2 Monday)

**Defined:** 2026-09-14 (re-scoped from generic hardware domain to household food inventory domain)
**Reverted:** 2026-09-28 (food-inventory reframing dropped; back to the assignment's generic HaaS/hardware-resource domain)
**Core Value:** A project member can see what hardware sets a project has, request/check out units they need, and check units back in — all from live shared data, with no hard-coded values anywhere in the app.

Source: `Team Project_Fa26.pdf` (Stakeholder Needs SN0–SN6, System Requirements SR1–SR5, MVP feature spec for User Management / Resource Management), implemented directly per the assignment's own domain — no reframing.

## v1 Requirements

### Account (SN1, SR3)

- [ ] **ACCT-01**: User can sign in with userid and password
- [ ] **ACCT-02**: User can click "New User" to open a sign-up form and create a userid/password
- [ ] **ACCT-03**: Userid and password are encrypted (not stored or transmitted in plaintext)
- [ ] **ACCT-04**: User session persists across page navigation within the app

### Project (SN1, SR4, SR5)

- [ ] **PROJ-01**: User can create a new project by providing name, description, and projectID
- [ ] **PROJ-02**: User can join/access an existing project by entering its projectID
- [ ] **PROJ-03**: User can view the list of projects they belong to

### Hardware Resources (SN2, SN3, SN4, SN5, SR5)

- [x] **RES-01**: User can view all hardware sets in a project, each showing capacity (total units) and availability (units not yet checked out)
- [x] **RES-02**: User can check in a hardware set — add units to its capacity/availability
- [x] **RES-03**: User can request/claim units of a hardware set for themselves without removing them from availability
- [x] **RES-04**: User can check out units of a hardware set, and the action is rejected if it would exceed what's currently available
- [x] **RES-05**: A project can define any number of named hardware sets, not limited to a fixed pair

### Data & API (SR2, SR5, R2-1, R2-2)

- [ ] **DATA-01**: User, project, and hardware-set data are persisted in MongoDB — no hard-coded data on any page
- [ ] **DATA-02**: A REST API layer exposes user/project/hardware-set operations to the React frontend
- [ ] **DATA-03**: Frontend renders all displayed values (capacity, availability, project list, hardware-set details) from live API responses

### Deployment & Quality (SN6, SR1, R2-3, SN0)

- [ ] **OPS-01**: App is deployed to a cloud host and reachable via a public URL for TAs/instructor
- [ ] **OPS-02**: Automated tests (PyTest) cover core backend routes (login, create/join project, request, checkout, checkin)

### Stretch Features (not from PDF rubric — promoted backlog)

- [ ] **STRETCH-01**: User can reset a forgotten password via the existing Forgot Password flow — **owned by Track D** (moved from Track C 2026-09-28, so Track D has standalone feature work spread through the project instead of only infra/testing/deploy — see Phase 4's rescope note in ROADMAP.md)
- [ ] **STRETCH-02**: User can explicitly create, rename, or deactivate a hardware-set *type* for a project, independent of checking something in — **owned by Track C**. The base data model already supports any number of named sets (RES-05, created implicitly on first checkin); this stretch item is the remaining distinct gap, explicit type management without needing a checkin first.

> Note: R1-1 (Project Plan — team members, sprint cadence, collaboration tools, methodology, toolchain) is now owned by Track A.

## Rubric Item Ownership

| Rubric Item | Description | Owning Track |
|-------------|--------------|--------------|
| R1-1 | Project Plan (team members, sprint cadence, collaboration tools, methodology, toolchain) | Track A |
| R1-2 | Feature board (all features + initial work items) | Track B |
| R1-4 | Tool choice & approach | Track C |
| R1-3 | High-level sketch of application architecture | Track D |
| R2-1 | Hardware resources stored in DB with an API | Track B |
| R2-2 | User/project info live in the app, no hard-coded data | Track A |
| R2-3 | Cloud deployment reachable via public URL | Track D |

> Track C has no numbered R2 rubric item (only 3 exist for 4 tracks). Its Phase 2 contribution is instead the Stretch Features group above (STRETCH-02 only, as of the 2026-09-28 rescope — STRETCH-01 moved to Track D as additional work on top of its own R2-3, to spread Track D's workload across the whole project instead of backloading it onto deploy).

## v2 Requirements

Deferred — acknowledged as valuable but out of committed scope for this PoC.

### Automated Capture

- **CAP-01**: RFID/barcode scanning to auto-detect hardware entering/leaving storage
- **CAP-02**: Sensor-based automatic detection of checkout/checkin events

### Intelligent Tracking

- **INT-01**: Usage analytics — which hardware sets are checked out most, run low most often
- **INT-02**: Per-user behavior adaptation (e.g., typical checkout duration, frequent requesters) driving smarter availability forecasting

### Planning & Procurement

- **PLAN-01**: Low-availability alerts and automated reorder/procurement suggestions
- **PLAN-02**: Checkout-duration reminders / overdue-return notifications

### Enhancements (from prior scoping pass, still applicable)

- **ENH-01**: Password reset / "Forgot Password" flow (scaffold page `ForgotMyPassword.js` exists but not required by stakeholder needs) — **promoted to v1 committed scope as STRETCH-01 under Track D**
- **ENH-02**: Admin view to explicitly manage named hardware-set types — **promoted to v1 committed scope as STRETCH-02 under Track C**
- **ENH-03**: Partial/fractional quantity tracking within a unit — raised during Track B's discuss-phase; deferred, v1 uses whole-unit integer quantities only.

## Out of Scope

| Feature | Reason |
|---------|--------|
| OAuth / third-party login | Not required by SN1; adds complexity beyond PoC scope |
| Real-time multi-user live sync (websockets) | Not a stated stakeholder need; refresh-based updates suffice |
| Mobile app | SR2 specifies a web front-end only |
| Any physical sensor/hardware integration | No hardware budget/timeline for a course project — see v2 Automated Capture items instead |
| Billing / payment processing | Not a stakeholder need |
| Per-location/storage grouping of hardware sets | Not part of the assignment's mockup — a flat list of named hardware sets, no location dimension |

## Traceability

Which tracks cover which requirements. Populated during roadmap creation.

| Requirement | Track | Status |
|-------------|-------|--------|
| ACCT-01 | Track A | Pending |
| ACCT-02 | Track A | Pending |
| ACCT-03 | Track A | Pending |
| ACCT-04 | Track A | Pending |
| PROJ-01 | Track A | Pending |
| PROJ-02 | Track A | Pending |
| PROJ-03 | Track A | Pending |
| RES-01 | Track B | Complete |
| RES-02 | Track B | Complete |
| RES-03 | Track B | Complete |
| RES-04 | Track B | Complete |
| RES-05 | Track B | Complete |
| DATA-01 | Track C | Pending |
| DATA-02 | Track C | Pending |
| DATA-03 | Track C | Pending |
| OPS-01 | Track D | Pending |
| OPS-02 | Track D | Pending |
| STRETCH-01 | Track D | Pending |
| STRETCH-02 | Track C | Pending |

**Coverage:**

- v1 requirements: 19 total
- Mapped to tracks: 19 (Track A: 7, Track B: 5, Track C: 4, Track D: 3)
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-14*
*Last updated: 2026-09-28 — reverted food-inventory domain (HH-*/INV-* IDs) back to generic HaaS domain (PROJ-*/RES-* IDs), status marks preserved from the equivalent already-shipped Track B work*
