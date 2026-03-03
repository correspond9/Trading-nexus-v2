import re
from urllib.parse import urljoin
import requests

base = 'https://tradingnexus.pro'
html = requests.get(base, timeout=20).text
main_path = re.findall(r'<script[^>]+src="([^"]+)"', html)[0]
main_url = urljoin(base, main_path)
main_js = requests.get(main_url, timeout=30).text

chunk_paths = sorted(set(re.findall(r'(?:/)?assets/[^\"\']+\.js', main_js)))
print('main:', main_url)
print('chunk count detected in main bundle:', len(chunk_paths))
for cp in chunk_paths:
    print('chunk:', cp)

keywords = [
    '/trading/orders/historic/orders',
    '/trading/orders/executed',
    '/trading/orders',
    'No orders found for the selected criteria.',
    'No executed trades found for the selected period.',
    'data?.data',
    'res?.data||[]',
]

found = []
for path in chunk_paths:
    url = urljoin(base, path)
    try:
        js = requests.get(url, timeout=30).text
    except Exception:
        continue
    hit = [k for k in keywords if k in js]
    if hit:
        found.append((path, hit, len(js)))

for path, hit, ln in found:
    print('\n', path, 'len=', ln)
    for h in hit:
        print('  -', h)

print('\nmatched chunks:', len(found))
