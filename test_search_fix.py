import requests

# Test basic connection
print("Testing backend connection...")
try:
    resp = requests.get('http://72.62.228.112:8000', timeout=5)
    print(f'✅ Backend is reachable: Status {resp.status_code}')
except Exception as e:
    print(f'❌ Backend not reachable: {e}')
    exit(1)

# Test the search endpoint
print("\nTesting search endpoint with RELIANCE...")
try:
    resp = requests.get('http://72.62.228.112:8000/api/v2/instruments/search?q=RELIANCE&limit=5', timeout=5)
    if resp.ok:
        data = resp.json()
        print(f'✅ Search endpoint working. Found {len(data)} results')
        for item in data[:3]:
            symbol = item.get('symbol')
            exch = item.get('exchange_segment')
            inst_type = item.get('instrument_type')
            print(f'   - {symbol}: {exch} ({inst_type})')
    else:
        print(f'❌ Search failed: {resp.status_code}')
        print(resp.text)
except Exception as e:
    print(f'❌ Error: {e}')

print("\n✅ Tests complete")
