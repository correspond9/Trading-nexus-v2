import requests,time
base='http://72.62.228.112:8000'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466','Content-Type':'application/json'}
for i in range(2):
 r=requests.post(base+'/api/v1/applications/x8gg0og8440wkgc8ow0ococs/restart',headers=h,timeout=15)
 print('restart',i+1,r.status_code,r.text)
 time.sleep(1)
