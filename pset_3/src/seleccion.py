"""Decisión CV inmutable, una evaluación final conjunta recuperable y Registry v2."""
from pathlib import Path
from datetime import datetime,timezone
import json,time,pickle,os
import numpy as np,pandas as pd,mlflow,mlflow.sklearn
from sklearn.inspection import permutation_importance
from threadpoolctl import threadpool_limits
from .common import ROOT,identity,sha256
from .datos import cargar_snapshot
from .evaluacion import probabilidades,metricas,negocio,seleccionar,CLASSES
from .experimentos import entrada,log_pipeline,api_spend
from .seguimiento import configurar,protocolo,registrar_base,exportar
OUT=ROOT/'docs/seleccion';PRIVATE=ROOT/'.local/seleccion';MODEL='oulad-apoyo-academico-v2-modelo'
def local_forest_explanation(model,X,prob):
    estimator=model.named_steps['modelo']
    if not hasattr(estimator,'estimators_') or not all(hasattr(t,'tree_') for t in estimator.estimators_):return {'method':'global permutation only; no forest path available'}
    position=int(np.argmax(prob[:,1]));row=X.iloc[[position]]
    prep=model[:-1];z=prep.transform(row);names=prep.get_feature_names_out();counts={};leaves=[]
    fail=list(model.classes_).index('Fail')
    for tree in estimator.estimators_:
        leaf=int(tree.apply(z)[0]);value=tree.tree_.value[leaf][0];leaves.append(float(value[fail]/value.sum()))
        for node in tree.decision_path(z).indices:
            f=int(tree.tree_.feature[node])
            if f>=0:counts[str(names[f])]=counts.get(str(names[f]),0)+1
    np.testing.assert_allclose(np.mean(leaves),prob[position,1],rtol=1e-12)
    return {'method':'RandomForest: average of leaf probabilities across trees; path-use counts are not additive SHAP contributions.',
            'case_selection':'highest predicted Fail score, without looking at true label; no identifier published',
            'predicted_fail_score':float(prob[position,1]),'trees':len(leaves),'mean_leaf_fail_score':float(np.mean(leaves)),
            'most_used_path_features':sorted([{'feature':k,'path_uses':v} for k,v in counts.items()],key=lambda r:-r['path_uses'])[:12],
            'causal_interpretation':False}

def decision():
 plan=protocolo();d=json.loads((ROOT/'docs/negocio/finalistas.json').read_text());assert identity(d['content'])==d['decision_id'] and d['content']['protocol_id']==plan['id'];return d

def save_model(p,path):
 with path.open('wb') as f:pickle.dump(p,f)
 os.chmod(path,0o600)

def load_models(refs):
 models={}
 for name,ref in refs.items():
  local=PRIVATE/(name+'.pkl')
  if local.exists():
   with local.open('rb') as f:models[name]=pickle.load(f)
  else:models[name]=mlflow.sklearn.load_model(f"runs:/{ref['run_id']}/pipeline")
 return models

def explain(models,refs):
 costs=OUT/'costos.csv';importance=OUT/'explicabilidad.csv'
 if costs.exists() and importance.exists():return
 train,_=cargar_snapshot();x=entrada(train);sample=x.sample(n=200,random_state=42);meta=train.loc[sample.index];y=meta.target_class.to_numpy();rows=[];timing=[]
 for name,p in models.items():
  batch=x.iloc[:1000];start=time.perf_counter();before=api_spend()
  with threadpool_limits(limits=2):p.predict_proba(batch)
  cold=time.perf_counter()-start;freshcost=api_spend()-before;times=[]
  for _ in range(5):
   start=time.perf_counter()
   with threadpool_limits(limits=2):p.predict_proba(batch)
   times.append(time.perf_counter()-start)
  timing.append({'model':name,'family':refs[name].get('family','dummy'),'rows':1000,'first_pass_seconds':cold,'first_pass_api_cost_usd':freshcost,'median_replay_seconds':float(np.median(times)),'repeats':5,'replay_uses_cache_for_llm':refs[name].get('family')=='llm_generativo','training_cv_seconds':refs[name].get('cv_fit_seconds_total',5*refs[name].get('mean_fold_fit_seconds',0)),'refit_seconds':refs[name].get('refit_seconds')})
  if name in ['winner','challenger']:
   def score(est,values,truth):return negocio(meta,truth,probabilidades(est,values)[:,1])['coverage']
   with threadpool_limits(limits=2):result=permutation_importance(p,sample,y,scoring=score,n_repeats=2,random_state=42,n_jobs=1)
   for i,c in enumerate(sample):rows.append({'model':name,'feature':c,'mean_coverage_drop':float(result.importances_mean[i]),'std_coverage_drop':float(result.importances_std[i]),'development_rows':200,'repeats':2,'causal':False})
  save_model(p,PRIVATE/(name+'.pkl'))
 pd.DataFrame(timing).to_csv(costs,index=False);pd.DataFrame(rows).to_csv(importance,index=False)

def register(d,report):
 client=mlflow.MlflowClient()
 try:
  model=client.get_registered_model(MODEL);assert model.tags.get('project')=='pset3-oulad-v2'
 except mlflow.exceptions.MlflowException as exc:
  if exc.error_code!='RESOURCE_DOES_NOT_EXIST':raise
  client.create_registered_model(MODEL,tags={'project':'pset3-oulad-v2'},description='Benchmark retrospectivo reutilizado; selección por CV de cobertura preventiva a cupo fijo.')
 entries=[]
 for name,alias in [('winner','champion'),('challenger','challenger')]:
  found=[v for v in client.search_model_versions(f"name='{MODEL}'") if v.tags.get('decision_id')==d['decision_id'] and v.tags.get('role')==name]
  if found:version=found[0]
  else:
   version=mlflow.register_model(f"runs:/{report['final_run_id']}/{name}_pipeline",MODEL)
   for key,value in {'decision_id':d['decision_id'],'role':name,'source_model_run_id':d['content'][name]['run_id'],'protocol_id':d['content']['protocol_id']}.items():client.set_model_version_tag(MODEL,version.version,key,value)
  client.set_registered_model_alias(MODEL,alias,version.version);entries.append({'alias':alias,'version':str(version.version),'run_id':report['final_run_id'],'source_model_run_id':d['content'][name]['run_id'],'family':d['content'][name]['family'],'uri':f'models:/{MODEL}@{alias}'})
 return entries

def main():
 configurar();d=decision();OUT.mkdir(exist_ok=True);PRIVATE.mkdir(parents=True,exist_ok=True);reportpath=OUT/'evaluacion.json'
 if reportpath.exists():
  report=json.loads(reportpath.read_text());assert report['decision_id']==d['decision_id'];report['registry']=register(d,report);report['status']='registered';reportpath.write_text(json.dumps(report,indent=2));return report
 refs={key:d['content'][key] for key in ['winner','challenger']}
 for row in d['content']['static_controls']:refs['static_'+row['family']]=row
 refs['dummy']=json.loads((ROOT/'docs/modelos/resultados.json').read_text())['baselines'][0]
 models=load_models(refs);explain(models,refs);marker=PRIVATE/'test-opened.json'
 if marker.exists():
  state=json.loads(marker.read_text());assert state['decision_id']==d['decision_id'];assert state['state'] in ['RUNNING','FAILED_RECOVERABLE']
  run_id=state['run_id']
 else:
  with mlflow.start_run(run_name='evaluacion-final-v2') as run:
   run_id=run.info.run_id;registrar_base('final',d['content']['winner']['family'],{'winner_source_run_id':refs['winner']['run_id'],'challenger_source_run_id':refs['challenger']['run_id']});mlflow.log_dict(d,'decision-before-test.json')
  state={'decision_id':d['decision_id'],'state':'RUNNING','opened_at_utc':datetime.now(timezone.utc).isoformat(),'run_id':run_id}
  with marker.open('x') as f:json.dump(state,f,indent=2)
 results={};editions=[]
 with mlflow.start_run(run_id=run_id):
  test,_=cargar_snapshot(particion='test',permitir_prueba=True);x=entrada(test);y=test.target_class.to_numpy();pred=test[['enrollment_key','id_student','edition_key','target_class']].copy()
  for name,p in models.items():
   checkpoint=PRIVATE/(name+'-predictions.npz')
   if checkpoint.exists():
    data=np.load(checkpoint);prob=data['p'];seconds=float(data['seconds']);cost=float(data['cost'])
   else:
    start=time.perf_counter();before=api_spend()
    with threadpool_limits(limits=2):prob=probabilidades(p,x)
    seconds=time.perf_counter()-start;cost=api_spend()-before;save_model(p,PRIVATE/(name+'.pkl'));np.savez_compressed(checkpoint,p=prob,seconds=seconds,cost=cost)
   tech=metricas(y,prob);biz={str(c):negocio(test,y,prob[:,1],c) for c in [.05,.1,.2]};results[name]={'source_model_run_id':refs[name]['run_id'],'family':refs[name].get('family','dummy'),'technical':tech,'business':biz,'test_inference_seconds':seconds,'test_api_cost_usd':cost,'relative_error_cost_scenarios':{str(w):w*biz['0.1']['fn']+biz['0.1']['fp'] for w in [1,2,5,10]}}
   for j,c in enumerate(CLASSES):pred[name+'__'+c]=prob[:,j]
   mlflow.log_metrics({name+'_test_'+k:v for k,v in tech.items()});mlflow.log_metrics({name+'_coverage':biz['0.1']['coverage'],name+'_tp':biz['0.1']['tp'],name+'_test_inference_seconds':seconds,name+'_test_api_cost_usd':cost})
   for edition,idx in test.groupby('edition_key').groups.items():
    group=test.loc[idx];score=prob[np.asarray(idx),1];selected,k=seleccionar(group,score);mask=group.enrollment_key.isin(selected).to_numpy();editions.append({'model':name,'edition':edition,**negocio(group,group.target_class,score),'score_cutoff':float(score[mask].min()) if mask.any() else None,'tie_rule':'enrollment_key ascending, never label'})
   if name in ['winner','challenger']:log_pipeline(p,x,path=name+'_pipeline')
   if name=='winner':
    local=local_forest_explanation(p,x,prob);local.update(predicted_fail_score_highest=float(prob[:,1].max()),interpretation='descriptive model behavior; no causal interpretation');(OUT/'explicacion_local.json').write_text(json.dumps(local,indent=2))
  pred.to_parquet(PRIVATE/'predicciones_prueba.parquet',index=False)
  winner=results['winner']['business']['0.1'];static=results['static_'+refs['winner']['family']]['business']['0.1'];reactive_tp=sum(min(int(np.floor(.1*len(g))),int(g.target_class.eq('Fail').sum())) for _,g in test.groupby('edition_key'))
  report={'status':'evaluated','decision_id':d['decision_id'],'protocol_id':d['content']['protocol_id'],'final_run_id':run_id,'evaluated_at_utc':datetime.now(timezone.utc).isoformat(),'rows':len(test),'unique_students':int(test.id_student.nunique()),'models':results,'reactive':{'preventive_coverage':0.,'after_closure_tp':reactive_tp,'capacity':winner['k'],'fail':winner['fail'],'after_closure_coverage':reactive_tp/winner['fail']},'longitudinal_vs_matched_static':{'static_tp':static['tp'],'longitudinal_tp':winner['tp'],'absolute_tp_gain':winner['tp']-static['tp'],'relative_tp_gain_pct':100*(winner['tp']-static['tp'])/static['tp'] if static['tp'] else None,'causal_effect':False},'winner_changed_using_test':False,'test_previously_observed_in_v1':True,'threshold_rule':'top floor(.10*N) per edition, score descending and key ascending for ties; maximizes expected Fail capture at fixed filled capacity and homogeneous error costs. Monetary costs unspecified; relative FN/FP weights are scenarios.','prediction_sha256':sha256(PRIVATE/'predicciones_prueba.parquet'),'registry':[]}
  pd.DataFrame(editions).to_csv(OUT/'por_edicion.csv',index=False);reportpath.write_text(json.dumps(report,indent=2));mlflow.log_dict(report,'evaluation.json');mlflow.log_artifacts(str(OUT),'evidence')
 report['registry']=register(d,report);report['status']='registered';reportpath.write_text(json.dumps(report,indent=2));state.update(state='COMPLETE',final_run_id=run_id);marker.write_text(json.dumps(state,indent=2));exportar();return report
