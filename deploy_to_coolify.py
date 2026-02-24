#!/usr/bin/env python3
"""
TRADING-NEXUS V2 DEPLOYMENT TO COOLIFY
Creates new 'trading-nexus' resource and deploys with updated code and data
"""
import requests, json, time, sys

API_URL = "http://72.62.228.112:8000/api/v1"
API_TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
GIT_REPO = "https://github.com/correspond9/Trading-nexus-v2.git"
GIT_BRANCH = "main"

# IDs from analysis
PROJECT_UUID = "vwwc8c0kgssscc8so8ocwckw"  # trade-nexuss project
ENV_UUID = "b0og88kc444w8o84ckoo0g8c"  # production environment

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

def log_step(num, title):
    print(f"\n{'='*70}")
    print(f"[STEP {num}] {title}")
    print('='*70)

def create_application():
    """Create new application/resource in Coolify"""
    log_step(1, "CREATE NEW APPLICATION RESOURCE")
    
    payload = {
        "name": "trading-nexus"
    }
    
    print(f"Creating application 'trading-nexus' in:")
    print(f"  Project: {PROJECT_UUID}")
    print(f"  Environment: {ENV_UUID}")
    
    try:
        url = f"{API_URL}/projects/{PROJECT_UUID}/environments/{ENV_UUID}/applications"
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        app = response.json()
        app_uuid = app['uuid']
        
        print(f"\n✓ Application created successfully!")
        print(f"  Name: {app.get('name')}")
        print(f"  UUID: {app_uuid}")
        print(f"  Status: {app.get('status', 'unknown')}")
        
        return app_uuid
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ FAILED: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        sys.exit(1)

def configure_git_source(app_uuid):
    """Configure Git source for the application"""
    log_step(2, "CONFIGURE GIT SOURCE")
    
    # Get current app details first
    try:
        url = f"{API_URL}/applications/{app_uuid}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        app = response.json()
        print(f"Current app status: {app.get('status', 'unknown')}")
    except:
        pass
    
    print(f"Configuring Git source:")
    print(f"  Repository: {GIT_REPO}")
    print(f"  Branch: {GIT_BRANCH}")
    
    payload = {
        "git_repository": GIT_REPO,
        "git_branch": GIT_BRANCH
    }
    
    try:
        url = f"{API_URL}/applications/{app_uuid}"
        response = requests.put(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        app = response.json()
        print(f"\n✓ Git source configured!")
        print(f"  Repository: {app.get('git_repository', GIT_REPO)}")
        print(f"  Branch: {app.get('git_branch', GIT_BRANCH)}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ FAILED: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return False

def set_environment_variables(app_uuid):
    """Set environment variables for production"""
    log_step(3, "SET ENVIRONMENT VARIABLES")
    
    # Using actual password from existing trade-nexuss production setup
    POSTGRES_PASSWORD = "Financio1026"
    
    env_vars = {
        "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
        "DATABASE_URL": f"postgresql://postgres:{POSTGRES_PASSWORD}@db:5432/trading_terminal",
        "LOG_LEVEL": "WARNING",
        "ENVIRONMENT": "production",
        "DEBUG": "false",
        "STARTUP_LOAD_MASTER": "true",
        "STARTUP_LOAD_TIER_B": "true",
        "STARTUP_START_STREAMS": "true",
        "CORS_ORIGINS_RAW": "https://app.tradingnexus.pro,https://tradingnexus.pro,https://www.tradingnexus.pro,http://localhost:3000,http://localhost:5173",
        "SERVICE_FQDN_BACKEND": "api.tradingnexus.pro",
        "SERVICE_FQDN_FRONTEND": "tradingnexus.pro",
    }
    
    print(f"Setting {len(env_vars)} environment variables:")
    for key in env_vars.keys():
        value_preview = "***" if "PASSWORD" in key or "SECRET" in key else env_vars[key][:50]
        print(f"  - {key} = {value_preview}")
    
    # Coolify expects a different format for env vars
    env_string = ""
    for key, value in env_vars.items():
        env_string += f"{key}={value}\n"
    
    payload = {
        "env": env_string
    }
    
    try:
        url = f"{API_URL}/applications/{app_uuid}"
        response = requests.put(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        print(f"\n✓ Environment variables set!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ FAILED: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return False

def deploy_application(app_uuid):
    """Start deployment"""
    log_step(4, "START DEPLOYMENT")
    
    print(f"Initiating deployment of application...")
    print(f"This will:")
    print(f"  1. Clone repository from GitHub")
    print(f"  2. Build Docker images")
    print(f"  3. Run database migrations (including data restore)")
    print(f"  4. Start all services")
    
    try:
        url = f"{API_URL}/applications/{app_uuid}/deploy"
        response = requests.post(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"\n✓ Deployment initiated!")
        print(f"Status: {response.status_code}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ FAILED: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return False

def check_deployment_status(app_uuid):
    """Check deployment status"""
    log_step(5, "CHECK DEPLOYMENT STATUS")
    
    print(f"Monitoring deployment (checking every 10 seconds, timeout in 5 minutes)...")
    
    max_checks = 30
    for i in range(max_checks):
        try:
            url = f"{API_URL}/applications/{app_uuid}"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            app = response.json()
            status = app.get('status', 'unknown')
            logs = app.get('last_log', '')
            
            elapsed = (i + 1) * 10
            print(f"\n[{elapsed}s] Status: {status}")
            
            if status == 'running' or status == 'started':
                print(f"\n✓ APPLICATION IS RUNNING!")
                return True
            elif 'error' in status.lower() or 'failed' in status.lower():
                print(f"\n✗ Deployment failed!")
                print(f"Last log: {logs[:500]}")
                return False
            
            time.sleep(10)
            
        except Exception as e:
            print(f"[{elapsed}s] Error checking status: {e}")
            time.sleep(10)
    
    print(f"\n⚠ Timeout after {max_checks * 10} seconds")
    print(f"Note: Deployment may still be running. Check Coolify dashboard for status.")
    return None

# ============================================================
# MAIN EXECUTION
# ============================================================
print("\n" + "╔" + "═"*68 + "╗")
print("║" + " " * 68 + "║")
print("║" + "TRADING-NEXUS V2 COOLIFY DEPLOYMENT".center(68) + "║")
print("║" + "Automated End-to-End Deployment".center(68) + "║")
print("║" + " " * 68 + "║")
print("╚" + "═"*68 + "╝")

try:
    # Step 1: Create application
    app_uuid = create_application()
    if not app_uuid:
        sys.exit(1)
    
    # Step 2: Configure Git
    if not configure_git_source(app_uuid):
        sys.exit(1)
    
    # Step 3: Set environment variables
    if not set_environment_variables(app_uuid):
        sys.exit(1)
    
    # Step 4: Deploy
    if not deploy_application(app_uuid):
        sys.exit(1)
    
    # Step 5: Monitor status
    check_deployment_status(app_uuid)
    
    print("\n" + "="*70)
    print("DEPLOYMENT INITIATED SUCCESSFULLY!")
    print("="*70)
    print(f"\nNext steps:")
    print(f"  1. Monitor deployment in Coolify dashboard:")
    print(f"     → http://72.62.228.112:8000/")
    print(f"  2. Once 'trading-nexus' shows as Running, verify it:")
    print(f"     → http://72.62.228.112:8000/api/v2/health")
    print(f"  3. When confirmed working, stop/delete old 'trade-nexuss' resource")
    print("="*70)
    
except KeyboardInterrupt:
    print("\n\n[!] Deployment cancelled by user")
    sys.exit(0)
except Exception as e:
    print(f"\n\n[!] Unexpected error: {e}")
    sys.exit(1)
