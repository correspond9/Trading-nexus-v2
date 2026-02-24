# TRADING NEXUS - COMPLETE ENVIRONMENT VARIABLES
## For Coolify Deployment

### Application Details
- **Project**: My first project
- **Application**: trading-nexus-v2:main-q808cc0w88wcs488o4wwgoso
- **Repository**: https://github.com/correspond9/Trading-nexus-v2.git
- **Branch**: main

---

## 1. DATABASE CONFIGURATION

```
DATABASE_URL=postgresql://postgres:postgres@db:5432/trading_nexus_db
```

**Notes:**
- Host: `db` (internal Docker network name for PostgreSQL service)
- Port: `5432` (PostgreSQL default)
- Database: `trading_nexus_db`
- User: `postgres`
- Password: Change from `postgres` to a strong password (you can update this in Coolify)

---

## 2. REDIS CONFIGURATION (Optional, if using caching)

```
REDIS_URL=redis://redis:6379/0
```

**Notes:**
- Host: `redis` (internal Docker network name)
- Port: `6379` (Redis default)
- Optional database number: `0`

---

## 3. DHAN HQ AUTHENTICATION

### Option A: Auto-TOTP Mode (Recommended)
```
DHAN_CLIENT_ID=<your_dhan_client_id>
DHAN_ACCESS_TOKEN=<your_dhan_access_token>
DHAN_TOKEN_EXPIRY=<expiry_timestamp>
AUTH_MODE=auto_totp
```

### Option B: Static IP Mode (if using static IP credentials)
```
DHAN_CLIENT_ID=<your_dhan_client_id>
DHAN_API_KEY=<your_dhan_api_key>
DHAN_CLIENT_SECRET=<your_dhan_client_secret>
AUTH_MODE=static_ip
```

**Notes:**
- Get these from your DhanHQ account settings
- Keep these values SECRET - don't commit to git
- AUTH_MODE determines which authentication method to use
- DHAN_TOKEN_EXPIRY can be left empty initially

---

## 4. CORS AND API CONFIGURATION

```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://tradingnexus.pro,https://www.tradingnexus.pro
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=*
```

**Notes:**
- Include all domains that will access the backend API
- http://localhost:3000 for local frontend development
- https://tradingnexus.pro for production domain
- Allow credentials needed for auth cookies

---

## 5. SERVICE URLS (For Internal Communication)

```
SERVICE_URL_BACKEND=http://trading-nexus-backend:8000
SERVICE_URL_FRONTEND=http://trading-nexus-frontend:3000
VITE_API_BASE_URL=http://backend:8000
```

**Notes:**
- SERVICE_URL_BACKEND: Backend service endpoint (Docker internal)
- SERVICE_URL_FRONTEND: Frontend service endpoint (Docker internal)
- VITE_API_BASE_URL: Frontend env var for API endpoint
- Backend container name: `trading-nexus-backend`
- Frontend container name: `trading-nexus-frontend`

---

## 6. APPLICATION CONFIGURATION

```
TRADING_MODE=paper
GREEKS_POLL_INTERVAL_S=15
PAPER_DEFAULT_BALANCE=1000000
PAPER_SLIPPAGE_TICKS=1
PAPER_BROKERAGE_MODE=flat
PAPER_BROKERAGE_FLAT=20
```

**Notes:**
- TRADING_MODE: `paper` for paper trading, `live` for live trading
- GREEKS_POLL_INTERVAL_S: Seconds between Greeks updates (15 = 15 seconds)
- PAPER_DEFAULT_BALANCE: Starting balance for paper trading accounts (in Rupees)
- PAPER_BROKERAGE_MODE: `flat` (fixed fees), `custom` (custom %), or `zero`
- PAPER_BROKERAGE_FLAT: Fixed brokerage per trade (₹20)

---

## 7. OPTIONAL: LOGGING AND DEBUG

```
LOG_LEVEL=INFO
DEBUG=false
```

**Notes:**
- LOG_LEVEL: Can be DEBUG, INFO, WARNING, ERROR, CRITICAL
- DEBUG: Set to true only for development/troubleshooting

---

## 8. OPTIONAL: FRONTEND SPECIFIC (In frontend/.env or build args)

```
VITE_API_BASE_URL=/api/v2
VITE_APP_NAME=Trading Nexus
```

---

## COMPLETE VARIABLE SET FOR COPY-PASTE

Use **exactly** this for Coolify configuration panel:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/trading_nexus_db

# Redis  
REDIS_URL=redis://redis:6379/0

# DhanHQ (Choose ONE authentication method)
# --- Auto-TOTP Method ---
DHAN_CLIENT_ID=YOUR_DHAN_CLIENT_ID_HERE
DHAN_ACCESS_TOKEN=YOUR_DHAN_ACCESS_TOKEN_HERE
AUTH_MODE=auto_totp

# --- OR Static IP Method (uncomment if using) ---
# DHAN_API_KEY=YOUR_DHAN_API_KEY_HERE
# DHAN_CLIENT_SECRET=YOUR_DHAN_CLIENT_SECRET_HERE
# AUTH_MODE=static_ip

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://tradingnexus.pro,https://www.tradingnexus.pro
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=*

# Service URLs (Internal Docker)
SERVICE_URL_BACKEND=http://trading-nexus-backend:8000
SERVICE_URL_FRONTEND=http://trading-nexus-frontend:3000
VITE_API_BASE_URL=http://backend:8000

# Trading Configuration
TRADING_MODE=paper
GREEKS_POLL_INTERVAL_S=15
PAPER_DEFAULT_BALANCE=1000000
PAPER_SLIPPAGE_TICKS=1
PAPER_BROKERAGE_MODE=flat
PAPER_BROKERAGE_FLAT=20

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

---

## 🔑 MANDATORY vs OPTIONAL

### ✅ MANDATORY (Application won't start without these)
- `DATABASE_URL` - Database connection
- `AUTH_MODE` - Authentication method
- Either `DHAN_CLIENT_ID + DHAN_ACCESS_TOKEN` (auto-TOTP) or `DHAN_API_KEY + DHAN_CLIENT_SECRET` (static IP)

### ⚠️ STRONGLY RECOMMENDED
- `CORS_ORIGINS` - Required if frontend on different domain
- `SERVICE_URL_BACKEND` - If backend and frontend are separate services
- `VITE_API_BASE_URL` - For frontend to communicate with backend

### ✨ OPTIONAL (Have sensible defaults)
- `REDIS_URL` - Can work without Redis (uses in-memory caching)
- `TRADING_MODE` - Defaults to `paper`
- `LOG_LEVEL` - Defaults to `INFO`
- `DEBUG` - Defaults to `false`

---

## 🔐 SECURITY NOTES

**DON'T HARDCODE IN ENVIRONMENT VARIABLES:**
- DhanHQ credentials (store in Coolify Secrets instead)
- Database passwords (should be auto-generated by Coolify)
- API keys/secrets

**USE COOLIFY SECRETS FOR:**
1. DHAN_CLIENT_ID
2. DHAN_ACCESS_TOKEN
3. DHAN_API_KEY
4. DHAN_CLIENT_SECRET

**HOW TO IN COOLIFY UI:**
- Configuration → Environment Variables → Toggle "Is Secret" checkbox
- Mark sensitive variables with lock icon
- Coolify won't display them after saving

---

## 📝 STEP-BY-STEP COOLIFY CONFIGURATION

1. **Go to Coolify Dashboard**: http://72.62.228.112:8000
2. **Navigate**: Projects → "My first project" → Applications → "trading-nexus-v2:main-q808cc0w88wcs488o4wwgoso" → Configuration
3. **Click**: "Environment Variables" tab
4. **Add each variable:**
   - Click "+ Add" button
   - Enter variable name (e.g., `DATABASE_URL`)
   - Enter variable value
   - Toggle "Is Secret" for sensitive vars (DHAN credentials, passwords)
   - Click "Save"
5. **For Database Connection:**
   - **First**, ensure PostgreSQL service exists in same project
   - Coolify usually auto-injects `DATABASE_URL`
   - Verify it matches the pattern above

---

## 🚀 DEPLOYMENT CHECKLIST

Before I deploy, verify:

- [ ] PostgreSQL service created in project (if not, Coolify can create it)
- [ ] All MANDATORY variables are set
- [ ] DHAN credentials are valid (or marked as TODO to add later)
- [ ] CORS_ORIGINS includes your domain
- [ ] Application port is set to 8000 (FastAPI runs on 8000)

**READY TO DEPLOY?** 

Let me know when you've entered these variables in Coolify, and I'll trigger the deployment!

---

## ✅ AFTER DEPLOYMENT VALIDATION

Once deployment is complete:

```bash
# Test health endpoint (replace with your domain)
curl http://72.62.228.112:8000/health
# Expected: {"status":"ok","version":"1.0.0"}

# Check database
curl http://72.62.228.112:8000/api/v1/admin/health
# Should show database connected

# Verify migrations ran
# Login to Coolify → PostgreSQL → Connect → Query:
SELECT COUNT(*) FROM brokerage_plans;  -- Should be 12
```

---

**Questions?**
- Missing variable? → Check app/config.py in GitHub
- Unsure about a value? → I can help determine it
- Want different settings? → Let me know!

**Ready for deployment confirmation:**
1. ✅ Code fixes are in GitHub main
2. ✅ All migrations are idempotent  
3. ✅ Environment variables are ready (above)
4. ⏳ Waiting for you to input variables in Coolify UI

Once variables are set, I'll deploy!
