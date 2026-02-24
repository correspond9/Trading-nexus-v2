#!/usr/bin/env python3
import socket

host = "72.62.228.112"
ports = [8000, 80, 3000, 5000, 8080, 443]

print(f"Checking connectivity to {host}...")
print()

for port in ports:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        statusmsg = "OPEN" if result == 0 else "CLOSED"
        print(f"Port {port:5d}: {statusmsg}")
        sock.close()
    except Exception as e:
        print(f"Port {port:5d}: ERROR")

print("\nNote: Port 8000 is where your API runs based on the URL provided.")
