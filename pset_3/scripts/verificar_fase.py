"""Comprueba evidencias de fases terminadas sin entrenar, registrar o inferir por API."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
REPORTS={'modelos':'docs/modelos/resultados.json','tuning':'docs/tuning/resultados.json','ablacion':'docs/ablacion/resultados.json','negocio':'docs/negocio/finalistas.json','anticipacion':'docs/anticipacion/resultados.json','seleccion':'docs/seleccion/evaluacion.json'}
def verificar(phase):
 from src.seguimiento import protocolo
 from src.common import read_bundle,identity
 plan=protocolo();read_bundle();read_bundle('splits-current.json')
 report=json.loads((ROOT/REPORTS[phase]).read_text());content=report.get('content',report)
 assert content['protocol_id']==plan['id']
 if phase=='negocio':assert report['decision_id']==identity(content)
 elif phase=='seleccion':assert report['status']=='registered' and report['winner_changed_using_test'] is False
 else:assert report['status']=='complete'
 result={'status':'verified_existing','phase':phase,'root':str(ROOT),'protocol_id':plan['id'],'new_model_fits':0,'new_api_requests':0};print(json.dumps(result,ensure_ascii=False));return result
