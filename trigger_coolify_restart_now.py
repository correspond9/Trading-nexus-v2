import requests

API = "http://72.62.228.112:8000/api/v1"
TOKEN = "1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466"
APP_UUID = "x8gg0og8440wkgc8ow0ococs"

headers = {"Authorization": f"Bearer {TOKEN}"}

r = requests.post(f"{API}/applications/{APP_UUID}/restart", headers=headers, timeout=20)
print("status", r.status_code)
print(r.text[:500])
