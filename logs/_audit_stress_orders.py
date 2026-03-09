import requests, time, json
BASE='http://localhost:8000/api/v2'
s=requests.Session()
login=s.post(BASE+'/auth/login',json={'mobile':'7777777777','password':'user123'},timeout=10).json()
H={'X-AUTH':login['access_token'],'Authorization':f"Bearer {login['access_token']}"}

payload={'instrument_token':45535,'exchange_segment':'NSE_FNO','side':'BUY','quantity':1,'order_type':'LIMIT','limit_price':600}
res=[]
for i in range(20):
    t=time.time()
    r=s.post(BASE+'/trading/orders',headers=H,json=payload,timeout=10)
    dt=round((time.time()-t)*1000,2)
    res.append({'i':i+1,'status':r.status_code,'ms':dt,'body':r.text[:140]})

out={'count':len(res),'statuses':{},'slow_over_1000ms':sum(1 for x in res if x['ms']>1000),'samples':res[:5]}
for x in res: out['statuses'][str(x['status'])]=out['statuses'].get(str(x['status']),0)+1
open('logs/_audit_stress_orders.json','w',encoding='utf-8').write(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
