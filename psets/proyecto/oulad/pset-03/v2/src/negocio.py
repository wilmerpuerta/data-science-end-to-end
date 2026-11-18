"""Controles equivalentes y elección previa a prueba por CV de negocio."""
from datetime import datetime,timezone
import json
import mlflow
from .common import ROOT,identity,read_bundle
from .tuning import choose,run_trial
from .seguimiento import configurar,protocolo,registrar_base,exportar
OUT=ROOT/'docs/negocio';PRIVATE=ROOT/'.local/negocio'

def normalized(row):
 r=dict(row)
 r['cv_brier_fail_mean']=row.get('cv_brier_fail_mean',-row.get('cv_neg_brier_fail_mean',0))
 r['origin']='tuning' if 'config_index' in row else 'default'
 return r

def main():
 configurar();plan=protocolo();OUT.mkdir(parents=True,exist_ok=True);PRIVATE.mkdir(parents=True,exist_ok=True)
 path=OUT/'finalistas.json'
 if path.exists():
  d=json.loads(path.read_text());assert d['decision_id']==identity(d['content']);assert d['content']['protocol_id']==plan['id'];return d
 defaults=json.loads((ROOT/'docs/modelos/resultados.json').read_text())['candidates']
 tuning=json.loads((ROOT/'docs/tuning/resultados.json').read_text());assert tuning['status']=='complete' and len(tuning['configurations'])>=90
 best=[]
 for family in [r['family'] for r in defaults]:
  rows=[normalized(r) for r in defaults+tuning['configurations'] if r['family']==family]
  best.append(choose(rows))
 winner=choose(best);challenger=choose([r for r in best if r['family']!=winner['family']]);controls=[]
 spaces=json.loads((ROOT/'config/espacios-tuning.json').read_text())
 for finalist in [winner,challenger]:
  family=finalist['family'];parentfile=PRIVATE/(family+'-static-parent.json')
  if parentfile.exists():parent=json.loads(parentfile.read_text())['run_id']
  else:
   with mlflow.start_run(run_name='control-estatico-'+family) as run:
    parent=run.info.run_id;registrar_base('control_estatico_parent',family,{'mode':'static','n_configurations':31});mlflow.log_dict({'draws':spaces[family]+[{}],'same_folds_as_main':True},'search-plan.json')
   parentfile.write_text(json.dumps({'run_id':parent,'protocol_id':plan['id']}))
  with mlflow.start_run(run_id=parent):rows=[normalized(run_trial(family,i,p,mode='static')) for i,p in enumerate(spaces[family]+[{}])]
  controls.append(choose(rows));(OUT/(family+'-static.json')).write_text(json.dumps(rows,indent=2))
 delta=winner['cv_coverage_mean']-challenger['cv_coverage_mean'];variability=max(winner['cv_coverage_std'],challenger['cv_coverage_std'])
 improvements=[]
 for family in tuning['families']:
  default=next(r for r in defaults if r['family']==family);tuned=choose([normalized(r) for r in tuning['configurations'] if r['family']==family]);gain=tuned['cv_coverage_mean']-default['cv_coverage_mean'];spread=max(default['cv_coverage_std'],tuned['cv_coverage_std'])
  improvements.append({'family':family,'default_run_id':default['run_id'],'tuned_run_id':tuned['run_id'],'delta_coverage':gain,'cv_spread_reference':spread,'improvement_exceeds_fold_variation':gain>spread,'interpretation':'mejora respaldada por el criterio descriptivo de la rúbrica' if gain>spread else 'sin mejora demostrada frente a la variación entre pliegues'})
 content={'protocol_id':plan['id'],'created_at_utc':datetime.now(timezone.utc).isoformat(),'snapshot_id':read_bundle()[1]['id'],'split_id':read_bundle('splits-current.json')[1]['id'],'winner':winner,'challenger':challenger,'family_best':best,'static_controls':controls,'tuning_improvements':improvements,'selection_criterion':'maximum mean CV Fail coverage at 10% per edition/fold; fixed ties in protocol','winner_challenger_difference':delta,'fold_variation_reference':variability,'difference_exceeds_fold_variation':delta>variability,'uncertainty_scope':'descriptive fold variability, not independent confidence intervals; all choices use development only','holdout_previously_observed_in_v1':True,'v2_holdout_evaluated':False}
 d={'decision_id':identity(content),'content':content}
 with path.open('x') as f:json.dump(d,f,indent=2,ensure_ascii=False)
 with mlflow.start_run(run_name='decision-CV-antes-de-prueba'):
  registrar_base('decision_previa','comparacion_finalistas');mlflow.log_dict(d,'decision.json');mlflow.log_metrics({'winner_cv_coverage':winner['cv_coverage_mean'],'challenger_cv_coverage':challenger['cv_coverage_mean'],'difference':delta,'fold_variation_reference':variability})
 exportar();print(json.dumps({'decision_id':d['decision_id'],'winner':winner['family'],'challenger':challenger['family'],'test_opened':False}),flush=True);return d
