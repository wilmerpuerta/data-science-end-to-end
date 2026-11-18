from pathlib import Path
import sys,json,os
import numpy as np
R=Path(__file__).resolve().parents[1];os.environ['PSET3_V2_ROOT']=str(R);sys.path.insert(0,str(R))
import requests
from src.openai_api import settings,credential_status,ResponsesClient,MODEL
c=settings();status=credential_status()
if not status['configured']:
 print(json.dumps({'status':'missing_key',**status}));raise SystemExit(0)
r=requests.get('https://api.openai.com/v1/models',headers={'Authorization':'Bearer '+c['OPENAI_API_KEY'].strip()},timeout=30)
if r.status_code!=200:raise RuntimeError('No se pudo validar acceso a OpenAI, HTTP '+str(r.status_code))
ids={x['id'] for x in r.json()['data']}
public_choices=[x for x in [MODEL,'gpt-5-nano','gpt-4o-mini-2024-07-18','gpt-4o-mini'] if x in ids]
print(json.dumps({'status':'models_access_checked','selected_model':MODEL,'selected_accessible':MODEL in ids,'available_public_alternatives':public_choices}),flush=True)
if MODEL not in ids:
 (R/'docs/preflight-openai.json').write_text(json.dumps({'status':'selected_model_unavailable','model':MODEL,'available_public_alternatives':public_choices},indent=2));raise SystemExit(0)
client=ResponsesClient();p,meta=client.predict_batch('Return three nonnegative probabilities summing to one, ordered Approved, Fail, Withdrawn. This is a synthetic connectivity test, not a study evaluation.',json.dumps({'training_prior':[.55,.3,.15],'queries':[[0,1],[1,0]]}),2)
a=np.asarray(p);assert a.shape==(2,3) and np.isfinite(a).all() and (a>=0).all() and np.allclose(a.sum(axis=1),1,atol=.02)
report={'status':'ok','model':MODEL,'synthetic_only':True,'study_rows_sent':0,'budget':client.book.summary(),'cache_hit':meta['cache_hit'],'response_request_hash':meta['request_hash'],'structured_output_checked':True}
(R/'docs/preflight-openai.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
