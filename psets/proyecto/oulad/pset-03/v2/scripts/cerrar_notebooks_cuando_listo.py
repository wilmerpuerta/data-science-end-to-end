"""Espera el estudio real y ejecuta el cierre de notebooks; no entrena ni llama a OpenAI."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,time,os,fcntl,subprocess
ROOT=Path(__file__).resolve().parents[1];OUTPUT=ROOT/'docs/cierre-notebooks.json'
def publish(state,**extra):OUTPUT.write_text(json.dumps({'state':state,'pid':os.getpid(),'updated_at_utc':datetime.now(timezone.utc).isoformat(),**extra},ensure_ascii=False,indent=2)+'\n')
def main():
 with (ROOT/'.local/cierre-notebooks.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise RuntimeError('Ya hay un cierre de notebooks en espera')
  publish('waiting_for_experiments')
  while True:
   try:state=json.loads((ROOT/'docs/estado-v2.json').read_text())
   except (FileNotFoundError,json.JSONDecodeError):time.sleep(10);continue
   if state.get('state','').startswith('failed'):
    publish('blocked_by_experiment_failure',failed_phase=state.get('failed_phase'));return
   if state.get('experiments_complete') is True:break
   publish('waiting_for_experiments',current_phase=state.get('phase'));time.sleep(20)
  publish('executing_notebooks')
  for script in ['ejecutar_notebooks_finales.py','verificar_avance_rubrica.py']:
   result=subprocess.run([sys.executable,str(ROOT/'scripts'/script)],cwd=ROOT)
   if result.returncode:publish('failed_requires_inspection',failed_script=script,exit_code=result.returncode);raise SystemExit(result.returncode)
  publish('notebooks_verified_editorial_pending',remaining=['memo','MLflow capture','final audit','ZIP'])
if __name__=='__main__':main()
