"""ZIP académico público con manifiesto interno; excluye runtime privado y estados volátiles."""
from pathlib import Path
import os,sys,json,hashlib,stat,zipfile,subprocess
ROOT=Path(__file__).resolve().parents[1];B=ROOT.parent;REPO=ROOT.parents[1]
EXCLUDE={'v2/docs/estado-v2.json','v2/docs/cierre-notebooks.json','v2/docs/matriz-rubrica-v2.json','v2/docs/matriz-rubrica-v2.md','v2/docs/preparacion-v2.json','v2/docs/recursos-autorizados.json','v2/docs/respaldo-v1.json','v2/docs/estructura-entrega.json','v2/docs/publicacion-github.json','v2/docs/respaldo-final.json','v2/docs/entrega-verificacion.json'}
FORBIDDEN={'.local','.venv','.secrets','backups','tmp','__pycache__'}
def digest(data):return hashlib.sha256(data).hexdigest()
def main():
 tracked=subprocess.run(['git','ls-files','-z','--','pset-03'],cwd=REPO,capture_output=True,check=True).stdout.decode().split('\0');files=[]
 for rel in tracked:
  if not rel:continue
  path=REPO/rel;inside=str(path.relative_to(B))
  if inside in EXCLUDE or path.suffix=='.zip' or inside.startswith('v2/output/'):continue
  if any(p in FORBIDDEN for p in path.relative_to(B).parts) or path.name=='.env' or path.suffix in ['.parquet','.pkl','.pem','.p8','.key']:raise RuntimeError('Archivo privado entre los versionados: '+inside)
  data=os.readlink(path).encode() if path.is_symlink() else path.read_bytes();files.append((inside,path,data))
 manifest={'format':'pset3.public.bundle.v2','canonical_execution_root':'pset-03/v2','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'private_runtime_excluded':True,'files':{name:{'sha256':digest(data),'bytes':len(data),'kind':'symlink' if path.is_symlink() else 'file'} for name,path,data in files}}
 output=ROOT/'output/PSet3_Puerta_Wilmer.zip';output.parent.mkdir(exist_ok=True)
 with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,path,data in files:
   entry=zipfile.ZipInfo('pset-03/'+name,date_time=(2026,11,18,0,0,0));entry.create_system=3;entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=((stat.S_IFLNK|0o777) if path.is_symlink() else (stat.S_IFREG|0o644))<<16;z.writestr(entry,data)
  z.writestr('pset-03/entrega-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
 with zipfile.ZipFile(output) as z:
  assert z.testzip() is None
  for name,info in manifest['files'].items():assert digest(z.read('pset-03/'+name))==info['sha256']
 report={'status':'ok','zip_sha256':digest(output.read_bytes()),'zip_bytes':output.stat().st_size,'files_verified':len(files),'embedded_manifest_sha256':digest(json.dumps(manifest,ensure_ascii=False,indent=2).encode()),'source_commit':manifest['source_commit'],'private_resources_included':False,'scope':'Public evidence and source; exact model/runtime reproduction needs private snapshot and MLflow backup; symlink entrypoints optional, canonical v2 contains real files.'}
 (ROOT/'docs/entrega-verificacion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');output.with_suffix('.zip.sha256').write_text(report['zip_sha256']+'  '+output.name+'\n');print(json.dumps(report,indent=2));return report
if __name__=='__main__':main()
