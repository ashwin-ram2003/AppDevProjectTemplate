<!-- GSD:project-start source:PROJECT.md -->

## Project

**PantryTrack — Household Food Inventory PoC (Group 2 Monday — ECE 461L Team Project)**

A Proof-of-Concept web application that lets members of a household track shared food inventory across the pantry, fridge, and freezer. Users create secure accounts, create or join a household, and use it to see what food is on hand, reserve items for themselves, log consumption, and log restocking — all backed by a live database, with the class's HaaS "hardware resource" concept reframed as **food item stock** (each item has a total capacity and a remaining availability, the same shape as the assignment's HWSet1/HWSet2 mockup). Built with a Flask/MongoDB backend and a React frontend (starter scaffold already exists in `server/` and `client/`).

**Core Value:** A household member can see what food the household has across pantry/fridge/freezer, reserve or consume items, and restock — all from live shared data, with no hard-coded values anywhere in the app.

### Constraints

- **Tech stack**: Flask + MongoDB + React — matches the existing scaffold (stack choice/toolchain is documented in the separate Project Plan)
- **Process**: User stories must be ≤3 sentences (Mountain Goat Software style); issues (bugs/improvements) tracked separately from user-story board, not combined
- **Security**: Userid and password must be encrypted at rest/in transit (SR3) — non-negotiable rubric item
- **Domain simplification**: No physical sensors are available or in scope — all inventory capture (adding/removing/reserving items) is manual user input via the web UI, not automated detection

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
