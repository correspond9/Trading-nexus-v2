import requests

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

uuid = 'zccs8wko40occg44888kwooc'

print('=' * 80)
print('CHECKING APPLICATION LOGS FOR ERRORS')
print('=' * 80)
print()

try:
    # Get logs - try different endpoints that might work
    endpoints = [
        f'{base}/applications/{uuid}/logs',
        f'{base}/applications/{uuid}',
    ]
    
    for endpoint in endpoints:
        try:
            resp = requests.get(endpoint, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    app = data[0]
                else:
                    app = data.get('data', data) if isinstance(data, dict) else data
                
                print(f'Endpoint: {endpoint}')
                print('Status:', app.get('status') if isinstance(app, dict) else 'N/A')
                print('Online:', app.get('is_online') if isinstance(app, dict) else 'N/A')
                
                if isinstance(app, dict):
                    for k in ['build_pack', 'docker_compose_location', 'last_deployment_log']:
                        if k in app:
                            print(f'{k}: {app[k]}')
                print()
        except:
            pass
    
except Exception as e:
    print(f'Error: {e}')
