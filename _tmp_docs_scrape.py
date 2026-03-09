import requests,re
base='http://72.62.228.112:8000'
html=requests.get(base+'/docs',timeout=20).text
scripts=re.findall(r'<script[^>]+src="([^"]+)"',html)
print('scripts',scripts[:10])
for s in scripts[:6]:
 url=s if s.startswith('http') else base+s
 try:
  t=requests.get(url,timeout=20).text
  if '/api/v1/' in t:
   print('\nFOUND in',url,'len',len(t))
   idx=t.find('/api/v1/')
   print(t[idx-200:idx+600])
 except Exception as e:
  print('err',url,e)
