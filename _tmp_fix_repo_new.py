import requests
base='http://72.62.228.112:8000/api/v1'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466','Content-Type':'application/json'}
app='aw8kowwwgc4w40cg48840css'
payload={
  'git_repository':'correspond9/Trading-nexus-v2',
  'git_branch':'main',
  'docker_compose_location':'/learn-trading-nexus/docker-compose.coolify.yml',
  'docker_compose_domains':[{'name':'learn','domain':'https://learn.tradingnexus.pro'}],
  'name':'learn-trading-nexus',
  'build_pack':'dockercompose',
  'force_domain_override': True,
  'instant_deploy': True
}
r=requests.patch(base+f'/applications/{app}',headers=h,json=payload,timeout=35)
print(r.status_code)
print(r.text[:2000])
rs=requests.post(base+f'/applications/{app}/start',headers=h,timeout=25)
print('start',rs.status_code,rs.text)
