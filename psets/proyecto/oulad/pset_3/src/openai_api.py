"""Responses API con esquema estricto, caché privada y límite global explícito."""
from pathlib import Path
from decimal import Decimal
import hashlib,json,os
import requests
from dotenv import dotenv_values
from .costos import LibroCostos
ROOT=Path(os.environ.get('PSET3_V2_ROOT',str(Path(__file__).resolve().parents[1]))).resolve()
CREDENTIALS=ROOT/'.secrets/pset3-openai.env'
MODEL='gpt-6-luna'
RATES={'input':Decimal('.10'),'output':Decimal('.50'),'max_input':Decimal('.25')}

def accounted_cost(usage):
 total=int(usage['input_tokens']);details=usage.get('input_tokens_details')
 if not details or 'cache_write_tokens' not in details:extra=Decimal(total)*Decimal('.15')
 else:
  written=int(details.get('cache_write_tokens',0));ttl=details.get('cache_write_tokens_details',{});short=int(ttl.get('ttl_30m_tokens',0));long=int(ttl.get('ttl_12h_tokens',0))
  if min(total,written,short,long)<0 or written>total or short+long>written:raise RuntimeError('Desglose de cache incompatible; conservar reserva y reconciliar')
  unknown=written-short-long;extra=Decimal(short)*Decimal('.025')+Decimal(long+unknown)*Decimal('.15')
 infactor=Decimal(2) if total>272000 else Decimal(1);outfactor=Decimal('1.5') if total>272000 else Decimal(1)
 return ((Decimal(total)*RATES['input']+extra)*infactor+Decimal(usage['output_tokens'])*RATES['output']*outfactor)/Decimal(1000000)


def final_output_text(raw):
 messages=[o for o in raw.get('output',[]) if o.get('type')=='message']
 phased=any(o.get('phase') is not None for o in messages)
 final=[o for o in messages if o.get('phase')=='final_answer'] if phased else messages
 if len(final)!=1 or final[0].get('status')!='completed' or final[0].get('role')!='assistant':raise RuntimeError('No hay una respuesta final única y completa; cobro archivado')
 if any(c.get('type')=='refusal' for c in final[0].get('content',[])):raise RuntimeError('Respuesta final rechazada; no se inventan probabilidades')
 return [c['text'] for c in final[0].get('content',[]) if c.get('type')=='output_text']

def settings():
 c={**dotenv_values(CREDENTIALS),**{k:v for k,v in os.environ.items() if k.startswith('OPENAI_')}}
 if c.get('OPENAI_MODEL',MODEL)!=MODEL:raise ValueError('Cambiar modelo requiere versionar protocolo y tarifas')
 if c.get('OPENAI_BASE_URL','https://api.openai.com/v1').rstrip('/')!='https://api.openai.com/v1':raise ValueError('Solo se permite el endpoint oficial configurado')
 if Decimal(c.get('OPENAI_MAX_BUDGET_USD','10'))>10:raise ValueError('Tope de USD 10 excedido')
 return c

def credential_status():
 c=settings();return {'configured':bool(c.get('OPENAI_API_KEY','').strip()),'model':MODEL,'limit_usd':c.get('OPENAI_MAX_BUDGET_USD','10'),'credentials_file':str(CREDENTIALS)}

class ResponsesClient:
 def __init__(self):
  if not (ROOT/'config/protocolo-v2.json').is_file():raise RuntimeError('Defina PSET3_V2_ROOT con la carpeta pset_3 antes de realizar llamadas nuevas')
  self.cache=ROOT/'.local/llm/requests';self.cache.mkdir(parents=True,exist_ok=True)
  self.book=LibroCostos(ROOT/'.local/llm/costos.json',10)
 def predict_batch(self,system,user,n):
  if not isinstance(n,int) or n<=0:raise ValueError('El tamaño del lote debe ser positivo')
  labels=['Approved','Fail','Withdrawn'];keys=[f'q{i:03d}' for i in range(n)]
  triple={'type':'object','properties':{c:{'type':'number'} for c in labels},'required':labels,'additionalProperties':False}
  rows={'type':'object','properties':{key:triple for key in keys},'required':keys,'additionalProperties':False}
  schema={'type':'object','properties':{'probabilities':rows},'required':['probabilities'],'additionalProperties':False}
  system+=' Output the required probabilities object: q000 corresponds to the first query, q001 to the second, and so on. Each query has exactly the three named outcome fields. Do not repeat any query or field.'
  payload={'model':MODEL,'input':[{'role':'system','content':system},{'role':'user','content':user}],'reasoning':{'effort':'none'},'text':{'format':{'type':'json_schema','name':'academic_risk','strict':True,'schema':schema}},'max_output_tokens':max(1024,n*160+256),'store':False,'tools':[],'service_tier':'default'}
  wire=json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode();key=hashlib.sha256(wire).hexdigest();path=self.cache/(key+'.json')
  if path.exists():return json.loads(path.read_text())['parsed'],{'cache_hit':True,'request_hash':key}
  c=settings();secret=c.get('OPENAI_API_KEY','').strip()
  if not secret:raise RuntimeError('Configura OPENAI_API_KEY en '+str(CREDENTIALS))
  # Cota por bytes de todo el JSON + margen; no se aplica descuento de caché ni se usan herramientas pagadas.
  input_bound=len(wire)+4096
  in_factor=Decimal(2) if input_bound>272000 else Decimal(1)
  out_factor=Decimal('1.5') if input_bound>272000 else Decimal(1)
  upper=((Decimal(input_bound)*RATES['max_input']*in_factor)+Decimal(payload['max_output_tokens'])*RATES['output']*out_factor)/Decimal(1000000)
  reservation=self.book.reserve(upper,key)
  try:
   response=requests.post('https://api.openai.com/v1/responses',headers={'Authorization':'Bearer '+secret,'Content-Type':'application/json'},data=wire,timeout=90)
  except requests.RequestException as exc:
   # La reserva queda consumiendo presupuesto ante cobro incierto; no reintentar automáticamente.
   raise RuntimeError('Fallo de red; reserva pendiente para reconciliar, sin reintento automático') from exc
  if response.status_code!=200:
   if response.status_code in [401,403,404,429]:self.book.release_unbilled(reservation,response.status_code)
   try:error=response.json().get('error',{})
   except ValueError:error={}
   info={'http_status':response.status_code,'code':error.get('code'),'type':error.get('type'),'request_hash':key}
   with (self.cache.parent/'errores.jsonl').open('a') as log:log.write(json.dumps(info)+'\n')
   raise RuntimeError('OpenAI rechazó la petición: '+json.dumps(info)+'; credenciales y contenido individual omitidos')
  raw=response.json();archive=self.cache.parent/'responses';archive.mkdir(exist_ok=True);rawpath=archive/(key+'.json');rawpath.write_text(json.dumps({'request_hash':key,'request':payload,'response':raw},ensure_ascii=False));os.chmod(rawpath,0o600);usage=raw.get('usage')
  if not usage:raise RuntimeError('Respuesta sin usage: conservar reserva y revisar antes de continuar')
  cost=accounted_cost(usage)
  self.book.settle(reservation,cost,usage,raw.get('id'))
  texts=final_output_text(raw) if raw.get('status')=='completed' else []
  if raw.get('status')!='completed' or not texts:
   info={'http_status':200,'code':'incomplete_response','details':raw.get('incomplete_details'),'request_hash':key}
   with (self.cache.parent/'errores.jsonl').open('a') as log:log.write(json.dumps(info)+'\n')
   raise RuntimeError('Respuesta incompleta o rechazo; cobro y respuesta archivados: '+json.dumps(info))
  def unique_object(pairs):
   value={}
   for key,item in pairs:
    if key in value:raise ValueError('Campo JSON repetido: '+key)
    value[key]=item
   return value
  try:
   decoded=json.loads(''.join(texts),object_pairs_hook=unique_object)
   if set(decoded)!={'probabilities'}:raise ValueError('Campos superiores inesperados')
   entries=decoded['probabilities']
   if set(entries)!=set(keys):raise ValueError('Claves de consultas incompletas o adicionales')
   if any(not isinstance(entries[key],dict) or set(entries[key])!=set(labels) for key in keys):raise ValueError('Clases incompletas o adicionales')
   parsed=[[entries[key][label] for label in labels] for key in keys]
  except (ValueError,KeyError,TypeError) as exc:raise RuntimeError('Salida no interpretable; cobro y respuesta archivados') from exc
  saved={'request_hash':key,'model':raw.get('model'),'response_id':raw.get('id'),'request':payload,'response':raw,'parsed':parsed,'cost_upper_accounted_usd':str(cost)}
  tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(saved,ensure_ascii=False));os.chmod(tmp,0o600);tmp.replace(path)
  return parsed,{'cache_hit':False,'request_hash':key,'usage':usage,'cost_usd':str(cost)}
