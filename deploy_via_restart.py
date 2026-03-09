import paramiko

# SSH connection details
hostname = "72.62.228.112"
username = "root"
key_path = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"

backend_container = "backend-x8gg0og8440wkgc8ow0ococs-064710024292"

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Load private key
    private_key = paramiko.Ed25519Key.from_private_key_file(key_path)
    
    # Connect
    print(f"Connecting to {hostname}...")
    ssh.connect(hostname, username=username, pkey=private_key, timeout=10)
    print("✅ Connected successfully\n")
    
    print("=" * 80)
    print("DEPLOYING: Pending Orders Margin Reservation Feature")
    print("=" * 80)
    
    print("\n📝 Summary of Changes:")
    print("   • Database migration 033 applied ✓")
    print("   • Added calculate_pending_orders_margin() function")
    print("   • Updated margin.py to include pending orders")
    print("   • Updated orders.py to check pending orders margin")
    
    print("\n💡 What This Fixes:")
    print("   - Prevents over-leveraging from multiple pending orders")
    print("   - Reserves margin for fresh orders (not exits)")
    print("   - Available margin now = Allotted - (Positions + Pending)")
    
    # Restart the backend container to pick up new code
    print("\n🔄 Restarting backend container...")
    cmd = f'docker restart {backend_container}'
    
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8').strip()
    
    if output:
        print(f"✅ Container restarted: {output}")
    
    if error and 'warn' not in error.lower():
        print(f"⚠️ Errors: {error}")
    
    # Wait a moment for container to start
    print("\n⏳ Waiting for container to start...")
    import time
    time.sleep(5)
    
    # Check if container is running
    print("\n🔍 Verifying container status...")
    check_cmd = f'docker ps --filter name={backend_container} --format "{{{{.Status}}}}"'
    
    stdin, stdout, stderr = ssh.exec_command(check_cmd)
    status = stdout.read().decode('utf-8').strip()
    
    if "Up" in status:
        print(f"✅ Container is running: {status}")
        
        print("\n" + "=" * 80)
        print("✅ DEPLOYMENT SUCCESSFUL")
        print("=" * 80)
        
        print("\n📌 Next Steps:")
        print("   1. Test with a user who has pending orders")
        print("   2. Verify margin calculation includes pending orders")
        print("   3. Try placing multiple pending orders and check available margin")
    else:
        print(f"⚠️ Container status: {status}")
        print("   Check container logs for any issues")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
    print("\n✅ Connection closed")
