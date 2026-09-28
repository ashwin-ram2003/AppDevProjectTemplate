<!-- GSD:project-start source:PROJECT.md -->

## Project

**HaaS Resource Manager PoC (Group 2 Monday — ECE 461L Team Project)**

A Proof-of-Concept web application implementing the assignment's Hardware-as-a-Service (HaaS) system directly: users create secure accounts, create or join a project, and use it to view, request, check out, and check in named hardware sets (HWSet1, HWSet2, ... — any number of named sets, not hard-limited to two) — all backed by a live database. Each hardware set has a total `capacity` and a remaining `available` count, matching the assignment's Figure 3 mockup exactly. Built with a Flask/MongoDB backend and a React frontend (starter scaffold in `server/` and `client/`).

**Core Value:** A project member can see what hardware sets a project has, request/check out units they need, and check units back in — all from live shared data, with no hard-coded values anywhere in the app.

### Constraints

- **Tech stack**: Flask + MongoDB + React — matches the existing scaffold (stack choice/toolchain is documented in the separate Project Plan)
- **Process**: User stories must be ≤3 sentences (Mountain Goat Software style); issues (bugs/improvements) tracked separately from user-story board, not combined
- **Security**: Userid and password must be encrypted at rest/in transit (SR3) — non-negotiable rubric item
- **Domain simplification**: No physical sensors are available or in scope — all hardware-set capture (checking in/out) is manual user input via the web UI, not automated detection
- **Domain naming**: An earlier iteration reframed this as household food inventory and was reverted (TD-10). Do not reintroduce pantry/fridge/freezer, freshness, batch, or restock concepts.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->

## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
