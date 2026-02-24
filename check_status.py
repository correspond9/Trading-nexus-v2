import requests
import time

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
headers = {'Authorization': f'Bearer {token}'}
url = 'http://72.62.228.112:8000/api/v1/applications/zccs8wko40occg44888kwooc'

for i in range(60):  # 60 checks = 10 minutes with 10s delay
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            d = resp.json()['data']
            status = d['status']
            online = d['is_online']
            print(f"[{i+1:02d}] Status: {status:25} | Online: {online}")
            
            if 'running' in status.lower():
                print("\n✅ DEPLOYMENT SUCCESSFUL!")
                break
            elif 'exited' in status.lower() and 'healthy' not in status.lower():
                print("\n❌ DEPLOYMENT FAILED")
                break
        else:
            print(f"[{i+1:02d}] API Error: {resp.status_code}")
    except Exception as e:
        print(f"[{i+1:02d}] Exception: {e}")
    
    time.sleep(10)
