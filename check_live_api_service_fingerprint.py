import requests

js = requests.get('https://tradingnexus.pro/assets/index-C7qa5k3_.js', timeout=30).text
print('has Failed to fetch:', 'Failed to fetch' in js)
print('has tn-auth-expired:', 'tn-auth-expired' in js)
print('has X-AUTH:', 'X-AUTH' in js)
print('has mode:cors token:', 'mode:"cors"' in js or "mode:'cors'" in js or 'mode:cors' in js)
print('has axios string:', 'axios' in js.lower())
