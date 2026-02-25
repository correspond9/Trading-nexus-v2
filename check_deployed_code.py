import requests
import re

# Check what JavaScript is served
r = requests.get('https://tradingnexus.pro/')
html = r.text

# Find the main index asset
scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
index_asset = [s for s in scripts if 'index' in s]

if index_asset:
    asset_url = 'https://tradingnexus.pro' + index_asset[0]
    print('Checking asset:', index_asset[0])
    
    content = requests.get(asset_url).text
    
    # Check for the fix
    if 'String(user.id)' in content or 'String(user?.id)' in content:
        print('✓ FIXED CODE: String(user.id) found!')
    else:
        print('✗ OLD CODE: String(user.id) NOT found')
        print('  Looking for user_id references...')
        count = content.count('user_id')
        print(f'  Found {count} user_id references')
else:
    print('No index asset found')
