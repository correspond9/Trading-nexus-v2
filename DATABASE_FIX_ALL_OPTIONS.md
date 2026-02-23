# 🚀 DATABASE FIX - ALL OPTIONS

## ✅ Option 1: Coolify Web Terminal (EASIEST)

### Steps:
1. **Open**: http://72.62.228.112:8000
2. **Login** with your Coolify credentials
3. **Navigate to**: Applications → Backend App → Terminal
4. **Paste this command**:

```bash
BACKEND=$(docker ps --format '{{.Names}}' | grep -iE 'j0sk408|backend' | grep -v frontend | head -1) && DB=$(docker ps --format '{{.Names}}' | grep -iE 'j0sk408.*db|postgres' | head -1) && echo "Backend: $BACKEND" && echo "Database: $DB" && docker stop $BACKEND && docker exec $DB psql -U postgres -c "DROP DATABASE IF EXISTS trading_terminal; CREATE DATABASE trading_terminal;" && docker start $BACKEND && echo "Waiting 30 seconds..." && sleep 30 && docker logs $BACKEND --tail 50
```

5. **Wait**: ~30 seconds
6. **Test**: https://tradingnexus.pro (login: 9999999999 / admin123)

---

## ✅ Option 2: SSH Direct Access

### Steps:
1. **From your local PowerShell**:
```powershell
ssh root@72.62.228.112
```

2. **Once connected, run**:
```bash
# Check container names first
docker ps --format '{{.Names}}'

# Run the fix
BACKEND=$(docker ps --format '{{.Names}}' | grep -iE 'j0sk408|backend' | grep -v frontend | head -1) && DB=$(docker ps --format '{{.Names}}' | grep -iE 'j0sk408.*db|postgres' | head -1) && echo "Backend: $BACKEND" && echo "Database: $DB" && docker stop $BACKEND && docker exec $DB psql -U postgres -c "DROP DATABASE IF EXISTS trading_terminal; CREATE DATABASE trading_terminal;" && docker start $BACKEND && sleep 30 && docker logs $BACKEND --tail 50
```

---

## ✅ Option 3: Manual (If container names are known)

### If you know the exact container names:

```bash
# Replace with your actual container names
BACKEND=your-backend-container-name
DB=your-db-container-name

# Stop backend
docker stop $BACKEND

# Reset database
docker exec $DB psql -U postgres -c "DROP DATABASE IF EXISTS trading_terminal; CREATE DATABASE trading_terminal;"

# Start backend (migrations run automatically)
docker start $BACKEND

# Wait for migrations
sleep 30

# Check logs
docker logs $BACKEND --tail 50

# Verify database
docker exec $DB psql -U postgres -d trading_terminal -c "SELECT user_no, mobile, role FROM users;"
```

---

## ✅ Option 4: Use the Script

### Upload and run the script:

```bash
# Make executable
chmod +x fix_database_coolify.sh

# Run it
./fix_database_coolify.sh
```

---

## 🔍 Common Container Name Patterns

Coolify typically names containers like:
- **Backend**: `<uuid>-j0sk408owsssswkwwk0kwwws` or `trading-nexus-backend-1`
- **Database**: `<uuid>-db-1` or `trading-nexus-db-1`  
- **Frontend**: `<uuid>-frontend` or `trading-nexus-frontend-1`

To find yours:
```bash
docker ps --format 'table {{.Names}}\t{{.Status}}'
```

---

## ✅ Expected Result

After successful reset:

```
✓ Backend container: <name>
✓ Database container: <name>
✓ Database dropped and recreated
✓ Backend started
✓ Migrations completed (23 files)
✓ 4 demo users created
```

---

## 🧪 Verification Steps

1. **Check logs show migrations**:
```bash
docker logs <backend-container> | grep -i migration
```

2. **Check users exist**:
```bash
docker exec <db-container> psql -U postgres -d trading_terminal -c "SELECT user_no, mobile, role FROM users ORDER BY user_no;"
```

Expected output:
```
 user_no |   mobile   |    role     
---------+------------+-------------
    1001 | 9999999999 | SUPER_ADMIN
    1002 | 8888888888 | ADMIN
    1003 | 6666666666 | SUPER_USER
    1004 | 7777777777 | USER
```

3. **Test web interface**:
   - Login: https://tradingnexus.pro
   - Credentials: 9999999999 / admin123
   - Check Users page shows 4 users
   - Try creating a new user
   - Try saving theme

---

## ❌ Troubleshooting

### If command fails with "No such container":

1. List all containers:
```bash
docker ps --format '{{.Names}}'
```

2. **SEND ME THE OUTPUT** and I'll give you exact commands

### If migrations don't run:

```bash
# Restart backend
docker restart <backend-container>

# Watch logs in real-time
docker logs -f <backend-container>
```

### If database errors persist:

```bash
# Check database is running
docker exec <db-container> psql -U postgres -c "\l"

# Check if trading_terminal exists
docker exec <db-container> psql -U postgres -d trading_terminal -c "SELECT version();"
```

---

## 📞 Need Help?

**Send me the OUTPUT of**:
```bash
docker ps --format '{{.Names}}'
```

And I'll provide exact, customized commands for your setup!

---

## ⏱️ Total Time: ~2 minutes
- Command execution: 5 seconds
- Migration wait: 30 seconds  
- Verification: 1 minute
