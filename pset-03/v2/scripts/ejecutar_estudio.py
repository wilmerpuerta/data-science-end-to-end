"""Ejecuta las fases autorizadas y actualiza estado; se detiene ante cualquier fallo."""
from pathlib import Path
from datetime import datetime,timezone
import sys,os,json,time,subprocess,fcntl,argparse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['PSET3_V2_ROOT']=str(ROOT)
from src.costos import LibroCostos
from src.seguimiento import protocolo,commit_actual
PHASES=[('modelos','ejecutar_comparacion.py'),('tuning','ejecutar_tuning.py'),('ablacion','ejecutar_ablacion.py'),('negocio','ejecutar_negocio.py'),('anticipacion','ejecutar_anticipacion.py'),('seleccion','ejecutar_seleccion.py'),('reproduccion','reproducir.py')]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--desde',choices=[p for p,_ in PHASES],default='modelos');args=parser.parse_args();plan=protocolo();private=ROOT/'.local';status=ROOT/'docs/estado-v2.json';book=LibroCostos(private/'llm/costos.json',10)
 with (private/'ejecucion-v2.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise RuntimeError('Ya hay un coordinador v2 activo; no ejecutar dos estudios')
  state={'state':'running','started_at_utc':datetime.now(timezone.utc).isoformat(),'coordinator_pid':os.getpid(),'code_commit':commit_actual(),'protocol_id':plan['id'],'complete':False,'experiments_complete':False,'unit_tests':40,'notebooks_executed':['01_eda.ipynb','02_features.ipynb'],'finished_phases':[],'backup_v1_verified':True,'old_attempt_preserved':'.local/attempts/intento_1','limits':['2014J observed in v1; reused retrospective benchmark','API upper accounted cost includes all attempts and integration tests','new memo and remaining notebooks are separate editorial closure']}
  def publish():
   state.update(updated_at_utc=datetime.now(timezone.utc).isoformat(),api_budget=book.summary());temp=status.with_suffix('.tmp');temp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n');temp.replace(status)
  start=[p for p,_ in PHASES].index(args.desde)
  for phase,script in PHASES[start:]:
   logfile=private/('definitivo-'+phase+'.log');state.update(state='running',phase=phase,log=str(logfile.relative_to(ROOT)));publish()
   with logfile.open('a') as log:
    log.write('\nNueva ejecución del coordinador: '+datetime.now(timezone.utc).isoformat()+'\n');log.flush()
    process=subprocess.Popen([sys.executable,str(ROOT/'scripts'/script)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);state['phase_pid']=process.pid;publish()
    while process.poll() is None:time.sleep(10);publish()
   if process.returncode:
    state.update(state='failed_requires_inspection',failed_phase=phase,exit_code=process.returncode);publish();raise SystemExit(process.returncode)
   state['finished_phases'].append(phase);publish()
  state.update(state='experiments_complete_documents_pending',experiments_complete=True,complete=False,remaining=['execute final notebooks with saved outputs','real MLflow UI capture','legible six-page memo','rubric audit','public delivery ZIP']);publish();print(json.dumps(state,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
