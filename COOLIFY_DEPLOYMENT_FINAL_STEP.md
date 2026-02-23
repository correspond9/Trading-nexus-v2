# Trading Nexus v2 - Coolify Deployment Instruction

## Current Status

The backend is fully operational and users API is working:
- ✅ Backend health: http://kww8g880ggkkwgosw40kco0o.72.62.228.112.sslip.io/api/v2/health
- ✅ Users API: http://kww8g880ggkkwgosw40kco0o.72.62.228.112.sslip.io/api/v2/admin/users (returns 4 users)
- ✅ Login works with credentials: 9999999999 / admin123

The frontend loads but users list doesn't display.

## Required Action for Coolify

Set the following environment variable in the Coolify application settings:

**Variable Name:** `VITE_API_URL`
**Value:** `http://kww8g880ggkkwgosw40kco0o.72.62.228.112.sslip.io/api/v2`

Then trigger a rebuild of the frontend component.

This will compile the React app with the correct backend API URL so the frontend can communicate with the backend.

##Steps:

1. Go to Coolify Application Settings (bsgc4kwsk88s04kgws0408c4)
2. Find "Environment Variables" or "Build Args" section
3. Add: `VITE_API_URL=http://kww8g880ggkkwgosw40kco0o.72.62.228.112.sslip.io/api/v2`
4. Save any changes
5. Trigger a new deployment (force rebuild)
6. Wait for build to complete (~2-3 minutes)
7. Refresh the frontend at http://ko8ws0gg08ccwkk04oc4o0go.72.62.228.112.sslip.io/users
8. Users list should now display all 4 users

## Test Credentials

Super Admin: `9999999999 / admin123`
Admin: `8888888888 / admin123`
Super User: `6666666666 / super123`  
User: `7777777777 / user123`

All users have 1,000,000.00 wallet balance for paper trading.

## Commits Since Last Session

- 8b3f8df: Add extensive debug logging to users endpoint
- 2e3d600: Remove brokerage_plan from users query
- 2a7e2ef: Fix encoding issue in migration 023
- 2be1f79: Allow all CORS origins (secured by auth)
- f04a227: Add Nginx reverse proxy for backend API
- f1cd0b5: Revert nginx proxy - use VITE_API_URL env var
- a62e204: Add improved Nginx reverse proxy with WebSocket support
- 46c7323: Remove hardcoded VITE_API_URL default

## Architecture Notes

In Coolify:
- Backend (FastAPI) runs on port 8000 internally, exposed as: http://kww8g880ggkkwgosw40kco0o.72.62.228.112.sslip.io
- Frontend (React/Vite) runs on port 80 internally, exposed as: http://ko8ws0gg08ccwkk04oc4o0go.72.62.228.112.sslip.io
- Each service has a separate public domain
- Frontend needs to be rebuilt with the backend URL to know how to reach it

The application is 99% functional - only missing the final build-time configuration step.
