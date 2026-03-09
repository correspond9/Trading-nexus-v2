import requests, json, time
base='http://72.62.228.112:8000/api/v1'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466','Content-Type':'application/json'}
payload={
  'project_uuid':'i8k44sw0gsg8ocoogw8s0ook',
  'environment_uuid':'qw8k0k0sc0gg0ogkcck0g4ss',
  'server_uuid':'zk0wks40sw4cw8gg8s8kogko',
  'destination_uuid':'y8scs44gwc0gcw88ggcwwcko',
  'name':'learn-trading-nexus-'+str(int(time.time())),
  'git_repository':'https://github.com/correspond9/Trading-nexus-v2.git',
  'git_branch':'main',
  'build_pack':'dockercompose',
  'docker_compose_location':'/docker-compose.prod.yml',
  'ports_exposes':'80',
  'instant_deploy': False,
  'is_auto_deploy_enabled': True
}
r=requests.post(base+'/applications/public',headers=h,json=payload,timeout=30)
print('status',r.status_code)
print(r.text[:2000])
