# QUICK REFERENCE CARD
## Common Commands & Procedures for Coolify Deployment

---

## DATABASE VERIFICATION (Run in Coolify psql console)

```sql
-- ✅ Quick Status Check (run all together)
SELECT COUNT(*) as tables FROM information_schema.tables WHERE table_schema='public';
SELECT COUNT(*) as brokerage_plans FROM brokerage_plans;
SELECT COUNT(*) as users FROM users;
SELECT COUNT(*) as users_with_plans FROM users WHERE brokerage_plan_equity_id IS NOT NULL;

-- ✅ Full Validation
SELECT COUNT(*) FROM brokerage_plans;  -- Must be 12
SELECT COUNT(*) FROM users;            -- Must be >= 5
SELECT COUNT(*) FROM instrument_master WHERE symbol IS NOT NULL;  -- Check instruments loaded

-- ✅ Verify No Duplicates
SELECT plan_code, COUNT(*) FROM brokerage_plans GROUP BY plan_code HAVING COUNT(*) > 1;
-- Should return: (no rows)

-- ✅ List All Brokerage Plans
SELECT plan_id, plan_code, plan_name, instrument_group FROM brokerage_plans ORDER BY plan_id;

-- ✅ Check User Assignments
SELECT u.username, bp.plan_code FROM users u 
LEFT JOIN brokerage_plans bp ON u.brokerage_plan_equity_id = bp.plan_id;

-- ✅ Verify Table Existence (should be 26+)
SELECT table_name FROM information_schema.tables 
WHERE table_schema='public' ORDER BY table_name;
```

---

## BACKEND API VERIFICATION

```bash
# ✅ Health Endpoint
curl http://72.62.228.112:8000/health
# Expected: {"status":"ok","version":"1.0.0"}

# ✅ With Domain (after DNS configured)
curl https://tradingnexus.pro/health
curl https://api.tradingnexus.pro/health

# ✅ Verbose Response
curl -v http://72.62.228.112:8000/health 2>&1 | grep -E "Connected|HTTP|status"

# ✅ Test With Timeout (useful if slow to respond)
curl --max-time 30 http://72.62.228.112:8000/health
```

---

## COOLIFY OPERATIONS

### View Logs
```bash
# In Coolify UI:
# Application → Logs (shows build, startup, runtime logs)
# Useful for debugging deployment issues
```

### Restart Application
```bash
# In Coolify UI:
# Application → Stop → Deploy
# This will restart the application while preserving database
```

### View Database
```bash
# In Coolify UI:
# PostgreSQL Service → Console or CLI
# Or use external psql tool with connection details shown
```

### Redeploy Latest Code
```bash
# In Coolify UI:
# Application → Deploy
# Pulls latest from GitHub main branch and rebuilds
```

---

## TESTING SCENARIOS

### Test 1: Form Validation (THE FIX WE MADE)
```
1. Login to admin dashboard
2. Navigate to Super Admin → Historic Position tab
3. In Symbol field, try typing: "LENSKART NSE EQUITY"
4. EXPECTED: Form shows red error "⚠️ Please search and select from dropdown"
5. EXPECTED: Cannot submit form without selecting from dropdown
6. Try typing just "RELIANCE" and select from dropdown
7. EXPECTED: Form accepts it and allows submission
STATUS: ✅ PASS if form rejects full names but accepts symbols
```

### Test 2: Database Migrations
```sql
-- Run in database console:
SELECT COUNT(*) FROM brokerage_plans;
-- EXPECTED: 12
-- If 0: Migrations didn't run, check logs
-- If > 12 or < 12: Duplicate or missing data
```

### Test 3: API Response Format
```bash
curl -s http://72.62.228.112:8000/health | python -m json.tool
# EXPECTED:
# {
#   "status": "ok",
#   "version": "1.0.0"
# }
```

---

## TROUBLESHOOTING CHECKLIST

### Issue: "Connection refused" on :8000
- [ ] Backend running in Coolify? (check status in UI)
- [ ] Health endpoint timeout? (wait 30 seconds after deploy)
- [ ] Port exposed correctly? (should be :8000)
- **Solution**: Check Coolify logs, restart application

### Issue: Database not initialized (0 brokerage plans)
- [ ] Did migrations run? (check logs for "migration" messages)
- [ ] Did PostgreSQL service start? (check Coolify service status)
- [ ] Wrong database? (verify database name in connection)
- **Solution**: Restart application to re-trigger migrations

### Issue: 12 brokerage plans but form still broken
- [ ] Frontend deployed? (or still on old version)
- [ ] Frontend connecting to correct backend? (check network calls)
- [ ] Browser cache? (clear cache or use incognito)
- **Solution**: Redeploy frontend, hard refresh browser

### Issue: Domain returns 404
- [ ] Domain DNS pointing to correct IP? (run `nslookup tradingnexus.pro`)
- [ ] Coolify reverse proxy configured? (check Traefik settings)
- [ ] SSL certificate provisioning? (takes 1-2 minutes)
- **Solution**: Wait for SSL cert, verify reverse proxy config

### Issue: Form accepts full names like "LENSKART NSE EQUITY"
- [ ] This means the fix didn't deploy correctly
- [ ] Check frontend code in GitHub main branch
- [ ] Verify frontend was redeployed after code changes
- [ ] Check browser network tab for API responses
- **Solution**: Redeploy frontend, clear cache

---

## PERFORMANCE CHECKS

```bash
# Check backend response time
time curl http://72.62.228.112:8000/health
# Should be < 100ms after warmup

# Check database connectivity from backend
# (would require app endpoint, not available in this version)

# Check network latency to VPS
ping 72.62.228.112
# Should be < 50ms (adjust based on your location)
```

---

## COMMON OPERATIONS

### After Coolify Deploy Completes
1. **Wait 30 seconds** for health checks to pass
2. **Test health endpoint**: `curl http://72.62.228.112:8000/health`
3. **Check database**: Run validation SQL queries
4. **Verify brokerage plans**: `SELECT COUNT(*) FROM brokerage_plans;` should be 12
5. **Test form validation**: Try the historic position form

### If Need to Pull Latest Code
1. In Coolify UI, click **Deploy** on the Application
2. Check **Logs** to verify build completed
3. Wait for **health checks to pass** (green status)
4. Test again

### If Need to Reset Database
1. In Coolify UI, go to **PostgreSQL Service**
2. Delete the service (data will be lost)
3. Redeploy Application (will recreate PostgreSQL and run migrations)

### If Need to Check Git Status
1. In Coolify UI, go to **Application → Settings**
2. Check **Git Branch** is `main`
3. Check **Last Deployed At** timestamp

---

## VALIDATION SCRIPT USAGE

```bash
# Run validation script (from project root)
python validate_deployment.py \
  --host 72.62.228.112 \
  --port 5432 \
  --db trading_nexus_db \
  --user postgres \
  --password <your_password>

# Output will show:
# ✅ PASSED: All validations successful
# ⚠️  WARNINGS: Some issues but deployment works
# ❌ ERRORS: Critical issues that need fixing
```

---

## EXPECTED TIMELINE

- **T+0s**: Deploy triggered in Coolify
- **T+30s**: Builder starts (pulling from GitHub)
- **T+2m**: Docker image built, PostgreSQL container starting
- **T+2m30s**: Database ready, migrations running
- **T+3m**: Migrations complete, app starting
- **T+3m30s**: Health checks passing, app ready
- **T+5m**: All systems ready for testing

---

## SUPPORT QUICK LINKS

**GitHub Repository**: https://github.com/correspond9/Trading-nexus-v2.git
**Tech Stack**: FastAPI + React/Vue + PostgreSQL 16 + Redis
**Deployment Platform**: Coolify (self-hosted Docker orchestration)
**Monitoring**: Coolify UI provides logs, status, metrics

---

## STATUS INDICATORS

| Indicator | Status | Action |
|-----------|--------|--------|
| 🟢 Application running | ✅ OK | Proceed with testing |
| 🟡 Health checks pending | ⏳ Wait | Wait 30 seconds, retry |
| 🔴 Application exited | ❌ Error | Check logs, restart |
| 🟢 Database ready | ✅ OK | Proceed with migrations |
| 🔴 Database connection error | ❌ Error | Check credentials, restart |
| ✅ Brokerage plans = 12 | ✅ OK | Database initialized correctly |
| ❌ Brokerage plans ≠ 12 | ❌ Error | Re-run migrations or restart |

---

**Remember**: All operations go through Coolify UI. No direct SSH/docker commands needed!
