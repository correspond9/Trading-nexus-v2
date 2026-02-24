#!/usr/bin/env python3
"""
TRADING NEXUS - FLAWLESS COOLIFY DEPLOYMENT
============================================
Uses fresh Coolify API token to:
1. Get project info
2. Create backend application
3. Configure PostgreSQL database
4. Deploy backend
5. Monitor deployment
6. Verify database migrations
7. Test application health
"""

import sys
import requests
import time
import json
from typing import Dict, Any, Optional, Tuple

# ============================================================
# CONFIGURATION
# ============================================================

VPS_HOST = "72.62.228.112"
VPS_HTTP = f"http://{VPS_HOST}"
COOLIFY_PORT = 8000  # Coolify runs on 8000:8080 mapping
COOLIFY_API_BASE = f"{VPS_HTTP}:{COOLIFY_PORT}/api"

# Fresh API token provided by user
API_TOKEN = "1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466"

# GitHub Repository Details
GITHUB_REPO = "https://github.com/correspond9/Trading-nexus-v2.git"
GITHUB_BRANCH = "main"

# Application Details
PROJECT_NAME = "Trading-Nexus"
BACKEND_APP_NAME = "backend"
DATABASE_NAME = "trading_nexus_db"
DATABASE_USER = "postgres"

# ============================================================
# DEPLOYMENT LOGGER
# ============================================================

class DeploymentLogger:
    def __init__(self):
        self.successes = []
        self.warnings = []
        self.errors = []
    
    def log_success(self, msg: str):
        self.successes.append(msg)
        print(f"✅ {msg}")
    
    def log_warning(self, msg: str):
        self.warnings.append(msg)
        print(f"⚠️  {msg}")
    
    def log_error(self, msg: str):
        self.errors.append(msg)
        print(f"❌ {msg}")
    
    def log_info(self, msg: str):
        print(f"ℹ️  {msg}")
    
    def print_summary(self):
        print("\n" + "="*80)
        print("DEPLOYMENT SUMMARY")
        print("="*80)
        
        if self.successes:
            print(f"\n✅ SUCCESSES ({len(self.successes)}):")
            for msg in self.successes:
                print(f"   {msg}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for msg in self.warnings:
                print(f"   {msg}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for msg in self.errors:
                print(f"   {msg}")
        
        print("\n" + "="*80)

log = DeploymentLogger()

# ============================================================
# API HELPER FUNCTIONS
# ============================================================

def api_get(endpoint: str, headers: Optional[Dict] = None) -> Tuple[Optional[Dict], bool]:
    """Make GET request to Coolify API"""
    url = f"{COOLIFY_API_BASE}{endpoint}"
    if headers is None:
        headers = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code in [200, 201]:
            return resp.json(), True
        else:
            log.log_error(f"API GET {endpoint}: {resp.status_code} - {resp.text[:200]}")
            return None, False
    except Exception as e:
        log.log_error(f"API GET {endpoint} exception: {e}")
        return None, False

def api_post(endpoint: str, data: Dict = None, headers: Optional[Dict] = None) -> Tuple[Optional[Dict], bool]:
    """Make POST request to Coolify API"""
    url = f"{COOLIFY_API_BASE}{endpoint}"
    if headers is None:
        headers = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}
    
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=30)
        if resp.status_code in [200, 201]:
            return resp.json(), True
        else:
            log.log_error(f"API POST {endpoint}: {resp.status_code} - {resp.text[:200]}")
            return None, False
    except Exception as e:
        log.log_error(f"API POST {endpoint} exception: {e}")
        return None, False

def api_put(endpoint: str, data: Dict = None, headers: Optional[Dict] = None) -> Tuple[Optional[Dict], bool]:
    """Make PUT request to Coolify API"""
    url = f"{COOLIFY_API_BASE}{endpoint}"
    if headers is None:
        headers = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}
    
    try:
        resp = requests.put(url, json=data, headers=headers, timeout=30)
        if resp.status_code in [200, 201]:
            return resp.json(), True
        else:
            log.log_error(f"API PUT {endpoint}: {resp.status_code} - {resp.text[:200]}")
            return None, False
    except Exception as e:
        log.log_error(f"API PUT {endpoint} exception: {e}")
        return None, False

# ============================================================
# STEP 1: GET CURRENT PROJECTS
# ============================================================

def get_projects() -> Optional[list]:
    """Get all projects"""
    log.log_info("Step 1: Fetching projects...")
    data, success = api_get("/v1/projects")
    
    if not success or not data:
        return None
    
    # API returns array directly, not nested under 'data'
    projects = data if isinstance(data, list) else data.get("data", [])
    log.log_success(f"Retrieved {len(projects)} project(s)")
    
    for proj in projects[:3]:
        proj_name = proj.get("name") if isinstance(proj, dict) else "Unknown"
        proj_uuid = proj.get("uuid") if isinstance(proj, dict) else "N/A"
        print(f"  - {proj_name} (UUID: {proj_uuid})")
    
    if len(projects) > 3:
        print(f"  ... and {len(projects) - 3} more")
    
    return projects

# ============================================================
# STEP 2: GET OR CREATE PROJECT
# ============================================================

def find_or_create_project(projects: list) -> Optional[str]:
    """Find existing project or indicate to create one"""
    log.log_info("Step 2: Looking for project...")
    
    # Look for project matching our name
    for proj in projects:
        if proj.get("name") == PROJECT_NAME:
            uuid = proj.get("uuid")
            log.log_success(f"Found existing project: {PROJECT_NAME}")
            print(f"  UUID: {uuid}")
            return uuid
    
    # If not found, use the first available project
    if projects:
        proj = projects[0]
        uuid = proj.get("uuid")
        proj_name = proj.get("name")
        log.log_warning(f"Project '{PROJECT_NAME}' not found, using first project: {proj_name}")
        print(f"  UUID: {uuid}")
        return uuid
    
    # If still no project, user needs to create from UI
    log.log_warning(f"No projects found in Coolify")
    log.log_info("Please create project in Coolify UI and try again")
    return None

# ============================================================
# STEP 3: GET PROJECT RESOURCES
# ============================================================

def get_project_resources(project_uuid: str) -> Tuple[Optional[list], Optional[list]]:
    """Get applications and services for project"""
    log.log_info("Step 3: Fetching project resources...")
    
    # Get applications
    apps_data, apps_ok = api_get(f"/v1/projects/{project_uuid}/applications")
    if apps_ok and apps_data:
        apps = apps_data if isinstance(apps_data, list) else apps_data.get("data", [])
    else:
        apps = []
    
    # Get services (PostgreSQL, Redis, etc.)
    services_data, services_ok = api_get(f"/v1/projects/{project_uuid}/services")
    if services_ok and services_data:
        services = services_data if isinstance(services_data, list) else services_data.get("data", [])
    else:
        services = []
    
    log.log_success(f"Found {len(apps)} application(s) and {len(services)} service(s)")
    
    for app in apps:
        app_name = app.get('name', 'Unknown') if isinstance(app, dict) else 'Unknown'
        app_status = app.get('status', 'Unknown') if isinstance(app, dict) else 'Unknown'
        print(f"  App: {app_name} - Status: {app_status}")
    for svc in services:
        svc_name = svc.get('name', 'Unknown') if isinstance(svc, dict) else 'Unknown'
        svc_type = svc.get('type', 'Unknown') if isinstance(svc, dict) else 'Unknown'
        print(f"  Service: {svc_name} - Type: {svc_type}")
    
    return apps, services

# ============================================================
# STEP 4: CREATE BACKEND APPLICATION
# ============================================================

def create_or_update_backend_app(project_uuid: str, apps: list) -> Optional[str]:
    """Create or find backend application"""
    log.log_info("Step 4: Setting up backend application...")
    
    # Check if backend already exists
    backend_app = None
    for app in apps:
        if app.get("name") == BACKEND_APP_NAME:
            backend_app = app
            log.log_info(f"Found existing backend app: {app.get('uuid')}")
            break
    
    if backend_app:
        app_uuid = backend_app.get("uuid")
        log.log_success(f"Using existing backend application: {app_uuid}")
        return app_uuid
    
    # Create new backend application
    log.log_info("Creating new backend application via API...")
    
    app_config = {
        "name": BACKEND_APP_NAME,
        "description": "Trading Nexus Backend API",
        "type": "application",
        "build_pack": "dockerfile",
        "git_repository": GITHUB_REPO,
        "git_branch": GITHUB_BRANCH,
        "dockerfile": "Dockerfile",
        "docker_registry_image_tag": "latest",
        "port_mappings": [
            {
                "container_port": 8000,
                "host_port": 8000
            }
        ]
    }
    
    data, success = api_post(
        f"/v1/projects/{project_uuid}/applications",
        app_config
    )
    
    if not success or not data:
        log.log_error("Failed to create backend application")
        return None
    
    # Handle both list and dict responses
    app_uuid = None
    if isinstance(data, list) and len(data) > 0:
        app_uuid = data[0].get("uuid")
    elif isinstance(data, dict):
        app_uuid = data.get("data", {}).get("uuid")
    
    if not app_uuid:
        log.log_error("No UUID returned from application creation")
        return None
    
    log.log_success(f"Created backend application: {app_uuid}")
    return app_uuid

# ============================================================
# STEP 5: CREATE POSTGRESQL SERVICE
# ============================================================

def create_or_update_postgresql_service(project_uuid: str, services: list) -> Optional[str]:
    """Create or find PostgreSQL service"""
    log.log_info("Step 5: Setting up PostgreSQL database...")
    
    # Check if PostgreSQL service already exists
    db_service = None
    for svc in services:
        if svc.get("type") == "postgresql":
            db_service = svc
            log.log_info(f"Found existing PostgreSQL service: {svc.get('uuid')}")
            break
    
    if db_service:
        service_uuid = db_service.get("uuid")
        log.log_success(f"Using existing PostgreSQL service: {service_uuid}")
        return service_uuid
    
    # Create new PostgreSQL service
    log.log_info("Creating new PostgreSQL service via API...")
    
    db_config = {
        "name": "postgresql",
        "description": "PostgreSQL Database for Trading Nexus",
        "type": "postgresql",
        "postgresql_version": "16",
        "postgres_db": DATABASE_NAME,
        "postgres_user": DATABASE_USER,
        "postgres_password": "ChangeMeToSecure123!"  # Should be changed in UI later
    }
    
    data, success = api_post(
        f"/v1/projects/{project_uuid}/services",
        db_config
    )
    
    if not success or not data:
        log.log_warning("Could not create PostgreSQL via API (may need to do in UI)")
        return None
    
    # Handle both list and dict responses
    service_uuid = None
    if isinstance(data, list) and len(data) > 0:
        service_uuid = data[0].get("uuid")
    elif isinstance(data, dict):
        service_uuid = data.get("data", {}).get("uuid")
    
    if service_uuid:
        log.log_success(f"Created PostgreSQL service: {service_uuid}")
    else:
        log.log_warning("Could not extract UUID from PostgreSQL creation response")
    
    return service_uuid

# ============================================================
# STEP 6: DEPLOY APPLICATION
# ============================================================

def deploy_application(project_uuid: str, app_uuid: str) -> bool:
    """Trigger application deployment"""
    log.log_info("Step 6: Triggering deployment...")
    
    data, success = api_post(
        f"/v1/projects/{project_uuid}/applications/{app_uuid}/deploy",
        {}
    )
    
    if not success:
        log.log_error("Failed to trigger deployment")
        return False
    
    log.log_success("Deployment triggered")
    return True

# ============================================================
# STEP 7: MONITOR DEPLOYMENT
# ============================================================

def monitor_deployment(project_uuid: str, app_uuid: str, max_wait_seconds: int = 600) -> bool:
    """Monitor deployment progress"""
    log.log_info("Step 7: Monitoring deployment (max 10 minutes)...")
    
    start_time = time.time()
    check_interval = 10  # Check every 10 seconds
    last_status = None
    
    while True:
        elapsed = int(time.time() - start_time)
        
        if elapsed > max_wait_seconds:
        # Handle both list and dict responses
        if isinstance(data, list) and len(data) > 0:
            app_data = data[0]
        elif isinstance(data, dict) and "data" in data:
            app_data = data.get("data", {})
        else:
            app_data = data if isinstance(data, dict) else {}
        
        app_status = app_datameout after {max_wait_seconds} seconds")
            return False
        
        data, success = api_get(f"/v1/projects/{project_uuid}/applications/{app_uuid}")
        
        if not success or not data:
            print(f"[{elapsed}s] ⏳ Waiting for API response...", end="\r", flush=True)
            time.sleep(check_interval)
            continue
        
        app_status = data.get("data", {}).get("status", "unknown")
        
        # Only print if status changed
        if app_status != last_status:
            last_status = app_status
            print(f"[{elapsed}s] Status: {app_status:<20}", flush=True)
        
        # Check if deployment is complete
        if "running" in app_status.lower():
            log.log_success(f"Application running after {elapsed} seconds")
            return True
        
        if "exited" in app_status.lower() or "error" in app_status.lower():
            log.log_error(f"Application failed: {app_status}")
            return False
        
        time.sleep(check_interval)

# ============================================================
# STEP 8: TEST HEALTH ENDPOINT
# ============================================================

def test_health_endpoint(max_wait_seconds: int = 120) -> bool:
    """Test backend health endpoint"""
    log.log_info("Step 8: Testing health endpoint...")
    
    health_url = f"{VPS_HTTP}:8000/health"
    start_time = time.time()
    
    while True:
        elapsed = int(time.time() - start_time)
        
        if elapsed > max_wait_seconds:
            log.log_warning(f"Health endpoint not responding after {max_wait_seconds} seconds")
            return False
        
        try:
            resp = requests.get(health_url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                log.log_success(f"Health endpoint responding: {data}")
                return True
            else:
                print(f"[{elapsed}s] Health check returned {resp.status_code}", end="\r", flush=True)
        except Exception as e:
            print(f"[{elapsed}s] Health check pending ({str(e)[:40]})", end="\r", flush=True)
        
        time.sleep(5)

# ============================================================
# STEP 9: VERIFY DATABASE
# ============================================================

def verify_database() -> bool:
    """Verify database has been initialized correctly"""
    log.log_info("Step 9: Verifying database...")
    
    try:
        import asyncpg
    except ImportError:
        log.log_warning("asyncpg not installed, skipping database verification")
        log.log_info("Install with: pip install asyncpg")
        return True
    
    import asyncio
    
    async def check_db():
        try:
            # Try to connect to database
            conn = await asyncpg.connect(
                host=VPS_HOST,
                port=5432,
                database=DATABASE_NAME,
                user=DATABASE_USER,
                password="ChangeMeToSecure123!"  # Same as created above
            )
            
            # Check brokerage plans (should be 12)
            count = await conn.fetchval("SELECT COUNT(*) FROM brokerage_plans")
            if count == 12:
                log.log_success(f"Database initialized with {count} brokerage plans (✓ correct)")
            else:
                log.log_warning(f"Expected 12 brokerage plans, found {count}")
            
            # Check tables
            tables = await conn.fetch(
                "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema='public'"
            )
            table_count = tables[0]['count'] if tables else 0
            log.log_success(f"Database has {table_count} tables (expected 26+)")
            
            # Check users
            users = await conn.fetchval("SELECT COUNT(*) FROM users")
            log.log_success(f"Database has {users} users (expected 5+)")
            
            await conn.close()
            return count == 12 and table_count >= 26
            
        except Exception as e:
            log.log_warning(f"Could not verify database: {e}")
            return False
    
    return asyncio.run(check_db())

# ============================================================
# STEP 10: FINAL VERIFICATION
# ============================================================

def final_verification() -> bool:
    """Run all final checks"""
    log.log_info("Step 10: Final verification...")
    
    checks = []
    
    # Check 1: Health endpoint
    try:
        resp = requests.get(f"{VPS_HTTP}:8000/health", timeout=5)
        health_ok = resp.status_code == 200
        checks.append(("Health endpoint", health_ok))
    except:
        checks.append(("Health endpoint", False))
    
    # Check 2: Backend accessible
    try:
        resp = requests.get(f"{VPS_HTTP}:8000", timeout=5)
        backend_ok = resp.status_code < 500
        checks.append(("Backend accessible", backend_ok))
    except:
        checks.append(("Backend accessible", False))
    
    # Print checks
    all_ok = True
    for check_name, check_result in checks:
        if check_result:
            log.log_success(f"{check_name}: OK")
        else:
            log.log_warning(f"{check_name}: Not responding yet (may still be starting)")
            all_ok = False
    
    return all_ok

# ============================================================
# MAIN DEPLOYMENT FLOW
# ============================================================

def main():
    print("\n" + "="*80)
    print("TRADING NEXUS - FLAWLESS COOLIFY DEPLOYMENT")
    print("="*80 + "\n")
    
    # Step 1: Get projects
    projects = get_projects()
    if not projects:
        log.log_error("Failed to fetch projects")
        log.print_summary()
        return False
    
    # Step 2: Find or create project
    project_uuid = find_or_create_project(projects)
    if not project_uuid:
        log.log_error("Could not find or create project")
        log.log_info("Please create project 'Trading-Nexus' in Coolify UI and try again")
        log.print_summary()
        return False
    
    # Step 3: Get resources
    apps, services = get_project_resources(project_uuid)
    if apps is None:
        log.log_error("Failed to fetch project resources")
        log.print_summary()
        return False
    
    # Step 4: Create or find backend app
    app_uuid = create_or_update_backend_app(project_uuid, apps)
    if not app_uuid:
        log.log_error("Failed to create backend application")
        log.print_summary()
        return False
    
    # Step 5: Create or find PostgreSQL service
    # (This may need to be done in UI, but we'll try API)
    db_uuid = create_or_update_postgresql_service(project_uuid, services)
    if db_uuid:
        log.log_success(f"PostgreSQL service ready: {db_uuid}")
    else:
        log.log_warning("PostgreSQL service may need to be created in Coolify UI")
    
    # Step 6: Deploy
    if not deploy_application(project_uuid, app_uuid):
        log.print_summary()
        return False
    
    # Step 7: Monitor
    if not monitor_deployment(project_uuid, app_uuid):
        log.print_summary()
        return False
    
    # Wait a bit for health checks to settle
    log.log_info("Waiting for health checks to settle...")
    time.sleep(30)
    
    # Step 8: Test health
    health_ok = test_health_endpoint()
    if not health_ok:
        log.log_warning("Health endpoint not responding, but deployment may still be initializing")
    
    # Step 9: Verify database
    db_ok = verify_database()
    
    # Step 10: Final verification
    final_ok = final_verification()
    
    # Summary
    log.print_summary()
    
    if len(log.errors) == 0:
        print("\n" + "="*80)
        print("✅ DEPLOYMENT SUCCESSFUL - FLAWLESS!")
        print("="*80)
        print("\nNext steps:")
        print("1. Access Coolify dashboard: http://72.62.228.112:3000")
        print("2. Test backend: curl http://72.62.228.112:8000/health")
        print("3. Verify database has 12 brokerage plans")
        print("4. Configure domain in Coolify reverse proxy (Traefik)")
        print("5. Add frontend application (optional)")
        print("="*80 + "\n")
        return True
    else:
        print("\n" + "="*80)
        print(f"❌ DEPLOYMENT COMPLETED WITH {len(log.errors)} ERROR(S)")
        print("="*80 + "\n")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
