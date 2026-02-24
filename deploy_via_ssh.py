#!/usr/bin/env python3
"""
Recreate Trading Nexus application in Coolify via SSH and trigger deployment.
"""

import paramiko
import json
import time
from io import StringIO

# Private key content
key_content = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

def main():
    # Connect to VPS
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("Connecting to VPS (72.62.228.112)...")
    try:
        # Load key from string
        key_file = StringIO(key_content)
        private_key = paramiko.Ed25519Key.from_private_key(key_file)
        
        ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
        print("✓ Connected via SSH")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False
    
    # Create application
    print("\nCreating application in Coolify...")
    
    curl_cmd = """curl -s -X POST \
  -H 'Authorization: Bearer 2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7' \
  -H 'Content-Type: application/json' \
  -d '{"name":"Trading Nexus","description":"Trading platform with Django backend and React frontend","git_repository":"https://github.com/correspond9/Trading-nexus-v2.git","git_branch":"main","docker_compose_file":"docker-compose.yml","type":"docker-compose","port":"8000"}' \
  http://localhost:3000/api/v1/applications"""
    
    stdin, stdout, stderr = ssh.exec_command(curl_cmd)
    response_text = stdout.read().decode().strip()
    
    print("\nResponse from Coolify:")
    print(response_text)
    
    if not response_text:
        print("✗ No response from server")
        ssh.close()
        return False
    
    try:
        response = json.loads(response_text)
        if 'data' not in response or not isinstance(response['data'], dict):
            print("✗ Unexpected response format")
            ssh.close()
            return False
        
        if not response['data'].get('uuid'):
            print("✗ No UUID in response")
            ssh.close()
            return False
        
        app_uuid = response['data']['uuid']
        print(f"\n✓ Application created successfully!")
        print(f"  UUID: {app_uuid}")
        
        # Trigger deployment
        print(f"\nTriggering deployment...")
        deploy_cmd = f"""curl -s -X POST \
  -H 'Authorization: Bearer 2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7' \
  http://localhost:3000/api/v1/applications/{app_uuid}/deploy"""
        
        stdin, stdout, stderr = ssh.exec_command(deploy_cmd)
        deploy_response = stdout.read().decode().strip()
        
        print("Deploy response:")
        print(deploy_response if deploy_response else "(no output - deployment started)")
        print(f"\n✓ Deployment triggered for UUID: {app_uuid}")
        print("\nMonitoring deployment status...")
        
        # Monitor deployment
        for i in range(120):
            check_cmd = f"""curl -s -H 'Authorization: Bearer 2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7' \
  http://localhost:3000/api/v1/applications/{app_uuid}"""
            
            stdin, stdout, stderr = ssh.exec_command(check_cmd)
            status_text = stdout.read().decode().strip()
            
            if status_text:
                try:
                    status_json = json.loads(status_text)
                    if 'data' in status_json:
                        status = status_json['data'].get('status', 'unknown')
                        is_online = status_json['data'].get('is_online', False)
                        if i % 6 == 0:  # Print every 60 seconds
                            print(f"[{i*10}s] Status: {status} | Online: {is_online}")
                        
                        if 'running' in status.lower() and is_online:
                            print(f"[{i*10}s] Status: {status} | Online: {is_online}")
                            print("\n✓ DEPLOYMENT SUCCESSFUL!")
                            ssh.close()
                            return True
                        
                        if 'exited' in status.lower() or 'failed' in status.lower():
                            print(f"[{i*10}s] Status: {status} | Online: {is_online}")
                            print("\n✗ Deployment failed")
                            ssh.close()
                            return False
                except json.JSONDecodeError:
                    pass
            
            time.sleep(10)
        
        print("\n⚠ Deployment monitoring timeout - check Coolify dashboard")
        ssh.close()
        return None
        
    except json.JSONDecodeError as e:
        print(f"✗ Failed to parse response as JSON: {e}")
        ssh.close()
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
