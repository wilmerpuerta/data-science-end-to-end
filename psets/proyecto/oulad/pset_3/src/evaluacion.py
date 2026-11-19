"""Métricas y capacidad; desempates por clave, nunca por etiqueta."""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score,log_loss,brier_score_loss
CLASSES=['Approved','Fail','Withdrawn']

def probabilidades(model,X):
    classes=list(model.classes_);p=model.predict_proba(X)
    return p[:,[classes.index(c) for c in CLASSES]]

def seleccionar(meta,scores,capacity=.10):
    if not 0<capacity<=1:raise ValueError('Capacidad inválida')
    if len(meta)!=len(scores) or meta.enrollment_key.duplicated().any():raise ValueError('Claves/puntuaciones inválidas')
    scores=np.asarray(scores,dtype=float)
    if not np.isfinite(scores).all():raise ValueError('Puntuaciones no finitas')
    data=meta[['enrollment_key','edition_key']].copy();data['score']=scores
    data=data.sort_values(['edition_key','score','enrollment_key'],ascending=[True,False,True])
    k=(data.groupby('edition_key').size()*capacity).apply(np.floor).astype(int)
    keep=data.groupby('edition_key').cumcount()<data.edition_key.map(k)
    return set(data.loc[keep,'enrollment_key']),k

def negocio(meta,y,scores,capacity=.10):
    selected,k=seleccionar(meta,scores,capacity)
    fail=np.asarray(y)=='Fail';keep=meta.enrollment_key.isin(selected).to_numpy()
    tp=int((keep&fail).sum());fp=int((keep&~fail).sum());den=int(fail.sum())
    return {'tp':tp,'fp':fp,'fn':den-tp,'n':len(meta),'fail':den,'k':int(k.sum()),
            'coverage':tp/den if den else None,'precision_at_k':tp/int(keep.sum()) if keep.any() else None,
            'unique_students_selected':int(meta.loc[keep,'id_student'].nunique())}

def metricas(y,p):
    return {'ap_fail':float(average_precision_score(np.asarray(y)=='Fail',p[:,1])),
            'logloss':float(log_loss(y,p,labels=CLASSES)),
            'brier_fail':float(brier_score_loss(np.asarray(y)=='Fail',p[:,1]))}
