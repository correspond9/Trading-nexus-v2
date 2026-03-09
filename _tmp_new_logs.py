import requests
base='http://72.62.228.112:8000/api/v1'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'}
app='aw8kowwwgc4w40cg48840css'
r=requests.get(base+f'/applications/{app}/logs',headers=h,timeout=25)
print(r.status_code)
print(r.text[:5000])
