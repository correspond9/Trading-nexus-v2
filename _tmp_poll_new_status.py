import requests, time, json
base='http://72.62.228.112:8000/api/v1'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'}
app='aw8kowwwgc4w40cg48840css'
for i in range(10):
 d=requests.get(base+f'/applications/{app}',headers=h,timeout=20).json()
 print(i+1,'status=',d.get('status'),'updated_at=',d.get('updated_at'),'name=',d.get('name'))
 time.sleep(6)
