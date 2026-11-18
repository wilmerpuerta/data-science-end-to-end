"""Estudio autorizado; recuperación acotada de JSON completo sin regenerar predicciones."""
from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal
import sys,os,json,time,subprocess,fcntl,argparse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['PSET3_V2_ROOT']=str(ROOT)
from src.costos import LibroCostos
from src.seguimiento import protocolo,commit_actual
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

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--desde',choices=[p for p,_ in PHASES],default='modelos');args=parser.parse_args();plan=protocolo();private=ROOT/'.local';status=ROOT/'docs/estado-v2.json';book=LibroCostos(private/'llm/costos.json',10)
 with (private/'ejecucion-v2.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise RuntimeError('Ya hay un coordinador v2 activo; no ejecutar dos estudios')
  state={'state':'running','started_at_utc':datetime.now(timezone.utc).isoformat(),'coordinator_pid':os.getpid(),'code_commit':commit_actual(),'protocol_id':plan['id'],'complete':False,'experiments_complete':False,'unit_tests':42,'notebooks_executed':['01_eda.ipynb','02_features.ipynb'],'finished_phases':[],'format_recoveries':[],'backup_v1_verified':True,'old_attempts_preserved':['.local/attempts/intento_1','.local/attempts/intento_2'],'limits':['2014J observed in v1; reused retrospective benchmark','API upper accounted cost includes all attempts and integration tests','format recovery only uses complete archived JSON, without changing values or re-requesting the failed batch','new memo and remaining notebooks are separate editorial closure']}
  def publish():
   state.update(updated_at_utc=datetime.now(timezone.utc).isoformat(),api_budget=book.summary());temp=status.with_suffix('.tmp');temp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n');temp.replace(status)
  start=[p for p,_ in PHASES].index(args.desde)
  for phase,script in PHASES[start:]:
   logfile=private/('definitivo-'+phase+'.log');state.update(state='running',phase=phase,log=str(logfile.relative_to(ROOT)));publish();recoveries=0
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
    state.update(state='failed_requires_inspection',failed_phase=phase,exit_code=process.returncode);publish();raise SystemExit(process.returncode)
   state['finished_phases'].append(phase);state['state']='running';publish()
  state.update(state='experiments_complete_documents_pending',experiments_complete=True,complete=False,remaining=['execute final notebooks with saved outputs','real MLflow UI capture','legible six-page memo','rubric audit','public delivery ZIP']);publish();print(json.dumps(state,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
