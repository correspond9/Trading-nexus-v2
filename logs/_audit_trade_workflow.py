import requests, json

BASE='http://localhost:8000/api/v2'

s=requests.Session()

def login(m,p):
    r=s.post(BASE+'/auth/login',json={'mobile':m,'password':p},timeout=10)
    return r.status_code, (r.json() if 'application/json' in r.headers.get('content-type','') else {})

res={}
for name,m,p in [('super_admin','9999999999','admin123'),('admin','8888888888','admin123'),('user','7777777777','user123')]:
    code,body=login(m,p)
    res[name]={'login_status':code,'user':body.get('user'),'token':body.get('access_token')}

u_tok=res['user']['token']
headers={'X-AUTH':u_tok,'Authorization':f'Bearer {u_tok}'}

# discover a tradable instrument from search endpoint (known flaky)
q=s.get(BASE+'/instruments/search?q=NIFTY&limit=5',headers=headers,timeout=10)
res['instrument_search']={'status':q.status_code,'body':q.text[:300]}

# fallback: market quote token from known default index token
quote=s.get(BASE+'/market/snapshot/11536',headers=headers,timeout=10)
res['snapshot_11536']={'status':quote.status_code,'body':quote.text[:300]}

# attempt valid-ish market order using NIFTY token path
order_payload={
    'instrument_token':11536,
    'exchange_segment':'IDX_I',
    'side':'BUY',
    'quantity':1,
    'order_type':'MARKET',
    'product_type':'NORMAL'
}
ord=s.post(BASE+'/trading/orders',headers=headers,json=order_payload,timeout=12)
res['order_place_idx']={'status':ord.status_code,'body':ord.text[:600]}

# request validation checks
bad1=s.post(BASE+'/trading/orders',headers=headers,json={'quantity':0},timeout=10)
bad2=s.post(BASE+'/trading/orders',headers=headers,json={'instrument_token':'abc','quantity':1},timeout=10)
res['order_bad_qty']={'status':bad1.status_code,'body':bad1.text[:300]}
res['order_bad_token_type']={'status':bad2.status_code,'body':bad2.text[:300]}

# fetch order lists / positions / pnl
for k,ep in [
    ('orders','/trading/orders'),
    ('orders_executed','/trading/orders/executed'),
    ('orders_historic','/trading/orders/historic/orders'),
    ('positions','/portfolio/positions'),
    ('pnl_summary','/portfolio/positions/pnl/summary'),
    ('pnl_historic','/portfolio/positions/pnl/historic'),
    ('ledger','/ledger'),
]:
    r=s.get(BASE+ep,headers=headers,timeout=12)
    res[k]={'status':r.status_code,'body':r.text[:500]}

open('logs/_audit_trade_workflow.json','w',encoding='utf-8').write(json.dumps(res,indent=2))
print('WROTE logs/_audit_trade_workflow.json')
print('order_place_idx',res['order_place_idx']['status'])
print('order_bad_qty',res['order_bad_qty']['status'])
print('order_bad_token_type',res['order_bad_token_type']['status'])
