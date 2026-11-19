"""Casos límite de outliers y separación de la EDA."""
import unittest
import numpy as np
import pandas as pd
from src.eda import tabla_outliers,analizar

class Eda(unittest.TestCase):
    def test_zscore_includes_exactly_three_and_excludes_missing(self):
        frame=pd.DataFrame({'x':[0.]*9+[10.,np.nan]})
        row=tabla_outliers(frame,['x']).iloc[0]
        self.assertEqual(row.n_observado,10)
        self.assertEqual(row.n_z_abs_ge_3,1)
        self.assertEqual(row.n_iqr,1)
        self.assertTrue(row.iqr_cero)
    def test_constant_and_fully_missing_have_undefined_z(self):
        frame=pd.DataFrame({'constant':[1.,1.,1.],'missing':[np.nan]*3})
        result=tabla_outliers(frame,list(frame)).set_index('variable')
        self.assertFalse(result.z_definido.any())
        self.assertEqual(result.n_z_abs_ge_3.sum(),0)
        self.assertEqual(result.loc['missing','n_observado'],0)
    def test_analysis_rejects_holdout_flag(self):
        frame=pd.DataFrame({'enrollment_key':['fake']});frame.attrs['partition']='test'
        with self.assertRaisesRegex(ValueError,'desarrollo congeladas'):analizar(frame)
