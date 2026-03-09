import requests

requests.packages.urllib3.disable_warnings()
urls = [
    'https://tradingnexus.pro/api/v2/health',
    'https://api.tradingnexus.pro/api/v2/health',
    'https://api.tradingnexus.pro/health',
]
for u in urls:
    try:
        r = requests.get(u, verify=False, timeout=15)
        print(u, r.status_code, r.text[:160])
    except Exception as e:
        print(u, 'ERR', e)
