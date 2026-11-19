"""Diagnósticos de preparación sin estimadores ni métricas de clasificación."""
from pathlib import Path
import json,pickle
import numpy as np
import pandas as pd
from .datos import cargar_snapshot,pliegues_congelados
from .pipeline import FeaturesAlCorte,construir_preparacion,columnas
from .common import ROOT,read_bundle,sha256

def validar():
    train,snapshot_id=cargar_snapshot();folds=list(pliegues_congelados(train))
    variants={'estatica':{'solo_estaticas':True},'longitudinal_original':{'derivadas':False},'longitudinal_derivadas':{}}
    rows=[]
    for name,options in variants.items():
        for fold,(fit,valid) in enumerate(folds):
            a,b=train.iloc[fit],train.iloc[valid]
            p=construir_preparacion(**options).fit(a)
            state=pickle.dumps(p)
            z=p.transform(b)
            assert pickle.dumps(p)==state,'transform modificó estadísticas'
            assert np.isfinite(z).all() and len(z)==len(b)
            assert not set(a.id_student)&set(b.id_student)
            numeric,_=columnas(**options)
            clean=p.named_steps['features'].transform(a)[numeric]
            raw=clean.to_numpy(dtype=float)
            median=np.asarray([np.nanmedian(raw[:,j]) if not np.isnan(raw[:,j]).all() else 0. for j in range(raw.shape[1])])
            n=p.named_steps['preparacion'].named_transformers_['num']
            np.testing.assert_allclose(n.named_steps['imputar'].statistics_,median)
            imputed=n.named_steps['imputar'].transform(clean)
            np.testing.assert_allclose(n.named_steps['escalar'].mean_,imputed.mean(axis=0),atol=1e-10)
            altered=b.assign(final_result='Fail',target_class='Approved',date_unregistration=-999,
                             id_student=-1,enrollment_key='ignorado',cv_fold=99,future_clicks=10**9)
            np.testing.assert_array_equal(z,p.transform(altered))
            assert pickle.dumps(p)==state
            rows.append({'variante':name,'fold':fold,'filas_fit':len(a),'filas_validacion':len(b),'columnas_salida':z.shape[1],
                         'salida_finita':True,'medianas_solo_fit':True,'escalado_solo_fit':True,'transform_sin_reajuste':True,'etiquetas_ids_futuro_ignorados':True,'alumnos_compartidos':0})
    f=FeaturesAlCorte().fit_transform(train)
    derived=f[['log1p_clicks_current_14d','clicks_per_active_day_14d']]
    descriptive=[]
    for c in derived:
        for cls in ['Approved','Fail','Withdrawn']:
            v=derived.loc[train.target_class.eq(cls),c]
            descriptive.append({'feature':c,'clase':cls,'observados':int(v.notna().sum()),'faltantes':int(v.isna().sum()),'mediana':float(v.median())})
    reference=pd.read_csv(ROOT/'docs/eda/candidatas_derivadas.csv')
    for row in descriptive:
        ref=reference.loc[reference.variable_candidata.eq(row['feature'])&reference.clase.eq(row['clase'])].iloc[0]
        assert row['faltantes']==ref.n_faltante
        np.testing.assert_allclose(row['mediana'],ref.mediana,rtol=1e-6)
    out=ROOT/'docs/features';out.mkdir(parents=True,exist_ok=True)
    table=pd.DataFrame(rows);table.to_csv(out/'validacion_folds.csv',index=False)
    pd.DataFrame(descriptive).to_csv(out/'derivadas_descriptivos.csv',index=False)
    _,snap=read_bundle()
    contract={'version':'pset3.features.v1','cutoff_day':56,
        'features':[{'name':'log1p_clicks_current_14d','formula':'log(1 + clicks_current_14d)','source_columns':['clicks_current_14d'],'evidence':'EDA: mediana 53, máximo 7028, asimetría 8.82. Compresión determinista de cola; aporte pendiente de ablación.'},
                    {'name':'clicks_per_active_day_14d','formula':'clicks_current_14d / active_days_current_14d si denominador > 0; NaN en otro caso','source_columns':['clicks_current_14d','active_days_current_14d'],'evidence':'EDA: actividad y resultado asociados; normalizar intensidad por exposición registrada. 2602 denominadores cero. Aporte pendiente de ablación.'}],
        'availability':'Solo agregados ya calculados <= cutoff. No consulta etiquetas, retiros ni eventos futuros. Supone disponibilidad de registros y atributos según límites PSet 2.',
        'numeric_missing':'Mediana de fit; add_indicator=True; keep_empty_features=True (fallback 0 si columna totalmente faltante en fit). Indicadores con StandardScaler junto a numéricas.',
        'categorical_missing':'pd.NA/None -> np.nan; categoría __MISSING__; OneHotEncoder(handle_unknown=ignore, sparse_output=False). No se supone orden entre categorías.',
        'numeric_scaling':'StandardScaler aprendido solo en fit; no clipping ni eliminación de extremos.',
        'booleans':'is_imd_missing estática y has_recorded_activity longitudinal como 0/1. No se incluyen audit log_coverage_known ni last_activity_day como predictores.',
        'variants':{name:{'numeric':columnas(**opts)[0],'categorical':columnas(**opts)[1]} for name,opts in variants.items()},
        'ablation_plan':'Tras registrar ingenua y reactiva, comparar misma familia/folds: estática, longitudinal original y longitudinal derivadas; además activar cada derivada por separado en una extensión de versión si se atribuye aporte individual. No elegir por hold-out.',
        'no_benefit_claimed':True}
    (out/'contrato.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n')
    summary={'status':'ok','snapshot_id':snapshot_id,'split_id':train.attrs['split_id'],'snapshot_at_utc':snap['identity']['snapshot_at_utc'],
        'development_rows':len(train),'new_features':2,'preparation_fits':len(rows),'cv_folds':5,'variants':list(variants),
        'zero_current_active_days':int(train.active_days_current_14d.eq(0).sum()),'derived_missing':int(derived.clicks_per_active_day_14d.isna().sum()),
        'heldout_analyzed':False,'classifier_fitted':False,'ablation_performance_pending':True,
        'code_sha256':{x:sha256(ROOT/x) for x in ['src/pipeline.py','src/features_evidencia.py','requirements.lock.txt']}}
    return summary,table,pd.DataFrame(descriptive),contract
