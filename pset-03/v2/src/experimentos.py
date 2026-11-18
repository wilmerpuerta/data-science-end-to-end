"""Baselines y seis candidatos, mismo pool/folds/preparación, métricas y recursos."""
from pathlib import Path
from datetime import datetime,timezone
from importlib.metadata import version
import json,time,warnings,os,hashlib
import numpy as np,pandas as pd
import mlflow,mlflow.sklearn
from mlflow.models import infer_signature
from sklearn.model_selection import train_test_split
from sklearn.base import clone
from threadpoolctl import threadpool_limits
from .common import ROOT,sha256,read_bundle
from .datos import cargar_snapshot,pliegues_congelados
from .pipeline import columnas,construir_pipeline
from .modelos import candidatos,ingenua,construir_modelo
from .evaluacion import probabilidades,metricas,negocio
from .seguimiento import configurar,registrar_base,protocolo,exportar
from .openai_api import credential_status
from .costos import LibroCostos

def api_spend():
 return float(LibroCostos(ROOT/'.local/llm/costos.json',10).summary()['accounted_spend_usd'])

OUT=ROOT/'docs/modelos';PRIVATE=ROOT/'.local/modelos'

def entrada(frame):
 num,cat=columnas();cols=[c for c in num if not c.startswith('log1p_') and c!='clicks_per_active_day_14d']+cat
 x=frame[cols].copy()
 for c in cols:
  if c in cat:x[c]=x[c].astype(object).where(x[c].notna(),np.nan)
  else:x[c]=x[c].to_numpy(dtype=float,na_value=np.nan)
 return x

def log_pipeline(p,x,path='pipeline'):
 example=pd.DataFrame({c:[x[c].mode(dropna=True).iloc[0] if x[c].dtype==object else float(x[c].median())] for c in x})
 output=p.predict_proba(example)
 deps=[f'{n}=={version(n)}' for n in ['mlflow','scikit-learn','numpy','pandas','scipy','cloudpickle','joblib','threadpoolctl','requests','python-dotenv']]
 mlflow.sklearn.log_model(p,artifact_path=path,pyfunc_predict_fn='predict_proba',signature=infer_signature(example,output),input_example=example,code_paths=[str(ROOT/'src')],pip_requirements=deps)

def train_metric_sample(y,indices,fold):
 if len(indices)<=1000:return indices
 chosen,_=train_test_split(indices,train_size=1000,random_state=730+fold,stratify=np.asarray(y)[indices]);return np.sort(chosen)

def evaluate(name,family,phase,*,mode='long',params=None):
 plan=protocolo();params=params or {};train,_=cargar_snapshot();x=entrada(train);y=train.target_class.to_numpy();folds=list(pliegues_congelados(train))
 directory=PRIVATE/name;directory.mkdir(parents=True,exist_ok=True);done=directory/'result.json'
 if done.exists():
  r=json.loads(done.read_text());assert r['protocol_id']==plan['id'];return r
 def build():
  if family=='dummy':return construir_pipeline(ingenua(),solo_estaticas=True)
  p=construir_modelo(family,solo_estaticas=mode=='static');p.named_steps['modelo'].set_params(**params);return p
 study_spend_before=api_spend()
 parentpath=directory/'parent.json'
 if parentpath.exists():parent=json.loads(parentpath.read_text())['run_id']
 else:
  with mlflow.start_run(run_name=name) as r:
   parent=r.info.run_id;registrar_base(phase,family,{'mode':mode,**{'model__'+key:str(v) for key,v in build().named_steps['modelo'].get_params(deep=False).items()}})
  parentpath.write_text(json.dumps({'run_id':parent,'protocol_id':plan['id']}))
 scores=np.zeros((len(train),3));details=[]
 with mlflow.start_run(run_id=parent):
  for k,(a,b) in enumerate(folds):
   cache=directory/f'fold-{k}.json';predfile=directory/f'fold-{k}.parquet'
   if cache.exists():
    r=json.loads(cache.read_text());assert r['protocol_id']==plan['id'];pb=pd.read_parquet(predfile)[['Approved','Fail','Withdrawn']].to_numpy();scores[b]=pb;details.append(r);continue
   m=train_metric_sample(y,a,k);p=build();fold_spend_before=api_spend()
   with mlflow.start_run(run_name=f'{name}-fold-{k}',nested=True) as run:
    registrar_base(phase+'_fold',family,{'mode':mode,'fold':k,'train_metric_sample_rows':len(m),'train_metric_sample_sha256':hashlib.sha256('\n'.join(train.iloc[m].enrollment_key).encode()).hexdigest(),**{'model__'+key:str(v) for key,v in p.named_steps['modelo'].get_params(deep=False).items()}})
    begin=time.perf_counter()
    with warnings.catch_warnings(record=True) as caught,threadpool_limits(limits=2):
     warnings.simplefilter('always');p.fit(x.iloc[a],y[a]);fit_seconds=time.perf_counter()-begin
     start=time.perf_counter();pa=probabilidades(p,x.iloc[m]);train_inference=time.perf_counter()-start
     start=time.perf_counter();pb=probabilidades(p,x.iloc[b]);inference=time.perf_counter()-start
    scores[b]=pb;tm=metricas(y[m],pa);vm=metricas(y[b],pb);biz=negocio(train.iloc[b],y[b],pb[:,1])
    metrics={**{'train_'+key:v for key,v in tm.items()},**{'cv_'+key:v for key,v in vm.items()},'cv_coverage':biz['coverage'],'cv_precision_at_k':biz['precision_at_k'],'fit_seconds':fit_seconds,'inference_seconds':inference,'train_metric_inference_seconds':train_inference}
    mlflow.log_metrics(metrics);warn=[{'category':w.category.__name__,'message':str(w.message)} for w in caught];mlflow.log_dict({'warnings':warn,'validation_business':biz},'evaluation.json');log_pipeline(p,x.iloc[a])
    metrics['api_cost_accounted_usd']=api_spend()-fold_spend_before;mlflow.log_metric('api_cost_accounted_usd',metrics['api_cost_accounted_usd'])
    result={'fold':k,'protocol_id':plan['id'],'run_id':run.info.run_id,'train_rows':len(a),'validation_rows':len(b),'train_metric_rows':len(m),**metrics,'warnings':warn}
   pd.DataFrame(pb,columns=['Approved','Fail','Withdrawn']).to_parquet(predfile,index=False);cache.write_text(json.dumps(result,indent=2));details.append(result)
   print(f'{name}: fold {k+1}/5 completado; AP={vm["ap_fail"]:.4f}, cobertura={biz["coverage"]:.4f}',flush=True)
  table=pd.DataFrame(details);summary={}
  for key in ['ap_fail','logloss','brier_fail','coverage','precision_at_k']:
   summary['cv_'+key+'_mean']=float(table['cv_'+key].mean());summary['cv_'+key+'_std']=float(table['cv_'+key].std(ddof=1))
  summary.update(train_ap_fail_mean=float(table.train_ap_fail.mean()),ap_gap=float(table.train_ap_fail.mean()-table.cv_ap_fail.mean()),cv_fit_seconds_total=float(table.fit_seconds.sum()),cv_inference_seconds_total=float(table.inference_seconds.sum()))
  full=build();begin=time.perf_counter()
  with threadpool_limits(limits=2):full.fit(x,y)
  summary['refit_seconds']=time.perf_counter()-begin;log_pipeline(full,x);summary['api_cost_new_calls_usd']=api_spend()-study_spend_before;summary['api_cost_folds_including_prior_checkpoints_usd']=float(table.api_cost_accounted_usd.sum());mlflow.log_metrics(summary);mlflow.log_dict({'folds':details},'folds.json')
  mlflow.log_artifacts(str(ROOT/'src'),'source')
  r={'name':name,'family':family,'phase':phase,'mode':mode,'params':params,'protocol_id':plan['id'],'run_id':parent,**summary,'folds':details,'oof_business':negocio(train,y,scores[:,1]),'train_metric_scope':'same 1000-row stratified training sample per fold for every candidate'}
  if family=='llm_generativo':r['llm_context_scope']='18 train-fold examples by default and full-fold priors; not all training rows fit weights. Computation happens in predict.'
 pd.DataFrame({'enrollment_key':train.enrollment_key,**{c:scores[:,i] for i,c in enumerate(['Approved','Fail','Withdrawn'])}}).to_parquet(directory/'oof.parquet',index=False)
 table.to_csv(OUT/(name+'_folds.csv'),index=False);done.write_text(json.dumps(r,indent=2));return r

def main():
 configurar();OUT.mkdir(parents=True,exist_ok=True);PRIVATE.mkdir(parents=True,exist_ok=True);plan=protocolo()
 preflight=ROOT/'docs/preflight-openai.json'
 if not preflight.exists() or json.loads(preflight.read_text()).get('status')!='ok':raise RuntimeError('Falta el preflight de inferencia OpenAI; no basta con que exista una clave')
 if not credential_status()['configured']:raise RuntimeError('Completar la API de OpenAI antes de iniciar la evaluación definitiva de seis candidatos')
 rows=[evaluate('ingenua','dummy','baseline',mode='static')]
 reactive=PRIVATE/'reactiva.json'
 if not reactive.exists():
  with mlflow.start_run(run_name='reactiva') as run:
   registrar_base('baseline','politica_reactiva');mlflow.log_metrics({'preventive_coverage':0.});mlflow.log_dict({'rule':'after closure, at most K known Fail, no preventive knowledge'},'policy.json');r={'name':'reactiva','run_id':run.info.run_id,'phase':'baseline','protocol_id':plan['id'],'preventive_coverage':0.}
  reactive.write_text(json.dumps(r,indent=2))
 for family in candidatos():rows.append(evaluate(family,family,'candidato'))
 # Cuatro ablaciones logísticas con el mismo split. Se ejecutan en etapa de features comparativas posterior.
 result={'status':'complete','protocol_id':plan['id'],'baselines':[rows[0],json.loads(reactive.read_text())],'candidates':rows[1:],'holdout_evaluated':False}
 (OUT/'resultados.json').write_text(json.dumps(result,indent=2));pd.DataFrame([{k:v for k,v in r.items() if k not in ['folds','oof_business']} for r in rows]).to_csv(OUT/'comparacion.csv',index=False);exportar();print('Dos baselines y seis candidatos v2 completados.',flush=True);return result
