import requests
base='http://72.62.228.112:8000/api/v1'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466','Content-Type':'application/json'}
app='aw8kowwwgc4w40cg48840css'
for endpoint in ['start','restart']:
 r=requests.post(base+f'/applications/{app}/'+endpoint,headers=h,timeout=20)
 print(endpoint,r.status_code,r.text)
