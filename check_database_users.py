#!/usr/bin/env python3
"""
Check database users on production VPS
"""
import paramiko
import getpass

VPS_HOST = "72.62.228.112"
VPS_USER = "root"
APP_UUID = "p488ok8g8swo4ockks040ccg"

def main():
    password = getpass.getpass(f"SSH password for {VPS_USER}@{VPS_HOST}: ")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"\nConnecting to {VPS_HOST}...")
        ssh.connect(VPS_HOST, username=VPS_USER, password=password)
        print("✓ Connected")
        
        # Find the database container
        print("\nFinding database container...")
        stdin, stdout, stderr = ssh.exec_command(
            f"docker ps --format '{{{{.Names}}}}' | grep 'db-{APP_UUID}'"
        )
        db_container = stdout.read().decode().strip()
        
        if not db_container:
            print("❌ Database container not found!")
            return
        
        print(f"✓ Found: {db_container}")
        
        # Check users table
        print("\n" + "=" * 80)
        print("CHECKING USERS TABLE")
        print("=" * 80)
        
        check_query = """
        docker exec {container} psql -U trading_user -d trading_nexus_production -c "
            SELECT 
                user_no,
                mobile, 
                name,
                role,
                is_active,
                created_at
            FROM users 
            ORDER BY user_no;
        "
        """.format(container=db_container)
        
        stdin, stdout, stderr = ssh.exec_command(check_query)
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if error and "ERROR" in error:
            print(f"❌ Database error:\n{error}")
        else:
            print(output)
        
        # Check user_sessions table
        print("\n" + "=" * 80)
        print("CHECKING ACTIVE SESSIONS")
        print("=" * 80)
        
        sessions_query = """
        docker exec {container} psql -U trading_user -d trading_nexus_production -c "
            SELECT 
                s.token,
                u.mobile,
                u.name,
                u.role,
                s.created_at,
                s.expires_at,
                (s.expires_at > NOW()) as is_valid
            FROM user_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.expires_at > NOW() - INTERVAL '1 hour'
            ORDER BY s.created_at DESC
            LIMIT 10;
        "
        """.format(container=db_container)
        
        stdin, stdout, stderr = ssh.exec_command(sessions_query)
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if error and "ERROR" in error:
            print(f"❌ Database error:\n{error}")
        else:
            print(output)
        
        # Check if migrations ran
        print("\n" + "=" * 80)
        print("CHECKING MIGRATIONS")
        print("=" * 80)
        
        migrations_query = """
        docker exec {container} psql -U trading_user -d trading_nexus_production -c "
            SELECT * FROM _migrations 
            WHERE name LIKE '%seed%' OR name LIKE '%user%'
            ORDER BY id DESC
            LIMIT 5;
        "
        """.format(container=db_container)
        
        stdin, stdout, stderr = ssh.exec_command(migrations_query)
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if error and "ERROR" in error:
            print(f"❌ Database error:\n{error}")
        else:
            print(output)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
