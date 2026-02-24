# ============================================================================
# COOLIFY DOCKER COMPOSE - TRAEFIK ROUTING FIX
# ============================================================================

## ROOT CAUSE
Docker Compose apps in Coolify need service-level configuration for each
service you want to expose via Traefik. The Traefik labels in our 
docker-compose.prod.yml are being ignored or overridden by Coolify.

## SOLUTION - SSH INTO VPS AND RUN
The issue is that Coolify expects per-service configuration for Docker
Compose deployments. We need to:

1. SSH into your VPS:
   ```bash
   ssh root@72.62.228.112
   ```

2. Find the actual container names:
   ```bash
   docker ps | grep trading
   ```

3. Check if containers are on coolify network:
   ```bash
   docker network ls
   docker network inspect coolify
   ```

4. If containers are NOT on coolify network, manually connect them:
   ```bash
   # Get the backend container name (example: p488ok8g8swo4ockks040ccg-backend-1)
   export BACKEND_CONTAINER=$(docker ps --format '{{.Names}}' | grep 'p488ok8.*backend')
   export FRONTEND_CONTAINER=$(docker ps --format '{{.Names}}' | grep 'p488ok8.*frontend')
   
   echo "Connecting containers to coolify network..."
   docker network connect coolify $BACKEND_CONTAINER
   docker network connect coolify $FRONTEND_CONTAINER
   
   echo "Done! Testing..."
   ```

5. Test immediately:
   ```bash
   curl -v http://api.tradingnexus.pro/health
   curl -v http://72.62.228.112:8001/health
   ```

## CURRENT STATE
- Application UUID: p488ok8g8swo4ockks040ccg
- App Status: running:unknown
- Exposed Port in Coolify: 8000
- Network Config: Added to docker-compose.prod.yml
- Traefik Labels: Present in docker-compose.prod.yml
- Issue: Containers likely not on coolify network despite configuration

## WHY THIS HAPPENS
When Coolify deploys Docker Composefile apps, it may:
1. Create containers BEFORE parsing network directives
2. Override network configuration for isolation
3. Expect manual network connection for security

## VERIFICATION  
After connecting to network, check:
```bash
# Should return 200 OK:
curl -I http://api.tradingnexus.pro/health

# Should show your backend container:
docker network inspect coolify | grep -A 10 backend
```

If this fixes it, we'll need to determine if this is a one-time fix or
if we need a startup script to ensure network connection persists.

## ALTERNATIVE (if network connect doesnt work)
If manual network connection doesn't work, the issue might be Traefik
configuration itself not recognizing the labels. In that case

, we may need
to check Traefik's configuration or use Coolify's service-specific domain
settings through the UI (which we've been unable to configure via API).
