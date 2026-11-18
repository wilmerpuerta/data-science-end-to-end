"""Libro global con reservas conservadoras; nunca autoriza más de USD 10."""
from pathlib import Path
from contextlib import contextmanager
from decimal import Decimal
from datetime import datetime,timezone
import fcntl,json,os,uuid

class PresupuestoAgotado(RuntimeError):pass
class LibroCostos:
 def __init__(self,path,limit=10):
  self.path=Path(path);self.limit=Decimal(str(limit))
  if not 0<self.limit<=10:raise ValueError('El límite autorizado es como máximo USD 10')
  self.path.parent.mkdir(parents=True,exist_ok=True)
 @contextmanager
 def locked(self):
  lock=self.path.with_suffix('.lock')
  with lock.open('a+') as f:
   os.chmod(lock,0o600);fcntl.flock(f,fcntl.LOCK_EX)
   try:
    state=json.loads(self.path.read_text()) if self.path.exists() else {'limit':str(self.limit),'spent':'0','pending':{},'events':[]}
    if Decimal(state['limit'])!=self.limit:raise ValueError('Límite modificado respecto del libro existente')
    yield state
    tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2));os.chmod(tmp,0o600);tmp.replace(self.path)
   finally:fcntl.flock(f,fcntl.LOCK_UN)
 def reserve(self,upper,request_hash):
  value=Decimal(str(upper));assert value>=0
  with self.locked() as s:
   used=Decimal(s['spent'])+sum((Decimal(x['upper']) for x in s['pending'].values()),Decimal(0))
   if used+value>self.limit:raise PresupuestoAgotado(f'La siguiente petición excedería el tope de USD {self.limit}; consumo/reservas {used}, nueva reserva {value}')
   key=uuid.uuid4().hex;s['pending'][key]={'upper':str(value),'request_hash':request_hash,'at_utc':datetime.now(timezone.utc).isoformat()}
  return key
 def settle(self,key,cost,usage,response_id):
  cost=Decimal(str(cost))
  with self.locked() as s:
   reservation=s['pending'][key]
   if cost>Decimal(reservation['upper']):raise RuntimeError('Uso reportado excede la cota reservada; se requiere reconciliación')
   s['spent']=str(Decimal(s['spent'])+cost);del s['pending'][key]
   s['events'].append({'reservation':key,'cost':str(cost),'usage':usage,'response_id':response_id,'request_hash':reservation['request_hash']})
 def release_unbilled(self,key,status):
  if status not in [400,401,403,404,413,422,429]:raise ValueError('Estado no confirmado como rechazo previo a inferencia')
  with self.locked() as s:
   r=s['pending'].pop(key);s['events'].append({'reservation':key,'request_hash':r['request_hash'],'unbilled_status':status})
 def summary(self):
  with self.locked() as s:return {'limit_usd':s['limit'],'accounted_spend_usd':s['spent'],'pending_upper_usd':str(sum((Decimal(x['upper']) for x in s['pending'].values()),Decimal(0))),'completed_paid_calls':sum('cost' in x for x in s['events'])}
