# STEP-BY-STEP COOLIFY DEPLOYMENT GUIDE
**For**: Trading Nexus v2 Fresh Installation on Ubuntu 24.04

---

## PHASE 1: COOLIFY SETUP (You're handling this)

1. ✅ Ubuntu 24.04 installed on VPS (72.62.228.112)
2. ✅ Coolify installed and running
3. ✅ Coolify dashboard accessible at http://72.62.228.112:3000
4. ✅ Admin account created in Coolify

**Status**: Once complete, notify me with "Coolify is ready"

---

## PHASE 2: CREATE PROJECT IN COOLIFY UI

When Coolify dashboard is ready:

### Step 1: Create New Project
- Name: `Trading-Nexus` (or your preference)
- Description: (optional)

### Step 2: Add Application - Backend API
- **Name**: `backend`
- **Application Type**: `Docker`
- **Build Pack**: `Dockerfile`
- **Repository**: `https://github.com/correspond9/Trading-nexus-v2.git`
- **Branch**: `main`
- **Dockerfile Location**: `./Dockerfile` (relative to repo root)
- **Build Context**: `.` (root directory)

### Step 3: Set Environment Variables (in Coolify UI)
Leave these empty/default unless you need custom values:
- `DATABASE_URL`: (Coolify will manage PostgreSQL)
- `REDIS_URL`: (Coolify will manage Redis, if used)
- Any DhanHQ credentials: (Can be added through Admin panel later)

### Step 4: Configure Ports and Networking
- **Expose Port**: `8000` (HTTP - Backend API)
- **Health Check Endpoint**: `/health`
- **Health Check Interval**: 30 seconds

### Step 5: Add Service - PostgreSQL Database
Coolify can auto-provision:
- **Database Name**: `trading_nexus_db`
- **PostgreSQL Version**: 16 (or latest)
- **Username**: `postgres`
- **Password**: (auto-generate or specify)

Coolify will:
- Create network between backend and database
- Set `DATABASE_URL` environment variable automatically
- Initialize database

### Step 6: Deploy
- Click **Deploy** in Coolify UI
- Coolify will:
  1. Clone GitHub repository
  2. Build Docker image
  3. Create PostgreSQL container
  4. Run migrations (from docker CMD)
  5. Start backend service
  6. Run health checks

---

## PHASE 3: DEPLOYMENT MONITORING

### Monitor Logs
While deploying, watch logs in Coolify:
- **Build Logs**: Should show Docker build steps
- **Startup Logs**: Should show migration execution
- **Application Logs**: Should show FastAPI startup

### Expected Log Sequence
```
[1] Building Docker image...
[2] Image built successfully
[3] Creating PostgreSQL container...
[4] PostgreSQL ready to accept connections
[5] Running migrations...
    - 001_initial_schema.sql ✓
    - 002_users_baskets.sql ✓
    - ...
    - 025_production_brokerage_plans.sql ✓
[6] Starting FastAPI application...
[7] Application startup complete [INFO] Application startup complete
[8] Uvicorn running on 0.0.0.0:8000
```

### Verify Status in Coolify UI
- Application Status: **Running** (green)
- Health Check: **Passing** (green)
- Last Deploy: Should show successful timestamp

---

## PHASE 4: IMMEDIATE VERIFICATION

Once Coolify shows "Running":

### Test Health Endpoint (80 seconds after deploy starts)
```bash
curl http://72.62.228.112:8000/health
```
**Expected Response**:
```json
{"status":"ok","version":"1.0.0"}
```

### Test Database Connection
```bash
# Access Coolify's PostgreSQL console or use psql
psql -h 127.0.0.1 -U postgres -d trading_nexus_db -c "SELECT COUNT(*) FROM users;"
```

### Verify Migrations Ran
```sql
-- Connect to database through Coolify
SELECT COUNT(*) FROM brokerage_plans;  -- Should return 12
SELECT COUNT(*) FROM users;            -- Should return >= 5 (seed users)
```

---

## PHASE 5: FULL VERIFICATION

### Validation Checklist
- [ ] Backend API responds on `:8000`
- [ ] Health endpoint returns 200 OK
- [ ] PostgreSQL container running and connected
- [ ] All 26 tables in `information_schema.tables`
- [ ] Brokerage plans: exactly 12 rows
- [ ] Seed users: >= 5 rows
- [ ] No duplicate data in brokerage_plans

### Validation SQL Script (Run in Coolify psql)
```sql
-- Test 1: Count tables (should be 26+)
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Test 2: Verify brokerage plans (should be 12)
SELECT COUNT(*) as plan_count FROM brokerage_plans;

-- Test 3: Verify plan codes are unique (should return 0)
SELECT COUNT(*) as duplicates FROM (
  SELECT plan_code FROM brokerage_plans 
  GROUP BY plan_code HAVING COUNT(*) > 1
) t;

-- Test 4: List all brokerage plans
SELECT plan_id, plan_code, plan_name, instrument_group, is_active 
FROM brokerage_plans 
ORDER BY plan_id;

-- Test 5: Verify seed users (should be >= 5)
SELECT COUNT(*) as user_count FROM users;

-- Test 6: Verify users have brokerage plan assignments
SELECT COUNT(*) as users_with_plans 
FROM users 
WHERE brokerage_plan_equity_id IS NOT NULL;

-- Test 7: Check for any migration errors in system logs
SELECT * FROM system_config ORDER BY updated_at DESC LIMIT 5;
```

---

## PHASE 6: FRONTEND DEPLOYMENT (Optional - After Backend Verified)

Once backend is verified running:

### Add Frontend Application to Coolify
- **Name**: `frontend`
- **Application Type**: `Docker`
- **Build Pack**: `Dockerfile` (uses frontend/Dockerfile)
- **Repository**: `https://github.com/correspond9/Trading-nexus-v2.git`
- **Branch**: `main`
- **Dockerfile Location**: `./frontend/Dockerfile`
- **Build Context**: `./frontend`

### Frontend Configuration
- **Expose Port**: `3000` (HTTP - Frontend UI)
- **Build Args**: 
  - `VITE_API_BASE_URL=http://backend:8000` (internal network reference)
- **Health Check**: `/index.html` (HTTP 200)

### Deploy Frontend
Coolify will build and start frontend on :3000

---

## PHASE 7: DOMAIN CONFIGURATION (After Both Services Running)

Once backend AND frontend are running in Coolify:

### Configure Reverse Proxy (Traefik in Coolify)

In Coolify UI, add domains:

1. **For Backend**:
   - Domain: `api.tradingnexus.pro`
   - Forward to: `backend:8000`
   - SSL: Auto (Let's Encrypt)

2. **For Frontend**:
   - Domain: `tradingnexus.pro` (or `www.tradingnexus.pro`)
   - Forward to: `frontend:3000`
   - SSL: Auto (Let's Encrypt)

### DNS Configuration
Update your domain registrar:
- A record: `tradingnexus.pro` → `72.62.228.112`
- CNAME (optional): `api.tradingnexus.pro` → `tradingnexus.pro`

Coolify's Traefik handles:
- SSL certificate provisioning (Let's Encrypt)
- Certificate renewal (automatic)
- Service routing
- Load balancing (if needed)

---

## PHASE 8: FULL SYSTEM VERIFICATION

### Test Backend API
```bash
curl https://tradingnexus.pro/health
# or
curl https://api.tradingnexus.pro/health
```

### Test Frontend UI
Open browser to `https://tradingnexus.pro`
- Should load frontend
- Login page should display
- API calls should work (CORS configured in FastAPI)

### Test Historic Position Form (The Fix We Made)
1. Log in as admin
2. Go to Admin Dashboard → Historic Position tab
3. Try typing a symbol like "LENSKART NSE EQUITY"
4. **Expected**: Form shows error "⚠️ Please search and select from dropdown"
5. **Expected**: You must select from dropdown to proceed

---

## ROLLBACK PROCEDURE (If Issues)

If something goes wrong:

1. **Stop Application in Coolify UI**: Click "Stop"
2. **View Logs**: Check application logs for errors
3. **Check Database**: Manually connect to verify data integrity
4. **Restart**: Click "Deploy" again

If database corruption:
1. Stop application
2. Drop and recreate database in Coolify UI
3. Deploy again (migrations will re-run)

---

## SUPPORT QUERIES

**"How do I access the database?"**
- Coolify provides PostgreSQL management in UI
- Or via psql: `psql -h <coolify-host> -U postgres -d trading_nexus_db`

**"Where are the logs?"**
- Coolify UI → Application → Logs tab
- Shows build, startup, and runtime logs

**"How do I update the application?"**
1. Push changes to GitHub main branch
2. In Coolify UI, click "Deploy" again
3. Coolify will pull latest code and rebuild

**"How do I scale to multiple instances?"**
- Coolify UI → Application → Replicas setting
- Set number of instances (requires load balancer)

---

## CRITICAL REMINDERS

✅ **DO**:
- Deploy through Coolify UI (proper channel)
- Let Coolify manage database and containers
- Use Coolify's reverse proxy for domains
- Monitor health checks regularly
- Keep Coolify updated

❌ **DON'T**:
- SSH into VPS and manually run docker commands
- Edit database directly (use migrations)
- Delete containers or volumes from CLI
- Bypass Coolify's deployment pipeline

---

## STATUS CHECKLIST

Record status as you complete each phase:

- [ ] Phase 1: Ubuntu 24.04 + Coolify installed
- [ ] Phase 2: Notified when Coolify ready ("Coolify is ready")
- [ ] Phase 3: Project created in Coolify
- [ ] Phase 3: Backend application configured
- [ ] Phase 3: PostgreSQL provisioned
- [ ] Phase 3: Deployment triggered
- [ ] Phase 4: Health endpoint returns 200
- [ ] Phase 5: Database has 12 brokerage plans
- [ ] Phase 5: All tables initialized
- [ ] Phase 6: Frontend deployed (optional)
- [ ] Phase 7: Domain configured
- [ ] Phase 8: Full system accessible at domain
- [ ] Phase 8: Historic position form validation works

---

**Next Step**: Complete Ubuntu 24.04 + Coolify installation, then notify me when Coolify dashboard is accessible!
