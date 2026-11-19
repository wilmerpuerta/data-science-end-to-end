"""Aporte predictivo de cada derivada: CV fija, sin usar resultados de prueba."""
import json,time,warnings
import numpy as np,pandas as pd,mlflow
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits
from .common import ROOT
from .datos import cargar_snapshot,pliegues_congelados
from .pipeline import construir_pipeline
from .experimentos import entrada,log_pipeline,train_metric_sample
from .evaluacion import probabilidades,metricas,negocio
from .seguimiento import configurar,protocolo,registrar_base,exportar

MODES=['static','original','log_only','intensity_only','both']
def build(mode):
 if mode not in MODES:raise ValueError('Ablación desconocida')
 p=construir_pipeline(LogisticRegression(random_state=42),solo_estaticas=mode=='static',derivadas=mode not in ['static','original'])
 if mode in ['log_only','intensity_only']:
  prep=p.named_steps['preparacion'];name,trans,cols=prep.transformers[0];drop='clicks_per_active_day_14d' if mode=='log_only' else 'log1p_clicks_current_14d';prep.transformers[0]=(name,trans,[c for c in cols if c!=drop])
 return p

def main():
 configurar();plan=protocolo();out=ROOT/'docs/ablacion';private=ROOT/'.local/ablacion';out.mkdir(exist_ok=True);private.mkdir(parents=True,exist_ok=True)
 train,_=cargar_snapshot();x=entrada(train);y=train.target_class.to_numpy();folds=list(pliegues_congelados(train));results=[]
 for mode in MODES:
  path=private/(mode+'.json')
  if path.exists():results.append(json.loads(path.read_text()));continue
  rows=[]
  with mlflow.start_run(run_name='ablacion-'+mode) as parent:
   registrar_base('ablacion','lineal',{'mode':mode,'random_state':42,'max_iter':100})
   for k,(a,b) in enumerate(folds):
    with mlflow.start_run(run_name=f'{mode}-fold-{k}',nested=True) as run:
     registrar_base('ablacion_fold','lineal',{'mode':mode,'fold':k,'random_state':42,'max_iter':100})
     m=train_metric_sample(y,a,k);p=build(mode);start=time.perf_counter()
     with threadpool_limits(limits=2),warnings.catch_warnings(record=True) as ws:
      warnings.simplefilter('always');p.fit(x.iloc[a],y[a]);elapsed=time.perf_counter()-start;pa=probabilidades(p,x.iloc[m]);pb=probabilidades(p,x.iloc[b])
     tm=metricas(y[m],pa);vm=metricas(y[b],pb);biz=negocio(train.iloc[b],y[b],pb[:,1]);r={'fold':k,'train_ap_fail':tm['ap_fail'],**vm,'coverage':biz['coverage'],'fit_seconds':elapsed};rows.append(r)
     mlflow.log_metrics(r);mlflow.log_dict({'warnings':[str(w.message) for w in ws]},'warnings.json');log_pipeline(p,x.iloc[a])
   with threadpool_limits(limits=2):full=build(mode).fit(x,y)
   log_pipeline(full,x);table=pd.DataFrame(rows);metrics={key+'_'+agg:float(getattr(table[key],agg)(ddof=1) if agg=='std' else table[key].mean()) for key in ['ap_fail','coverage','train_ap_fail','fit_seconds'] for agg in ['mean','std']};mlflow.log_metrics(metrics)
   r={'mode':mode,'protocol_id':plan['id'],'run_id':parent.info.run_id,'folds':rows,**metrics}
  path.write_text(json.dumps(r,indent=2));results.append(r)
 reference=next(r for r in results if r['mode']=='original')
 for row in results:
  row['delta_ap_vs_original']=row['ap_fail_mean']-reference['ap_fail_mean'];row['delta_coverage_vs_original']=row['coverage_mean']-reference['coverage_mean']
  row['coverage_gain_exceeds_fold_variation']=row['delta_coverage_vs_original']>max(reference['coverage_std'],row['coverage_std'])
 report={'status':'complete','protocol_id':plan['id'],'results':results,'test_used':False,'negative_results_are_reported':True}
 (out/'resultados.json').write_text(json.dumps(report,indent=2));pd.DataFrame([{k:v for k,v in r.items() if k!='folds'} for r in results]).to_csv(out/'comparacion.csv',index=False);exportar();return report
