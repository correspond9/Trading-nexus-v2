import requests, json
base='http://72.62.228.112:8000/api/v1'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466','Content-Type':'application/json'}
app='aw8kowwwgc4w40cg48840css'
payload={
  'name':'learn-trading-nexus',
  'build_pack':'dockercompose',
  'git_repository':'https://github.com/correspond9/Trading-nexus-v2.git',
  'git_branch':'main',
  'docker_compose_location':'/learn-trading-nexus/docker-compose.coolify.yml',
  'docker_compose_domains':[{'name':'learn','domain':'https://learn.tradingnexus.pro'}],
  'ports_exposes':'3000',
  'instant_deploy': True,
  'is_auto_deploy_enabled': True,
  'autogenerate_domain': False,
  'force_domain_override': True
}
r=requests.patch(base+f'/applications/{app}',headers=h,json=payload,timeout=45)
print('patch',r.status_code)
print(r.text[:2400])
