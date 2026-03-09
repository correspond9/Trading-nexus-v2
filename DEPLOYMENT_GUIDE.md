# Learn Trading Nexus - Deployment Instructions

## Current Status
✅ Application is ready for production deployment to Coolify

### What's Been Completed
1. **Next.js Pages Updated**
   - Replaced all "Financio" branding with "Trading Nexus"
   - Updated form submission to use admin API instead of Google Sheets
   - All pages built and compiled successfully

2. **Docker Container Ready**
   - Docker image: `learn-trading-nexus:latest`
   - Running on Port: 3001 (localhost) / 3000 (internal)
   - Next.js version: 13.5.4
   - Status: ✅ Healthy and running

3. **Environment Configuration**
   - API Endpoint: `https://tradingnexus.pro/api/v2/admin/portal-signups`
   - Form submissions configured to use admin API
   - Environment variables set in docker-compose.yml

---

## Deployment to Coolify Server

### Method: Docker Compose Deployment

**Server Details:**
- IP: `72.62.228.112`
- Coolify URL: `http://72.62.228.112:8000`
- Project: "My first project"
- Environment: "production"

**Steps:**

### Step 1: SSH into the Server
```bash
ssh root@72.62.228.112
```
Use the SSH key from the workspace (check `check_coolify.py` for the private key).

### Step 2: Navigate to Coolify Projects
```bash
cd /opt/coolify/projects/my-first-project/production/
# or check the actual location with:
# find /opt -name "my-first-project" -type d
```

### Step 3: Create Project Directory
```bash
mkdir -p learn-trading-nexus
cd learn-trading-nexus
```

### Step 4: Copy Files to Server
From your local machine, copy the necessary files:
```bash
# Copy docker-compose.yml
scp learn-trading-nexus/docker-compose.yml root@72.62.228.112:/opt/coolify/projects/my-first-project/production/learn-trading-nexus/

# Copy Dockerfile
scp learn-trading-nexus/Dockerfile root@72.62.228.112:/opt/coolify/projects/my-first-project/production/learn-trading-nexus/

# Copy package files and config
scp learn-trading-nexus/package.json root@72.62.228.112:/opt/coolify/projects/my-first-project/production/learn-trading-nexus/
scp learn-trading-nexus/package-lock.json root@72.62.228.112:/opt/coolify/projects/my-first-project/production/learn-trading-nexus/

# Copy the built .next folder
scp -r learn-trading-nexus/.next root@72.62.228.112:/opt/coolify/projects/my-first-project/production/learn-trading-nexus/

# Copy public folder
scp -r learn-trading-nexus/public root@72.62.228.112:/opt/coolify/projects/my-first-project/production/learn-trading-nexus/

# Copy other config files
scp learn-trading-nexus/.env.local root@72.62.228.112:/opt/coolify/projects/my-first-project/production/learn-trading-nexus/
scp learn-trading-nexus/next.config.js root@72.62.228.112:/opt/coolify/projects/my-first-project/production/learn-trading-nexus/
scp learn-trading-nexus/postcss.config.js root@72.62.228.112:/opt/coolify/projects/my-first-project/production/learn-trading-nexus/
scp learn-trading-nexus/tailwind.config.js root@72.62.228.112:/opt/coolify/projects/my-first-project/production/learn-trading-nexus/
scp learn-trading-nexus/tsconfig.json root@72.62.228.112:/opt/coolify/projects/my-first-project/production/learn-trading-nexus/
```

### Step 5: Start the Container
On the server (SSH):
```bash
cd /opt/coolify/projects/my-first-project/production/learn-trading-nexus/
docker-compose up -d
```

### Step 6: Verify Container is Running
```bash
docker ps --filter "name=learn-trading-nexus"
docker logs learn-trading-nexus
```

### Step 7: Configure Domain in Coolify UI
1. Open Coolify Dashboard: http://72.62.228.112:8000
2. Go to "My first project" → "production" 
3. Look for the "learn-trading-nexus" resource
4. Add domain: `learn.tradingnexus.pro`
5. Enable SSL/TLS (Let's Encrypt)
6. Save configuration

### Step 8: Configure Traefik Networking (if needed)
If the traefik network doesn't exist on the server, create it:
```bash
docker network create traefik
```

Or update docker-compose.yml to use `external: false` temporarily.

---

## Verification Checklist

After deployment, verify:

- [ ] Container is running: `docker ps` shows "learn-trading-nexus"
- [ ] App is healthy: `docker logs learn-trading-nexus` shows "Ready"
- [ ] Port 3001 is accessible: `curl http://localhost:3001`
- [ ] Domain is accessible: https://learn.tradingnexus.pro
- [ ] Pages load correctly
- [ ] Form submission works and hits the admin API
- [ ] All "Trading Nexus" branding is visible (no "Financio")

---

## Rollback Instructions

If something goes wrong:

```bash
cd /opt/coolify/projects/my-first-project/production/learn-trading-nexus/
docker-compose down
rm -rf *
# Re-deploy with corrected files
```

---

## Support Files Included

- **docker-compose.yml** - Container orchestration configuration
- **Dockerfile** - Production Docker image definition
- **learn-trading-nexus-build.zip** - Complete built application archive
- **deploy_via_docker.py** - Local deployment testing script
- **deploy_learn_nextjs.py** - Coolify API configuration script

---

## Quick Reference

| Component | Value |
|-----------|-------|
| **Domain** | https://learn.tradingnexus.pro |
| **Container Port (Internal)** | 3000 |
| **Host Port** | 3001 |
| **Environment** | Production |
| **API Endpoint** | https://tradingnexus.pro/api/v2/admin/portal-signups |
| **Framework** | Next.js 13.5.4 |
| **Node Version** | 18-alpine |
| **Health Check** | Every 30s |

---

Generated: March 10, 2026
Status: Ready for Production Deployment
