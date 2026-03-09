import requests, json
BASE='http://localhost:8000/api/v2'

creds={
 'SUPER_ADMIN':('9999999999','admin123'),
 'ADMIN':('8888888888','admin123'),
 'USER':('7777777777','user123'),
 'SUPER_USER':('6666666666','super123'),
}

s=requests.Session()
headers={'GUEST':{}}
for role,(m,p) in creds.items():
    r=s.post(BASE+'/auth/login',json={'mobile':m,'password':p},timeout=10)
    if r.status_code==200:
        tok=r.json()['access_token']
        headers[role]={'X-AUTH':tok,'Authorization':f'Bearer {tok}'}
    else:
        headers[role]={}

checks=[
 ('GET','/auth/me',None),
 ('GET','/admin/token/status',None),
 ('GET','/admin/ws/status',None),
 ('GET','/admin/subscriptions',None),
 ('GET','/admin/users',None),
 ('GET','/admin/positions/userwise',None),
 ('POST','/admin/market-config',{'NSE':{'open':'01:00','close':'01:01','days':[0]}}),
 ('GET','/market/stream-status',None),
 ('GET','/margin/account',None),
 ('POST','/margin/calculate',{'symbol':'NIFTY','transaction_type':'BUY','quantity':1,'ltp':100,'is_option':True}),
 ('GET','/trading/orders',None),
 ('POST','/trading/orders',{'instrument_token':45535,'exchange_segment':'NSE_FNO','side':'BUY','quantity':1,'order_type':'LIMIT','limit_price':600}),
 ('GET','/ledger',None),
 ('GET','/payouts',None),
]

result=[]
for method,path,body in checks:
    row={'endpoint':f'{method} {path}'}
    for role,h in headers.items():
        try:
            if method=='GET':
                r=s.get(BASE+path,headers=h,timeout=10)
            else:
                r=s.post(BASE+path,headers=h,json=body or {},timeout=10)
            row[role]=r.status_code
        except Exception as e:
            row[role]=f'ERR:{type(e).__name__}'
    result.append(row)

open('logs/_audit_targeted_auth_matrix.json','w',encoding='utf-8').write(json.dumps(result,indent=2))
print('WROTE logs/_audit_targeted_auth_matrix.json')
for r in result:
    print(r)
