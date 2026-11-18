"""Importa solo los dos bundles privados originales y crea un kernelspec local."""
from pathlib import Path
import argparse,json,shutil,sys,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.common import read_bundle,sha256,identity
parser=argparse.ArgumentParser();parser.add_argument('--origen-local',type=Path);args=parser.parse_args()
assert sys.version_info[:2]==(3,11),'Usar el entorno Python 3.11 con requirements.lock.txt'
local=ROOT/'.local';local.mkdir(exist_ok=True);os.chmod(local,0o700);config=json.loads((ROOT/'config/protocolo-v2.json').read_text())
for pointer,expected in [('snapshot-current.json',config['snapshot_id']),('splits-current.json',config['split_id'])]:
 if not (local/pointer).exists():
  if args.origen_local is None:raise RuntimeError('Se requiere --origen-local con los bundles privados congelados; no se publican en GitHub')
  origin=args.origen_local.resolve();ref=json.loads((origin/pointer).read_text());folder=(origin/ref['directory']).resolve();assert origin in folder.parents
  manifest=json.loads((folder/'manifest.json').read_text());assert ref['id']==manifest['id']==identity(manifest['identity'])==expected
  for name,info in manifest['identity']['files'].items():assert Path(name).name==name and sha256(folder/name)==info['sha256']
  target=local/ref['directory'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(folder,target,dirs_exist_ok=False);shutil.copyfile(origin/pointer,local/pointer)
 _,manifest=read_bundle(pointer);assert manifest['id']==expected
kernel=local/'share/jupyter/kernels/pset3-v2';kernel.mkdir(parents=True,exist_ok=True);(kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'PSet3 v2 · Python 3.11','language':'python'},indent=2))
print('Bundles originales verificados; kernel local preparado. Usar JUPYTER_PATH='+str(local/'share/jupyter'))
