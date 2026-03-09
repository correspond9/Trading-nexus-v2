import requests, time
u='http://72.62.228.112:8000/api/v1/applications'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466','Content-Type':'application/json'}
payload={'name':'learn-trading-nexus-test-'+str(int(time.time())),'build_pack':'dockercompose'}
r=requests.post(u,headers=h,json=payload,timeout=20)
print(r.status_code)
print(r.text[:1500])
