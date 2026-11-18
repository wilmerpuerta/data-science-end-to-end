"""Contrato HTTP, cobros, fallos y representación real del sexto candidato, sin red."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
import numpy as np,pandas as pd,requests
from src import openai_api as api
from src.modelos import construir_modelo
from src.evaluacion import probabilidades

class ApiTests(unittest.TestCase):
 def setup_client(self,folder):
  root=Path(folder);(root/'config').mkdir();(root/'config/protocolo-v2.json').write_text('{}')
  return root
 def response(self,status=200):
  response=Mock(status_code=status)
  response.json.return_value={'id':'test-response','model':api.MODEL,'status':'completed','usage':{'input_tokens':50,'output_tokens':20},'output':[{'content':[{'type':'output_text','text':json.dumps({'probabilities':[[.2,.7,.1],[.6,.3,.1]]})}]}]}
  return response
 def test_esquema_estricto_y_cache_sin_segunda_llamada(self):
  with tempfile.TemporaryDirectory() as temp:
   root=self.setup_client(temp)
   with patch.object(api,'ROOT',root),patch.object(api,'settings',return_value={'OPENAI_API_KEY':'test-key'}),patch.object(api.requests,'post',return_value=self.response()) as post:
    client=api.ResponsesClient();a,meta=client.predict_batch('system','user',2);b,meta2=client.predict_batch('system','user',2)
    self.assertEqual(a,b);self.assertTrue(meta2['cache_hit']);self.assertEqual(post.call_count,1)
    wire=json.loads(post.call_args.kwargs['data']);self.assertTrue(wire['text']['format']['strict']);self.assertFalse(wire['store']);self.assertEqual(wire['tools'],[])
    self.assertEqual(client.book.summary()['completed_paid_calls'],1);self.assertEqual(client.book.summary()['pending_upper_usd'],'0')
 def test_credito_agotado_libera_reserva_sin_reintentar(self):
  with tempfile.TemporaryDirectory() as temp:
   root=self.setup_client(temp);response=Mock(status_code=429);response.json.return_value={'error':{'code':'credit_balance_exhausted','type':'insufficient_quota'}}
   with patch.object(api,'ROOT',root),patch.object(api,'settings',return_value={'OPENAI_API_KEY':'test-key'}),patch.object(api.requests,'post',return_value=response) as post:
    client=api.ResponsesClient()
    with self.assertRaisesRegex(RuntimeError,'credit_balance_exhausted'):client.predict_batch('system','user',2)
    self.assertEqual(post.call_count,1);self.assertEqual(client.book.summary()['accounted_spend_usd'],'0');self.assertEqual(client.book.summary()['pending_upper_usd'],'0')
    self.assertNotIn('test-key',(root/'.local/llm/errores.jsonl').read_text())
 def test_timeout_conserva_reserva_y_no_reintenta(self):
  with tempfile.TemporaryDirectory() as temp:
   root=self.setup_client(temp)
   with patch.object(api,'ROOT',root),patch.object(api,'settings',return_value={'OPENAI_API_KEY':'test-key'}),patch.object(api.requests,'post',side_effect=requests.Timeout) as post:
    client=api.ResponsesClient()
    with self.assertRaisesRegex(RuntimeError,'sin reintento'):client.predict_batch('system','user',2)
    self.assertEqual(post.call_count,1);self.assertGreater(float(client.book.summary()['pending_upper_usd']),0)
 def test_respuesta_incompleta_registra_cobro_y_falla(self):
  with tempfile.TemporaryDirectory() as temp:
   root=self.setup_client(temp);response=self.response();response.json.return_value['status']='incomplete'
   with patch.object(api,'ROOT',root),patch.object(api,'settings',return_value={'OPENAI_API_KEY':'test-key'}),patch.object(api.requests,'post',return_value=response):
    client=api.ResponsesClient()
    with self.assertRaisesRegex(RuntimeError,'incompleta'):client.predict_batch('system','user',2)
    self.assertEqual(client.book.summary()['completed_paid_calls'],1);self.assertFalse(list(client.cache.glob('*.json')));self.assertTrue(list((client.cache.parent/'responses').glob('*.json')))
 def test_llm_pipeline_real_tiene_nombres_y_excluye_objetivo(self):
  from src.pipeline import columnas,DERIVADAS
  num,cat=columnas();n=12
  x=pd.DataFrame({c:np.arange(n,dtype=float) for c in num if c not in DERIVADAS})
  for c in cat:x[c]='category'
  x['target_class']='forbidden';x['id_student']=np.arange(n)+100000
  y=np.array(['Approved','Fail','Withdrawn']*4)
  model=construir_modelo('llm_generativo');model.named_steps['modelo'].set_params(examples_per_class=1)
  client=Mock();client.predict_batch.side_effect=lambda system,user,n:([[.2,.6,.2]]*n,{})
  with patch('src.llm.ResponsesClient',return_value=client):
   model.fit(x,y);p=probabilidades(model,x.iloc[:2]);self.assertEqual(p.shape,(2,3))
  payload=json.loads(client.predict_batch.call_args.args[1]);self.assertTrue(any('num__' in c for c in payload['columns']));self.assertFalse(any('target_class' in c or 'id_student' in c for c in payload['columns']));self.assertEqual(len(payload['examples']),3)

 def test_cache_writes_premium_se_incluye(self):
  from decimal import Decimal
  usage={'input_tokens':1000000,'output_tokens':0,'input_tokens_details':{'cache_write_tokens':600000,'cache_write_tokens_details':{'ttl_30m_tokens':400000,'ttl_12h_tokens':200000}}}
  self.assertEqual(api.accounted_cost(usage),Decimal('.28'))
  usage['input_tokens_details']['cache_write_tokens_details']={}
  self.assertEqual(api.accounted_cost(usage),Decimal('.38'))
 def test_reservas_concurrentes_comparten_tope(self):
  from concurrent.futures import ThreadPoolExecutor
  from src.costos import LibroCostos,PresupuestoAgotado
  with tempfile.TemporaryDirectory() as temp:
   book=LibroCostos(Path(temp)/'ledger.json',10)
   def reserve(i):
    try:return book.reserve(2,str(i))
    except PresupuestoAgotado:return None
   with ThreadPoolExecutor(max_workers=8) as pool:keys=list(pool.map(reserve,range(20)))
   self.assertEqual(sum(k is not None for k in keys),5);self.assertEqual(float(book.summary()['pending_upper_usd']),10)
