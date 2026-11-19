"""Proceso limpio: cargar champion por alias y verificar sin nuevas llamadas al LLM."""
from pathlib import Path
import sys,os,json
from unittest.mock import patch
import numpy as np,pandas as pd,mlflow,mlflow.sklearn
from threadpoolctl import threadpool_limits
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['PSET3_V2_ROOT']=str(ROOT)
from src.datos import cargar_snapshot
from src.experimentos import entrada
from src.evaluacion import probabilidades,metricas,negocio,CLASSES
from src.seguimiento import configurar,protocolo
from src.common import sha256
from src.seleccion import MODEL

def main():
 configurar();protocolo();report=json.loads((ROOT/'docs/seleccion/evaluacion.json').read_text());assert report['status']=='registered'
 saved=ROOT/'.local/seleccion/predicciones_prueba.parquet';assert sha256(saved)==report['prediction_sha256']
 model=mlflow.sklearn.load_model(f'models:/{MODEL}@champion');test,_=cargar_snapshot(particion='test',permitir_prueba=True);x=entrada(test)
 with patch('src.openai_api.requests.post',side_effect=RuntimeError('La reproducción exacta no permite nuevas inferencias API')),threadpool_limits(limits=2):p=probabilidades(model,x)
 prior=pd.read_parquet(saved);assert prior.enrollment_key.tolist()==test.enrollment_key.tolist();expected=prior[['winner__'+c for c in CLASSES]].to_numpy();np.testing.assert_allclose(p,expected,rtol=1e-12,atol=1e-14)
 tech=metricas(test.target_class,p);biz=negocio(test,test.target_class,p[:,1]);recorded=report['models']['winner']
 assert tech['ap_fail']==recorded['technical']['ap_fail'] and biz==recorded['business']['0.1']
 result={'status':'ok','decision_id':report['decision_id'],'fresh_process':True,'uri':f'models:/{MODEL}@champion','api_new_requests':0,'predictions_array_exact':bool(np.array_equal(p,expected)),'prediction_max_abs_difference':float(np.max(np.abs(p-expected))),'ap_exact':True,'business_exact':True,'technical':tech,'business':biz}
 (ROOT/'docs/seleccion/reproduccion-champion.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));return result
if __name__=='__main__':main()
