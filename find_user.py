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
    
    # Search for users with mobile containing 9326890165
    print("Searching for user with mobile 9326890165...")
    query = "SELECT id, mobile, created_at, is_active FROM users WHERE mobile LIKE '%9326890165%';"
    docker_cmd = f'docker exec {db_container} psql -U {db_user} -d {db_name} -c "{query}"'
    
    stdin, stdout, stderr = ssh.exec_command(docker_cmd, get_pty=False)
    output = stdout.read().decode('utf-8')
    
    print(output)
    
    if "(0 rows)" in output:
        print("\nUser not found with that mobile. Let me show all users:")
        query2 = "SELECT id, mobile, created_at, is_active FROM users ORDER BY id;"
        docker_cmd2 = f'docker exec {db_container} psql -U {db_user} -d {db_name} -c "{query2}"'
        
        stdin, stdout, stderr = ssh.exec_command(docker_cmd2, get_pty=False)
        output2 = stdout.read().decode('utf-8')
        print(output2)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
    print("\n✅ Connection closed")
