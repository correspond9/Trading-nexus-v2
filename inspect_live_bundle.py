import re
from urllib.parse import urljoin
import requests

base = 'https://tradingnexus.pro'
html = requests.get(base, timeout=20).text
scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
print('scripts:', scripts)

if not scripts:
    raise SystemExit('No script tags found')

for idx, script_path in enumerate(scripts):
    js_url = urljoin(base, script_path)
    js = requests.get(js_url, timeout=30).text
    print(f'--- Script #{idx+1}: {js_url}')
    print('contains /trading/orders/historic/orders:', '/trading/orders/historic/orders' in js)
    print('contains /trading/orders/executed:', '/trading/orders/executed' in js)
    print('contains data?.data:', 'data?.data' in js)
    print('contains res?.data||[]:', 'res?.data||[]' in js)
    print('contains No orders found for the selected criteria.:', 'No orders found for the selected criteria.' in js)
    print('length:', len(js))
