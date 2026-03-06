import subprocess

def ssh(cmd):
    result = subprocess.run(["ssh", "root@72.62.228.112", cmd], capture_output=True, text=True)
    print(result.stdout[:3000])
    if result.stderr:
        print("STDERR:", result.stderr[:500])

# Find the container running the app
print("=== FINDING APP CONTAINER ===")
ssh("docker ps --format '{{.Names}} {{.Image}}' | grep -v db | grep -v coolify")

print("\n=== FIND APP CONTAINER NAME ===")
ssh("docker ps --format '{{.Names}}' | head -20")
