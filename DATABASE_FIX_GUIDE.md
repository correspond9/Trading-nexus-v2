# Database Fix Instructions for Production

## Problem
- Cannot create users (HTTP 500 error)
- Cannot load existing users  
- Cannot save themes
- Database queries failing

## Root Cause
Database schema is incomplete or migrations didn't run properly during deployment.

## Solution Options

### Option 1: Quick Fix via Coolify Dashboard (EASIEST)

1. **Open Coolify**: http://72.62.228.112:8000
2. **Navigate to**: Applications → Trading Backend
3. **Click**: Terminal / Execute Command
4. **Run these commands** one by one:

```bash
# Stop backend
docker stop trading-nexus-backend-1

# Reset database
docker exec trading-nexus-db-1 psql -U postgres -c "DROP DATABASE IF EXISTS trading_terminal; CREATE DATABASE trading_terminal;"

# Start backend (migrations run automatically)
docker start trading-nexus-backend-1

# Wait 30 seconds
sleep 30

# Check logs
docker logs trading-nexus-backend-1 --tail 50
```

5. **Test**: Visit https://tradingnexus.pro and login with `9999999999` / `admin123`

---

### Option 2: Via SSH (if you have command line access)

**From your local computer (Windows PowerShell):**

```powershell
# Run the PowerShell script
.\Reset-ProductionDB.ps1
```

**OR manually via SSH:**

```bash
ssh root@72.62.228.112

# Then run:
docker stop trading-nexus-backend-1
docker exec trading-nexus-db-1 psql -U postgres -c "DROP DATABASE IF EXISTS trading_terminal; CREATE DATABASE trading_terminal;"
docker start trading-nexus-backend-1
docker logs trading-nexus-backend-1 --tail 50
```

---

### Option 3: Run migration scripts

**If you want to try migrations first without deleting data:**

```bash
# Make scripts executable
chmod +x run_migrations.sh

# Run migrations
./run_migrations.sh
```

**If that doesn't work, do complete reset:**

```bash
# Make script executable
chmod +x reset_production_database.sh

# Run reset
./reset_production_database.sh
```

---

## What These Commands Do

1. **Stop backend**: Prevents connections during reset
2. **Drop & Create database**: Fresh clean database
3. **Start backend**: 
   - App starts
   - Connects to database  
   - Runs all 23 migrations automatically
   - Creates 4 demo users
4. **Logs check**: Verify migrations completed

---

## After Reset - Default Users

| Mobile      | Password  | Role        |
|-------------|-----------|-------------|
| 9999999999  | admin123  | SUPER_ADMIN |
| 8888888888  | admin123  | ADMIN       |
| 6666666666  | super123  | SUPER_USER  |
| 7777777777  | user123   | USER        |

---

## Verification Steps

After running the fix:

1. **Login** to https://tradingnexus.pro
2. **Go to** Users page
3. **Should see** 4 users listed
4. **Try creating** a new user
5. **Try changing** theme (should save successfully)
6. **Check** margin calculations display properly

---

## If Still Not Working

Check the backend logs for specific errors:

```bash
docker logs trading-nexus-backend-1 --tail 100
```

Look for:
- Database connection errors
- Migration failures
- Python exceptions

Share the error output for further diagnosis.

---

## Database Schema Info

The fresh database will have these tables:
- `users` - User accounts
- `paper_accounts` - Wallet balances  
- `positions` - Trading positions
- `ledger_entries` - Transaction history
- `payout_requests` - Withdrawal requests
- `baskets` - Saved baskets
- `theme_presets` - Custom themes
- `span_margin_cache` - Margin calculations
- Plus 15+ other tables

All created automatically by migrations on startup.
