"""Sondeo interno: rechazo de comandos libres y reutilización de trabajos existentes."""
from pathlib import Path
import argparse,json,re,urllib.request,urllib.error
p=argparse.ArgumentParser();p.add_argument('--execution-id',required=True);a=p.parse_args()
assert re.fullmatch('[A-Za-z0-9_-]{1,100}',a.execution_id)
report={'execution_id':a.execution_id,'status':'ok','workers':{}}
for kind in ['dbt','spark']:
    def call(path,data=None):
        req=urllib.request.Request('http://'+kind+'-runner:8090'+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=10) as response:return response.status,json.loads(response.read())
        except urllib.error.HTTPError as e:return e.code,None
    assert call('/health')[0]==200
    assert call('/jobs',{'execution_id':'invalid_api_probe','command':'not_allowed'})[0]==400
    assert call('/jobs/invalid_api_probe')[0]==404
    result={'health_ok':True,'arbitrary_command_rejected':True,'invalid_request_started_no_job':True}
    status,before=call('/jobs/'+a.execution_id)
    if status==200 and before['state'] in ['QUEUED','RUNNING','SUCCESS']:
        status,after=call('/jobs',{'execution_id':a.execution_id})
        assert status==200 and after['job_id']==before['job_id'] and after['attempt']==before['attempt']
        result.update(duplicate_post_reused_job=True,job_id=after['job_id'],attempt=after['attempt'])
    report['workers'][kind]=result
folder=Path('/workspace/pipeline')/a.execution_id;folder.mkdir(parents=True,exist_ok=True)
(folder/'api-probe.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
