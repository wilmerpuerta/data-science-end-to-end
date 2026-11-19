"""Validación exploratoria por cortes propios, sin labels de 2014J ni cambios de champion."""
from pathlib import Path
from datetime import datetime,timezone
import json,time,warnings
import numpy as np,pandas as pd,mlflow
from sklearn.model_selection import StratifiedGroupKFold
from threadpoolctl import threadpool_limits
from .common import ROOT,LOCAL,read_bundle,sha256,identity
from .pipeline import FeaturesAlCorte
from .modelos import construir_modelo
from .experimentos import entrada,log_pipeline,train_metric_sample,api_spend
from .evaluacion import probabilidades,metricas,negocio
from .seguimiento import configurar,protocolo,registrar_base,exportar
CUTS=[14,28,42,56];MODES=['estatico','indicador','longitudinal']
OUT=ROOT/'docs/anticipacion';PRIVATE=LOCAL/'anticipacion'
class EstaticasConRegistro(FeaturesAlCorte):
    def _convertir(self,X):
        out=super()._convertir(X)
        if 'has_recorded_activity' not in X:raise ValueError('Falta estado de registros al corte')
        flag=pd.to_numeric(X.has_recorded_activity,errors='raise').to_numpy(dtype=float,na_value=np.nan)
        if not np.isin(flag,[0.,1.]).all():raise ValueError('Indicador inválido')
        out['has_recorded_activity']=flag
        return out

def cohortes():
    folder,snapshot=read_bundle();f=pd.read_parquet(folder/'features.parquet')
    test_ids=set(f.loc[f.code_presentation.eq('2014J'),'id_student'])
    dev=f.loc[f.code_presentation.isin(['2013B','2013J','2014B']) & ~f.id_student.isin(test_ids)].copy()
    base=dev.loc[dev.cutoff_day.eq(14)].sort_values('enrollment_key').reset_index(drop=True)
    # Los outcomes se restringen a claves de desarrollo antes de cualquier unión/perfil.
    y=pd.read_parquet(folder/'outcomes.parquet');y=y.loc[y.enrollment_key.isin(base.enrollment_key)]
    base=base.merge(y,on='enrollment_key',validate='one_to_one');assert base.target_class.notna().all()
    assert not set(base.id_student)&test_ids
    assignments=base[['enrollment_key','id_student','edition_key']].copy();fold=np.full(len(base),-1)
    cv=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=1706)
    for k,(_,b) in enumerate(cv.split(base,base.target_class,groups=base.id_student)):fold[b]=k
    assignments['cv_fold']=fold
    assert assignments.groupby('id_student').cv_fold.nunique().eq(1).all()
    frames={}
    for cut in CUTS:
        d=dev.loc[dev.cutoff_day.eq(cut)].merge(assignments[['enrollment_key','cv_fold']],on='enrollment_key',validate='one_to_one')
        d=d.merge(y,on='enrollment_key',validate='one_to_one').sort_values('enrollment_key').reset_index(drop=True)
        assert d.target_class.notna().all() and set(d.enrollment_key)<=set(base.enrollment_key)
        assert not set(d.id_student)&test_ids
        assert (d.loc[d.last_activity_day.notna(),'last_activity_day']<=cut).all()
        for k in range(5):
            a=d.loc[d.cv_fold.ne(k)];b=d.loc[d.cv_fold.eq(k)]
            assert not set(a.id_student)&set(b.id_student)
            assert set(a.target_class)==set(b.target_class)=={'Approved','Fail','Withdrawn'}
        frames[cut]=d
    return frames,assignments,snapshot

def simulate_policy(frames,scores,rounds,shares,capacity=.10):
    """K nace de elegibles día14; cuotas acumuladas, sin repetir matrícula.
    Ranking dentro de edición y fold: no mezcla escalas de modelos OOF distintos.
    """
    if len(rounds)!=len(shares) or abs(sum(shares)-1)>1e-10 or any(x<0 for x in shares):raise ValueError('Cuotas inválidas')
    if not 0<capacity<=1:raise ValueError('Capacidad inválida')
    base=frames[14];keys=['edition_key','cv_fold']
    budgets=(base.groupby(keys).size()*capacity).apply(np.floor).astype(int)
    chosen=set();selected=[];history=[]
    for cut,fraction in zip(rounds,np.cumsum(shares)):
        d=frames[cut].copy();d['score']=np.asarray(scores[cut])
        if not np.isfinite(d.score).all():raise ValueError('Scores inválidos')
        for (edition,fold),K in budgets.items():
            past=sum(x['edition_key']==edition and x['cv_fold']==int(fold) for x in selected)
            quota=max(0,int(np.floor(float(K)*float(fraction)+1e-9))-past)
            eligible=d.loc[d.edition_key.eq(edition)&d.cv_fold.eq(fold)&~d.enrollment_key.isin(chosen)].sort_values(['score','enrollment_key'],ascending=[False,True]).head(quota)
            for r in eligible.itertuples(index=False):
                chosen.add(r.enrollment_key)
                selected.append({'enrollment_key':r.enrollment_key,'id_student':int(r.id_student),'edition_key':edition,'cv_fold':int(fold),'cutoff_day':cut,'is_fail':r.target_class=='Fail','lead_days':float(r.module_presentation_length-cut)})
        history.append({'cutoff_day':cut,'cumulative_slots':len(selected),'new_slots':sum(x['cutoff_day']==cut for x in selected)})
    assert len(chosen)==len(selected)<=int(budgets.sum())
    den=int(base.target_class.eq('Fail').sum());tp=sum(x['is_fail'] for x in selected)
    return {'n_base_14':len(base),'fail_base_14':den,'budget':int(budgets.sum()),'used':len(selected),'tp':tp,'fp':len(selected)-tp,'coverage':tp/den,'precision':tp/len(selected) if selected else None,'unique_students':len({x['id_student'] for x in selected}),'mean_lead_weeks':float(np.mean([x['lead_days']/7 for x in selected])) if selected else None,
            'tp_with_margin_day56':sum(x['is_fail'] and x['cutoff_day']+21<=56 for x in selected),
            'tp_with_margin_day70':sum(x['is_fail'] and x['cutoff_day']+21<=70 for x in selected),'rounds':history},pd.DataFrame(selected)

def association(frame):
    d=frame.copy();d['no_record']=~d.has_recorded_activity.astype(bool);d['fail']=d.target_class.eq('Fail')
    grouped=d.groupby('no_record').agg(n=('fail','size'),fail=('fail','sum'));n0=int(grouped.loc[True,'n']);a=int(grouped.loc[True,'fail']);n1=int(grouped.loc[False,'n']);c=int(grouped.loc[False,'fail'])
    rates=[a/n0,c/n1]
    tab=d.groupby(['edition_key','no_record']).agg(n=('fail','size'),fail=('fail','sum')).reset_index()
    wide=tab.pivot(index='edition_key',columns='no_record',values=['n','fail']).fillna(0)
    ok=(wide['n'][True]>=5)&(wide['n'][False]>=5);w=wide.loc[ok].copy()
    weights=(w['n'][True]+w['n'][False]);weights/=weights.sum()
    standardized=float((weights*(w['fail'][True]/w['n'][True]-w['fail'][False]/w['n'][False])).sum())
    # IC por remuestreo de alumno, manteniendo juntas sus matrículas.
    students=pd.Index(d.id_student.unique());idx=students.get_indexer(d.id_student)
    cells=np.zeros((len(students),4))
    for j,mask in enumerate([d.no_record&d.fail,d.no_record&~d.fail,~d.no_record&d.fail,~d.no_record&~d.fail]):np.add.at(cells[:,j],idx,mask.to_numpy(dtype=int))
    rng=np.random.default_rng(1706+int(d.cutoff_day.iloc[0]));diff=[];ratio=[]
    for _ in range(1000):
        count=np.bincount(rng.integers(0,len(students),len(students)),minlength=len(students));aa,bb,cc,dd=count@cells
        r0=aa/(aa+bb);r1=cc/(cc+dd);diff.append(r0-r1);ratio.append(r0/r1)
    phi=(a*(n1-c)-(n0-a)*c)/np.sqrt(n0*n1*(a+c)*(n0+n1-a-c))
    return {'cutoff_day':int(d.cutoff_day.iloc[0]),'no_record_n':n0,'no_record_fail':a,'record_n':n1,'record_fail':c,'risk_no_record':rates[0],'risk_record':rates[1],'risk_difference':rates[0]-rates[1],'risk_ratio':rates[0]/rates[1],'phi_binary':float(phi),'risk_difference_ci95':np.quantile(diff,[.025,.975]).tolist(),'risk_ratio_ci95':np.quantile(ratio,[.025,.975]).tolist(),'standardized_risk_difference':standardized,'strata_included':int(ok.sum()),'standardization_population_fraction':float(w['n'].to_numpy().sum()/len(d)),'scope':'Observed development association; standardization by module-presentation is not causal adjustment proof.'},tab

def build(family,params,mode):
 p=construir_modelo(family,solo_estaticas=mode!='longitudinal');p.named_steps['modelo'].set_params(**params)
 if mode=='indicador':
  p.steps[0]=('features',EstaticasConRegistro(solo_estaticas=True));prep=p.named_steps['preparacion'];name,transform,cols=prep.transformers[0];prep.transformers[0]=(name,transform,cols+['has_recorded_activity'])
 return p

def main():
 configurar();protocol=protocolo();OUT.mkdir(exist_ok=True);PRIVATE.mkdir(parents=True,exist_ok=True)
 decision=json.loads((ROOT/'docs/negocio/finalistas.json').read_text())['content'];families=[decision['winner'],decision['challenger']]
 frames,assignments,snapshot=cohortes()
 content={'protocol_id':protocol['id'],'cuts':CUTS,'fold_seed':1706,'assignments_sha256':identity(assignments.to_dict('records')),'families':[{'family':r['family'],'params':r['params']} for r in families],'variants':MODES,'hyperparameters':'same longitudinal-finalist parameters fixed across all information variants and cuts, no early-cohort tuning','cohort':'own eligible cohort each cut, purge all students appearing in any 2014J features without using outcomes','sequential_policy':{'rounds':[14,28,42],'shares':[.4,.3,.3],'capacity':.10},'margin_scenarios':{'coordination_days':7,'support_days':14,'deadlines':[56,70],'validated':False},'uses_test_labels':False}
 plan={'id':identity(content),'content':content};planfile=OUT/'plan.json'
 if planfile.exists():assert json.loads(planfile.read_text())==plan
 else:planfile.write_text(json.dumps(plan,indent=2))
 reportpath=OUT/'resultados.json'
 if reportpath.exists():
  report=json.loads(reportpath.read_text());assert report['plan_id']==plan['id'];return report
 assignments.to_csv(PRIVATE/'assignments.csv',index=False);results=[];oof={};associations=[];cohorts=[]
 for cut in CUTS:
  frame=frames[cut];y=frame.target_class.to_numpy();x=entrada(frame);cohorts.append({'cutoff_day':cut,'n':len(frame),'unique_students':int(frame.id_student.nunique()),'fail':int(frame.target_class.eq('Fail').sum()),'no_activity':int((~frame.has_recorded_activity.astype(bool)).sum())})
  assoc,table=association(frame);associations.append(assoc);table.to_csv(OUT/f'association-{cut}.csv',index=False)
  for finalist in families:
   family=finalist['family'];params=finalist['params']
   for mode in MODES:
    name=f'{family}-{cut}-{mode}';cache=PRIVATE/(name+'.json');op=PRIVATE/(name+'-oof.parquet')
    if cache.exists():
     saved=json.loads(cache.read_text());assert saved['plan_id']==plan['id'];results.append(saved);oof[(family,cut,mode)]=pd.read_parquet(op).p_fail.to_numpy();continue
    rows=[];scores=np.zeros((len(frame),3));before=api_spend()
    with mlflow.start_run(run_name='anticipacion-'+name) as parent:
     registrar_base('anticipacion',family,{'cutoff_day':cut,'split_id':content['assignments_sha256'],'mode':mode,**{'model__'+k:str(v) for k,v in params.items()}});mlflow.log_dict(plan,'early-plan.json')
     for k in range(5):
      a=np.flatnonzero(frame.cv_fold.ne(k));b=np.flatnonzero(frame.cv_fold.eq(k));assert not set(frame.iloc[a].id_student)&set(frame.iloc[b].id_student)
      m=train_metric_sample(y,a,k);p=build(family,params,mode)
      with mlflow.start_run(run_name=f'{name}-fold-{k}',nested=True):
       registrar_base('anticipacion_fold',family,{'cutoff_day':cut,'split_id':content['assignments_sha256'],'mode':mode,'fold':k,**{'model__'+key:str(v) for key,v in params.items()}})
       start=time.perf_counter()
       with threadpool_limits(limits=2),warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter('always');p.fit(x.iloc[a],y[a]);seconds=time.perf_counter()-start
        start=time.perf_counter();pa=probabilidades(p,x.iloc[m]);pb=probabilidades(p,x.iloc[b]);predict_seconds=time.perf_counter()-start
       scores[b]=pb;vm=metricas(y[b],pb);tm=metricas(y[m],pa);biz=negocio(frame.iloc[b],y[b],pb[:,1]);row={'fold':k,**vm,'coverage':biz['coverage'],'precision_at_k':biz['precision_at_k'],'train_ap_fail':tm['ap_fail'],'fit_seconds':seconds,'inference_seconds':predict_seconds};rows.append(row);mlflow.log_metrics(row);mlflow.log_dict({'warnings':[str(w.message) for w in ws]},'warnings.json');log_pipeline(p,x.iloc[a])
     with threadpool_limits(limits=2):full=build(family,params,mode).fit(x,y)
     log_pipeline(full,x);table=pd.DataFrame(rows);metrics={key+'_'+agg:float(table[key].std(ddof=1) if agg=='std' else table[key].mean()) for key in ['ap_fail','coverage','train_ap_fail','fit_seconds','inference_seconds'] for agg in ['mean','std']};metrics['api_cost_accounted_usd']=api_spend()-before;mlflow.log_metrics(metrics);mlflow.log_dict({'folds':rows},'folds.json');saved={'family':family,'cutoff_day':cut,'mode':mode,'run_id':parent.info.run_id,'plan_id':plan['id'],**metrics,'folds':rows}
    pd.DataFrame({'enrollment_key':frame.enrollment_key,'p_fail':scores[:,1]}).to_parquet(op,index=False);cache.write_text(json.dumps(saved,indent=2));results.append(saved);oof[(family,cut,mode)]=scores[:,1];print('Anticipación completada: '+name,flush=True)
 policies=[]
 for finalist in families:
  family=finalist['family']
  for name,mode,rounds,shares in [('estatico_semana2','estatico',[14],[1.]),('longitudinal_semana2','longitudinal',[14],[1.]),('longitudinal_semana4','longitudinal',[28],[1.]),('longitudinal_semana6','longitudinal',[42],[1.]),('longitudinal_escalonada','longitudinal',[14,28,42],[.4,.3,.3])]:
   policy,selected=simulate_policy(frames,{cut:oof[(family,cut,mode)] for cut in rounds},rounds,shares);policy.update(family=family,policy=name);policies.append(policy);selected.to_parquet(PRIVATE/(family+'-'+name+'.parquet'),index=False)
 report={'status':'complete','plan_id':plan['id'],'protocol_id':protocol['id'],'models':results,'cohorts':cohorts,'associations':associations,'policies':policies,'holdout_used':False,'winner_changed':False,'limits':['exploratory reused development CV; no causal intervention estimate','same hyperparameters across early variants, not independent early tuning','policy ranks within edition/fold, one shared K based on day14; enrollment and unique-student units differ','21-day margin is an illustrative operational scenario, not an institutional deadline','early label-maturity and publication lag prevent prospective certification']}
 reportpath.write_text(json.dumps(report,indent=2));pd.DataFrame(cohorts).to_csv(OUT/'cohortes.csv',index=False);pd.DataFrame([{k:v for k,v in r.items() if k!='folds'} for r in results]).to_csv(OUT/'comparacion.csv',index=False);pd.DataFrame([{k:v for k,v in p.items() if k!='rounds'} for p in policies]).to_csv(OUT/'politicas.csv',index=False)
 with mlflow.start_run(run_name='politicas-anticipacion-presupuesto-compartido'):
  registrar_base('anticipacion_politicas','politica_operativa',{'split_id':content['assignments_sha256']});mlflow.log_dict(report,'resultados.json')
 exportar();return report
