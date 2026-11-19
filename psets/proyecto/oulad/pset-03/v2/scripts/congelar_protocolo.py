"""Congela entradas, código y diseño antes de cualquier clasificador del estudio v2."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,sys
ROOT=Path(__file__).resolve().parents[1];os.environ['PSET3_V2_ROOT']=str(ROOT);sys.path.insert(0,str(ROOT))
from src.common import identity,sha256,read_bundle
from src.seguimiento import commit_actual,protocolo
from src.openai_api import ResponsesClient,MODEL

def main():
 target=ROOT/'docs/protocolo-congelado.json'
 if target.exists():
  fixed=protocolo();print('Protocolo ya congelado y verificado: '+fixed['id']);return fixed
 check=ROOT/'docs/preflight-openai.json'
 if not check.exists():raise RuntimeError('Primero debe completarse un preflight sintético real de OpenAI')
 report=json.loads(check.read_text())
 if report.get('status')!='ok' or report.get('model')!=MODEL or not report.get('structured_output_checked'):raise RuntimeError('El recurso LLM todavía no permite inferencia; no iniciar el estudio definitivo')
 budget=ResponsesClient().book.summary()
 if budget['completed_paid_calls']<1 or float(budget['pending_upper_usd'])>0:raise RuntimeError('Resolver el uso API antes de congelar')
 if (ROOT/'docs/modelos/resultados.json').exists():raise RuntimeError('No se puede congelar después de comparar candidatos')
 snapshot=read_bundle()[1];split=read_bundle('splits-current.json')[1]
 config=json.loads((ROOT/'config/protocolo-v2.json').read_text())
 assert snapshot['id']==config['snapshot_id'] and split['id']==config['split_id']
 sources=['src/'+x+'.py' for x in ['common','datos','pipeline','evaluacion','modelos','costos','openai_api','llm','experimentos','tuning','seguimiento']]
 sources+=['config/espacios-tuning.json','config/feature-contract.json','requirements.txt','requirements.lock.txt']
 content={'configuration':config,'git_commit_at_freeze':commit_actual(),'training_sources':{p:sha256(ROOT/p) for p in sources},'snapshot_id':snapshot['id'],'split_id':split['id'],'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'openai_preflight_sha256':sha256(check),'budget_at_freeze':budget,'holdout_previously_observed_in_v1':True}
 fixed={'id':identity(content),'content':content,'design_state':'frozen'}
 with target.open('x') as f:json.dump(fixed,f,indent=2,ensure_ascii=False)
 assert protocolo()['id']==fixed['id'];print(json.dumps({'status':'frozen','protocol_id':fixed['id'],'holdout_evaluated_in_v2':False}));return fixed
if __name__=='__main__':main()
