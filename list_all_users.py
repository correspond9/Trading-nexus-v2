import paramiko

# SSH connection details
hostname = "72.62.228.112"
username = "root"
key_path = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"

# Database details
db_container = "db-x8gg0og8440wkgc8ow0ococs-064710036566"
db_name = "trading_nexus"
db_user = "postgres"

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
    
    # First, list all users to see what's in the database
    print("All users in database:")
    print("=" * 80)
    cmd = f"""docker exec {db_container} psql -U {db_user} -d {db_name} -t -A -c "SELECT id || '|' || mobile || '|' || created_at || '|' || is_active FROM users ORDER BY id;" """
    
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8').strip()
    
    if output:
        lines = output.split('\n')
        for line in lines:
            if line.strip() and '|' in line:
                parts = line.split('|')
                if len(parts) >= 4:
                    print(f"ID: {parts[0]:<5} | Mobile: {parts[1]:<15} | Created: {parts[2]:<30} | Active: {parts[3]}")
    else:
        print("No users found or error occurred")
    
    if error:
        print(f"\nErrors: {error}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
    print("\n✅ Connection closed")
