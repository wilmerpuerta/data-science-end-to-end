"""Contraste local descriptivo posterior a la decisión; solo desarrollo y sin identificadores."""
from pathlib import Path
from datetime import datetime,timezone
import sys,os,json,numpy as np,mlflow,mlflow.sklearn
from threadpoolctl import threadpool_limits
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['PSET3_V2_ROOT']=str(ROOT)
from src.datos import cargar_snapshot
from src.experimentos import entrada
from src.pipeline import ACTIVIDAD
from src.evaluacion import probabilidades
from src.seleccion import MODEL
from src.common import sha256
mlflow.set_tracking_uri('http://127.0.0.1:5001');model=mlflow.sklearn.load_model(f'models:/{MODEL}@champion');train,_=cargar_snapshot();x=entrada(train)
with threadpool_limits(limits=2):p=probabilidades(model,x)[:,1]
case=int(np.argmax(p));donor=int(np.argsort(p)[len(p)//2]);row=x.iloc[[case]].copy();reference=x.iloc[donor]
groups={'actividad_completa':ACTIVIDAD+['has_recorded_activity'],'ventanas_actual_previa':['clicks_current_14d','active_days_current_14d','clicks_previous_14d','click_change_14d'],'recencia':['recency_days'],'antecedentes':['num_of_prev_attempts','studied_credits'],'contexto_demografico':['gender','region','highest_education','imd_band','age_band','disability','is_imd_missing']};results=[]
for name,cols in groups.items():
 cf=row.copy()
 for col in cols:cf[col]=reference[col]
 with threadpool_limits(limits=2):value=float(probabilidades(model,cf)[0,1])
 results.append({'group':name,'actual_p_fail':float(p[case]),'p_fail_with_observed_reference_group':value,'delta':value-float(p[case])})
report={'status':'ok','recorded_at_utc':datetime.now(timezone.utc).isoformat(),'source_sha256':sha256(__file__),'uri':f'models:/{MODEL}@champion','scope':'post-decision descriptive analysis using only development data; no test labels or reselection','case_selection':'highest development model score, without using outcome','reference_selection':'development case at median model score, without using outcome','reference_risk':float(p[donor]),'groups':results,'identifiers_published':False,'causal':False,'limits':'Observed donor group substitution is a local model-behavior contrast, not additive SHAP nor a feasible/causal intervention; cross-group dependence can remain.'}
(ROOT/'docs/seleccion/explicacion_local_desarrollo.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Contraste local documentado sin entrenar ni consultar API.')
