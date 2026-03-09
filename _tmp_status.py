import requests,time,json
base='http://72.62.228.112:8000'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'}
for _ in range(6):
 d=requests.get(base+'/api/v1/applications/x8gg0og8440wkgc8ow0ococs',headers=h,timeout=15).json()
 print('status=',d.get('status'),'updated_at=',d.get('updated_at'))
 time.sleep(4)
