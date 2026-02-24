# DEPLOYMENT INSTRUCTIONS - Force Exit Endpoint

## Current Status

### ✅ Completed
1. **Case-Insensitive Lookup (Commit 0bac2a7)**
   - Status: ✅ DEPLOYED to production
   - Enables: "Lenskart Solutions" search works regardless of case
   - Verified: Via API tests (test_exact_case.py, test_browser_data.py)

2. **Force Exit Endpoint (Commit 482a4f2)**
   - Status: ✅ READY TO DEPLOY
   - File: `app/routers/admin.py` lines 1679-1759
   - Functionality: Admin can close any user's open position

### ⏳ REQUIRED: Manual Coolify Deployment

**IMPORTANT**: Coolify does NOT auto-deploy. You MUST deploy manually.

### Deployment Steps

#### Step 1: Deploy the code via Coolify
1. Open https://tradingnexus.pro/coolify (your Coolify dashboard)
2. Navigate to the trading-nexus application
3. Click "Deploy" or "Redeploy" button
4. Wait for deployment to complete (check logs for `uvicorn` startup)
5. Verify: Open https://tradingnexus.pro/dashboard and ensure dashboard loads

#### Step 2: Run the Post-Deployment Fix Script
Once deployment is confirmed, run this on your local machine:

```bash
cd d:\4.PROJECTS\FRESH\trading-nexus
python post_deployment_fix.py
```

This script will:
- Login as admin (9999999999/123456)
- Find and close user 1003's existing LENSKART position
- Create the new LENSKART SOLUTIONS position (580 qty @ 380.70)

#### Step 3: Verify in Browser
1. Go to https://tradingnexus.pro/dashboard
2. Go to "Users" tab  
3. Search for user "1003"
4. Check "Position" column - should show:
   - Symbol: Lenskart Solutions
   - Qty: 580
   - Entry Price: 380.70
   - Entry Date: 2026-02-20

---

## What Changed

### Force Exit Endpoint Implementation
**Location**: `app/routers/admin.py:1679-1759`

```python
@router.post("/admin/force-exit")
```

**Parameters**:
- `user_id`: User mobile or UUID
- `position_id`: Position UUID or ID
- `exit_price`: Exit price for the position

**Response**:
```json
{
  "success": true,
  "message": "Position closed at 380.70",
  "position_id": "...",
  "symbol": "Lenskart Solutions",
  "quantity": 580,
  "exit_price": 380.70
}
```

### Why This Was Needed
1. Original issue: User 1003 already had an open LENSKART position from earlier attempt
2. Cannot create new position while one is open
3. Force-exit stub in original code didn't work
4. Now admins can forcefully close positions via the Force Exit Position form

---

## Testing the Endpoints Manually (After Deployment)

### 1. Login as Admin
```bash
curl -X POST https://tradingnexus.pro/api/v2/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"mobile":"9999999999","password":"123456"}'
```

### 2. Get User Positions
```bash
curl -X GET https://tradingnexus.pro/api/v2/admin/positions/userwise \
  -H "X-AUTH: <token_from_step1>"
```

### 3. Force Exit Position
```bash
curl -X POST https://tradingnexus.pro/api/v2/admin/force-exit \
  -H "X-AUTH: <token>" \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "1003",
    "position_id": "<position_id_from_step2>",
    "exit_price": 380.70
  }'
```

### 4. Create New Position  
```bash
curl -X POST https://tradingnexus.pro/api/v2/admin/backdate-position \
  -H "X-AUTH: <token>" \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "1003",
    "symbol": "Lenskart Solutions",
    "qty": 580,
    "price": 380.70,
    "trade_date": "2026-02-20",
    "instrument_type": "EQ",
    "exchange": "NSE"
  }'
```

---

## Summary: Case-Insensitive Fix ✅ + Force Exit ✨

| Feature | Status | Evidence |
|---------|--------|----------|
| Case-insensitive "Lenskart Solutions" lookup | ✅ DEPLOYED | test_exact_case.py: SUCCESS |
| Creates position via API | ✅ WORKING | test_browser_data.py: SUCCESS |
| Creates position via browser form | ⏳ BLOCKED | Existing position for user 1003 |
| Force exit endpoint implementation | ✅ CODED | app/routers/admin.py:1679-1759 |
| Force exit deployment | ⏳ PENDING | Requires manual Coolify deploy |
| Create new position (final test) | ⏳ PENDING | After force exit + deployment |

---

## Next Actions For User

1. **DEPLOY**: Go to Coolify and click deploy (code is ready)
2. **RUN SCRIPT**: Execute `python post_deployment_fix.py` 
3. **VERIFY**: Check dashboard to confirm position created

The case-insensitive fix is already live! 🎉
