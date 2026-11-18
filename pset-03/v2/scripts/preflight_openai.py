"""Una sola prueba sintética; sin filas del estudio, sin reintentos automáticos."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,os
import numpy as np,requests
ROOT=Path(__file__).resolve().parents[1];os.environ['PSET3_V2_ROOT']=str(ROOT);sys.path.insert(0,str(ROOT))
from src.openai_api import settings,credential_status,ResponsesClient,MODEL

def main():
 destination=ROOT/'docs/preflight-openai.json';client=ResponsesClient();c=settings();status=credential_status()
 report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'model':MODEL,'synthetic_only':True,'study_rows_sent':0}
 try:
  if not status['configured']:raise RuntimeError('missing_key')
  response=requests.get('https://api.openai.com/v1/models',headers={'Authorization':'Bearer '+c['OPENAI_API_KEY'].strip()},timeout=30)
  if response.status_code!=200:raise RuntimeError('models_access_http_'+str(response.status_code))
  ids={x['id'] for x in response.json()['data']};report['selected_model_accessible']=MODEL in ids
  if MODEL not in ids:raise RuntimeError('selected_model_unavailable')
  p,meta=client.predict_batch('Return three nonnegative probabilities summing to one, ordered Approved, Fail, Withdrawn. This is a synthetic connectivity test, not a study evaluation.',json.dumps({'training_prior':[.55,.3,.15],'queries':[[0,1],[1,0]]}),2)
  a=np.asarray(p);assert a.shape==(2,3) and np.isfinite(a).all() and (a>=0).all() and (a<=1).all() and np.allclose(a.sum(axis=1),1,atol=.02)
  report.update(status='ok',structured_output_checked=True,cache_hit=meta['cache_hit'],response_request_hash=meta['request_hash'])
 except Exception as exc:
  # Solo tipo/resumen saneado del cliente, jamás cabeceras, clave o filas.
  message=str(exc) if isinstance(exc,(RuntimeError,AssertionError)) else type(exc).__name__
  report.update(status='pending_api_resources',error=message)
 finally:
  report['budget']=client.book.summary();destination.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
 if report['status']!='ok':raise SystemExit(2)
 return report
if __name__=='__main__':main()
