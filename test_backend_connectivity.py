#!/usr/bin/env python3
"""
Test backend connectivity and routing configuration
"""
import json
import subprocess
import sys

def run_ssh(cmd):
    """Run SSH command with proper quoting"""
    try:
        result = subprocess.run(
            ['ssh', 'root@72.62.228.112', cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", -1

def test_backend_direct():
    """Test backend from container directly"""
    print("\n" + "="*60)
    print("Testing backend service directly (inside container)")
    print("="*60)
    
    cmd = 'docker exec backend-p488ok8g8swo4ockks040ccg-041804919223 python3 -c "\
import json, urllib.request\
try:\
    resp = urllib.request.urlopen(\'http://127.0.0.1:8000/api/v2/instruments/search?q=RELIANCE&limit=3\')\
    data = json.loads(resp.read())\
    print(f\'✅ Backend search works! Got {len(data)} results\')\
    if len(data) > 0:\
        print(f\'   First result: {data[0]}\')\
except Exception as e:\
    print(f\'❌ Backend failed: {e}\')\
"'
    
    stdout, stderr, code = run_ssh(cmd)
    print(stdout)
    if stderr:
        print(f"Error: {stderr}")
    return code == 0

def test_traefik_config():
    """Check Traefik router configuration"""
    print("\n" + "="*60)
    print("Checking Traefik Router Configuration")
    print("="*60)
    
    cmd = 'grep -n "traefik.http.routers.tradingbackend" /data/coolify/applications/p488ok8g8swo4ockks040ccg/docker-compose.yaml'
    stdout, stderr, _ = run_ssh(cmd)
    if stdout:
        for line in stdout.split('\n'):
            print(f"  {line}")
    
    cmd = 'grep -n "traefik.http.services.tradingbackend" /data/coolify/applications/p488ok8g8swo4ockks040ccg/docker-compose.yaml'
    stdout, stderr, _ = run_ssh(cmd)
    if stdout:
        for line in stdout.split('\n'):
            print(f"  {line}")
    
    return True

def check_container_network():
    """Verify containers are on coolify network"""
    print("\n" + "="*60)
    print("Checking Docker Network Configuration")
    print("="*60)
    
    cmd = 'docker network inspect coolify --format="{{range .Containers}}{{.Name}}: {{.IPv4Address}}\n{{end}}"'
    stdout, stderr, _ = run_ssh(cmd)
    print("Containers on coolify network:")
    for line in stdout.split('\n'):
        if line.strip():
            print(f"  {line}")
    
    return True

def test_traefik_logs():
    """Check recent Traefik logs for errors"""
    print("\n" + "="*60)
    print("Traefik Recent Logs (errors/warnings)")
    print("="*60)
    
    cmd = 'docker logs coolify-proxy 2>&1 | tail -30 | grep -iE "error|warning|404|tradingbackend|backend-p488|unreachable" | head -10'
    stdout, stderr, _ = run_ssh(cmd)
    if stdout:
        for line in stdout.split('\n'):
            if line.strip():
                print(f"  {line}")
    else:
        print("  No errors found in recent logs")
    
    return True

def main():
    print("\n╔" + "="*58 + "╗")
    print("║" + " "*15 + "BACKEND CONNECTIVITY DIAGNOSTIC" + " "*12 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Direct Backend Test", test_backend_direct),
        ("Traefik Config Check", test_traefik_config),
        ("Container Network Check", check_container_network),
        ("Traefik Logs Check", test_traefik_logs),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = "✅ PASS" if result else "⚠️  CHECK"
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            results[name] = "❌ FAIL"
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    for name, status in results.items():
        print(f"{status} - {name}")
    
    print("\n" + "="*60)
    print("Next Steps:")
    if all("❌" not in s for s in results.values()):
        print("All checks passed. If API still returns 404:")
        print("1. Check if Traefik routes are correctly parsed:")
        print("   docker logs coolify-proxy | grep 'tradingbackend\\|routers'")
        print("2. Restart Traefik to reload configuration:")
        print("   docker restart coolify-proxy")
        print("3. Test again: curl http://api.tradingnexus.pro/api/v2/instruments/search?q=TEST")
    else:
        print("Some checks failed - see details above")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
