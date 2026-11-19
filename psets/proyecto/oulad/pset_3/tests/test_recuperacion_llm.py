import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from recuperar_respuestas_llm import extract_verified
class RecoveryTests(unittest.TestCase):
 def body(self):return json.dumps({'probabilities':{'q000':{'Approved':.2,'Fail':.7,'Withdrawn':.1}}})
 def test_prefijo_se_excluye_sin_cambiar_probabilidades(self):
  p,proof=extract_verified('texto de transporte\n?'+self.body(),['q000']);self.assertEqual(p,[[.2,.7,.1]]);self.assertGreater(proof['prefix_chars'],0)
 def test_objeto_extra_y_campos_repetidos_se_rechazan(self):
  with self.assertRaises(ValueError):extract_verified(self.body()+self.body(),['q000'])
  duplicate='{"probabilities":{"q000":{"Approved":0.2,"Approved":0.1,"Fail":0.7,"Withdrawn":0.1}}}'
  with self.assertRaises(ValueError):extract_verified(duplicate,['q000'])
 def test_consultas_faltantes_y_probabilidades_invalidas_se_rechazan(self):
  with self.assertRaises(ValueError):extract_verified(self.body(),['q000','q001'])
  invalid=json.dumps({'probabilities':{'q000':{'Approved':.1,'Fail':.1,'Withdrawn':.1}}})
  with self.assertRaises(ValueError):extract_verified(invalid,['q000'])
