"""Features deterministas y preparación aprendida dentro de cada fold."""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.validation import check_is_fitted

CATEGORICAS = ['gender','region','highest_education','imd_band','age_band','disability']
ESTATICAS = ['num_of_prev_attempts','studied_credits','module_presentation_length','registration_days_before_start']
ACTIVIDAD = ['clicks_through_cutoff','active_days_through_cutoff','resources_through_cutoff',
             'clicks_current_14d','active_days_current_14d','clicks_previous_14d','click_change_14d','recency_days']
DERIVADAS = ['log1p_clicks_current_14d','clicks_per_active_day_14d']

def columnas(solo_estaticas=False,derivadas=True):
    numeric=ESTATICAS+['is_imd_missing']
    if not solo_estaticas:numeric+=ACTIVIDAD+['has_recorded_activity']+(DERIVADAS if derivadas else [])
    return numeric,CATEGORICAS.copy()

class FeaturesAlCorte(TransformerMixin,BaseEstimator):
    """No aprende estadísticas. Descarta targets, IDs, folds y auditoría por allowlist."""
    def __init__(self,solo_estaticas=False,derivadas=True):
        self.solo_estaticas=solo_estaticas
        self.derivadas=derivadas

    def fit(self,X,y=None):
        self._convertir(X)
        self.feature_names_in_=np.asarray(X.columns,dtype=object)
        self.n_features_in_=len(X.columns)
        return self

    def _convertir(self,X):
        if not isinstance(X,pd.DataFrame):raise TypeError('Se requiere DataFrame con nombres de columnas')
        num,cat=columnas(self.solo_estaticas,self.derivadas)
        required=[c for c in num if c not in DERIVADAS]+cat
        if X.columns.duplicated().any():raise ValueError('Columnas duplicadas')
        missing=sorted(set(required)-set(X))
        if missing:raise ValueError('Faltan entradas: '+str(missing))
        if not self.solo_estaticas and {'cutoff_day','last_activity_day'}<=set(X):
            known=X.last_activity_day.notna()
            if (X.loc[known,'last_activity_day']>X.loc[known,'cutoff_day']).any():raise ValueError('Actividad posterior al corte')
        out=pd.DataFrame(index=X.index)
        for c in required:
            if c in cat:
                out[c]=X[c].astype(object).where(X[c].notna(),np.nan)
            else:
                out[c]=pd.to_numeric(X[c],errors='raise').to_numpy(dtype=float,na_value=np.nan)
                if np.isinf(out[c]).any():raise ValueError('Valor infinito: '+c)
        if not self.solo_estaticas:
            if (out.clicks_current_14d.dropna()<0).any() or not out.active_days_current_14d.dropna().between(0,14).all():raise ValueError('Ventana inválida')
            if self.derivadas:
                out['log1p_clicks_current_14d']=np.log1p(out.clicks_current_14d)
                out['clicks_per_active_day_14d']=out.clicks_current_14d.div(out.active_days_current_14d.where(out.active_days_current_14d>0))
        return out[num+cat]

    def transform(self,X):
        check_is_fitted(self,'feature_names_in_')
        return self._convertir(X)

    def get_feature_names_out(self,input_features=None):
        check_is_fitted(self,'feature_names_in_')
        num,cat=columnas(self.solo_estaticas,self.derivadas)
        return np.asarray(num+cat,dtype=object)

def construir_preparacion(*,solo_estaticas=False,derivadas=True):
    num,cat=columnas(solo_estaticas,derivadas)
    transformer=ColumnTransformer([
        ('num',Pipeline([('imputar',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)),
                         ('escalar',StandardScaler())]),num),
        ('cat',Pipeline([('imputar',SimpleImputer(strategy='constant',fill_value='__MISSING__',keep_empty_features=True)),
                         ('codificar',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cat)
    ],remainder='drop',verbose_feature_names_out=True)
    return Pipeline([('features',FeaturesAlCorte(solo_estaticas=solo_estaticas,derivadas=derivadas)),('preparacion',transformer)])

def construir_pipeline(modelo,*,solo_estaticas=False,derivadas=True):
    return Pipeline(construir_preparacion(solo_estaticas=solo_estaticas,derivadas=derivadas).steps+[('modelo',modelo)])
