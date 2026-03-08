# Configuration Synchronization Checklist
## What Needs to be Synchronized Beyond Docker Images & Database

This document answers: "What other things or settings need to be synchronized that you may have overlooked?"

---

## ✅ ALREADY COVERED (by the setup scripts)

### 1. Docker Images & Containers ✓
- Backend image (FastAPI + Python)
- Frontend image (React + Nginx)
- PostgreSQL container

### 2. Database Tables & Data ✓
All 30+ tables including:
- Users, sessions, authentication
- Orders, positions, trades
- Ledger entries, payouts
- Watchlists, baskets
- Margin caches
- Instrument master data
- System configuration

### 3. Environment Variables ✓
- Database credentials
- DhanHQ API credentials (Client ID, PIN, TOTP secret)
- Feature flags
- CORS settings
- Log levels

### 4. Static Data Files ✓
- Instrument master CSV files
- Migration SQL files

---

## 🔍 ADDITIONAL ITEMS TO CONSIDER

### 5. Network Configuration

**Production Setup:**
```
Internet → Traefik → Frontend (port 80)
                   → Backend (port 8000)
                   → Database (port 5432, internal only)
```

**Local Setup:**
```
localhost → Frontend (port 80)
localhost:8000 → Backend (direct access)
localhost:5432 → Database (direct access)
```

**What to sync:**
- ❌ SSL/TLS certificates (not needed locally)
- ❌ Traefik configuration (not needed locally)
- ✅ CORS origins (already handled - set to localhost)
- ✅ Port mappings (already configured in docker-compose.yml)

**Action Required:** None - already handled differently for local vs production.

---

### 6. File System Volumes & Persistent Data

**Production Volumes:**
- `/var/lib/postgresql/data` (database storage)
- Possibly log directories
- Uploaded files (if any)

**Local Volumes:**
- `trading_nexus_pg_data` (Docker volume)
- `./logs/` (local directory)

**What to sync:**
- ✅ Database data (already handled by dump/import)
- ⚠️ **Log files** (optional - if you want historical logs)
- ⚠️ **Uploaded files** (if users can upload files to the system)

**Action Required:**
```powershell
# Optional: Download production logs via Coolify
# See section below for script
```

---

### 7. Background Jobs & Scheduled Tasks

**Check if production has:**
- Cron jobs running outside Docker
- Scheduled database cleanups
- Automated backups
- Market data refresh jobs

**What to sync:**
- Background tasks configuration
- Scheduler settings (if using APScheduler, Celery, etc.)

**Action Required:**
Check if your application has background jobs:
```powershell
# Check app code for schedulers
Get-ChildItem -Recurse -Include "*.py" | Select-String -Pattern "scheduler|cron|periodic|background"
```

---

### 8. External API Keys & Credentials

**DhanHQ Credentials:** ✅ Already synced

**Other possible integrations:**
- ❓ Payment gateway credentials (Razorpay, Stripe, etc.)
- ❓ SMS/Email service credentials (Twilio, SendGrid, etc.)
- ❓ Cloud storage credentials (AWS S3, Google Cloud, etc.)
- ❓ Analytics services (Google Analytics, Mixpanel, etc.)
- ❓ Error tracking services (Sentry, etc.)

**Action Required:**
Check your production `.env` or Coolify environment variables for:
```powershell
# Run this to review all production env vars
python -c "import json; print(json.dumps(json.load(open('production_db_export/production_env_vars.json')), indent=2))"
```

Add any missing API keys to your local `.env` file.

---

### 9. WebSocket Configuration

**In Production:**
- WebSocket connections to DhanHQ for market data
- Possibly WebSocket connections from frontend to backend

**In Local:**
- ✅ **DISABLED by default** to prevent conflicts

**Feature flags that control this:**
```env
DISABLE_DHAN_WS=true              # Disables DhanHQ WebSocket
DISABLE_MARKET_STREAMS=true       # Disables market data streams
STARTUP_START_STREAMS=false       # Don't auto-start on startup
```

**Action Required:** None - already safely configured.

If you need to test WebSocket functionality locally:
1. Update `.env`: Set `DISABLE_DHAN_WS=false`
2. Restart: `docker compose restart backend`
3. Monitor: `docker compose logs -f backend`

---

### 10. Rate Limits & Throttling

**Production may have:**
- Rate limiting on API endpoints
- Request throttling
- Connection limits

**What to sync:**
- Rate limit configurations
- Throttle settings

**Where to check:**
```powershell
# Search for rate limit middleware
Get-ChildItem app -Recurse -Include "*.py" | Select-String -Pattern "RateLimiter|rate_limit|throttle"
```

**Action Required:** Usually not needed for local development. But if you want to test rate limiting:
- Check `app/main.py` for rate limit middleware
- Ensure settings are in `.env` or config files

---

### 11. Security Settings

**Production Security:**
- JWT secret keys
- Password hashing salts
- CORS allowed origins
- Secure headers

**What to sync:**
```env
# Check if these exist in production
SECRET_KEY=...
JWT_SECRET=...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=...
```

**Action Required:**
```powershell
# Review security settings in production env vars
Select-String -Path "production_db_export/production_env_vars.json" -Pattern "SECRET|JWT|KEY|TOKEN"
```

Add any missing security settings to local `.env`.

⚠️ **Note:** For local development, security can be relaxed, but production secrets should still be kept secure.

---

### 12. Feature Flags & Toggles

**Common feature flags:**
- ✅ `STARTUP_LOAD_MASTER` (instrument master loading)
- ✅ `STARTUP_LOAD_TIER_B` (tier B instruments)
- ✅ `STARTUP_START_STREAMS` (auto-start market streams)
- ❓ Others specific to your app

**Action Required:**
Review `production_env_vars.json` for any feature flags you want to test:
```powershell
Get-Content production_db_export/production_env_vars.json | Select-String -Pattern "ENABLE|DISABLE|FEATURE"
```

---

### 13. Third-Party Services State

**May need to sync:**
- ❓ Redis cache data (if using Redis)
- ❓ Message queue state (if using RabbitMQ, etc.)
- ❓ Search indices (if using Elasticsearch)
- ❓ CDN cache (usually not needed locally)

**Action Required:**
Check docker-compose.yml for additional services:
```powershell
# Your current setup only has: db, backend, frontend
# Check if production has additional services
Select-String -Path docker-compose.yml -Pattern "services:" -Context 0,20
```

✅ **Current setup: No additional services needed.**

---

### 14. Time Zone Settings

**Production server timezone:** Likely UTC or Asia/Kolkata

**Local system timezone:** May differ

**What to sync:**
```env
TZ=Asia/Kolkata  # Set timezone if needed
```

**Impact:**
- Affects log timestamps
- Affects scheduled jobs
- Affects market hours validation

**Action Required:**
```powershell
# Check if TZ is set in production
Select-String -Path "production_db_export/production_env_vars.json" -Pattern "TZ|TIMEZONE"
```

Add to `.env` if found:
```env
TZ=Asia/Kolkata
```

---

### 15. Database Sequences & Auto-Increment

**After importing data:**
- PostgreSQL sequences may need resetting
- Auto-increment IDs might not continue correctly

**Action Required:**
Run this after database import:
```sql
-- Reset all sequences to correct values
SELECT setval(pg_get_serial_sequence('users', 'id'), (SELECT MAX(id) FROM users));
SELECT setval(pg_get_serial_sequence('paper_orders', 'id'), (SELECT MAX(id) FROM paper_orders));
SELECT setval(pg_get_serial_sequence('paper_positions', 'id'), (SELECT MAX(id) FROM paper_positions));
-- Repeat for all tables with auto-increment IDs
```

**Or run this script:**
```powershell
docker exec trading_nexus_db psql -U postgres -d trading_nexus -c "
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND column_default LIKE 'nextval%'
    )
    LOOP
        EXECUTE format('SELECT setval(pg_get_serial_sequence(%L, %L), (SELECT COALESCE(MAX(%I), 1) FROM %I))',
            r.table_name, r.column_name, r.column_name, r.table_name);
    END LOOP;
END \$\$;
"
```

---

### 16. Frontend Build Configuration

**Production frontend may have:**
- Different build optimizations
- Different environment variables
- Different base path/routing

**What to sync:**
Check `frontend/.env` or `frontend/.env.production`:
```powershell
Get-Content frontend/.env* 2>$null
```

**Common frontend env vars:**
```env
VITE_API_URL=http://localhost:8000/api/v2
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENVIRONMENT=development
```

**Action Required:**
Verify `frontend/.env` exists with correct values for local development.

---

### 17. Nginx/Reverse Proxy Configuration

**Production:** Traefik handles routing  
**Local:** Nginx in frontend container

**Check configuration:**
```powershell
# View Nginx config in frontend container
docker exec trading_nexus_frontend cat /etc/nginx/nginx.conf
```

**What to verify:**
- ✅ API proxy to backend (`/api` → `backend:8000`)
- ✅ Static file serving
- ✅ WebSocket upgrade headers (if using WS)

✅ **Already configured in** `frontend/Dockerfile` and Nginx config.

---

### 18. Database Connection Pooling

**Production settings:**
- Connection pool size
- Max connections
- Timeout settings

**What to sync:**
```env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
```

**Action Required:**
Check if these are defined in production:
```powershell
Select-String -Path "production_db_export/production_env_vars.json" -Pattern "POOL|CONNECTION|DATABASE"
```

Usually default values work fine for local development.

---

### 19. Monitoring & Observability

**Production may have:**
- Application Performance Monitoring (APM)
- Error tracking (Sentry)
- Log aggregation
- Metrics collection

**What to disable locally:**
```env
SENTRY_DSN=  # Leave empty to disable error reporting
APM_ENABLED=false
METRICS_ENABLED=false
```

**Action Required:** None - these should be disabled by default locally.

---

### 20. Instrument Master Data Updates

**Production:** Instrument master CSV updated periodically  

**Action Required:**
Ensure you have the latest CSV:
```powershell
# Download latest from DhanHQ or production
# Option 1: From production server
python -c "
import requests
COOLIFY_API_URL = 'https://coolify.tradingnexus.pro/api/v1'
COOLIFY_TOKEN = open('COOLIFY API.txt').read().strip()
APP_UUID = 'hpwwkcs'
# Execute command to get the CSV file
# (Add implementation if needed)
"

# For now, your existing file should work
ls instrument_master/
```

---

## 📝 COMPLETE SYNCHRONIZATION CHECKLIST

Use this checklist when setting up local environment:

### Core (Automated by scripts)
- [x] Docker images rebuilt
- [x] Database exported from production
- [x] Database imported to local
- [x] Environment variables synced
- [x] CORS origins configured for localhost
- [x] Market streams disabled (safe mode)
- [x] Log level set to DEBUG

### Additional Checks
- [ ] Verify all API keys present in `.env`
- [ ] Check for background job configurations
- [ ] Verify timezone settings if relevant
- [ ] Reset database sequences (run after import)
- [ ] Verify frontend `.env` file exists
- [ ] Check for Redis/cache dependencies
- [ ] Verify instrument master CSV is up-to-date
- [ ] Test WebSocket connections (if needed)
- [ ] Verify file upload directories (if applicable)
- [ ] Check rate limiting configuration

### Testing Verification
- [ ] Frontend loads at http://localhost
- [ ] Backend API responds at http://localhost:8000
- [ ] Can login with existing production users
- [ ] Can view orders/positions from production data
- [ ] Watchlists display correctly
- [ ] Ledger/P&L data matches production
- [ ] No errors in backend logs

---

## 🚀 Quick Verification Script

After running all setup scripts, run this comprehensive check:

```powershell
# Create verification script
@"
Write-Host "=== Trading Nexus Local Environment Verification ===" -ForegroundColor Cyan
Write-Host ""

# 1. Docker services
Write-Host "[1] Docker Services:" -ForegroundColor Yellow
docker compose ps

# 2. Database connectivity
Write-Host "`n[2] Database Test:" -ForegroundColor Yellow
docker exec trading_nexus_db psql -U postgres -d trading_nexus -c "SELECT COUNT(*) as user_count FROM users;"

# 3. Backend health
Write-Host "`n[3] Backend Health:" -ForegroundColor Yellow
curl http://localhost:8000/health

# 4. Frontend
Write-Host "`n[4] Frontend Status:" -ForegroundColor Yellow
curl -I http://localhost

# 5. Environment variables
Write-Host "`n[5] Critical Env Vars:" -ForegroundColor Yellow
Select-String -Path .env -Pattern "DHAN_CLIENT_ID|DB_PASSWORD|DISABLE_DHAN_WS"

# 6. Log check
Write-Host "`n[6] Recent Backend Logs:" -ForegroundColor Yellow
docker logs trading_nexus_backend --tail 10

Write-Host "`n=== Verification Complete ===" -ForegroundColor Green
"@ | Out-File -FilePath verify_local_setup.ps1

.\verify_local_setup.ps1
```

---

## 📞 Summary

**You asked: "What else needs to be synchronized that you may have overseen?"**

**Answer:** The automated scripts cover the essentials (Docker images, database, environment variables). The main additional items to verify are:

1. **API Keys** - Ensure all third-party service keys are in `.env`
2. **Database Sequences** - Reset after import to avoid ID conflicts
3. **Frontend Environment** - Verify `frontend/.env` exists
4. **Instrument Master CSV** - Ensure it's up-to-date
5. **Time Zone** - Set if market hours validation depends on it

Everything else is either:
- Already handled by the scripts ✅
- Not needed for local development ✅
- Production-specific (SSL, Traefik) and intentionally different ✅

The setup is **comprehensive and production-ready** for local testing! 🎉
