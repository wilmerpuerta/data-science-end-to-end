from pathlib import Path
from datetime import datetime,timezone
import os,sys,json
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
os.environ['PSET3_V2_ROOT']=str(ROOT);os.environ['JUPYTER_PATH']=str(ROOT/'.local/share/jupyter');sys.path.insert(0,str(ROOT))
from src.common import sha256,read_bundle
for name in ['01_eda.ipynb','02_features.ipynb']:
 path=ROOT/'notebooks'/name;marker=ROOT/'docs'/(name[:2]+'-verificacion.json')
 if marker.exists():
  saved=json.loads(marker.read_text());assert saved['notebook_sha256']==sha256(path);print(name+' ya ejecutado y verificado');continue
 nb=nbformat.read(path,as_version=4)
 NotebookClient(nb,timeout=600,kernel_name='pset3-v2',resources={'metadata':{'path':str(ROOT)}}).execute()
 nbformat.write(nb,path)
 code=[c for c in nb.cells if c.cell_type=='code'];assert all(c.execution_count is not None and not any(o.output_type=='error' for o in c.outputs) for c in code)
 rep={'status':'ok','checked_at_utc':datetime.now(timezone.utc).isoformat(),'notebook_sha256':sha256(path),'fresh_kernel':True,'code_cells':len(code),'snapshot_id':read_bundle()[1]['id'],'split_id':read_bundle('splits-current.json')[1]['id'],'new_classifier_fits':0,'new_holdout_analysis':False}
 marker.write_text(json.dumps(rep,indent=2));print(json.dumps(rep),flush=True)
