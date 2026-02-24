#!/usr/bin/env python3
import requests

url = "http://72.62.228.112:8000/"

print("Checking what's running on port 8000...")
print()

try:
    response = requests.get(url, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"\nHeaders:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    print(f"\nBody (first 1000 chars):")
    print(response.text[:1000])
    
    if 'coolify' in response.text.lower():
        print("\n✓ This appears to be Coolify!")
    elif 'trading' in response.text.lower():
        print("\n✓ This appears to be Trading App!")
    else:
        print("\n? Service is unclear")
        
except Exception as e:
    print(f"Error: {e}")
