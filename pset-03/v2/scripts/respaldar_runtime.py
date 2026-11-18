"""Respaldo privado sellado: workspace v2, SQLite, artefactos e imagen exacta; no publica."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,tarfile,hashlib,os,sqlite3,tempfile
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
DEST=REPO/'backups'/('pset-03-v2-final-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S'))
DEST.mkdir(parents=True,mode=0o700);os.chmod(DEST,0o700)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
 return h.hexdigest()
def manifest(root):
 out={}
 for p in sorted(root.rglob('*')):
  if p.is_symlink():out[str(p.relative_to(root))]={'kind':'symlink','target':os.readlink(p)}
  elif p.is_file():out[str(p.relative_to(root))]={'kind':'file','bytes':p.stat().st_size,'sha256':sha(p)}
 return out
def verify(archive,expected):
 actual={}
 with tarfile.open(archive,'r|gz') as tar:
  for member in tar:
   name=member.name[2:] if member.name.startswith('./') else member.name
   if member.isfile():
    h=hashlib.sha256();f=tar.extractfile(member)
    for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    actual[name]={'kind':'file','bytes':member.size,'sha256':h.hexdigest()}
   elif member.issym():actual[name]={'kind':'symlink','target':member.linkname}
   elif member.islnk():
    target=member.linkname[2:] if member.linkname.startswith('./') else member.linkname
    actual[name]=actual[target].copy()
 assert actual==expected,'El archivo no coincide con el manifiesto'
 return len(actual)
compose=['docker','compose','-f',str(ROOT.parent/'docker-compose.yml')];cid=subprocess.check_output(compose+['ps','-q','mlflow'],text=True).strip();info=json.loads(subprocess.check_output(['docker','inspect',cid],text=True))[0];assert info['State']['Running']
volumes={m['Destination']:m['Name'] for m in info['Mounts'] if m['Type']=='volume'};subprocess.run(['docker','stop',cid],check=True,stdout=subprocess.DEVNULL)
container_code="""from pathlib import Path
import tarfile,json,hashlib,os
r=Path('/src');name=os.environ['BACKUP_NAME'];out={}
for p in sorted(r.rglob('*')):
 if p.is_symlink():out[str(p.relative_to(r))]={'kind':'symlink','target':os.readlink(p)}
 elif p.is_file():
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  out[str(p.relative_to(r))]={'kind':'file','bytes':p.stat().st_size,'sha256':h.hexdigest()}
with tarfile.open('/backup/'+name+'.tar.gz','w:gz') as t:
 for p in sorted(r.iterdir()):t.add(p,arcname=p.name)
Path('/backup/'+name+'-manifest.json').write_text(json.dumps(out,indent=2))
"""
try:
 for target,volume in volumes.items():
  name='backend' if target.endswith('backend') else 'artifacts'
  subprocess.run(['docker','run','--rm','-v',volume+':/src:ro','-v',str(DEST)+':/backup','-e','BACKUP_NAME='+name,'pset3-mlflow-repro-final','python','-c',container_code],check=True)
finally:subprocess.run(['docker','start',cid],check=True,stdout=subprocess.DEVNULL)
print('Volúmenes copiados y servidor original reiniciado.',flush=True)
workspace=manifest(ROOT);(DEST/'workspace-manifest.json').write_text(json.dumps(workspace,indent=2))
with tarfile.open(DEST/'workspace.tar.gz','w:gz') as t:
 for p in sorted(ROOT.iterdir()):t.add(p,arcname=p.name)
verified={}
for name in ['workspace','backend','artifacts']:
 expected=workspace if name=='workspace' else json.loads((DEST/(name+'-manifest.json')).read_text());verified[name]=verify(DEST/(name+'.tar.gz'),expected)
with tempfile.TemporaryDirectory() as temp:
 with tarfile.open(DEST/'backend.tar.gz') as t:
  member=next(m for m in t.getmembers() if m.name.endswith('mlflow.db'));db=Path(temp)/'mlflow.db';db.write_bytes(t.extractfile(member).read())
 conn=sqlite3.connect(str(db));integrity=conn.execute('PRAGMA integrity_check').fetchone()[0];count=conn.execute('SELECT count(*) FROM runs').fetchone()[0];versions=conn.execute('SELECT count(*) FROM model_versions').fetchone()[0];conn.close();assert integrity=='ok'
old=REPO/'backups/pset-03-v1-20261117-225736/mlflow-image.tar';state_path=Path('/private/tmp/pset3-rebuild/state.json');state=json.loads(state_path.read_text()) if state_path.exists() else {}
if old.exists() and state.get('image')==info['Image']:os.link(old,DEST/'mlflow-image.tar')
else:subprocess.run(['docker','image','save','-o',str(DEST/'mlflow-image.tar'),info['Image']],check=True)
subprocess.run(['git','bundle','create',str(DEST/'source-history.bundle'),'main'],cwd=REPO,check=True)
checks={p.name:sha(p) for p in DEST.iterdir() if p.is_file()};(DEST/'checksums.json').write_text(json.dumps(checks,indent=2))
report={'status':'verified','created_at_utc':datetime.now(timezone.utc).isoformat(),'backup_relative':str(DEST.relative_to(REPO)),'entries_verified':verified,'sqlite_integrity':integrity,'sqlite_runs':count,'model_versions':versions,'image_id':info['Image'],'volumes':volumes,'credential_keys_included':False,'external_dependencies':'Provision pinned Python runtime; workspace virtualenv includes external Python symlinks. API keys are managed outside v2 and excluded. Restore original volume contents and image before exact Registry reproduction.'}
(DEST/'backup-verificacion.json').write_text(json.dumps(report,indent=2));(ROOT/'docs/respaldo-final.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
