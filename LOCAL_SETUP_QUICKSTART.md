# 🚀 Quick Start - Local Development Environment

## What I Created for You

I've built a **complete automated setup system** to recreate your exact production environment locally. Everything is automated - you just run the scripts!

---

## 📦 What You Get

### ✅ Automated Scripts (5 Steps)
1. **`local_setup_1_rebuild_docker.ps1`** - Rebuilds Docker images
2. **`local_setup_2_export_production_db.ps1`** - Exports production database
3. **`local_setup_3_import_to_local.ps1`** - Imports to local PostgreSQL
4. **`local_setup_4_sync_config.ps1`** - Syncs all configuration
5. **`local_setup_5_start_and_verify.ps1`** - Starts and verifies everything

### ✅ Master Script (All-in-One)
- **`local_setup_complete.ps1`** - Runs all 5 steps automatically!

### ✅ Documentation
- **`LOCAL_SETUP_GUIDE.md`** - Complete guide with explanations
- **`LOCAL_SETUP_SYNCHRONIZATION_CHECKLIST.md`** - Comprehensive checklist of what gets synced

---

## 🎯 EASIEST WAY - One Command Setup

```powershell
.\local_setup_complete.ps1
```

**That's it!** This will:
- ✅ Rebuild your Docker images
- ✅ Export production database via Coolify API
- ✅ Import all data to local PostgreSQL
- ✅ Configure environment variables
- ✅ Start all services
- ✅ Verify everything works

**Time:** ~20 minutes total

---

## 📝 Alternative: Step-by-Step Manual

If you prefer to run steps individually:

```powershell
# Step 1: Rebuild Docker images (~5 min)
.\local_setup_1_rebuild_docker.ps1

# Step 2: Export production DB (~3 min)
.\local_setup_2_export_production_db.ps1

# Step 3: Import to local (~5 min)
.\local_setup_3_import_to_local.ps1

# Step 4: Sync configuration (~1 min)
.\local_setup_4_sync_config.ps1

# Step 5: Start & verify (~3 min)
.\local_setup_5_start_and_verify.ps1
```

---

## 💡 Your Questions - Answered

### 1️⃣ "Rebuild the Docker image"
**Answer:** ✅ Done by `local_setup_1_rebuild_docker.ps1`

- Stops old containers
- Removes outdated images
- Builds fresh backend + frontend images
- Uses latest code from your repository

### 2️⃣ "Import databases from production"
**Answer:** ✅ Done by `local_setup_2` + `local_setup_3`

**All these tables are imported:**
- ✅ `users` - All user accounts
- ✅ `user_sessions` - Login sessions
- ✅ `paper_orders` - All orders
- ✅ `paper_positions` - All positions
- ✅ `paper_trades` - Trade history
- ✅ `ledger_entries` - All financial transactions
- ✅ `watchlists` + `watchlist_items` - User watchlists
- ✅ `basket_orders` + `basket_order_legs` - Basket orders
- ✅ `brokerage_plans` - Pricing plans
- ✅ `instrument_master` - All instruments
- ✅ `span_margin_cache` - Margin data
- ✅ `payout_requests` - Payout history
- ✅ And 20+ more tables...

**How it works:**
- Connects to your production server via Coolify API
- Runs `pg_dump` to export complete database
- Saves to `production_db_export/` folder
- Imports into your local PostgreSQL container

### 3️⃣ "What else needs synchronization?"
**Answer:** ✅ Everything covered! See detailed list below.

**Configuration synced:**
- ✅ Environment variables (database config, feature flags)
- ✅ Feature flags (market streams DISABLED for safety)
- ✅ CORS settings (set to localhost)
- ✅ Log levels (DEBUG for local dev)
- ✅ Database connection strings
- ❌ DhanHQ credentials (NOT needed - streams disabled)

**Static files:**
- ✅ Instrument master CSV files
- ✅ Database migration scripts

**What's different (intentionally):**
- ❌ SSL/TLS certificates (not needed locally)
- ❌ Traefik configuration (using simple Nginx)
- ❌ Production domains (using localhost)
- ❌ Market data streams (DISABLED to prevent conflicts)

See **`LOCAL_SETUP_SYNCHRONIZATION_CHECKLIST.md`** for complete details.

---

## 🎨 What Your Local Environment Looks Like

```
┌─────────────────────────────────────────────────────┐
│                   localhost                         │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  Frontend   │  │   Backend   │  │ PostgreSQL │ │
│  │   (React)   │  │  (FastAPI)  │  │   (DB)     │ │
│  │             │  │             │  │            │ │
│  │  Port 80    │  │  Port 8000  │  │  Port 5432 │ │
│  └─────────────┘  └─────────────┘  └────────────┘ │
│                                                     │
│  Docker Network: trading_nexus_network              │
└─────────────────────────────────────────────────────┘
```

**Access points:**
- Frontend: `http://localhost`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Database: `localhost:5432`

---

## 🔒 Safety Features

Your local environment is **completely isolated from production**:

✅ **Separate database** - Changes don't affect production  
✅ **Market streams DISABLED** - Won't interfere with live trading  
✅ **Local Docker network** - No network conflicts  
✅ **Debug logging** - Catch issues early  
✅ **No outbound DhanHQ connections** - Safe testing mode  

---

## 📊 After Setup - What You Can Do

✅ **Test with real data** - All production users, orders, positions  
✅ **Develop new features** - Full production-like environment  
✅ **Debug issues** - Reproduce production bugs locally  
✅ **Run migrations** - Test database changes safely  
✅ **API testing** - Interactive docs at `/docs`  
✅ **Performance testing** - Realistic data volumes  

---

## 🛠️ Daily Workflow

```powershell
# Make code changes in your editor
# ...

# Rebuild affected service
docker compose build backend
docker compose up -d backend

# View logs
docker compose logs -f backend

# Test your changes
# Visit http://localhost:8000/docs

# Iterate until satisfied

# When ready, deploy to production
# (separate deployment process via Coolify)
```

---

## 🔄 Keeping Local in Sync

To refresh with latest production data:

```powershell
# Re-export production DB
.\local_setup_2_export_production_db.ps1

# Stop local services
docker compose down

# Re-import fresh data
.\local_setup_3_import_to_local.ps1

# Restart
docker compose up -d
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **LOCAL_SETUP_QUICKSTART.md** | This quick start guide |
| **LOCAL_SETUP_GUIDE.md** | Complete guide with explanations |
| **LOCAL_SETUP_SYNCHRONIZATION_CHECKLIST.md** | Detailed sync checklist |

---

## 🆘 Troubleshooting

### Docker not running?
```powershell
# Check Docker Desktop is running
docker info
# If not, start Docker Desktop from Start Menu
```

### Services won't start?
```powershell
# View detailed logs
docker compose logs

# Restart everything
docker compose down
docker compose up -d
```

### Database import fails?
```powershell
# Ensure DB is running
docker compose up -d db
Start-Sleep -Seconds 30

# Try import again
.\local_setup_3_import_to_local.ps1
```

### Backend API not responding?
```powershell
# Check backend logs
docker logs trading_nexus_backend --tail 50

# Verify .env file
cat .env

# Restart backend
docker compose restart backend
```

---

## ✨ Summary

**You asked for:**
1. ✅ Docker image rebuild
2. ✅ Database import from production
3. ✅ What else needs synchronization

**I delivered:**
- ✅ 5 automated scripts (step-by-step)
- ✅ 1 master script (all-in-one)
- ✅ Complete documentation
- ✅ Safety features (streams disabled)
- ✅ Verification checks
- ✅ Troubleshooting guides

**Just run:**
```powershell
.\local_setup_complete.ps1
```

**And you're done!** 🎉

Your exact production environment will be running locally in ~20 minutes, ready for testing without any VPS restrictions!

---

## 🎯 Next Steps

1. **Run the setup:**
   ```powershell
   .\local_setup_complete.ps1
   ```

2. **Access your local app:**
   - Open http://localhost in browser
   - Login with production credentials
   - Start testing!

3. **Develop & test:**
   - Make code changes
   - Test locally
   - Deploy when ready

**Happy coding! 🚀**
