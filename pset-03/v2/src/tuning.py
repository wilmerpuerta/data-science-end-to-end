"""Top tres por negocio, >=30 configuraciones únicas, misma CV y preparación."""
from pathlib import Path
import json,time,warnings
import numpy as np,pandas as pd
from scipy.stats import loguniform
from sklearn.model_selection import ParameterSampler,RandomizedSearchCV
from threadpoolctl import threadpool_limits
import mlflow
from .common import ROOT,identity
from .datos import cargar_snapshot,pliegues_congelados
from .modelos import construir_modelo
from .experimentos import entrada,log_pipeline,train_metric_sample,api_spend
from .evaluacion import probabilidades,metricas,negocio
from .seguimiento import configurar,protocolo,registrar_base,exportar

OUT=ROOT/'docs/tuning';PRIVATE=ROOT/'.local/tuning'

def plain(value):
 if isinstance(value,dict):return {k:plain(v) for k,v in value.items()}
 if isinstance(value,(list,tuple)):return [plain(x) for x in value]
 if hasattr(value,'item'):return value.item()
 return value

def configurations():
 spaces={
 'lineal':{'C':loguniform(.001,100),'class_weight':[None,'balanced'],'max_iter':[300,600,1000],'tol':loguniform(1e-5,1e-3)},
 'bagging':{'n_estimators':[50,100,150],'max_depth':[4,8,12,20],'min_samples_leaf':[1,2,5,10,20],'min_samples_split':[2,5,10],'max_features':['sqrt',.3,.6],'class_weight':[None,'balanced']},
 'boosting':{'learning_rate':loguniform(.02,.2),'max_iter':[60,100,160],'max_leaf_nodes':[7,15,31,63],'max_depth':[None,3,5,8],'min_samples_leaf':[10,20,40,80],'l2_regularization':loguniform(.0001,10),'early_stopping':[False,True]},
 'bayes':{'var_smoothing':loguniform(1e-12,1e-3)},
 'red_neuronal':{'hidden_layer_sizes':[(50,),(100,),(100,50)],'alpha':loguniform(1e-6,.1),'learning_rate_init':loguniform(.0001,.01),'max_iter':[200,400,800],'early_stopping':[False]},
 'llm_generativo':{'examples_per_class':[0,3,6],'score_temperature':[.55,.65,.75,.85,.95,1.05,1.15,1.25,1.5,2.]}}
 return {family:[plain(x) for x in ParameterSampler(space,n_iter=30,random_state=42+i)] for i,(family,space) in enumerate(spaces.items())}

def scorers(train,folds):
 trainsets={frozenset(a):k for k,(a,b) in enumerate(folds)}
 def score(kind,est,x,y):
  group=frozenset(x.index);fold=trainsets.get(group)
  idx=train_metric_sample(train.target_class.to_numpy(),x.index.to_numpy(),fold) if fold is not None else x.index.to_numpy()
  key=tuple(idx)
  if not hasattr(est,'_v2_score_cache'):est._v2_score_cache={}
  if key not in est._v2_score_cache:
   p=probabilidades(est,x.loc[idx]);truth=train.loc[idx].target_class.to_numpy();tech=metricas(truth,p);biz=negocio(train.loc[idx],truth,p[:,1])
   est._v2_score_cache[key]={'ap_fail':tech['ap_fail'],'coverage':biz['coverage'],'precision_at_k':biz['precision_at_k'],'neg_brier_fail':-tech['brier_fail'],'neg_logloss':-tech['logloss']}
  return est._v2_score_cache[key][kind]
 return {kind:(lambda est,x,y,kind=kind:score(kind,est,x,y)) for kind in ['ap_fail','coverage','precision_at_k','neg_brier_fail','neg_logloss']}

def run_trial(family,index,params,mode='long'):
 plan=protocolo();folder=PRIVATE/mode/family;folder.mkdir(parents=True,exist_ok=True);path=folder/f'{index:02d}.json'
 if path.exists():
  row=json.loads(path.read_text());assert row['protocol_id']==plan['id'] and row['params']==params;return row
 train,_=cargar_snapshot();x=entrada(train);folds=list(pliegues_congelados(train));base=construir_modelo(family,solo_estaticas=mode=='static')
 with mlflow.start_run(run_name=f'{mode}-{family}-config-{index:02d}',nested=True) as run:
  actual={**base.named_steps['modelo'].get_params(deep=False),**params}
  registrar_base('tuning' if mode=='long' else 'control_estatico',family,{'mode':mode,'config_index':index,'train_metric_sample_rows':1000,**{'model__'+k:str(v) for k,v in actual.items()}})
  search=RandomizedSearchCV(base,{'modelo__'+k:[v] for k,v in params.items()},n_iter=1,scoring=scorers(train,folds),refit='coverage',cv=folds,return_train_score=True,n_jobs=1,random_state=42,error_score='raise')
  spend_before=api_spend();begin=time.perf_counter()
  with warnings.catch_warnings(record=True) as caught,threadpool_limits(limits=2):
   warnings.simplefilter('always');search.fit(x,train.target_class.to_numpy())
  elapsed=time.perf_counter()-begin;cv=search.cv_results_;details=[]
  for k in range(5):
   f={'fold':k}
   for part in ['train','test']:
    for metric in ['ap_fail','coverage','precision_at_k','neg_brier_fail','neg_logloss']:f[part+'_'+metric]=float(cv[f'split{k}_{part}_{metric}'][0])
   details.append(f)
  table=pd.DataFrame(details);metrics={}
  for metric in ['ap_fail','coverage','precision_at_k','neg_brier_fail','neg_logloss']:
   metrics['cv_'+metric+'_mean']=float(table['test_'+metric].mean());metrics['cv_'+metric+'_std']=float(table['test_'+metric].std(ddof=1))
  metrics.update(train_ap_fail_mean=float(table.train_ap_fail.mean()),ap_gap=float(table.train_ap_fail.mean()-table.test_ap_fail.mean()),search_seconds=elapsed,mean_fold_fit_seconds=float(cv['mean_fit_time'][0]),refit_seconds=float(search.refit_time_))
  mlflow.log_metrics(metrics);mlflow.log_dict({'folds':details,'warnings':[{'category':w.category.__name__,'message':str(w.message)} for w in caught]},'evaluation.json');log_pipeline(search.best_estimator_,x)
  metrics['api_cost_accounted_usd']=api_spend()-spend_before;mlflow.log_metric('api_cost_accounted_usd',metrics['api_cost_accounted_usd'])
  row={'family':family,'mode':mode,'config_index':index,'params':params,'protocol_id':plan['id'],'run_id':run.info.run_id,**metrics,'folds':details,'warnings':len(caught)}
  table.to_csv(OUT/f'{mode}-{family}-{index:02d}.csv',index=False)
 path.write_text(json.dumps(row,indent=2));print(f'{mode} {family} {index+1}: cobertura {row["cv_coverage_mean"]:.4f}, AP {row["cv_ap_fail_mean"]:.4f}',flush=True);return row

def choose(rows):
 return sorted(rows,key=lambda r:(-r['cv_coverage_mean'],r['cv_coverage_std'],-r['cv_ap_fail_mean'],r.get('cv_brier_fail_mean',-r.get('cv_neg_brier_fail_mean',0)),r.get('api_cost_accounted_usd',r.get('api_cost_new_calls_usd',0)),r.get('search_seconds',r.get('cv_fit_seconds_total',0)),r['run_id']))[0]

def main():
 configurar();plan=protocolo();OUT.mkdir(exist_ok=True);PRIVATE.mkdir(parents=True,exist_ok=True)
 defaults=json.loads((ROOT/'docs/modelos/resultados.json').read_text());assert len(defaults['candidates'])==6
 selected=sorted(defaults['candidates'],key=lambda r:(-r['cv_coverage_mean'],r['cv_coverage_std'],-r['cv_ap_fail_mean'],r['cv_brier_fail_mean'],r.get('api_cost_new_calls_usd',0),r.get('cv_fit_seconds_total',0),r['run_id']))[:3]
 configpath=ROOT/'config/espacios-tuning.json';allconfigs=json.loads(configpath.read_text())
 searchplan={'protocol_id':plan['id'],'families':[r['family'] for r in selected],'draws':{r['family']:allconfigs[r['family']] for r in selected}}
 target=OUT/'plan.json'
 if target.exists():assert json.loads(target.read_text())['content']==searchplan
 else:target.write_text(json.dumps({'id':identity(searchplan),'content':searchplan},indent=2))
 results=[]
 for family in searchplan['families']:
  parentfile=PRIVATE/(family+'-parent.json')
  if parentfile.exists():parent=json.loads(parentfile.read_text())['run_id']
  else:
   with mlflow.start_run(run_name='tuning-'+family) as run:parent=run.info.run_id;registrar_base('tuning_parent',family,{'mode':'long','n_configurations':30});mlflow.log_dict(searchplan,'search-plan.json')
   parentfile.write_text(json.dumps({'run_id':parent,'protocol_id':plan['id']}))
  with mlflow.start_run(run_id=parent):results += [run_trial(family,i,p) for i,p in enumerate(searchplan['draws'][family])]
 record={'status':'complete','protocol_id':plan['id'],'families':searchplan['families'],'configurations':results,'holdout_evaluated':False}
 (OUT/'resultados.json').write_text(json.dumps(record,indent=2));exportar();return record
