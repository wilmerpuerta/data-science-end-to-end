"""Recuperación explícita de envoltura textual: conserva JSON original, sin nueva inferencia."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,math,os,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.openai_api import final_output_text
LABELS=['Approved','Fail','Withdrawn']
def unique_object(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('Campo repetido')
  d[k]=v
 return d

def extract_verified(text,keys):
 start=text.find('{')
 if start<0 or start>256:raise ValueError('No hay objeto JSON único con prefijo acotado')
 decoder=json.JSONDecoder(object_pairs_hook=unique_object)
 value,end=decoder.raw_decode(text,start);suffix=text[end:].strip()
 if suffix not in ['', '```']:raise ValueError('Texto u objeto adicional después del JSON')
 if not isinstance(value,dict) or set(value)!={'probabilities'}:raise ValueError('Objeto superior inválido')
 rows=value['probabilities']
 if not isinstance(rows,dict) or set(rows)!=set(keys):raise ValueError('Consultas faltantes o adicionales')
 parsed=[]
 for key in keys:
  row=rows[key]
  if not isinstance(row,dict) or set(row)!=set(LABELS):raise ValueError('Clases faltantes o adicionales')
  p=[row[c] for c in LABELS]
  if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in p):raise ValueError('Probabilidad inválida')
  if abs(sum(p)-1)>.02:raise ValueError('Suma de probabilidades inválida')
  parsed.append(p)
 return parsed,{'prefix_chars':start,'suffix_chars':len(suffix),'json_sha256':hashlib.sha256(text[start:end].encode()).hexdigest()}

def main():
 base=ROOT/'.local/llm';ledger=json.loads((base/'costos.json').read_text());recovered=[];rejected=[]
 for path in sorted((base/'responses').glob('*.json')):
  cache=base/'requests'/path.name
  if cache.exists():continue
  item=json.loads(path.read_text());raw=item['response'];payload=item['request']
  if raw.get('status')!='completed':continue
  fmt=payload['text']['format']['schema']['properties']['probabilities']
  if fmt.get('type')!='object':continue
  key=hashlib.sha256(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
  if key!=path.stem or item['request_hash']!=key:raise ValueError('Hash de petición incompatible')
  try:
   text=''.join(final_output_text(raw));parsed,normalization=extract_verified(text,fmt['required'])
  except (RuntimeError,ValueError,KeyError,TypeError) as exc:rejected.append({'request_hash':key,'reason':str(exc)});continue
  events=[e for e in ledger['events'] if e.get('request_hash')==key and e.get('response_id')==raw.get('id') and 'cost' in e]
  if len(events)!=1:raise ValueError('No se puede conciliar el cobro de la respuesta')
  saved={'request_hash':key,'model':raw.get('model'),'response_id':raw.get('id'),'request':payload,'response':raw,'parsed':parsed,'cost_upper_accounted_usd':events[0]['cost'],'recovery':{'method':'completed_assistant_final_answer_only_then_exact_schema_validation','probabilities_changed':False,'new_api_requests':0,**normalization}}
  tmp=cache.with_suffix('.tmp');tmp.write_text(json.dumps(saved,ensure_ascii=False));os.chmod(tmp,0o600);tmp.replace(cache)
  recovered.append({'request_hash':key,'rows':len(parsed),'original_response_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'original_response_preserved':True,'probabilities_changed':False,'new_api_requests':0,**normalization})
 report={'status':'ok' if not rejected else 'requires_inspection','recorded_at_utc':datetime.now(timezone.utc).isoformat(),'method':'explicit technical recovery, not a new model call and not an automatic retry','recovered':recovered,'rejected':rejected,'new_api_requests':0,'scope':'Only complete unique objects matching every requested key, class, numeric range and probability sum; no truncation repair, no filled or guessed predictions.'}
 output=ROOT/'docs/recuperacion-respuestas-llm.json';prior=json.loads(output.read_text()) if output.exists() else {'events':[]};prior['events'].append(report);output.write_text(json.dumps(prior,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));return report
if __name__=='__main__':
 if sys.argv[1:]==['--verificar']:
  ledger=json.loads((ROOT/'.local/llm/costos.json').read_text())
  print(json.dumps({'status':'paths_checked','requests':len(list((ROOT/'.local/llm/requests').glob('*.json'))),'responses':len(list((ROOT/'.local/llm/responses').glob('*.json'))),'new_api_requests':0,'recovery_executed':False}))
 else:main()
