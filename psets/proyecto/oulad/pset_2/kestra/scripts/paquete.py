"""Inventario público acotado a esta entrega; funciona también fuera de Git."""
from pathlib import Path
import hashlib,json,zipfile
BASE=Path(__file__).resolve().parents[2]
PRIVATE={'.git','.venv','.local','.secrets','secrets','__pycache__','.retry-probes','target','logs','dbt_packages','.ipynb_checkpoints'}
PRIVATE_SUFFIXES={'.pem','.p8','.key','.pub','.pyc','.parquet','.jar','.csv','.log','.tmp','.zip'}
ROOT_FILES={'docker-compose.yml','.env.example','.gitignore','README.md'}
FOLDERS={'kestra','dbt','spark','docs'}
def public_files():
 result=[]
 for p in sorted(BASE.rglob('*')):
  rel=p.relative_to(BASE)
  if set(rel.parts)&PRIVATE or p.is_symlink() or not p.is_file():continue
  if rel.parts[0] not in FOLDERS and str(rel) not in ROOT_FILES:continue
  if p.name.startswith('.env') and p.name!='.env.example':continue
  if p.suffix in PRIVATE_SUFFIXES or p.name.endswith('.local.sql') or p.name=='.DS_Store':continue
  result.append(p)
 return result
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 files=[p for p in public_files() if p.relative_to(BASE).as_posix() not in {'docs/entrega-verificacion.json','docs/publicacion-github.json','docs/entrega-manifest.json'}]
 manifest={'root':'pset_2','files':{p.relative_to(BASE).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files},'private_resources_included':False}
 target=BASE.parent/'PSet2_entrega_Puerta_Wilmer.zip'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in files:z.write(p,'pset_2/'+p.relative_to(BASE).as_posix())
  z.writestr('pset_2/docs/entrega-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  for name,entry in manifest['files'].items():assert hashlib.sha256(z.read('pset_2/'+name)).hexdigest()==entry['sha256']
 report={'status':'ok','files':len(files),'zip_bytes':target.stat().st_size,'zip_sha256':sha(target),'private_resources_included':False,'root':'pset_2'}
 (BASE/'docs/entrega-verificacion.json').write_text(json.dumps(report,indent=2)+'\n')
 target.with_suffix('.zip.sha256').write_text(report['zip_sha256']+'  '+target.name+'\n')
 print(json.dumps(report))
if __name__=='__main__':main()
