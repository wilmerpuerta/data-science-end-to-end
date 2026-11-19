"""Seguimiento de evidencias v2; no sustituye la auditoría de cumplimiento final."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import sys,json,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['PSET3_V2_ROOT']=str(ROOT)
from src.common import read_bundle,sha256,identity
from src.datos import cargar_snapshot,pliegues_congelados
from src.costos import LibroCostos
import pandas as pd

NOTEBOOKS=['01_eda.ipynb','02_features.ipynb','03_baseline_candidatos.ipynb','04_tuning.ipynb','05_seleccion.ipynb','anexos/06_anticipacion.ipynb']
def load(relative):
 p=ROOT/relative
 try:return json.loads(p.read_text()) if p.is_file() else {}
 except json.JSONDecodeError:return {'status':'being_written'}
def notebook_status(name):
 path=ROOT/'notebooks'/name
 if not path.exists():return {'name':name,'present':False,'executed':False,'verified':False}
 nb=load('notebooks/'+name);cells=[c for c in nb.get('cells',[]) if c.get('cell_type')=='code'];executed=bool(cells) and all(c.get('execution_count') is not None and not any(o.get('output_type')=='error' for o in c.get('outputs',[])) for c in cells)
 marker=load('docs/'+Path(name).name[:2]+'-verificacion.json');verified=executed and marker.get('fresh_kernel') is True and marker.get('notebook_sha256')==sha256(path)
 return {'name':name,'present':True,'executed':executed,'verified':verified}

def main():
 status=load('docs/estado-v2.json');proto=load('docs/protocolo-congelado.json');eda=load('docs/eda/resumen.json');features=load('docs/features/resumen.json');models=load('docs/modelos/resultados.json');tuning=load('docs/tuning/resultados.json');ablation=load('docs/ablacion/resultados.json');decision=load('docs/negocio/finalistas.json');early=load('docs/anticipacion/resultados.json');final=load('docs/seleccion/evaluacion.json');repro=load('docs/seleccion/reproduccion-champion.json')
 checks={};notes=[]
 try:
  snapshot=read_bundle()[1];folder,split=read_bundle('splits-current.json');train,_=cargar_snapshot();folds=list(pliegues_congelados(train));assignments=pd.read_csv(folder/'assignments.csv')
  checks['snapshot_split_integrity']=True;checks['five_student_group_folds']=len(folds)==5 and all(not set(train.iloc[a].id_student)&set(train.iloc[b].id_student) for a,b in folds) and sorted(i for a,b in folds for i in b)==list(range(len(train)))
  checks['no_test_students_in_train']=not bool(set(train.id_student)&set(assignments.loc[assignments.partition.eq('test'),'id_student']))
 except Exception as exc:
  checks.update(snapshot_split_integrity=False,five_student_group_folds=False,no_test_students_in_train=False);notes.append('Revisar integridad de datos: '+type(exc).__name__)
 checks['eda_preparation']=eda.get('status')=='ok' and len(eda.get('findings',[]))>=3 and features.get('status')=='ok' and features.get('new_features',0)>=2
 checks['predictive_feature_ablation']=ablation.get('status')=='complete' and ablation.get('test_used') is False
 checks['two_baselines_six_candidates']=models.get('status')=='complete' and len(models.get('baselines',[]))==2 and len(models.get('candidates',[]))==6 and all(len(r.get('folds',[]))==5 for r in models.get('candidates',[]))
 checks['foundational_llm_prompting']=checks['two_baselines_six_candidates'] and any(r.get('family')=='llm_generativo' for r in models['candidates'])
 checks['three_times_thirty']=False
 if tuning.get('status')=='complete':
  families=tuning.get('families',[]);rows=tuning.get('configurations',[])
  checks['three_times_thirty']=len(families)==3 and all(len({json.dumps(r['params'],sort_keys=True) for r in rows if r['family']==family})>=30 for family in families)
 checks['decision_frozen_by_cv']=bool(decision) and decision.get('decision_id')==identity(decision.get('content')) and decision.get('content',{}).get('v2_holdout_evaluated') is False
 aliases={r.get('alias') for r in final.get('registry',[])}
 checks['registry_and_exact_reproduction']=final.get('status')=='registered' and aliases=={'champion','challenger'} and repro.get('status')=='ok' and repro.get('ap_exact') is True and repro.get('business_exact') is True and repro.get('decision_id')==final.get('decision_id')
 checks['early_own_cohorts_and_policies']=early.get('status')=='complete' and early.get('holdout_used') is False and {14,28,42}<=set(c.get('cutoff_day') for c in early.get('cohorts',[]))
 checks['activity_association_and_increment']=checks['early_own_cohorts_and_policies'] and bool(early.get('associations')) and {'estatico','indicador','longitudinal'}<=set(r.get('mode') for r in early.get('models',[]))
 nbs=[notebook_status(name) for name in NOTEBOOKS];checks['six_fresh_kernel_notebooks']=all(r['verified'] for r in nbs)
 checks['memo_and_visual_verification']=False
 editorial=load('docs/revision-editorial.json')
 if editorial.get('status')=='ok' and (ROOT/'docs/PSet3_memo_Puerta_Wilmer.pdf').exists():
  checks['memo_and_visual_verification']=editorial.get('pages',99)<=6 and editorial.get('visual_review_passed') is True and editorial.get('pdf_sha256')==sha256(ROOT/'docs/PSet3_memo_Puerta_Wilmer.pdf')
 def state(ok,started=False):return 'evidencia disponible' if ok else ('parcial' if started else 'pendiente')
 rows=[
 {'criterion':'EDA y features','weight':15,'status':state(checks['eda_preparation'] and checks['predictive_feature_ablation'],checks['eda_preparation']),'evidence':['notebooks/01_eda.ipynb','notebooks/02_features.ipynb','docs/eda/resumen.json','docs/features/resumen.json','docs/ablacion/resultados.json'],'pending':'Ablación predictiva y revisión de su interpretación' if not checks['predictive_feature_ablation'] else ''},
 {'criterion':'Preparación y validación','weight':15,'status':state(all(checks[k] for k in ['snapshot_split_integrity','five_student_group_folds','no_test_students_in_train'])),'evidence':['src/pipeline.py','src/datos.py','docs/protocolo-congelado.json'],'pending':'Mantener declaración de benchmark 2014J previamente observado'},
 {'criterion':'Baselines y seis candidatos','weight':15,'status':state(checks['two_baselines_six_candidates'] and checks['foundational_llm_prompting'],bool(list((ROOT/'.local/modelos').glob('*/result.json')))),'evidence':['notebooks/03_baseline_candidatos.ipynb','docs/modelos/resultados.json','docs/prompting.md'],'pending':'Completar seis familias y contrastar cronología y artefactos en MLflow' if not checks['two_baselines_six_candidates'] else 'Auditoría de cronología y artefactos'},
 {'criterion':'Tuning','weight':15,'status':state(checks['three_times_thirty'],bool(tuning)),'evidence':['notebooks/04_tuning.ipynb','config/espacios-tuning.json','docs/tuning/resultados.json'],'pending':'Tres familias por negocio, >=30 configuraciones únicas por familia, nested y delta frente a dispersión'},
 {'criterion':'Tracking y Registry','weight':20,'status':'parcial','evidence':['docs/corridas.csv','docs/protocolo-congelado.json','docs/seleccion/evaluacion.json'],'pending':'Auditar metadata, firmas y ejemplos, padres/hijas, captura real y aliases vivos; esta matriz no los certifica'},
 {'criterion':'Selección y negocio','weight':15,'status':state(checks['decision_frozen_by_cv'] and checks['registry_and_exact_reproduction'],checks['decision_frozen_by_cv']),'evidence':['notebooks/05_seleccion.ipynb','docs/negocio/finalistas.json','docs/seleccion/evaluacion.json','docs/seleccion/reproduccion-champion.json'],'pending':'Decisión previa, evaluación conjunta, umbral a cupo fijo, costos, explicación y reproducción'},
 {'criterion':'Reproducibilidad y memo','weight':5,'status':state(checks['six_fresh_kernel_notebooks'] and checks['memo_and_visual_verification'],True),'evidence':['README.md','requirements.lock.txt','docs/01-verificacion.json','docs/05-verificacion.json','docs/PSet3_memo_Puerta_Wilmer.pdf'],'pending':'Ejecutar 03-06 en kernels nuevos, revisar PDF de hasta 6 páginas y auditar ZIP'},
 {'criterion':'Criterio del negocio y control estático','weight':None,'status':state(checks['decision_frozen_by_cv']),'evidence':['docs/protocolo-congelado.json','docs/negocio/finalistas.json'],'pending':'Dummy, reactiva y control estático son comparaciones distintas; elección por cobertura CV'},
 {'criterion':'Semanas 2/4/6 y margen para actuar','weight':None,'status':state(checks['early_own_cohorts_and_policies']),'evidence':['notebooks/anexos/06_anticipacion.ipynb','docs/anticipacion/resultados.json'],'pending':'Cohortes propias, cupo compartido sin repetir matrículas, estudiantes únicos y plazos explícitos'},
 {'criterion':'Ausencia de registros e incremento predictivo','weight':None,'status':state(checks['activity_association_and_increment']),'evidence':['docs/anticipacion/resultados.json'],'pending':'Asociación con incertidumbre y comparación E/E+I/L; sin afirmación causal'}]
 assert sum(r['weight'] or 0 for r in rows)==100
 result={'kind':'evidence_readiness_not_final_compliance_audit','checked_at':datetime.now(ZoneInfo('America/Guayaquil')).isoformat(),'source':'CD_PSet_3.pdf y criterios adicionales acordados; no se reutilizan métricas v1','phase':status.get('phase'),'execution_state':status.get('state'),'protocol_id':proto.get('id'),'api_budget':LibroCostos(ROOT/'.local/llm/costos.json',10).summary(),'checks':checks,'criteria':rows,'notebooks':nbs,'notes':notes,'final_compliance_certified':False}
 out=ROOT/'docs/matriz-rubrica-v2.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 text=['# Matriz de evidencia de la reconstrucción v2','',f"Actualización: {result['checked_at']}. Proceso: {result['execution_state']}; fase: {result['phase']}.",'','Seguimiento de evidencia disponible y pendiente. No asigna nota ni sustituye la auditoría final. Los notebooks preparados se distinguen de los ejecutados y verificados.','', '| Criterio | Peso | Estado | Evidencia | Comprobación pendiente |','|---|---:|---|---|---|']
 for r in rows:
  evidence='; '.join('`'+p+'`' for p in r['evidence']);weight=str(r['weight'])+' %' if r['weight'] is not None else 'adicional';text.append(f"| {r['criterion']} | {weight} | {r['status']} | {evidence} | {r['pending']} |")
 text+=['','## Notebooks','', '| Archivo | Preparado | Ejecutado | Hash y kernel nuevo verificados |','|---|---|---|---|']
 for r in nbs:text.append('| '+r['name']+' | '+str(r['present'])+' | '+str(r['executed'])+' | '+str(r['verified'])+' |')
 text+=['','La existencia de código o de una plantilla no prueba la finalización del experimento. Una respuesta inválida del LLM detiene la fase. La denominación fundacional no afirma rendimiento SOTA en OULAD. 2014J es un benchmark reutilizado y las simulaciones de tutoría no estiman un efecto causal.','', 'Regenerar: `.venv/bin/python scripts/verificar_avance_rubrica.py` desde v2.']
 (ROOT/'docs/matriz-rubrica-v2.md').write_text('\n'.join(text)+'\n');print(json.dumps({'state':result['execution_state'],'phase':result['phase'],'notebooks_prepared':sum(r['present'] for r in nbs),'notebooks_verified':sum(r['verified'] for r in nbs),'final_audit':False},ensure_ascii=False));return result
if __name__=='__main__':main()
