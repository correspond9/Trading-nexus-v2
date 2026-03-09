import requests, json
base='http://72.62.228.112:8000'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466','Content-Type':'application/json'}
paths=[
('/api/v1/applications','POST',{'name':'probe'}),
('/api/v1/application','POST',{'name':'probe'}),
('/api/v1/resources','POST',{'name':'probe','type':'application'}),
('/api/v1/projects/i8k44sw0gsg8ocoogw8s0ook/environments/qw8k0k0sc0gg0ogkcck0g4ss/resources','POST',{'name':'probe','type':'application'}),
('/api/v1/projects/i8k44sw0gsg8ocoogw8s0ook/environments/qw8k0k0sc0gg0ogkcck0g4ss/applications','POST',{'name':'probe'}),
('/api/v1/sources','GET',None),
('/api/v1/destinations','GET',None),
('/api/v1/servers','GET',None),
('/api/v1/resources','GET',None)
]
for path,method,payload in paths:
  try:
    if method=='GET': r=requests.get(base+path,headers=h,timeout=12)
    else: r=requests.post(base+path,headers=h,json=payload,timeout=12)
    print(method,path,'->',r.status_code,r.text[:180].replace('\n',' '))
  except Exception as e:
    print(method,path,'ERR',e)
