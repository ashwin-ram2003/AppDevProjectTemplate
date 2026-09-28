# HaaS Resource Manager — Project Plan (R1-1)

**Team:** Group 2 Monday · ECE 461L Team Project, Fall 2026
**Project:** A generic Hardware-as-a-Service (HaaS) resource-management web app (Proof of Concept), per the assignment's own domain
**Last updated:** 2026-09-28 (domain reverted from an earlier food-inventory reframing back to the assignment's generic hardware-resource domain)

## 1. Team Members

| Name | Track | Responsibility |
|------|-------|----------------|
| Siddharth Kolukuluri | A. Account & Project Management | Sign-up and sign-in, credential encryption, sessions, creating and joining projects |
| Aaron Phan | B. Hardware Resource Management + E. UI Design (dual duty) | Hardware-set status, checkin, request, checkout; plus cross-cutting UI/UX polish and documented component contracts for Tracks A and C to wire into |
| Kody Keo | C. Data Integration & API | REST API, live MongoDB data with no hard-coded values, password reset, arbitrary named hardware sets |
| Aashrith Attelli | D. Deployment & Quality | PyTest coverage, cloud deployment, architecture sketch |

## 2. Methodology

The team follows an Agile approach built around user stories.
- Work is written as user stories of three sentences or less, plus technical-debt and research items.
- Work is split into one-week sprints.
- Features are built on short-lived branches and merged through pull requests. [Proposed: at least one teammate reviews each PR before it merges to `main`.]
- [Proposed: bugs and improvements are tracked as GitHub Issues, separate from the story board.]

## 3. Sprint Cadence

| Activity | When | Where |
|----------|------|-------|
| Sprint review and planning | Every Monday, at the lab meeting | EER 0.818 |
| Midweek check-in | Every Thursday | Discord |

- Sprint length: 1 week, Monday to Monday.
- Sprint 1 starts 2026-09-21. Checkpoint 1 is due 2026-09-21 at 10:00 AM.

**Velocity:** measured as user stories completed per one-week sprint. No sprint has been completed yet, so the baseline will be recorded after Sprint 1 and used to plan later sprints.

## 4. Collaboration Tools

| Purpose | Tool |
|---------|------|
| Communication and check-ins | Discord |
| Source code | GitHub repository (Dr. Samant and the TAs have access) |
| User-story board | GitHub Projects board (To do, In progress, Done) |
| Bug and improvement tracking | [Proposed: GitHub Issues, kept separate from the story board] |
| Code review | GitHub pull requests |

## 5. Toolchain

| Layer | Tool |
|-------|------|
| Front end | React (built with Vite) |
| Back end | Python and Flask, exposing a REST API |
| Database | MongoDB (accessed with PyMongo) |
| Testing | PyTest, with mongomock for tests that don't need a live database |
| Configuration | python-dotenv, with the database connection string in a `MONGODB_URI` environment variable |
| Version control | Git and GitHub |
