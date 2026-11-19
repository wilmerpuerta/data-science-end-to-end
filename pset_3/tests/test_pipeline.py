import pickle,unittest
import numpy as np
import pandas as pd
from sklearn.base import clone
from src.pipeline import FeaturesAlCorte,construir_preparacion,CATEGORICAS,ESTATICAS,ACTIVIDAD

def sample():
    f=pd.DataFrame({c:pd.Series([1,2,3],dtype='Int64') for c in ESTATICAS+ACTIVIDAD})
    for c in CATEGORICAS:f[c]=pd.Series(['a',pd.NA,'b'],dtype='string')
    f['is_imd_missing']=pd.Series([False,True,False],dtype='boolean')
    f['has_recorded_activity']=True
    f['clicks_current_14d']=[0,8,12];f['active_days_current_14d']=[0,2,3]
    return f

class Preparation(unittest.TestCase):
    def test_formulas_and_undefined_denominator(self):
        x=sample();a=FeaturesAlCorte().fit_transform(x)
        np.testing.assert_allclose(a.log1p_clicks_current_14d,np.log1p([0,8,12]))
        self.assertTrue(np.isnan(a.clicks_per_active_day_14d.iloc[0]))
        np.testing.assert_allclose(a.clicks_per_active_day_14d.iloc[1:],[4,4])
    def test_labels_future_fields_ids_and_order_do_not_change_features(self):
        x=sample();p=construir_preparacion().fit(x);before=p.transform(x)
        polluted=x.assign(target_class='Fail',final_result='Withdrawn',date_unregistration=-100,
                          future_clicks=999999,id_student=999,cv_fold=4,enrollment_key='x')
        np.testing.assert_array_equal(before,p.transform(polluted[polluted.columns[::-1]]))
    def test_validation_does_not_refit_median_or_categories(self):
        x=sample();x['recency_days']=pd.Series([1,pd.NA,3],dtype='Int64')
        p=construir_preparacion().fit(x)
        numerical=p.named_steps['preparacion'].named_transformers_['num']
        before=numerical.named_steps['imputar'].statistics_.copy()
        cat=p.named_steps['preparacion'].named_transformers_['cat'].named_steps['codificar']
        old=[a.copy() for a in cat.categories_]
        valid=x.copy();valid['recency_days']=10**9;valid['region']='NUEVA_CATEGORIA'
        self.assertTrue(np.isfinite(p.transform(valid)).all())
        np.testing.assert_array_equal(before,numerical.named_steps['imputar'].statistics_)
        for a,b in zip(old,cat.categories_):np.testing.assert_array_equal(a,b)
        pos=list(p.named_steps['features'].get_feature_names_out()).index('recency_days')
        self.assertEqual(before[pos],2.)
    def test_static_does_not_require_or_use_activity(self):
        x=sample();p=construir_preparacion(solo_estaticas=True).fit(x)
        small=x[CATEGORICAS+ESTATICAS+['is_imd_missing']]
        np.testing.assert_array_equal(p.transform(x),p.transform(small))
        self.assertFalse(any('clicks' in n for n in p.get_feature_names_out()))
    def test_unknowns_all_missing_numeric_and_serialization(self):
        x=sample();x['recency_days']=np.nan
        p=construir_preparacion().fit(x)
        z=x.copy();z['region']='nueva';z['imd_band']=pd.NA
        a=p.transform(z);self.assertTrue(np.isfinite(a).all())
        np.testing.assert_array_equal(a,pickle.loads(pickle.dumps(p)).transform(z))
        self.assertEqual(clone(p).get_params()['features__derivadas'],True)
    def test_future_observed_activity_rejected(self):
        x=sample().assign(cutoff_day=56,last_activity_day=57)
        with self.assertRaisesRegex(ValueError,'posterior'):FeaturesAlCorte().fit_transform(x)
    def test_negative_counts_rejected(self):
        x=sample();x.loc[0,'clicks_current_14d']=-1
        with self.assertRaisesRegex(ValueError,'Ventana'):FeaturesAlCorte().fit_transform(x)
