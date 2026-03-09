import json, requests, csv, re
from collections import defaultdict

BASE='http://localhost:8000'
API=BASE+'/api/v2'

roles={
 'SUPER_ADMIN':('9999999999','admin123'),
 'ADMIN':('8888888888','admin123'),
 'USER':('7777777777','user123'),
 'SUPER_USER':('6666666666','super123'),
}

samples={
 'user_id':'7777777777',
 'order_id':'00000000-0000-0000-0000-000000000001',
 'position_id':'00000000-0000-0000-0000-000000000001',
 'payout_id':'00000000-0000-0000-0000-000000000001',
 'plan_id':'1',
 'token':'11536',
 'symbol':'NIFTY',
 'name':'watchlist_a',
 'list_name':'tier_a',
 'action':'start',
 'basket_id':'00000000-0000-0000-0000-000000000001',
}

def fill_path(p):
    def repl(m):
        k=m.group(1)
        return samples.get(k,'test')
    return re.sub(r'\{([^}]+)\}', repl, p)

sess=requests.Session()
openapi=sess.get(API+'/openapi.json',timeout=20).json()

# login
headers_by_role={'GUEST':{}}
for r,(mobile,pw) in roles.items():
    res=sess.post(API+'/auth/login',json={'mobile':mobile,'password':pw},timeout=20)
    if res.status_code==200:
        tok=res.json().get('access_token')
        headers_by_role[r]={'X-AUTH':tok,'Authorization':f'Bearer {tok}','X-USER':mobile}
    else:
        headers_by_role[r]={}

rows=[]
for raw_path,ops in openapi.get('paths',{}).items():
    for method,meta in ops.items():
        m=method.upper()
        if m not in {'GET','POST','PUT','PATCH','DELETE'}:
            continue
        p=fill_path(raw_path)
        url=BASE+p
        for role,h in headers_by_role.items():
            try:
                if m in {'POST','PUT','PATCH'}:
                    resp=sess.request(m,url,headers=h,json={},timeout=12)
                else:
                    resp=sess.request(m,url,headers=h,timeout=12)
                code=resp.status_code
                ctype=resp.headers.get('content-type','')
                schema_ok='unknown'
                if 'application/json' in ctype:
                    try:
                        body=resp.json()
                        schema_ok='json'
                        # quick consistency check for successful responses
                        if code<400 and not isinstance(body,(dict,list)):
                            schema_ok='json-scalar'
                    except Exception:
                        schema_ok='invalid-json'
                rows.append({
                    'path':raw_path,
                    'method':m,
                    'role':role,
                    'status':code,
                    'content_type':ctype,
                    'schema':schema_ok,
                })
            except Exception as e:
                rows.append({
                    'path':raw_path,'method':m,'role':role,'status':'ERR',
                    'content_type':'','schema':str(e)[:120]
                })

out='logs/_audit_endpoint_probe.csv'
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['path','method','role','status','content_type','schema'])
    w.writeheader();w.writerows(rows)

# summary
by_role=defaultdict(lambda: defaultdict(int))
for r in rows:
    by_role[r['role']][str(r['status'])]+=1

print('WROTE',out)
print('TOTAL_ROWS',len(rows))
for role in ['GUEST','USER','SUPER_USER','ADMIN','SUPER_ADMIN']:
    s=by_role[role]
    top=sorted(s.items(),key=lambda kv:(-kv[1],kv[0]))[:8]
    print(role,top)
