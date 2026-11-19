"""Estudio autorizado; recuperación acotada de JSON completo sin regenerar predicciones."""
from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal
import sys,os,json,time,subprocess,fcntl,argparse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['PSET3_V2_ROOT']=str(ROOT)
from src.costos import LibroCostos
from src.seguimiento import protocolo,commit_actual
from src.common import identity
PHASES=[('modelos','ejecutar_comparacion.py'),('tuning','ejecutar_tuning.py'),('ablacion','ejecutar_ablacion.py'),('negocio','ejecutar_negocio.py'),('anticipacion','ejecutar_anticipacion.py'),('seleccion','ejecutar_seleccion.py'),('reproduccion','reproducir.py')]
MAX_FORMAT_RECOVERIES=10

def can_recover(text,budget):
 return 'Salida no interpretable; cobro y respuesta archivados' in text and Decimal(budget['pending_upper_usd'])==0

def recover_format(text,book):
 if not can_recover(text,book.summary()):return []
 with (ROOT/'.local/recuperacion-formatos.log').open('a') as log:
  result=subprocess.run([sys.executable,str(ROOT/'scripts/recuperar_respuestas_llm.py')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:return []
 event=json.loads((ROOT/'docs/recuperacion-respuestas-llm.json').read_text())['events'][-1]
 if event['status']!='ok' or event['new_api_requests']!=0 or not event['recovered']:return []
 if any(r['probabilities_changed'] or r['new_api_requests'] for r in event['recovered']):raise RuntimeError('Recuperación incompatible con el protocolo')
 return [r['request_hash'] for r in event['recovered']]

def rejected_request(text):
 marker='OpenAI rechazó la petición: '
 if marker not in text:return None
 try:info=json.JSONDecoder().raw_decode(text[text.rfind(marker)+len(marker):])[0]
 except (ValueError,TypeError):return None
 key=info.get('request_hash','')
 return key if info.get('http_status')==400 and info.get('code')=='invalid_prompt' and info.get('type')=='invalid_request_error' and len(key)==64 and all(c in '0123456789abcdef' for c in key) else None

def retry_unbilled_rejection(text,book,attempted):
 key=rejected_request(text)
 if key is None:return None
 events=[json.loads(line) for line in (ROOT/'.local/llm/errores.jsonl').read_text().splitlines()]
 confirmed={e['request_hash'] for e in events if e.get('http_status')==400 and e.get('code')=='invalid_prompt' and e.get('type')=='invalid_request_error'}
 if key not in confirmed:return None
 with book.locked() as ledger:pending=list(ledger['pending'].items())
 for reservation,meta in pending:
  if meta['request_hash'] in confirmed:book.release_unbilled(reservation,400)
 if Decimal(book.summary()['pending_upper_usd']) or attempted.get(key,0)>=1:return None
 return key

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--desde',choices=[p for p,_ in PHASES],default='modelos');parser.add_argument('--verificar',action='store_true');parser.add_argument('--reanudar',action='store_true');args=parser.parse_args();plan=protocolo();amendment=json.loads((ROOT/'docs/enmienda-transporte.json').read_text());assert amendment['id']==identity(amendment['content']) and amendment['content']['base_protocol_id']==plan['id'];private=ROOT/'.local';status=ROOT/'docs/estado-v2.json';book=LibroCostos(private/'llm/costos.json',10)
 existing=json.loads(status.read_text()) if status.exists() else {}
 if args.verificar or (existing.get('complete') and not args.reanudar):
  from verificar_fase import verificar
  for phase in ['modelos','tuning','ablacion','negocio','anticipacion','seleccion']:verificar(phase)
  print('Estudio finalizado verificado; sin nuevas ejecuciones. --reanudar es una acción explícita distinta.');return existing
 with (private/'ejecucion-v2.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise RuntimeError('Ya hay un coordinador v2 activo; no ejecutar dos estudios')
  state={'state':'running','started_at_utc':datetime.now(timezone.utc).isoformat(),'coordinator_pid':os.getpid(),'code_commit':commit_actual(),'protocol_id':plan['id'],'io_patch_id':plan.get('io_patch_id','original'),'complete':False,'experiments_complete':False,'unit_tests':48,'notebooks_executed':['01_eda.ipynb','02_features.ipynb'],'finished_phases':[],'format_recoveries':[],'transport_retries':[],'execution_amendment_id':amendment['id'],'backup_v1_verified':True,'old_attempts_preserved':['.local/attempts/intento_1','.local/attempts/intento_2'],'limits':['2014J observed in v1; reused retrospective benchmark','API upper accounted cost includes all attempts and integration tests','format recovery only uses complete archived JSON, without changing values or re-requesting the failed batch','new memo and remaining notebooks are separate editorial closure']}
  def publish():
   state.update(updated_at_utc=datetime.now(timezone.utc).isoformat(),api_budget=book.summary());temp=status.with_suffix('.tmp');temp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n');temp.replace(status)
  start=[p for p,_ in PHASES].index(args.desde)
  for phase,script in PHASES[start:]:
   logfile=private/('definitivo-'+phase+'.log');state.update(state='running',phase=phase,log=str(logfile.relative_to(ROOT)));publish();recoveries=0;rejection_retries={}
   while True:
    with logfile.open('a') as log:
     log.write('\nEjecución del coordinador: '+datetime.now(timezone.utc).isoformat()+'\n');log.flush();offset=log.tell()
     process=subprocess.Popen([sys.executable,str(ROOT/'scripts'/script)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);state['phase_pid']=process.pid;publish()
     while process.poll() is None:time.sleep(10);publish()
    if not process.returncode:break
    with logfile.open() as log:log.seek(offset);failure=log.read()
    recovered=recover_format(failure,book) if recoveries<MAX_FORMAT_RECOVERIES else []
    if recovered:
     recoveries+=1;state['format_recoveries'].append({'phase':phase,'at_utc':datetime.now(timezone.utc).isoformat(),'request_hashes':recovered,'new_api_requests_for_recovered_batches':0});state['state']='resuming_from_verified_cache';publish();continue
    retry_key=retry_unbilled_rejection(failure,book,rejection_retries) if sum(rejection_retries.values())<20 else None
    if retry_key:
     rejection_retries[retry_key]=1;state['transport_retries'].append({'phase':phase,'request_hash':retry_key,'previous_request_status':400,'previous_request_confirmed_unbilled':True,'maximum_retries_for_this_hash':1,'at_utc':datetime.now(timezone.utc).isoformat()});state['state']='resuming_after_unbilled_rejection';publish();continue
    state.update(state='failed_requires_inspection',failed_phase=phase,exit_code=process.returncode);publish();raise SystemExit(process.returncode)
   state['finished_phases'].append(phase);state['state']='running';publish()
  state.update(state='experiments_complete_documents_pending',experiments_complete=True,complete=False,remaining=['execute final notebooks with saved outputs','real MLflow UI capture','legible six-page memo','rubric audit','public delivery ZIP']);publish();print(json.dumps(state,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
