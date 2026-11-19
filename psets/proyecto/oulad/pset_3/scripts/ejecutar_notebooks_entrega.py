"""Reejecución de entrega en kernels nuevos, sin registrar corridas ni consumir API."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,sys,time,hashlib
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['PSET3_V2_ROOT']=str(ROOT);os.environ['JUPYTER_PATH']=str(ROOT/'.local/share/jupyter')
from src.seguimiento import protocolo
from src.costos import LibroCostos
from src.common import sha256
import mlflow
NAMES=['01_eda.ipynb','02_features.ipynb','03_baseline_candidatos.ipynb','04_tuning.ipynb','05_seleccion.ipynb','anexos/06_anticipacion.ipynb']
def main():
 plan=protocolo();book=LibroCostos(ROOT/'.local/llm/costos.json',10);before=book.summary();mlflow.set_tracking_uri('http://127.0.0.1:5001');client=mlflow.MlflowClient();exp=client.get_experiment_by_name('oulad-apoyo-academico-v2');runs_before={r.info.run_id for r in client.search_runs([exp.experiment_id],max_results=5000)}
 for name in NAMES:
  path=ROOT/'notebooks'/name;nb=nbformat.read(path,as_version=4);begin=time.perf_counter();NotebookClient(nb,timeout=900,kernel_name='pset3-entrega',resources={'metadata':{'path':str(ROOT)}}).execute();cells=[c for c in nb.cells if c.cell_type=='code'];assert all(c.execution_count is not None and not any(o.output_type=='error' for o in c.outputs) for c in cells);assert book.summary()==before
  nb.metadata['pset3']={**nb.metadata.get('pset3',{}),'state':'executed_verified','distribution':'pset_3'};nbformat.write(nb,path)
  record={'status':'ok','checked_at_utc':datetime.now(timezone.utc).isoformat(),'notebook_sha256':sha256(path),'fresh_kernel':True,'code_cells':len(cells),'elapsed_seconds':time.perf_counter()-begin,'protocol_id':plan['id'],'distribution_patch_id':plan['distribution_patch_id'],'new_model_fits':0,'new_classifier_fits':0,'new_api_requests':0,'scope':'Packaged paths; recompute EDA/preparation and replay original recorded evidence; no new experiment runs'}
  (ROOT/'docs'/(Path(name).name[:2]+'-verificacion.json')).write_text(json.dumps(record,indent=2)+'\n');print(name+': OK',flush=True)
 runs_after={r.info.run_id for r in client.search_runs([exp.experiment_id],max_results=5000)};assert runs_before==runs_after
 (ROOT/'docs/portabilidad/notebooks-reproducidos.json').write_text(json.dumps({'status':'ok','notebooks':NAMES,'runs_before':len(runs_before),'runs_after':len(runs_after),'new_api_requests':0,'budget_unchanged':True},indent=2)+'\n')
if __name__=='__main__':main()
