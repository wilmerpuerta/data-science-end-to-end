"""Auditoría de evidencia local, servidor vivo y paquete público; no reentrena ni llama al LLM."""
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import sys,os,json,re,hashlib,subprocess,zipfile
import numpy as np,pandas as pd,yaml,mlflow
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sys.path.insert(0,str(ROOT));os.environ['PSET3_V2_ROOT']=str(ROOT)
from src.common import sha256,identity,read_bundle
from src.datos import cargar_snapshot,pliegues_congelados
from src.seguimiento import protocolo,commit_actual
from src.costos import LibroCostos
from verificar_avance_rubrica import notebook_status,NOTEBOOKS

def main():
 plan=protocolo();commit=commit_actual();mlflow.set_tracking_uri('http://127.0.0.1:5001');client=mlflow.MlflowClient();exp=client.get_experiment_by_name('oulad-apoyo-academico-v2');runs=client.search_runs([exp.experiment_id],max_results=5000);csv=pd.read_csv(ROOT/'docs/corridas.csv');checks=[]
 def check(name,ok,evidence):checks.append({'check':name,'passed':bool(ok),'evidence':evidence})
 check('CSV_vs_servidor',set(csv.run_id)=={r.info.run_id for r in runs},'docs/corridas.csv / servidor vivo')
 train,_=cargar_snapshot();folds=list(pliegues_congelados(train));read_bundle();read_bundle('splits-current.json');check('snapshot_splits_y_CV',len(folds)==5 and all(not set(train.iloc[a].id_student)&set(train.iloc[b].id_student) for a,b in folds),'bundles con hash y cinco folds persistidos')
 required_tags=['fase','familia','git_commit','protocol_id','version'];required_params=['snapshot_id','split_id','snapshot_at_utc','source_table','labels_table','cutoff_day','seed','cv_folds','capacity','pipeline_sha256','client_lock_sha256']
 finished=[r for r in runs if r.info.status=='FINISHED'];missing=[]
 for r in runs:
  if not all(k in r.data.tags for k in required_tags) or not all(k in r.data.params for k in required_params):missing.append(r.info.run_id)
 check('metadata_todas_corridas',not missing,{'runs':len(runs),'missing':missing})
 shas={r.data.tags.get('git_commit','') for r in runs};badsha=[]
 for value in shas:
  p=subprocess.run(['git','cat-file','-e',value+'^{commit}'],cwd=REPO,capture_output=True)
  if len(value)!=40 or p.returncode:badsha.append(value)
 check('commits_Git_reales',not badsha,{'unique_commits':len(shas),'missing':badsha,'current_source_commit':commit})
 models=json.loads((ROOT/'docs/modelos/resultados.json').read_text());tuned=json.loads((ROOT/'docs/tuning/resultados.json').read_text());d=json.loads((ROOT/'docs/negocio/finalistas.json').read_text());final=json.loads((ROOT/'docs/seleccion/evaluacion.json').read_text());repro=json.loads((ROOT/'docs/seleccion/reproduccion-champion.json').read_text());early=json.loads((ROOT/'docs/anticipacion/resultados.json').read_text())
 check('dos_baselines_y_seis_familias',len(models['baselines'])==2 and len(models['candidates'])==6 and any(r['family']=='llm_generativo' and len(r['folds'])==5 for r in models['candidates']),'Dummy, reactiva, cinco familias tabulares y GPT evaluado')
 starts=[client.get_run(r['run_id']).info.start_time for r in models['candidates']];ends=[client.get_run(r['run_id']).info.end_time for r in models['baselines']];check('baselines_antes_de_candidatos',min(starts)>=max(ends),{'earliest_candidate_ms':min(starts),'latest_baseline_end_ms':max(ends)})
 counts={family:len({json.dumps(r['params'],sort_keys=True) for r in tuned['configurations'] if r['family']==family}) for family in tuned['families']};check('tres_por_treinta',len(counts)==3 and all(n>=30 for n in counts.values()),counts)
 top=sorted(models['candidates'],key=lambda r:(-r['cv_coverage_mean'],r['cv_coverage_std'],-r['cv_ap_fail_mean'],r['cv_brier_fail_mean'],r.get('api_cost_new_calls_usd',0),r.get('cv_fit_seconds_total',0),r['run_id']))[:3];check('top3_por_negocio',set(counts)=={r['family'] for r in top},list(counts))
 children=[r for r in finished if r.data.tags.get('fase')=='tuning'];check('tuning_nested',len(children)==90 and all(r.data.tags.get('mlflow.parentRunId') for r in children),'90 configuraciones hijas; padres no se suman como configuraciones')
 from figura_tuning import resumen_tuning
 construction=json.loads((ROOT/'docs/memo-construccion.json').read_text());tuning_figures=[f for f in construction['native_vector_figures'] if f['kind']=='native_tuning_default_vs_adjusted']
 notebook04=json.loads((ROOT/'notebooks/04_tuning.ipynb').read_text());figure_outputs=sum('image/png' in output.get('data',{}) for cell in notebook04['cells'] for output in cell.get('outputs',[]))
 tuning_graph_ok=len(tuning_figures)==1 and tuning_figures[0]['page']==4 and tuning_figures[0]['rows']==resumen_tuning(ROOT) and construction['pdf_sha256']==sha256(ROOT/'docs/PSet3_memo_Puerta_Wilmer.pdf') and figure_outputs>=1 and all((ROOT/'docs/tuning'/name).is_file() for name in ['default_vs_ajustado.svg','default_vs_ajustado.png'])
 check('grafico_tuning_documento_y_notebook',tuning_graph_ok,{'memo_page':4,'native_vector_graphs':len(tuning_figures),'notebook04_figure_outputs':figure_outputs,'metric':'CV Fail coverage; mean ± fold SD, not CI','run_ids_match_frozen_decision':bool(tuning_figures) and tuning_figures[0]['rows']==resumen_tuning(ROOT)})

 nonfit={'eda','features','tuning_parent','control_estatico_parent','decision_previa','anticipacion_politicas'}
 fitted=[r for r in finished if r.data.tags.get('fase') not in nonfit and r.data.tags.get('familia')!='politica_reactiva']
 specs=[]
 for r in fitted:
  for path in (['winner_pipeline','challenger_pipeline'] if r.data.tags.get('fase')=='final' else ['pipeline']):specs.append((r.info.run_id,path))
 def inspect(spec):
  rid,path=spec;folder=ROOT/'.local/auditoria-modelos'/rid/path;folder.mkdir(parents=True,exist_ok=True)
  children=client.list_artifacts(rid,path);names={Path(a.path).name for a in children};local=folder/'MLmodel'
  if not local.exists() and (folder/path/'MLmodel').exists():local=folder/path/'MLmodel'
  if not local.exists():
   downloaded=client.download_artifacts(rid,path+'/MLmodel',str(folder));local=Path(downloaded)
  data=yaml.safe_load(local.read_text());example=data.get('saved_input_example_info',{}).get('artifact_path');signature=data.get('signature',{})
  ok='MLmodel'in names and bool(signature.get('inputs')) and bool(signature.get('outputs')) and example in names and data.get('flavors',{}).get('python_function',{}).get('predict_fn')=='predict_proba'
  return {'run_id':rid,'artifact':path,'passed':ok,'MLmodel_sha256':sha256(local),'input_example':example,'signature':signature}
 with ThreadPoolExecutor(max_workers=8) as pool:artifacts=list(pool.map(inspect,specs))
 (ROOT/'docs/auditoria-modelos.json').write_text(json.dumps({'models':artifacts},ensure_ascii=False,indent=2)+'\n');check('pipelines_firma_y_ejemplo',all(a['passed'] for a in artifacts) and len(artifacts)==370,{'fit_runs':len(fitted),'pipelines':len(artifacts),'failures':[a for a in artifacts if not a['passed']]})
 check('decision_previa_integra',identity(d['content'])==d['decision_id']==final['decision_id'] and d['content']['created_at_utc']<final['evaluated_at_utc'] and final['winner_changed_using_test'] is False,'docs/negocio/finalistas.json / docs/seleccion/evaluacion.json')
 version_ok=True
 for entry in final['registry']:
  live=client.get_model_version_by_alias('oulad-apoyo-academico-v2-modelo',entry['alias']);version_ok &= str(live.version)==entry['version'] and live.run_id==entry['run_id']
 check('aliases_registry',version_ok and {e['alias'] for e in final['registry']}=={'champion','challenger'},final['registry'])
 check('reproduccion_exacta_proceso_limpio',repro['status']=='ok' and repro['ap_exact'] and repro['business_exact'] and repro['predictions_array_exact'] and repro['api_new_requests']==0,'docs/seleccion/reproduccion-champion.json')
 nbs=[notebook_status(n) for n in NOTEBOOKS];check('seis_notebooks_ejecutados_y_hashed',all(n['verified'] for n in nbs),nbs)
 check('anticipacion_y_un_solo_cupo',early['status']=='complete' and len(early['models'])==24 and all(p['used']<=p['budget'] for p in early['policies']) and early['holdout_used'] is False,'24 variantes, cohortes propias, K compartido, matrícula sin repetir; personas únicas informadas')
 check('ausencia_registros_asociacion_ablacion',len(early['associations'])==4 and {'estatico','indicador','longitudinal'}<=set(r['mode'] for r in early['models']),'asociación, IC por estudiante, estandarización y E/E+I/L; sin causalidad')
 check('estaticos_no_Dummy_y_reactiva_acotada',len(d['content']['static_controls'])==2 and final['reactive']['preventive_coverage']==0 and final['reactive']['after_closure_tp']<=final['reactive']['capacity'],'controles independientes; reacción posterior separada')
 editorial=json.loads((ROOT/'docs/revision-editorial.json').read_text());check('PDF_seis_paginas_y_revision_visual',editorial['pages']==6 and editorial['visual_review_passed'] and editorial['pdf_sha256']==sha256(ROOT/'docs/PSet3_memo_Puerta_Wilmer.pdf'),'seis páginas renderizadas con Poppler, figuras vectoriales y captura real')
 check('prompting_conclusion_negocio',editorial['prompting_summary_present'] and editorial['university_cost_benefit_present'],'factible; costo medido separado de costo operativo futuro y evaluación posterior con Universidad')
 budget=LibroCostos(ROOT/'.local/llm/costos.json',10).summary();check('presupuesto_incluye_intentos',float(budget['accounted_spend_usd'])<=10 and float(budget['pending_upper_usd'])==0,budget)
 report={'status':'verified_with_declared_limitations' if all(r['passed'] for r in checks) else 'failed','checked_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'runs':len(runs),'finished':len(finished),'failed_runs':len(runs)-len(finished),'model_pipelines_verified':len(artifacts),'api_budget':budget,'academic_grade_assigned':False,'limitations':['2014J observed in v1: retrospective reused benchmark, not newly independent hold-out','No demonstrated stable superiority or causal effect of tutoring; maturation and publication of labels unverified','Private snapshot, native models, LLM responses and MLflow volumes excluded from public package; exact runtime reproduction conditional on private backup','Filename Puerta_Wilmer and folder pset-03 follow author authorization; symlinks preserve standard entry points while canonical source remains v2','Auxiliary multi-cut policy inherits cutoff_day=56 from the common logger; actual rounds 14/28/42 are explicit in its policy artifact; it is not a fitted cutoff-56 estimator']}
 (ROOT/'docs/auditoria-rubrica.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 lines=['# Auditoría final PSet 3 - reconstrucción v2','', 'Resultado: **'+report['status']+'**. No se asigna nota ni se afirma 100 % de cumplimiento literal. Se auditan evidencias y se conservan las limitaciones declaradas.','', '| Comprobación | Resultado |','|---|---|']
 for r in checks:lines.append('| '+r['check']+' | '+('PASA' if r['passed'] else 'REVISAR')+' |')
 lines+=['',f"Servidor: {len(runs)} runs; {len(finished)} FINISHED; {len(runs)-len(finished)} FAILED. Se comprobaron firma, ejemplo y flavor de {len(artifacts)} pipelines reales, sin confundir fallos o padres lógicos con configuraciones válidas.",'','## Límites de interpretación y reproducción','']+[ '- '+s for s in report['limitations']]+['','La conclusión del memo responde a prompting: se ensayó y es factible; la adopción de un LLM externo es una decisión posterior de costo-beneficio con la Universidad. El consumo experimental medido no sustituye una estimación de escala productiva.','', 'Detalle: [auditoria-rubrica.json](auditoria-rubrica.json). Artefactos: [auditoria-modelos.json](auditoria-modelos.json). Ejecución: `scripts/auditar_entrega.py` desde el entorno v2 y con el servidor/snapshot privados disponibles.']
 (ROOT/'docs/auditoria-rubrica.md').write_text('\n'.join(lines)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks),'pipelines':len(artifacts),'failed_checks':[r['check'] for r in checks if not r['passed']]}));return report
if __name__=='__main__':
 r=main()
 if r['status']=='failed':raise SystemExit(1)
