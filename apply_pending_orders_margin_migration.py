import paramiko

# SSH connection details
hostname = "72.62.228.112"
username = "root"
key_path = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"

# Database details
db_container = "db-x8gg0og8440wkgc8ow0ococs-064710036566"
db_name = "trading_terminal"
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
    
    # Read migration file
    print("Reading migration file...")
    with open(r"d:\4.PROJECTS\FRESH\trading-nexus\migrations\033_add_pending_orders_margin_calculation.sql", "r") as f:
        migration_sql = f.read()
    
    print("Migration SQL loaded.")
    print("-" * 80)
    
    # Upload migration to server
    print("\nUploading migration to server...")
    sftp = ssh.open_sftp()
    remote_path = "/tmp/033_add_pending_orders_margin_calculation.sql"
    sftp.put(r"d:\4.PROJECTS\FRESH\trading-nexus\migrations\033_add_pending_orders_margin_calculation.sql", remote_path)
    sftp.close()
    print(f"✅ Uploaded to {remote_path}")
    
    # Apply migration
    print("\nApplying migration...")
    cmd = f'cat {remote_path} | docker exec -i {db_container} psql -U {db_user} -d {db_name}'
    
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    print("Migration output:")
    print(output)
    
    if error and 'NOTICE' not in error and 'CREATE FUNCTION' not in error:
        print(f"\n⚠️ Errors/Warnings:\n{error}")
    
    # Verify the function was created
    print("\nVerifying function creation...")
    verify_cmd = f"""docker exec {db_container} psql -U {db_user} -d {db_name} -c "SELECT proname, pronargs FROM pg_proc WHERE proname = 'calculate_pending_orders_margin';" """
    
    stdin, stdout, stderr = ssh.exec_command(verify_cmd)
    verify_output = stdout.read().decode('utf-8')
    
    print(verify_output)
    
    if "calculate_pending_orders_margin" in verify_output:
        print("✅ Migration applied successfully!")
    else:
        print("❌ Function not found - migration may have failed")
    
    # Clean up
    print("\nCleaning up temp file...")
    ssh.exec_command(f'rm {remote_path}')
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
    print("\n✅ Connection closed")
