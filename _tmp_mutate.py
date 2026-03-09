import requests
base='http://72.62.228.112:8000'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466','Content-Type':'application/json'}
for p in ['/api/v1/applications/x8gg0og8440wkgc8ow0ococs/deploy','/api/v1/applications/x8gg0og8440wkgc8ow0ococs/restart','/api/v1/applications/x8gg0og8440wkgc8ow0ococs/stop','/api/v1/applications/x8gg0og8440wkgc8ow0ococs/execute']:
  try:
    r=requests.post(base+p,headers=h,json={'command':'echo hi'},timeout=15)
    print(p,'->',r.status_code,r.text[:200].replace('\n',' '))
  except Exception as e:
    print(p,'ERR',e)
