"""ZIP con raíz pset_3, archivos reales, manifiesto y exclusión de recursos privados."""
from pathlib import Path
import json,hashlib,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1]
REPO=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=ROOT,text=True).strip())
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 paths=subprocess.check_output(['git','ls-files','-z','--',str(ROOT.relative_to(REPO))],cwd=REPO,text=True).strip('\0').split('\0');files={}
 for rel in paths:
  if not rel:continue
  p=REPO/rel;name=p.relative_to(ROOT)
  if name.parts[0]=='output' or str(name) in ['docs/publicacion-github.json','docs/entrega-verificacion.json']:continue
  assert not p.is_symlink(),str(name)
  assert not any(x in {'.local','.venv','.secrets','tmp','__pycache__'} for x in name.parts) and p.name!='.env' and p.suffix not in {'.pkl','.parquet','.key','.pem'}
  files[str(name)]=p.read_bytes()
 required=['docker-compose.yml','.env.example','requirements.txt','README.md','src/datos.py','src/pipeline.py','docs/corridas.csv','docs/PSet3_memo_Puerta_Wilmer.pdf']+[f'notebooks/{n}' for n in ['01_eda.ipynb','02_features.ipynb','03_baseline_candidatos.ipynb','04_tuning.ipynb','05_seleccion.ipynb']]
 assert set(required)<=set(files)
 manifest={'root':'pset_3','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'files':{k:{'bytes':len(v),'sha256':sha(v)} for k,v in files.items()},'private_runtime_included':False,'symlinks':0}
 out=ROOT/'output/PSet3_Puerta_Wilmer.zip';out.parent.mkdir(exist_ok=True)
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in files.items():z.writestr('pset_3/'+name,data)
  z.writestr('pset_3/entrega-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  for name,data in files.items():assert z.read('pset_3/'+name)==data
 report={'status':'ok','root':'pset_3','files_verified':len(files),'zip_sha256':sha(out.read_bytes()),'zip_bytes':out.stat().st_size,'required_paths_verified':required,'symlinks':0,'private_resources_included':False,'source_commit':manifest['source_commit']}
 (ROOT/'docs/entrega-verificacion.json').write_text(json.dumps(report,indent=2)+'\n');out.with_suffix('.zip.sha256').write_text(report['zip_sha256']+'  '+out.name+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
