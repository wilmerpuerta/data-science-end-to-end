"""Contrato de metadatos común, con commit real y fuente limpia antes de cada corrida."""
from pathlib import Path
import json,subprocess,hashlib,os
import mlflow
from .common import ROOT,sha256,read_bundle,identity

def commit_actual():
 repo=ROOT.parents[1]
 result=subprocess.run(['git','rev-parse','--verify','HEAD'],cwd=repo,capture_output=True,text=True)
 if result.returncode:raise RuntimeError('Crear commit del código antes de registrar corridas v2')
 paths=[str(p.relative_to(repo)) for folder in ['src','scripts','config','prompts'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 paths += [str((ROOT/name).relative_to(repo)) for name in ['requirements.txt','requirements.lock.txt']]
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
 for name,expected in fixed['content']['training_sources'].items():
  if sha256(ROOT/name)!=expected:raise RuntimeError('Fuente de modelado cambió después de congelar: '+name)
 return fixed

def registrar_base(phase,family,extra=None,require_frozen=True):
 plan=protocolo(require_frozen);snapshot=read_bundle()[1];split=read_bundle('splits-current.json')[1]
 commit=commit_actual()
 mlflow.set_tags({'fase':phase,'familia':family,'git_commit':commit,'source_dirty':'false','protocol_id':plan['id'],'version':'v2','holdout_previously_observed_in_v1':'true','design_state':plan.get('design_state','frozen')})
 mlflow.log_params({'snapshot_id':snapshot['id'],'split_id':split['id'],'snapshot_at_utc':snapshot['identity']['snapshot_at_utc'],'source_table':'PSET2_OULAD.ANALYTICS.OBT_FEATURES','labels_table':'PSET2_OULAD.GOLD.OUTCOME_ENROLLMENT','cutoff_day':56,'seed':42,'cv_folds':5,'capacity':.10,'pipeline_sha256':sha256(ROOT/'src/pipeline.py'),'client_lock_sha256':sha256(ROOT/'requirements.lock.txt'),**(extra or {})})
 mlflow.log_dict(plan,'protocolo.json')
 return plan

def exportar():
 exp=configurar();data=mlflow.search_runs(experiment_ids=[exp.experiment_id]);data.to_csv(ROOT/'docs/corridas.csv',index=False);return data
