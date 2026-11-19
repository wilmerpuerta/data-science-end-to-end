import unittest
import numpy as np
import pandas as pd
from src.anticipacion import cohortes,simulate_policy,build
from src.experimentos import entrada

class AnticipacionTests(unittest.TestCase):
 def test_cohortes_propias_y_folds_por_alumno(self):
  frames,assignments,_=cohortes()
  self.assertGreater(len(frames[14]),len(frames[56]))
  self.assertTrue(assignments.groupby('id_student').cv_fold.nunique().eq(1).all())
  for cut,d in frames.items():
   self.assertNotIn('2014J',set(d.code_presentation))
   self.assertTrue((d.loc[d.last_activity_day.notna(),'last_activity_day']<=cut).all())
 def fixture(self):
  d=pd.DataFrame({'enrollment_key':[f'k{i:02}' for i in range(30)],'edition_key':'A','cv_fold':0,'id_student':range(30),'target_class':['Fail']*10+['Approved']*20,'module_presentation_length':200})
  return {c:d.copy() for c in [14,28,42]}
 def test_cupo_compartido_no_se_triplica(self):
  f=self.fixture();r,s=simulate_policy(f,{c:np.arange(30) for c in f},[14,28,42],[.4,.3,.3])
  self.assertEqual(r['budget'],3);self.assertEqual(r['used'],3)
  self.assertEqual(len(s.enrollment_key.unique()),3)
  self.assertEqual([x['cumulative_slots'] for x in r['rounds']],[1,2,3])
 def test_seleccion_no_depende_de_etiqueta(self):
  f=self.fixture();scores={c:np.arange(30) for c in f}
  _,a=simulate_policy(f,scores,[14,28,42],[.4,.3,.3])
  for d in f.values():d['target_class']='Fail'
  _,b=simulate_policy(f,scores,[14,28,42],[.4,.3,.3])
  self.assertEqual(a.enrollment_key.tolist(),b.enrollment_key.tolist())
 def test_indicador_no_incumple_allowlist_estatica(self):
  f=cohortes()[0][14].iloc[:15].copy();p=build('bagging',{},'indicador').named_steps['features']
  x=entrada(f);a=p.fit_transform(x)
  f['clicks_current_14d']=999999
  b=p.transform(entrada(f))
  pd.testing.assert_frame_equal(a,b)
  self.assertIn('has_recorded_activity',a)
  self.assertNotIn('clicks_current_14d',a)
