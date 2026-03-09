import requests,re
u='http://72.62.228.112:8000/build/assets/app-BNvJoPaw.js'
t=requests.get(u,timeout=30).text
print('len',len(t))
# print unique endpoint-like fragments containing /api/v1/
parts=set(re.findall(r'/api/v1/[A-Za-z0-9_\-/{}:.]*',t))
for p in sorted(parts):
 if len(p)<120:
  print(p)
# look for clone/create related tokens nearby
def show(tok):
 i=t.find(tok)
 print('\nTOK',tok,'idx',i)
 if i!=-1: print(t[max(0,i-180):i+280])
for tok in ['clone','applications','resources','/api/v1/applications','environment-variables','deploy','restart','stop','docker_compose_raw']:
 show(tok)
