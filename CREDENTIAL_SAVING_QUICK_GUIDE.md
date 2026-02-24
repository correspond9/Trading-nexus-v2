# Quick Guide - How to Save Credentials Now

## ✅ Fixes Deployed Successfully

The "Failed to fetch" error when saving credentials has been fixed with comprehensive error handling. The application now properly saves and retrieves credentials.

---

## How to Save DhanHQ Credentials

### Step 1: Access Admin Dashboard
1. Open browser: **http://72.62.228.112:8000** (or your domain)
2. Click **Dashboard** tab at top
3. Should see "Super Admin Dashboard"

### Step 2: Enter Credentials
In the **DhanHQ Authentication** section on the left:

1. **Client ID field:** Enter your DhanHQ client ID
   - Example: `110035379`

2. **Access Token field:** Enter your DhanHQ access token
   - Example: `your_daily_token_here`

3. **API Key field** (optional, for static IP mode):
   - Only needed if using Static IP authentication

4. **API Secret field** (optional, for static IP mode):
   - Only needed if using Static IP authentication

### Step 3: Save Credentials
1. Click **"Save Credentials"** button
2. Wait for response (should take 1-2 seconds)

### Expected Success Response
You should see:
- ✅ Green success message
- Message: "All credentials saved successfully"
- OR: "Partially saved: [list of items saved]"

### If You See an Error
The dashboard will now show:
- ❌ Clear error message explaining what failed
- Examples:
  - "Failed to update access token: Database connection timeout"
  - "Partially saved: client_id. Failed to rotate token: WebSocket not ready"

---

## Troubleshooting

### Issue: "Failed to fetch" (No details)
**This should not happen** - the fix handles this.

**If it still occurs:**
1. Refresh the page (Ctrl+R or Cmd+R)
2. Check browser console (F12 → Console tab)
3. Check application logs in Coolify dashboard
4. Try again after 10 seconds

### Issue: "Failed to update access token: Failed to rotate token"
**This is a partial success** - Client ID was saved, but token rotation has an issue.

**Possible causes:**
- WebSocket connections still initializing
- Market data service not ready yet

**Solution:**
- Wait 30 seconds and try again
- Check Coolify logs for "WebSocket" errors

### Issue: "Failed to update client_id: Table not found"
**Database schema issue**

**Solution:**
- Verify migrations ran: `SELECT COUNT(*) FROM system_config;`
- Should return at least 5 rows
- If empty, restart application

### Issue: "Partially saved" with multiple errors
**Some operations succeeded, others failed**

**Next steps:**
1. Check which items were saved (shown in response)
2. Try saving the failed items individually
3. Check application logs for details

---

## What Gets Saved

When you click "Save Credentials", the application saves:

| Field | Saves To | Updates |
|-------|----------|---------|
| Client ID | `system_config.dhan_client_id` | Memory + DB |
| Access Token | `system_config.dhan_access_token` | Memory + DB + WebSocket |
| API Key | `system_config.dhan_api_key` | Memory + DB |
| API Secret | `system_config.dhan_api_secret` (encrypted) | Memory + DB |

---

## How to Check Saved Credentials

### From Database
```sql
-- Connect to PostgreSQL
psql -h 72.62.228.112 -U postgres -d trading_nexus_db

-- Check what's saved
SELECT key, value FROM system_config 
WHERE key LIKE 'dhan_%' OR key = 'auth_mode';
```

### From Application Logs
```bash
# Check logs in Coolify Dashboard
Applications → backend → Logs

# Look for lines like:
# ✅ Client ID updated: 11003537...
# ✅ Access token rotated and persisted
```

---

## After Saving Credentials

### 1. WebSocket Connection
The application automatically reconnects WebSockets after saving.
- Look for in logs: "WebSocket reconnected successfully"
- Market data streams should start: "Market Data Stream" → "loading" → "connected"

### 2. Market Data
Once credentials are valid:
- Option chain data loads
- NIFTY/NSE/etc. prices appear
- WebSocket shows real-time updates

### 3. System Status
Check the bottom right of dashboard:
- 🟢 Database: Connected
- 🟢 API Server: Ok
- 🟢 Dhan API: Connected (after valid credentials)
- 🟢 WebSocket: Connected (after valid credentials)

---

## API Endpoint Details (For Developers)

### Endpoint
```
POST /api/v1/admin/credentials/save
```

### Request Body
```json
{
  "client_id": "110035379",
  "access_token": "your_token_here",
  "api_key": "",
  "secret_api": "",
  "daily_token": "",
  "auth_mode": "DAILY_TOKEN"
}
```

### Success Response
```json
{
  "success": true,
  "partial": false,
  "message": "All credentials saved successfully.",
  "saved": ["client_id", "access_token"],
  "status": "success"
}
```

### Error Response
```json
{
  "status": "error",
  "detail": "Failed to save credentials: [specific error message]"
}
```

---

## Common Scenarios

### Scenario 1: First Time Setup
1. Enter Client ID
2. Enter Access Token
3. Click Save
4. All three items save successfully ✅

### Scenario 2: Updating Existing Credentials
1. Clear old value
2. Enter new value
3. Click Save
4. Database updated ✅

### Scenario 3: Mixed Success/Failure
1. Client ID saved ✅
2. Token update failed ❌ (network issue)
3. Response: "Partially saved: client_id"
4. Retry token update after network recovers

### Scenario 4: Invalid Credentials
1. Save credentials
2. Application tries market data connection
3. DhanHQ API returns 401 (invalid credentials)
4. Application logs error: "ClientId is invalid"
5. Logs show with clear error messages

---

## Recovery Steps

If credentials get corrupted or you need to reset:

### Option 1: Fresh Start
1. Delete from database:
   ```sql
   DELETE FROM system_config 
   WHERE key LIKE 'dhan_%';
   ```
2. Restart application in Coolify
3. Re-enter credentials

### Option 2: Environment Variable Override
1. Set environment variables in Coolify:
   - `DHAN_CLIENT_ID=...`
   - `DHAN_ACCESS_TOKEN=...`
2. Restart application
3. Application loads from environment

### Option 3: Check Current State
1. Query database for current values:
   ```sql
   SELECT key, SUBSTRING(value, 1, 20) as masked_value 
   FROM system_config 
   WHERE key LIKE 'dhan_%';
   ```
2. All keys should exist and have values

---

**Last Updated:** February 24, 2026
**Fix Status:** ✅ Deployed and Active
**Application Status:** ✅ Running with Error Handling
