#!/usr/bin/env python3
"""
Check DNS resolution for all domains
"""

import socket
import subprocess

print("="*70)
print("DNS AND DOMAIN RESOLUTION CHECK")
print("="*70)

domains = {
    "tradingnexus.pro": "Main frontend domain",
    "www.tradingnexus.pro": "WWW subdomain",
    "learn.tradingnexus.pro": "Learn portal domain",
    "api.tradingnexus.pro": "Backend API domain",
}

vps_ip = "72.62.228.112"

print(f"\nExpected IP for all domains: {vps_ip}")
print("\n" + "="*70)

for domain, description in domains.items():
    print(f"\n{domain}")
    print(f"  ({description})")
    
    try:
        # Try DNS resolution
        ip = socket.gethostbyname(domain)
        match = "✓" if ip == vps_ip else "✗"
        print(f"  {match} Resolves to: {ip}")
        
        if ip != vps_ip:
            print(f"    WARNING: Expected {vps_ip}, got {ip}")
            print(f"    This means DNS is pointing to wrong IP!")
            
    except socket.gaierror as e:
        print(f"  ✗ DNS failed: {str(e)[:60]}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:60]}")

print("\n" + "="*70)
print("WHAT THIS MEANS:")
print("="*70)
print("""
If all domains resolve to 72.62.228.112:
  ✓ DNS is configured correctly
  ✓ Issue is NOT with DNS
  ✓ Issue must be Traefik routing or frontend container not running

If some domains resolve to different IPs:
  ✗ DNS is pointing to old server
  ✗ You need to update DNS A records
  ✗ May take 24-48 hours to propagate


If NO domains resolve:
  ✗ DNS not set up at all
  ✗ Contact domain registrar to add A records


IMPORTANT:
- For local testing, you can edit your hosts file:
  Windows: C:\\Windows\\System32\\drivers\\etc\\hosts
  Linux: /etc/hosts
  Mac: /etc/hosts
  
  Add:
  72.62.228.112 tradingnexus.pro
  72.62.228.112 www.tradingnexus.pro
  72.62.228.112 learn.tradingnexus.pro
  72.62.228.112 api.tradingnexus.pro
""")

# Also try to check DNS propagation status
print("\n" + "="*70)
print("DNS PROPAGATION:")
print("="*70)

try:
    # Try nslookup if available
    import platform
    if platform.system() == "Windows":
        print("\nTo check DNS propagation globally, use:")
        print("  nslookup tradingnexus.pro")
    else:
        print("\nTo check DNS propagation, use:")
        print("  dig tradingnexus.pro")
except:
    pass
