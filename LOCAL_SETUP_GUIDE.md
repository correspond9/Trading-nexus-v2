# Trading Nexus - Local Development Environment Setup

This guide will help you recreate your exact production environment locally for testing features without VPS restrictions.

## 📋 Overview

You'll be setting up:
- ✅ Fresh Docker images (backend + frontend)  
- ✅ Complete production database with all data
- ✅ Synchronized configuration and settings
- ✅ Production-like startup behavior, with streams routed to local `mockdhan`

## 🚀 Quick Start - Run Scripts in Order

All scripts are automated - just run them one by one:

### Step 1: Rebuild Docker Images
```powershell
.\local_setup_1_rebuild_docker.ps1
```
**What this does:**
- Stops existing containers
- Removes old images
- Builds fresh backend and frontend images
- Takes ~5-10 minutes

### Step 2: Export Production Database
```powershell
.\local_setup_2_export_production_db.ps1
```
**What this does:**
- Connects to production via Coolify API
- Exports complete database dump
- Saves all table data to `production_db_export/`
- Takes ~2-5 minutes depending on data size

### Step 3: Import to Local Database
```powershell
.\local_setup_3_import_to_local.ps1
```
**What this does:**
- Starts local PostgreSQL container
- Imports production data
- Verifies all tables
- Takes ~5 minutes

### Step 4: Sync Configuration
```powershell
.\local_setup_4_sync_config.ps1
```
**What this does:**
- Fetches production environment variables
- Creates local `.env` file
- Keeps stream startup ON but routes REST/WS endpoints to `mockdhan`
- Sets debug logging
- Takes ~1 minute

### Step 5: Start and Verify
```powershell
.\local_setup_5_start_and_verify.ps1
```
**What this does:**
- Starts all services (DB, backend, frontend)
- Runs health checks
- Tests API connectivity
- Shows data summary
- Takes ~2-3 minutes

## ✅ What Gets Synchronized

### 1. Docker Images ✓
- Backend (FastAPI + Python dependencies)
- Frontend (React + Nginx)

### 2. Databases ✓
All production tables including:
- **Users & Auth**: `users`, `user_sessions`, `portal_users`
- **Trading**: `paper_orders`, `paper_positions`, `paper_trades`
- **Financial**: `ledger_entries`, `payout_requests`, `brokerage_plans`
- **Market Data**: `instrument_master`, `subscription_state`
- **Watchlists**: `watchlists`, `watchlist_items`
- **Baskets**: `basket_orders`, `basket_order_legs`
- **Margin Data**: All SPAN margin caches
- **System**: All configuration and logs

### 3. Configuration Files ✓
- Environment variables (`.env`)
- DhanHQ credentials
- Feature flags
- Database connection strings
- CORS settings

### 4. Static Data ✓
- Instrument master CSV files
- Migration scripts

## 🔐 Safety Features

Your local environment is **completely isolated**:

✅ **Market streams routed to local mockdhan** - Won't interfere with production  
✅ **Local database** - Changes don't affect production  
✅ **Separate Docker network** - No cross-contamination  
✅ **Debug logging enabled** - Better troubleshooting  

## ⚠️ Important Notes

### DhanHQ Credentials
The scripts do not require live Dhan credentials locally because:
- Local stream source is `mockdhan`
- No connection to DhanHQ is made locally
- This keeps production credentials isolated
- Local environment remains safe and reproducible

If you need to test live market data connections:
1. Manually add credentials to `.env`
2. Enable streams: `DISABLE_DHAN_WS=false`, `DISABLE_MARKET_STREAMS=false`
3. Restart: `docker compose restart backend`

### Database Size
If your production database is large (>1GB), the export/import may take longer. The scripts handle this automatically.

### Market Data Streams
By default, market data streams are **ENABLED locally** but pointed to `mockdhan`.
This preserves production-like behavior without touching live Dhan connections.

## 📊 After Setup - Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost | React app UI |
| Backend API | http://localhost:8000 | FastAPI endpoints |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Database | localhost:5432 | PostgreSQL direct access |

### Database Access
- **Host**: localhost
- **Port**: 5432
- **User**: postgres
- **Password**: postgres123 (from `.env`)
- **Database**: trading_nexus

## 🔧 Useful Commands

```powershell
# View live logs from all services
docker compose logs -f

# View logs from specific service
docker compose logs -f backend

# Stop all services
docker compose down

# Restart specific service
docker compose restart backend

# Check service status
docker compose ps

# Connect to database directly
docker exec -it trading_nexus_db psql -U postgres -d trading_nexus
```

## 🐛 Troubleshooting

### Services won't start
```powershell
# Check Docker Desktop is running
docker info

# View detailed logs
docker compose logs

# Restart everything
docker compose down
docker compose up -d
```

### Database import fails
```powershell
# Check database is running
docker compose ps db

# Try manual import
docker compose up -d db
# Wait 30 seconds
docker cp production_db_export/production_dump_*.sql trading_nexus_db:/tmp/dump.sql
docker exec trading_nexus_db psql -U postgres -d trading_nexus -f /tmp/dump.sql
```

### Backend API not responding
```powershell
# Check backend health
docker logs trading_nexus_backend --tail 50

# Check .env file has required variables
cat .env | Select-String "DHAN_CLIENT_ID"

# Restart backend
docker compose restart backend
```

## 🔄 Updating Local Environment

To sync latest production data again:

```powershell
# Re-export production DB
.\local_setup_2_export_production_db.ps1

# Re-import to local
docker compose down
.\local_setup_3_import_to_local.ps1

# Restart services
docker compose up -d
```

## 📝 What's Different from Production?

| Aspect | Production | Local |
|--------|-----------|-------|
| Database | Remote PostgreSQL | Local Docker container |
| Domain | tradingnexus.pro | localhost |
| SSL/TLS | Enabled (Traefik) | Disabled |
| Market Streams | Enabled (DhanHQ) | Enabled (mockdhan) |
| Log Level | WARNING | DEBUG |
| CORS | Specific domains | localhost only |

## 🎯 Testing Workflow

1. **Make code changes** in your editor
2. **Rebuild** affected service:
   ```powershell
   docker compose build backend
   docker compose up -d backend
   ```
3. **Test** your changes at http://localhost:8000/docs
4. **Check logs**: `docker compose logs -f backend`
5. **Iterate** until satisfied
6. **Deploy to production** when ready (separate process)

## 📚 Additional Resources

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## ✨ Summary

After running all 5 scripts, you'll have:
- ✅ Complete local replica of production
- ✅ All users, orders, positions, and data
- ✅ Isolated testing environment
- ✅ Fast iteration without VPS restrictions
- ✅ Safe environment (won't affect production)

Now you can test features freely, make changes, and deploy confident that everything works! 🚀
