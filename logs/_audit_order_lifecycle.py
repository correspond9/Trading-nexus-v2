import requests, json
BASE='http://localhost:8000/api/v2'
s=requests.Session()
login=s.post(BASE+'/auth/login',json={'mobile':'7777777777','password':'user123'},timeout=10).json()
headers={'X-AUTH':login['access_token'],'Authorization':f"Bearer {login['access_token']}"}

live=s.get(BASE+'/options/live',params={'underlying':'NIFTY','expiry':'2026-03-10','strikes_around':5},headers=headers,timeout=12)
res={'live_status':live.status_code}
if live.status_code==200:
    d=live.json();
    tok=None; price=None; symbol='NIFTY'
    strikes=d.get('strikes',{})
    for k,v in strikes.items():
        ce=(v or {}).get('CE')
        if ce and ce.get('instrument_token') and ce.get('ltp'):
            tok=ce['instrument_token']; price=float(ce['ltp']); break
    res['picked']={'token':tok,'price':price}
    if tok:
        payload={
          'instrument_token':int(tok),
          'exchange_segment':'NSE_FNO',
          'side':'BUY',
          'quantity':1,
          'order_type':'LIMIT',
          'product_type':'NORMAL',
          'limit_price':price
        }
        o=s.post(BASE+'/trading/orders',headers=headers,json=payload,timeout=15)
        res['place_limit']={'status':o.status_code,'body':o.text[:500]}
        orders=s.get(BASE+'/trading/orders',headers=headers,timeout=12)
        res['orders_after']={'status':orders.status_code,'body':orders.text[:900]}
        if orders.status_code==200 and 'order_id' in orders.text:
            try:
                arr=orders.json().get('data',[])
                if arr:
                    oid=arr[0].get('order_id')
                    if oid:
                        c=s.delete(BASE+f'/trading/orders/{oid}',headers=headers,timeout=12)
                        res['cancel_first']={'status':c.status_code,'body':c.text[:300]}
            except Exception as e:
                res['cancel_first']={'status':'ERR','body':str(e)}

open('logs/_audit_order_lifecycle.json','w',encoding='utf-8').write(json.dumps(res,indent=2))
print('WROTE logs/_audit_order_lifecycle.json')
print(json.dumps(res)[:900])
