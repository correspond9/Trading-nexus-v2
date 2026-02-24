================================================================================
TRADING NEXUS - DEPLOYMENT & TESTING GUIDE
================================================================================

SITUATION:
- New instrument search code has been committed and pushed to GitHub main
- Backend container was restarted but still has old Docker image
- Docker images layer code, so restarting doesn't get new source code
- Need to rebuild the Docker image to pick up changes from git

================================================================================
SOLUTION #1: MANUAL REBUILD VIA COOLIFY UI (Recommended)
================================================================================

1. Open Coolify web interface: https://72.62.228.112:3000
2. Navigate to Applications > trade-nexus-v2-production
3. Look for a "Redeploy" or "Build" button
4. Click to trigger a full rebuild and redeployment
5. Wait 2-3 minutes for rebuild to complete
6. Backend will automatically restart with new code

After rebuild, test with:
  curl http://72.62.228.112:8000/api/v2/instruments/search?q=RELIANCE

Should return JSON array with results.

================================================================================
SOLUTION #2: FORCE REBUILD VIA SSH (If UI unavailable)  
================================================================================

SSH to VPS and run:

cd /opt/coolify/applications/p488ok8g8swo4ockks040ccg
docker-compose down
docker-compose up -d --build

This will:
- Stop all containers
- Rebuild Docker images from latest source
- Start containers with new code
- Run migrations if needed

Wait 3-5 minutes for startup.

================================================================================
SOLUTION #3: WORKAROUND - USE TEST INSTRUMENTS
================================================================================

While waiting for rebuild, test with instruments that definitely exist:

Suggested test data:
  - User ID: 9326890165 (mobile - exists in DB)
  - Symbol: RELIANCE (most common stock)
  - Qty: 100
  - Price: 4200.00
  - Trade Date: 2026-02-20
  - Instrument Type: Equity (EQ)
  - Exchange: NSE

The form now has AUTO-COMPLETE that will show suggestions as you type.
Just type "REL" and click on RELIANCE from the dropdown.

This will:
✅ Test the form submission
✅ Test authentication
✅ Test the database position creation
⚠️ NOT test the search endpoint (but form validation will work)

================================================================================
WHAT WAS FIXED
================================================================================

1. ✅ Backend search endpoint (/instruments/search)
   - Now accepts `limit` parameter
   - Returns array directly instead of wrapped in `{data: [...]}`

2. ✅ Frontend search handling
   - Correctly extracts results from response
   - Shows dropdown with matching instruments
   - Auto-fills other fields when you click a suggestion

3. ✅ Backdate position form
   - Already had all functionality  
   - Now has searchable instrument list
   - User-friendly UI with proper styling

================================================================================
CODE CHANGES MADE
================================================================================

Files modified:
- app/routers/search.py: Fixed endpoint to accept `limit` parameter
- frontend/src/pages/SuperAdmin.jsx: Fixed to handle response correctly

Commit: 7e10645
GitHub: https://github.com/correspond9/Trading-nexus-v2.git

================================================================================
NEXT STEPS
================================================================================

1. Rebuild application (see Solution #1 or #2 above)
2. Wait 3-5 minutes for rebuild
3. Test: python test_search_fix.py
4. If search returns results, try backdate position form
5. Use dropdown suggestions to select instrument

Once rebuilt, the form will show:
- Live search as you type
- Dropdown with matching stocks
- Exchange and type auto-filled
- Easy position creation

================================================================================
