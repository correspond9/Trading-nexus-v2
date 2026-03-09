import requests
base='http://72.62.228.112:8000'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'}
for path in ['/api/v1/resources','/api/v1/applications','/api/v1/projects','/api/v1/servers','/api/v1/applications/x8gg0og8440wkgc8ow0ococs']:
  for m in ['OPTIONS','HEAD']:
    try:
      r=requests.request(m,base+path,headers=h,timeout=12)
      print(m,path,'->',r.status_code,'Allow=',r.headers.get('Allow'))
    except Exception as e:
      print(m,path,'ERR',e)
