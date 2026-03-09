import requests, json
base='http://72.62.228.112:8000/api/v1'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'}
for path in ['/github-apps','/security/keys','/servers/zk0wks40sw4cw8gg8s8kogko/resources']:
 r=requests.get(base+path,headers=h,timeout=20)
 print('\n',path,r.status_code)
 try:
  d=r.json();
  print(json.dumps(d,indent=2)[:1800])
 except Exception:
  print(r.text[:1000])
