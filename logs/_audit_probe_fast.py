import csv, json, re, requests
from collections import defaultdict

BASE='http://localhost:8000'
API=BASE+'/api/v2'
TIMEOUT=2.0

roles={
 'SUPER_ADMIN':('9999999999','admin123'),
 'ADMIN':('8888888888','admin123'),
 'USER':('7777777777','user123'),
 'SUPER_USER':('6666666666','super123'),
}
samples={
 'user_id':'7777777777','order_id':'00000000-0000-0000-0000-000000000001',
 'position_id':'00000000-0000-0000-0000-000000000001','payout_id':'00000000-0000-0000-0000-000000000001',
 'plan_id':'1','token':'11536','symbol':'NIFTY','list_name':'tier_a','name':'watchlist_a','action':'start',
 'basket_id':'00000000-0000-0000-0000-000000000001'
}

def fill_path(p):
    return re.sub(r'\{([^}]+)\}', lambda m: samples.get(m.group(1),'test'), p)

s=requests.Session()
openapi=s.get(API+'/openapi.json',timeout=TIMEOUT).json()

headers={'GUEST':{}}
for role,(mobile,pw) in roles.items():
    try:
        r=s.post(API+'/auth/login',json={'mobile':mobile,'password':pw},timeout=TIMEOUT)
        if r.status_code==200:
            tok=r.json().get('access_token')
            headers[role]={'X-AUTH':tok,'Authorization':f'Bearer {tok}','X-USER':mobile}
        else:
            headers[role]={}
    except Exception:
        headers[role]={}

rows=[]
for raw_path,ops in openapi.get('paths',{}).items():
    for method in ops.keys():
        m=method.upper()
        if m not in {'GET','POST','PUT','PATCH','DELETE'}:
            continue
        url=BASE+fill_path(raw_path)
        for role,h in headers.items():
            status='ERR'; ctype=''; schema='error'
            try:
                if m in {'POST','PUT','PATCH'}:
                    resp=s.request(m,url,headers=h,json={},timeout=TIMEOUT)
                else:
                    resp=s.request(m,url,headers=h,timeout=TIMEOUT)
                status=resp.status_code
                ctype=resp.headers.get('content-type','')
                if 'application/json' in ctype.lower():
                    try:
                        body=resp.json(); schema='json'
                        if status < 400 and not isinstance(body,(dict,list)):
                            schema='json-scalar'
                    except Exception:
                        schema='invalid-json'
                else:
                    schema='non-json'
            except requests.exceptions.RequestException as e:
                schema=type(e).__name__
            rows.append({'path':raw_path,'method':m,'role':role,'status':status,'content_type':ctype,'schema':schema})

out='logs/_audit_endpoint_probe.csv'
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['path','method','role','status','content_type','schema'])
    w.writeheader(); w.writerows(rows)

# aggregate
summary=defaultdict(lambda: defaultdict(int))
for r in rows:
    summary[r['role']][str(r['status'])]+=1
print('WROTE',out)
print('TOTAL_ROWS',len(rows))
for role in ['GUEST','USER','SUPER_USER','ADMIN','SUPER_ADMIN']:
    items=sorted(summary[role].items(), key=lambda kv:(-kv[1],kv[0]))
    print(role, items[:10])

# endpoint-level auth signal: guest denied while super_admin can reach/validate
signals=[]
idx=defaultdict(dict)
for r in rows:
    idx[(r['path'],r['method'])][r['role']]=r
for k,v in idx.items():
    g=v.get('GUEST',{}).get('status')
    sa=v.get('SUPER_ADMIN',{}).get('status')
    signals.append((k[0],k[1],g,sa))
with open('logs/_audit_endpoint_auth_signals.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['path','method','guest_status','super_admin_status']); w.writerows(signals)
print('WROTE logs/_audit_endpoint_auth_signals.csv')
