"""Restart/Run All en kernels nuevos de 03-06, cuando todo el estudio esté terminado."""
from pathlib import Path
from datetime import datetime,timezone
import os,sys,json,time
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['PSET3_V2_ROOT']=str(ROOT);os.environ['JUPYTER_PATH']=str(ROOT/'.local/share/jupyter')
from src.common import sha256
from src.seguimiento import protocolo
from src.costos import LibroCostos
NAMES=['03_baseline_candidatos.ipynb','04_tuning.ipynb','05_seleccion.ipynb','anexos/06_anticipacion.ipynb']

def main():
 plan=protocolo();statuspath=ROOT/'docs/estado-v2.json';state=json.loads(statuspath.read_text())
 if state.get('experiments_complete') is not True:raise RuntimeError('Esperar al cierre del coordinador; no ejecutar notebooks contra un estudio incompleto')
 book=LibroCostos(ROOT/'.local/llm/costos.json',10);before=book.summary()
 for name in NAMES:
  path=ROOT/'notebooks'/name;marker=ROOT/'docs'/(Path(name).name[:2]+'-verificacion.json')
  if marker.exists():
   old=json.loads(marker.read_text());assert old['notebook_sha256']==sha256(path) and old['fresh_kernel'];print('Notebook verificado existente: '+name,flush=True);continue
  nb=nbformat.read(path,as_version=4);start=time.perf_counter();NotebookClient(nb,timeout=900,kernel_name='pset3-v2',resources={'metadata':{'path':str(ROOT)}}).execute()
  cells=[c for c in nb.cells if c.cell_type=='code'];assert cells and all(c.execution_count is not None and not any(o.output_type=='error' for o in c.outputs) for c in cells)
  after=book.summary();assert after['completed_paid_calls']==before['completed_paid_calls'] and after['accounted_spend_usd']==before['accounted_spend_usd'],'Los notebooks finales deben usar resultados/caché, sin nuevas llamadas API'
  nb.metadata.pset3.state='executed_verified';nbformat.write(nb,path)
  verification={'status':'ok','checked_at_utc':datetime.now(timezone.utc).isoformat(),'notebook_sha256':sha256(path),'fresh_kernel':True,'code_cells':len(cells),'elapsed_seconds':time.perf_counter()-start,'protocol_id':plan['id'],'new_model_fits':0,'new_api_requests':0,'scope':'reads actual experiment results and reproduces frozen decisions; notebook05 verifies already-recorded test metrics in a separate process'}
  marker.write_text(json.dumps(verification,indent=2)+'\n');print(json.dumps({'name':name,**verification}),flush=True)
 state=json.loads(statuspath.read_text());state.update(state='notebooks_complete_editorial_pending',notebooks_complete=True,notebooks_executed=['01_eda.ipynb','02_features.ipynb']+NAMES,remaining=['real MLflow comparison capture','legible six-page memo and visual review','final rubric audit','public delivery ZIP'],updated_at_utc=datetime.now(timezone.utc).isoformat())
 statuspath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n');return state
if __name__=='__main__':main()
