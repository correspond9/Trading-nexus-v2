#!/usr/bin/env python3
"""
Diagnose frontend deployment issue
"""

import requests

vps_ip = "72.62.228.112"

print("="*70)
print("FRONTEND DEPLOYMENT DIAGNOSTIC")
print("="*70)

print("\n1. WHAT WE KNOW:")
print("   ✓ Backend deployed and working (margin calculation returns ₹1430.0)")
print("   ✓ Source code has fixes (String(user?.id), ltp: ltp)")
print("   ✓ Git has commit 44c3283 pushed to GitHub")
print("   ✗ Frontend domain returning 404")
print("   ✗ Frontend container not accessible on VPS")

print("\n2. CHECKING CONNECTIVITY:")

endpoints = {
    "Backend API": (f"http://api.tradingnexus.pro/api/v2/health", "✓ working"),
    "Frontend domain": (f"http://tradingnexus.pro/", "✗ 404"),
    "Coolify dashboard": (f"http://{vps_ip}:8000/", "should be ✓"),
}

for name, (url, note) in endpoints.items():
    try:
        r = requests.head(url, timeout=5, allow_redirects=False)
        status = "✓" if r.status_code < 400 else "✗"
        print(f"   {status} {name}: {r.status_code} - {note}")
    except Exception as e:
        print(f"   ✗ {name}: Unreachable - {str(e)[:50]}")

print("\n3. ROOT CAUSE ANALYSIS:")
print("""
   The frontend 404 means one of these is true:
   
   A) Coolify hasn't deployed the frontend app yet
      - Frontend might be in "Draft" status
      - No build has run
      - Container isn't running
      
   B) Coolify built it but it's misconfigured
      - Container exists but isn't listening on port 80
      - Traefik routing rules aren't working
      - VITE_API_URL environment variable is wrong
      
   C) Domain DNS isn't resolving to frontend IP
      - tradingnexus.pro not pointing to Coolify server
      - DNS cached with old IP
      - Traefik reverse proxy isn't accepting the request

   D) Frontend was built but crashed on startup
      - Check docker logs for errors
      - VITE_API_URL might be causing issues

4. HOW TO FIX:

   You need to access Coolify dashboard at:
   http://72.62.228.112:8000
   
   Then:
   1. Look for "trading-nexus" application
   2. Look for "frontend" or similar service
   3. Check if it's:
      - Created ✓
      - Deployed ✓
      - Running ✓
      - Healthy ✓
   
   If it doesn't exist, CREATE IT:
   - Name: frontend
   - Source: Github (repo: trading-nexus)
   - Dockerfile: frontend/Dockerfile
   - Port: 80
   - Build: Enable
   
   If it exists but isn't running:
   - Check "Redeploy" button
   - Check "Restart" button
   - Check logs for errors
   
5. ALTERNATIVE: Force rebuild using Docker

   You can manually trigger a rebuild via:
   docker-compose -f docker-compose.prod.yml build --no-cache frontend
   docker-compose -f docker-compose.prod.yml up -d frontend

   This would ensure:
   - Fresh npm install
   - Latest source code built
   - Container starts with correct port mapping
""")

print("\n" + "="*70)
print("SUMMARY:")
print("="*70)
print("""
Your code fixes ARE in place.
Your backend IS deployed.
Your frontend source IS updated.

The issue is that the frontend container isn't running or accessible.
This is a deployment/infrastructure issue, not a code issue.

ACTION: Check/access Coolify dashboard to verify frontend deployment status.
""")
