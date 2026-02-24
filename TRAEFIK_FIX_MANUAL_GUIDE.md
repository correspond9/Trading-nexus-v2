# FIX FOR COOLIFY TRAEFIK ROUTING ISSUE

## Problem Summary

The Trading Nexus API endpoints are returning 404 because:

1. **Broken Traefik Label**: The docker-compose.yaml contains a malformed router rule:
   ```
   Host(``) && PathPrefix(`api.tradingnexus.pro`)
   ```
   This has an empty Host() matcher, which Traefik cannot parse.

2. **Port Conflict**: Coolify is listening on port 8000, intercepting all traffic and redirecting to `/login`

3. **Root Cause**: When Coolify rebuilt the application, it auto-generated broken routing labels

## Solution

### Step 1: SSH into the VPS
```bash
ssh root@72.62.228.112
```

### Step 2: Navigate to Application Directory  
```bash
cd /data/coolify/applications/p488ok8g8swo4ockks040ccg
```

### Step 3: Backup Current Configuration
```bash
cp docker-compose.yaml docker-compose.yaml.backup.$(date +%s)
```

### Step 4: Remove Broken Labels

Using a simple Python script to clean the YAML:

```bash
python3 << 'EOF'
import re

# Read the compose file
with open('docker-compose.yaml', 'r') as f:
    content = f.read()

# List of patterns to remove
patterns_to_remove = [
    r'^\s*- traefik\.http\.routers\.http-0.*$',
    r'^\s*- traefik\.http\.middlewares\.http-0.*$',
    r'^\s*- caddy_.*$',
    r"^\s*- 'caddy_.*$",
    r'^\s*- caddy_ingress_network.*$',
]

# Remove broken lines
lines = content.split('\n')
cleaned_lines = []
for line in lines:
    should_skip = any(re.match(pattern, line) for pattern in patterns_to_remove)
    if not should_skip:
        cleaned_lines.append(line)

# Write back
with open('docker-compose.yaml', 'w') as f:
    f.write('\n'.join(cleaned_lines))

print("Removed broken Traefik labels")
EOF
```

### Step 5: Verify the Fix

Check that broken labels are removed:
```bash
grep -c "traefik.http.routers.http-0" docker-compose.yaml
# Should return: 0
```

Check that good labels remain:
```bash
grep "traefik.http.routers.tradingbackend.rule" docker-compose.yaml
# Should show: traefik.http.routers.tradingbackend.rule=Host(`api.tradingnexus.pro`)
```

### Step 6: Restart Application

```bash
docker compose down --remove-orphans
docker compose up -d
```

Wait 30 seconds for containers to stabilize:
```bash
sleep 30
```

### Step 7: Test the Fix

Test from within the VPS:
```bash
# This should work since Traefik is properly configured
curl http://api.tradingnexus.pro/api/v2/instruments/search?q=RELIANCE&limit=5
```

Expected response: JSON array of instruments
```json
[
  {
    "symbol": "RELIANCE",
    "exchange_segment": "NSE",
    "instrument_token": 1234567,
    "instrument_type": "equity"
  },
  ...
]
```

### Step 8: Test from Your Local Machine

Once working on the VPS, test from outside:
```bash
curl http://api.tradingnexus.pro/api/v2/instruments/search?q=RELIANCE&limit=5
```

If using domain staging (DNS might take time to propagate):
```bash
curl -H "Host: api.tradingnexus.pro" http://72.62.228.112/api/v2/instruments/search?q=RELIANCE
```

## Troubleshooting

### If containers won't start:
```bash
docker compose logs backend
# Check for startup errors in logs
```

### If getting route `Host(): empty args` errors:
```bash
docker logs coolify-proxy | grep "Host()"
# Confirms the broken label - need to remove it
```

### If search endpoint still returns 404:
```bash
# Restart Traefik to reload configuration
docker restart coolify-proxy
# Wait 5 seconds
sleep 5
# Test again
curl http://api.tradingnexus.pro/api/v2/instruments/search?q=TEST
```

### If port conflicts:
```bash
# Check what's listening on port 8000
ss -tlnp | grep 8000
# Or
netstat -tlnp | grep 8000
```

## Verification Checklist

After applying the fix:

- [ ] No more "traefik.http.routers.http-0" labels in docker-compose.yaml
- [ ] Backend container is running and healthy (`docker ps | grep backend`)
- [ ] Search endpoint returns 200 status code
- [ ] API response contains instrument data
- [ ] Frontend dropdown component shows suggestions when typing
- [ ] Backdate position form can find and select instruments

##Success! The frontend is now ready to use the searchable instrument dropdown.
