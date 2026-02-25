import requests, re

r = requests.get('https://tradingnexus.pro/')
html = r.text

# Find script tags
scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
print('Frontend Assets:')
for s in scripts[:5]:
    print(' -', s)

# Check if main index asset contains the fix
if scripts:
    main_asset = [s for s in scripts if 'index' in s]
    if main_asset:
        print(f'\nChecking {main_asset[0]} for String(user.id)...')
        asset_url = 'https://tradingnexus.pro' + main_asset[0]
        asset_content = requests.get(asset_url).text
        if 'String(user.id)' in asset_content or 'String(user?.id)' in asset_content:
            print('✓ FIXED CODE FOUND!')
        else:
            print('✗ OLD CODE - String(user.id) not found!')
            print('  Searching for "user_id"...', asset_content.count('user_id'), 'occurrences')
