import re, json, pathlib
import requests

BASE='http://localhost:8000/api/v2'
openapi=requests.get(BASE+'/openapi.json',timeout=15).json()
paths=set(openapi.get('paths',{}).keys())

files=list(pathlib.Path('frontend/src').rglob('*'))
found=[]
for p in files:
    if p.suffix.lower() not in {'.js','.jsx','.ts','.tsx'}: continue
    txt=p.read_text(encoding='utf-8',errors='ignore')
    for m in re.finditer(r"['\"](/api/v2/[A-Za-z0-9_\-/{}/.]+)['\"]",txt):
        found.append((m.group(1),str(p).replace('\\','/')))
    for m in re.finditer(r"['\"](/admin/[A-Za-z0-9_\-/{}/.]+)['\"]",txt):
        found.append(('/api/v2'+m.group(1),str(p).replace('\\','/')))

# normalize dynamic paths only for exact openapi presence check
unmatched=[]
for ep,f in found:
    if ep not in paths:
        unmatched.append((ep,f))

# dedupe
seen=set(); out=[]
for ep,f in unmatched:
    k=(ep,f)
    if k in seen: continue
    seen.add(k); out.append({'endpoint':ep,'file':f})

with open('logs/_audit_frontend_endpoint_mismatches.json','w',encoding='utf-8') as fp:
    json.dump(out,fp,indent=2)
print('WROTE logs/_audit_frontend_endpoint_mismatches.json',len(out))
for x in out[:40]:
    print(x['endpoint'],'::',x['file'])
