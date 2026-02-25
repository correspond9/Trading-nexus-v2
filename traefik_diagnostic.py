#!/usr/bin/env python3
"""
Traefik Routing Diagnostic - Check if the routing rules are actually applied
"""

import requests
import json

vps_ip = "72.62.228.112"

print("="*70)
print("TRAEFIK ROUTING DIAGNOSTIC")
print("="*70)

print("\n✓ DNS is correctly configured (verified: all domains → 72.62.228.112)")
print("✗ But requests to 72.62.228.112 return 404")
print("\nThis means: Traefik is running, but routing config might be wrong\n")

print("="*70)
print("POSSIBLE ISSUES:")
print("="*70)

issues = [
    {
        "Issue": "Traefik routing rule syntax",
        "Command added in recent commit": 'traefik.http.routers.tradingfrontend.rule=Host(`tradingnexus.pro`) || Host(`www.tradingnexus.pro`) || Host(`learn.tradingnexus.pro`)',
        "Why it might fail": "If Traefik was using old docker-compose before the update",
        "Fix": "Restart Traefik or redeploy via Coolify"
    },
    {
        "Issue": "Frontend container image not built",
        "Happens when": "docker-compose build never ran for frontend service",
        "Why recently": "Coolify might only rebuild when explicitly triggered",
        "Fix": "Trigger rebuild in Coolify dashboard"
    },
    {
        "Issue": "Frontend container not running",
        "Check with": "docker ps | grep frontend",
        "Why recently": "Container might have crashed when new Traefik rules were applied",
        "Fix": "Check docker logs <container_id> for errors"
    },
    {
        "Issue": "Traefik labels not properly formatted",
        "Syntax": 'traefik.http.routers.tradingfrontend.rule=Host(...)',
        "If syntax wrong": "Traefik will ignore the label silently - no error",
        "Check in": "/etc/traefik/traefik.yml or docker inspect"
    },
]

for i, issue in enumerate(issues, 1):
    print(f"\n{i}. {issue.get('Issue', 'Unknown')}")
    for key, value in issue.items():
        if key != 'Issue':
            print(f"   {key}: {value}")

print("\n" + "="*70)
print("TO IDENTIFY THE ACTUAL PROBLEM:")
print("="*70)

print("""
You need to SSH into VPS (72.62.228.112) or access Coolify dashboard:

OPTION A: Via SSH (if you have credentials):
──────────────────────────────────────────
1. docker ps 
   → Check if "frontend" container is running
   
2. docker inspect <container_name> | grep -i traefik
   → See what Traefik routing rules are applied
   
3. docker logs <frontend_container_id>
   → See if container crashed on startup
   
4. docker network inspect coolify
   → See if container is on correct network
   

OPTION B: Via Coolify Dashboard:
────────────────────────────────
1. Go to http://72.62.228.112:8000
2. Login (you need credentials)
3. Find "trading-nexus" application
4. Look for "frontend" service:
   - Status: Running? Exited? Draft?
   - Logs: Any errors?
   - Build: When was it last built?
5. Click "Rebuild" or "Restart" if needed


OPTION C: Check Traefik Configuration:
──────────────────────────────────────
1. Access Traefik dashboard (if exposed):
   http://72.62.228.112:8080/dashboard/
   
2. Look for routers:
   - tradingfrontend should be there
   - Should have status "UP"
   - Should show rules: Host(`tradingnexus.pro`) || ...
   
3. Look for services:
   - tradingfrontend service should exist
   - Should point to frontend container
   - Should be healthy


MOST LIKELY ISSUE:
──────────────────
When you added learn.tradingnexus.pro:
1. docker-compose.prod.yml was updated with new Traefik rule
2. Coolify should have auto-redeployed
3. But frontend container might not have been rebuilt
4. OR Traefik rules weren't reloaded

QUICK FIX STEPS:
────────────────
1. Log into Coolify dashboard
2. Go to trading-nexus app → frontend service
3. Click "Redeploy" button
4. Wait for build to complete
5. Check logs for errors
6. If still 404, click "Restart" container
7. Clear browser cache (Ctrl+Shift+Delete)
8. Test: curl http://tradingnexus.pro/
""")

# Try Traefik dashboard if exposed
print("\n" + "="*70)
print("CHECKING TRAEFIK DASHBOARD:")
print("="*70)

try:
    responses = {}
    
    # Try different Traefik dashboard ports
    traefik_urls = [
        ("http://72.62.228.112:8080/dashboard/", "Standard Traefik port"),
        ("http://72.62.228.112:8080/api/routers", "Traefik API - Routers"),
        ("http://72.62.228.112:8080/api/services", "Traefik API - Services"),
    ]
    
    for url, desc in traefik_urls:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                print(f"  ✓ {desc}: Accessible")
                responses[url] = r.status_code
            else:
                print(f"  - {desc}: Status {r.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"  ✗ {desc}: Connection refused")
        except Exception as e:
            print(f"  ⚠ {desc}: {str(e)[:40]}")
    
    if responses:
        print("\n  Some Traefik endpoints are accessible!")
        print("  You might be able to query the API directly")
        
except Exception as e:
    print(f"  Could not check Traefik: {str(e)[:80]}")

print("\n" + "="*70)
