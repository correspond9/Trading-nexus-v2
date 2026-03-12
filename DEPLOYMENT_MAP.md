# TradingNexus Deployment Map (Single Source of Truth)

Last updated: 2026-03-12
Owner: TradingNexus

## 1) Production Topology

- Repository: https://github.com/correspond9/Trading-nexus-v2.git
- Primary branch: main
- Local workspace root: D:/4.PROJECTS/FRESH/trading-nexus
- Frontend app source: frontend/
- Backend app source: app/

## 2) Domain -> Service Mapping

- tradingnexus.pro
  - Purpose: Main website + learning pages
  - Served by: Main frontend container (single app)
  - Routes served here: /, /about, /course, /register, /signup, /crash-course, /funded, /rules, and app pages

- www.tradingnexus.pro
  - Purpose: Alias for main website
  - Served by: Main frontend container (single app)

- api.tradingnexus.pro
  - Purpose: Backend API
  - Served by: Main backend container
  - Base path: /api/v2

- learn.tradingnexus.pro
  - Current policy: Optional alias only
  - If used: Point to the SAME main frontend app
  - Must not have a separate codebase/container/repo anymore

## 3) Coolify Mapping

- Coolify project: trading-nexus-v2 (or active production project containing main app)
- Main app branch: main
- Frontend service: frontend
- Backend service: backend
- Supporting services: db, redis

Important: There should be no separate learn-trading-nexus application in production.

## 4) Code Ownership Map

- Frontend routes and pages: frontend/src/
- Educational pages currently in main app:
  - frontend/src/pages/nexus/LandingPage.tsx
  - frontend/src/pages/nexus/AboutPage.tsx
  - frontend/src/pages/nexus/CrashCourse.tsx
  - frontend/src/pages/nexus/SignupPage.tsx
  - frontend/src/pages/nexus/FundedProgram.tsx
  - frontend/src/pages/nexus/Rules.tsx
- Route registration: frontend/src/App.tsx

## 5) Deployment Rules (Do Not Break)

1. Deploy only from this repo.
2. Deploy only from main branch to production.
3. Do not create a second repo/folder/container for learn pages.
4. Keep /funded and /rules only in main frontend code.
5. If learn.tradingnexus.pro is active, map it to the same frontend app.

## 6) Pre-Deploy Checklist

- git branch is main for production deploy
- frontend build passes
- no references to learn-tradingnexus separate app remain
- domain routing in Coolify points both main aliases to one frontend
- backend health endpoint returns OK

## 7) Emergency Recovery (Quick)

If routing confusion returns:

1. Disable/remove separate learn app in Coolify (if re-created).
2. Ensure tradingnexus.pro and www.tradingnexus.pro point to main frontend service.
3. Optionally map learn.tradingnexus.pro to same main frontend service.
4. Redeploy main app from main branch.

## 8) Decision Log

- 2026-03-12: Consolidated to single codebase/frontend deployment model.
- 2026-03-12: Removed local learn-trading-nexus folder and learn-specific deployment docs/scripts.
