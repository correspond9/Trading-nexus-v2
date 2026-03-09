import csv, re, json, pathlib
from collections import defaultdict

root=pathlib.Path('.')
probe=list(csv.DictReader(open('logs/_audit_endpoint_probe.csv',encoding='utf-8')))

# by endpoint summary
ep=defaultdict(list)
for r in probe:
    ep[(r['path'],r['method'])].append(r)

rows=[]
for (path,method),vals in sorted(ep.items()):
    by={v['role']:v for v in vals}
    def st(role): return str(by.get(role,{}).get('status','NA'))
    rows.append({
        'path':path,'method':method,
        'guest':st('GUEST'),'user':st('USER'),'super_user':st('SUPER_USER'),'admin':st('ADMIN'),'super_admin':st('SUPER_ADMIN')
    })

with open('logs/_audit_endpoint_matrix.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['path','method','guest','user','super_user','admin','super_admin'])
    w.writeheader(); w.writerows(rows)

# suspicious auth results
suspicious=[]
for r in rows:
    p=r['path']
    if p.startswith('/api/v2/admin') and r['guest']=='200':
        suspicious.append(('admin_public_to_guest',r))
    if p.startswith('/api/v2/trading') and r['guest']=='200':
        suspicious.append(('trading_public_to_guest',r))
    if p.startswith('/api/v2/portfolio') and r['guest']=='200':
        suspicious.append(('portfolio_public_to_guest',r))

with open('logs/_audit_suspicious_auth.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['type','path','method','guest','user','super_user','admin','super_admin'])
    for t,r in suspicious:
        w.writerow([t,r['path'],r['method'],r['guest'],r['user'],r['super_user'],r['admin'],r['super_admin']])

# frontend usage mapping
src=pathlib.Path('frontend/src')
texts=[]
for p in src.rglob('*'):
    if p.suffix.lower() in {'.js','.jsx','.ts','.tsx'}:
        try: texts.append((p, p.read_text(encoding='utf-8',errors='ignore')))
        except Exception: pass

def route_variants(path):
    # produce exact and stripped variants likely used in frontend
    out={path}
    if path.startswith('/api/v2'): out.add(path[len('/api/v2'):])
    if path.endswith('/'): out.add(path[:-1])
    if '{' in path:
        out.add(re.sub(r'\{[^}]+\}','',path).replace('//','/'))
    return sorted(v for v in out if v)

usage=[]
for r in rows:
    variants=route_variants(r['path'])
    hit_files=[]
    for p,t in texts:
        if any(v in t for v in variants):
            hit_files.append(str(p).replace('\\','/'))
    usage.append({'path':r['path'],'method':r['method'],'used':bool(hit_files),'hits':';'.join(hit_files[:8]),'hit_count':len(hit_files)})

with open('logs/_audit_frontend_usage.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['path','method','used','hit_count','hits'])
    w.writeheader(); w.writerows(usage)

unused=[u for u in usage if not u['used']]
with open('logs/_audit_frontend_unused_routes.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['path','method','used','hit_count','hits'])
    w.writeheader(); w.writerows(unused)

print('WROTE logs/_audit_endpoint_matrix.csv', len(rows))
print('WROTE logs/_audit_suspicious_auth.csv', len(suspicious))
print('WROTE logs/_audit_frontend_usage.csv', len(usage))
print('WROTE logs/_audit_frontend_unused_routes.csv', len(unused))

# quick stdout top counts
public=[r for r in rows if r['guest']=='200']
print('GUEST_200_COUNT',len(public))
print('FIRST_20_GUEST_200')
for r in public[:20]:
    print(r['method'],r['path'])
