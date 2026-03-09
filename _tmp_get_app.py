import requests, json
u='http://72.62.228.112:8000/api/v1/applications/x8gg0og8440wkgc8ow0ococs'
h={'Authorization':'Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'}
r=requests.get(u,headers=h,timeout=20)
print(r.status_code)
d=r.json()
keys=['uuid','name','build_pack','git_repository','git_branch','source_id','destination_id','environment_id','docker_compose_location','docker_compose_raw','ports_exposes','destination_type','source_type']
for k in keys:
 print(k,':',d.get(k))
