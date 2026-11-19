"""Contrato de metadatos común, con commit real y fuente limpia antes de cada corrida."""
from pathlib import Path
import json,subprocess,hashlib,os
import mlflow
from .common import ROOT,sha256,read_bundle,identity
from .portabilidad import hash_fuente_original, raiz_git

def commit_actual():
 repo=raiz_git(ROOT)
 result=subprocess.run(['git','rev-parse','--verify','HEAD'],cwd=repo,capture_output=True,text=True)
 if result.returncode:raise RuntimeError('Crear commit del código antes de registrar corridas v2')
 paths=[str(p.relative_to(repo)) for folder in ['src','scripts','config','prompts'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 paths += [str((ROOT/name).relative_to(repo)) for name in ['requirements.txt','requirements.lock.txt']]
 for document in ['docs/enmienda-lectura-api.json','docs/enmienda-portabilidad.json']:
  if (ROOT/document).exists():paths.append(str((ROOT/document).relative_to(repo)))
 for rel in paths:
  check=subprocess.run(['git','ls-files','--error-unmatch',rel],cwd=repo,capture_output=True)
  if check.returncode:raise RuntimeError('Fuente no versionada: '+rel)
 dirty=subprocess.run(['git','diff','HEAD','--exit-code','--',*paths],cwd=repo,capture_output=True)
 if dirty.returncode:raise RuntimeError('Hay cambios de código/configuración sin commit; no se permite tag falso')
 return result.stdout.strip()

def configurar():
 mlflow.set_tracking_uri('http://127.0.0.1:5001')
 return mlflow.set_experiment('oulad-apoyo-academico-v2')

def protocolo(require_frozen=True):
 config=json.loads((ROOT/'config/protocolo-v2.json').read_text());path=ROOT/'docs/protocolo-congelado.json'
 if not path.exists():
  if require_frozen:raise RuntimeError('El protocolo definitivo aún no está congelado')
  return {'id':identity(config),'content':config,'design_state':'draft'}
 fixed=json.loads(path.read_text())
 if identity(fixed['content'])!=fixed['id'] or fixed['content']['configuration']!=config:raise RuntimeError('Protocolo cambiado después de congelar')
 commit_actual()
 changed={name:expected for name,expected in fixed['content']['training_sources'].items() if hash_fuente_original(name)!=expected}
 if changed:
  patchpath=ROOT/'docs/enmienda-lectura-api.json'
  if not patchpath.exists():raise RuntimeError('Fuentes cambiadas sin enmienda versionada: '+str(list(changed)))
  patch=json.loads(patchpath.read_text());content=patch['content']
  if identity(content)!=patch['id'] or content['base_protocol_id']!=fixed['id']:raise RuntimeError('Enmienda de lectura incompatible')
  allowed={'src/openai_api.py','src/seguimiento.py'}
  if set(content['sources'])!=set(changed) or not set(changed)<=allowed:raise RuntimeError('La enmienda no autoriza cambios del modelo')
  for name,expected in changed.items():
   if content['sources'][name]['before']!=expected or content['sources'][name]['after']!=hash_fuente_original(name):raise RuntimeError('Hash de parche incompatible: '+name)
  return {**fixed,'io_patch_id':patch['id'],'distribution_patch_id':json.loads((ROOT/'docs/enmienda-portabilidad.json').read_text())['id']}
 return fixed

def registrar_base(phase,family,extra=None,require_frozen=True):
 plan=protocolo(require_frozen);snapshot=read_bundle()[1];split=read_bundle('splits-current.json')[1]
 commit=commit_actual()
 mlflow.set_tags({'fase':phase,'familia':family,'git_commit':commit,'source_dirty':'false','protocol_id':plan['id'],'version':'v2','io_patch_id':plan.get('io_patch_id','original'),'holdout_previously_observed_in_v1':'true','design_state':plan.get('design_state','frozen')})
 mlflow.log_params({'snapshot_id':snapshot['id'],'split_id':split['id'],'snapshot_at_utc':snapshot['identity']['snapshot_at_utc'],'source_table':'PSET2_OULAD.ANALYTICS.OBT_FEATURES','labels_table':'PSET2_OULAD.GOLD.OUTCOME_ENROLLMENT','cutoff_day':56,'seed':42,'cv_folds':5,'capacity':.10,'pipeline_sha256':sha256(ROOT/'src/pipeline.py'),'client_lock_sha256':sha256(ROOT/'requirements.lock.txt'),**(extra or {})})
 mlflow.log_dict(plan,'protocolo.json')
 return plan

def exportar():
 exp=configurar();data=mlflow.search_runs(experiment_ids=[exp.experiment_id]);data.to_csv(ROOT/'docs/corridas.csv',index=False);return data
