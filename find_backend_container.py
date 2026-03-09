import paramiko

# SSH connection details
hostname = "72.62.228.112"
username = "root"
key_path = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"

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
    
    # List all containers related to the app
    print("Finding all containers related to x8gg0og8440wkgc8ow0ococs...")
    cmd = 'docker ps --filter name=x8gg0og8440wkgc8ow0ococs --format "{{.Names}} | {{.Status}}"'
    
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8').strip()
    
    print("\nContainers found:")
    print("=" * 80)
    if output:
        for line in output.split('\n'):
            print(line)
    else:
        print("No containers found!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
    print("\n✅ Connection closed")
