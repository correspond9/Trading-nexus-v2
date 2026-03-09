import requests, json
base='http://72.62.228.112:8000/api/v1'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'}
app='aw8kowwwgc4w40cg48840css'
r=requests.get(base+f'/deployments/applications/{app}',headers=h,timeout=25)
print('list',r.status_code)
print(r.text[:3000])
if r.status_code==200:
 d=r.json()
 if isinstance(d,list) and d:
  dep=d[0].get('deployment_uuid') or d[0].get('uuid')
  if dep:
   r2=requests.get(base+f'/deployments/{dep}',headers=h,timeout=25)
   print('\nDETAIL',r2.status_code)
   print(r2.text[:5000])
