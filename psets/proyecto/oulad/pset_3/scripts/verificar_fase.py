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

def entrada(phase,function):
 import argparse
 parser=argparse.ArgumentParser(description='Reutiliza evidencia terminada; --ejecutar activa la fase original deliberadamente')
 group=parser.add_mutually_exclusive_group();group.add_argument('--verificar',action='store_true');group.add_argument('--ejecutar',action='store_true')
 args=parser.parse_args()
 if args.ejecutar:return function()
 if args.verificar or (ROOT/REPORTS[phase]).is_file():return verificar(phase)
 return function()
