"""Carga verificada: desarrollo por defecto y prueba solo mediante acceso explícito."""
from pathlib import Path
import pandas as pd
from .common import read_bundle

KEY=['enrollment_key','cutoff_day']

def cargar_snapshot(path=None,cutoff=56,particion='train',*,permitir_prueba=False):
    """Retorna matrícula–corte etiquetada y snapshot_id; EDA solo usa train.

    Los archivos se verifican con SHA-256 antes de leerlos. El control de prueba
    evita accesos accidentales; no es un mecanismo de seguridad criptográfica.
    """
    if cutoff not in [14,28,42,56]:raise ValueError('Corte fuera del contrato')
    if particion not in ['train','test']:raise ValueError('Partición inválida')
    if particion=='test' and not permitir_prueba:
        raise ValueError('Hold-out reservado: habilitar explícitamente solo con los dos finalistas congelados')
    folder,snapshot=read_bundle()
    if path is not None and Path(path).resolve()!=folder:
        raise ValueError('Usar el bundle congelado actual o path=None; no un Parquet sin manifiesto')
    splits,manifest=read_bundle('splits-current.json')
    if manifest['identity']['snapshot_id']!=snapshot['id']:raise ValueError('Snapshot y particiones incompatibles')
    keys=pd.read_csv(splits/'assignments.csv',dtype={'enrollment_key':'string','id_student':'Int64','cv_fold':'Int64'})
    keys=keys.loc[keys.partition.eq(particion)]
    features=pd.read_parquet(folder/'features.parquet')
    # Restringir claves y corte antes de incorporar etiquetas.
    result=features.loc[features.cutoff_day.eq(cutoff)].merge(keys[['enrollment_key','cv_fold']],on='enrollment_key',how='inner',validate='one_to_one')
    labels=pd.read_parquet(folder/'outcomes.parquet')
    labels=labels.loc[labels.enrollment_key.isin(keys.enrollment_key)]
    result=result.merge(labels,on='enrollment_key',how='left',validate='one_to_one').sort_values('enrollment_key').reset_index(drop=True)
    if len(result)!=len(keys) or result.target_class.isna().any():raise ValueError('Partición incompleta')
    result.attrs.update(snapshot_id=snapshot['id'],split_id=manifest['id'],partition=particion)
    return result,snapshot['id']

def pliegues_congelados(train):
    """Índices posicionales reutilizables por todos los modelos; no regenera CV."""
    reference,_=cargar_snapshot(cutoff=int(train.cutoff_day.iloc[0]))
    if train.enrollment_key.duplicated().any() or set(train.enrollment_key)!=set(reference.enrollment_key):
        raise ValueError('CV exige todas y solo las claves de desarrollo congeladas')
    expected=reference.set_index('enrollment_key').cv_fold
    if not train.cv_fold.reset_index(drop=True).equals(train.enrollment_key.map(expected).reset_index(drop=True)):
        raise ValueError('Asignación de folds alterada')
    for fold in range(5):
        valid=train.cv_fold.eq(fold).to_numpy(dtype=bool)
        a,b=train.loc[~valid],train.loc[valid]
        if set(a.id_student)&set(b.id_student):raise ValueError('Alumnos compartidos en CV')
        import numpy as np
        yield np.flatnonzero(~valid),np.flatnonzero(valid)
