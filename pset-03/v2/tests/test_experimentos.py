import unittest
import numpy as np,pandas as pd
from sklearn.linear_model import LogisticRegression
from src.experimentos import train_metric_sample
from src.tuning import scorers,configurations
from src.modelos import candidatos

class DisenoTests(unittest.TestCase):
 def test_seis_candidatos_incluye_llm(self):
  self.assertEqual(len(candidatos()),6);self.assertIn('llm_generativo',candidatos())
 def test_cada_espacio_tiene_treinta_draws_unicos(self):
  import json
  for family,draws in configurations().items():
   self.assertEqual(len(draws),30,family)
   self.assertEqual(len({json.dumps(d,sort_keys=True) for d in draws}),30,family)
 def test_muestra_train_reproducible_y_no_incluye_validacion(self):
  y=np.array(['Approved','Fail','Withdrawn']*1000);train=np.arange(2000)
  a=train_metric_sample(y,train,0);b=train_metric_sample(y,train,0)
  np.testing.assert_array_equal(a,b);self.assertEqual(len(a),1000);self.assertFalse(set(a)&set(range(2000,3000)))
 def test_scorer_cache_separa_train_validacion(self):
  rng=np.random.default_rng(42);n=3000
  frame=pd.DataFrame({'id_student':np.arange(n),'enrollment_key':[f'e{i:04}' for i in range(n)],'edition_key':'module','target_class':['Approved','Fail','Withdrawn']*1000})
  x=pd.DataFrame({'f':rng.normal(size=n)});a=np.arange(2000);b=np.arange(2000,3000)
  p=LogisticRegression().fit(x.iloc[a],frame.target_class.iloc[a]);score=scorers(frame,[(a,b)])
  score['ap_fail'](p,x.iloc[a],frame.target_class.iloc[a]);score['coverage'](p,x.iloc[a],frame.target_class.iloc[a]);score['ap_fail'](p,x.iloc[b],frame.target_class.iloc[b])
  self.assertEqual(len(p._v2_score_cache),2)
  self.assertTrue(all(len(k)==1000 for k in p._v2_score_cache))
