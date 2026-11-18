import tempfile,unittest,json,pickle
from pathlib import Path
from decimal import Decimal
from unittest.mock import patch
import numpy as np
from src.costos import LibroCostos,PresupuestoAgotado
from src.llm import OpenAIPromptClassifier

class CostosTests(unittest.TestCase):
 def test_reservas_impiden_sobrepasar_diez(self):
  with tempfile.TemporaryDirectory() as tmp:
   b=LibroCostos(Path(tmp)/'book.json');r=b.reserve('8','a')
   with self.assertRaises(PresupuestoAgotado):b.reserve('2.01','b')
   b.settle(r,'1',{'input_tokens':1},'r1');b.reserve('9','c')
   with self.assertRaises(PresupuestoAgotado):b.reserve('.01','d')
 def test_fallo_desconocido_mantiene_reserva(self):
  with tempfile.TemporaryDirectory() as tmp:
   b=LibroCostos(Path(tmp)/'book.json');b.reserve('10','uncertain')
   with self.assertRaises(PresupuestoAgotado):b.reserve('.000001','next')
 def test_no_se_puede_ampliar_limite_silenciosamente(self):
  with self.assertRaises(ValueError):LibroCostos('/private/tmp/not-used.json',11)

class LLMTests(unittest.TestCase):
 def test_ejemplos_solo_del_train_y_predicciones_sin_etiquetas(self):
  x=np.arange(90,dtype=float).reshape(30,3);y=np.array(['Approved','Fail','Withdrawn']*10)
  p=OpenAIPromptClassifier(examples_per_class=2).fit(x,y)
  self.assertEqual(len(p.examples_),6)
  self.assertEqual(p.training_rows_,30)
  for e in p.examples_:
   value=dict(e['x']).get(0,0);self.assertIn(value,x[:,0])
  requests=[]
  class Fake:
   def predict_batch(self,system,user,n):requests.append(json.loads(user));return [[.6,.3,.1]]*n,{}
  with patch('src.llm.ResponsesClient',Fake):
   a=p.predict_proba([[1000,1001,1002]]);b=p.predict_proba([[1000,1001,1002]])
  np.testing.assert_array_equal(a,b);self.assertEqual(len(requests),1)
  self.assertNotIn('class',requests[0]['queries'][0]);self.assertEqual(pickle.loads(pickle.dumps(p)).predict([[1000,1001,1002]])[0],'Approved')
 def test_respuesta_invalida_no_se_sustituye_por_baseline(self):
  p=OpenAIPromptClassifier(examples_per_class=0).fit(np.zeros((3,2)),['Approved','Fail','Withdrawn'])
  class Bad:
   def predict_batch(self,system,user,n):return [[-1,1,1]]*n,{}
  with patch('src.llm.ResponsesClient',Bad),self.assertRaises(RuntimeError):p.predict_proba([[8,9]])
 def test_semilla_fija_seleccion_contexto(self):
  x=np.arange(90).reshape(30,3);y=['Approved','Fail','Withdrawn']*10
  a=OpenAIPromptClassifier().fit(x,y);b=OpenAIPromptClassifier().fit(x,y)
  self.assertEqual(a.examples_,b.examples_)
