import subprocess

def ssh(cmd):
    result = subprocess.run(["ssh", "root@72.62.228.112", cmd], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr and "ERROR" in result.stderr:
        print("STDERR:", result.stderr[:500])

BACKEND = "backend-x8gg0og8440wkgc8ow0ococs-145803796937"

# Read the deployed ledger.py from inside the running container
ssh(f"docker exec {BACKEND} cat /app/app/routers/ledger.py")
