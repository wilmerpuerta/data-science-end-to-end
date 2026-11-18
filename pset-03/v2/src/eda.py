"""EDA agregada de desarrollo; sin imputación, selección automática ni modelos."""
from pathlib import Path
from datetime import datetime, timezone
import json
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_bool_dtype
from .common import ROOT, read_bundle, sha256

CLASSES=['Approved','Fail','Withdrawn']

def tabla_outliers(frame,columns):
    rows=[]
    for col in columns:
        a=frame[col].dropna().astype(float)
        q1,q3=a.quantile([.25,.75]) if len(a) else (np.nan,np.nan)
        iqr=q3-q1;mean=a.mean();std=a.std(ddof=0)
        lower,upper=q1-1.5*iqr,q3+1.5*iqr
        extreme_iqr=(a.lt(lower)|a.gt(upper))
        extreme_z=(a.sub(mean).div(std).abs().ge(3)) if std>0 else pd.Series(False,index=a.index)
        rows.append({'variable':col,'n_observado':len(a),'q1':q1,'q3':q3,'iqr':iqr,'limite_inferior':lower,'limite_superior':upper,
                     'iqr_cero':bool(iqr==0),'n_iqr':int(extreme_iqr.sum()),'pct_iqr':100*extreme_iqr.mean() if len(a) else np.nan,
                     'media':mean,'std_poblacional':std,'n_z_abs_ge_3':int(extreme_z.sum()),'pct_z_abs_ge_3':100*extreme_z.mean() if len(a) else np.nan,
                     'z_definido':bool(std>0)})
    return pd.DataFrame(rows)

def tasas(frame,group):
    grouped=frame.assign(_fail=frame.target_class.eq('Fail').astype(int)).groupby(group,dropna=False,observed=True)
    return grouped.agg(n=('_fail','size'),n_fail=('_fail','sum'),tasa_fail=('_fail','mean')).reset_index()

def analizar(frame):
    folder,snapshot=read_bundle();split_folder,split=read_bundle('splits-current.json')
    assignments=pd.read_csv(split_folder/'assignments.csv',dtype={'enrollment_key':'string'})
    expected=set(assignments.loc[assignments.partition.eq('train'),'enrollment_key'])
    if frame.attrs.get('partition')!='train' or set(frame.enrollment_key)!=expected or frame.enrollment_key.duplicated().any():
        raise ValueError('EDA exige todas y solo las matrículas de desarrollo congeladas')
    if set(frame.cutoff_day)!={56}:raise ValueError('EDA principal solo en día 56')
    contract=json.loads((ROOT.parent/'pset-02/spark/feature-contract.json').read_text())
    static=contract['static_predictor_columns'];activity=contract['activity_predictor_columns']
    predictors=static+activity
    numeric=[c for c in predictors if is_numeric_dtype(frame[c]) and not is_bool_dtype(frame[c])]
    flags=[c for c in predictors if is_bool_dtype(frame[c])]
    categorical=[c for c in predictors if c not in numeric+flags]
    def role(c):
        if c in static:return 'predictor_estatico'
        if c in activity:return 'predictor_actividad'
        if c in contract['audit_columns']:return 'auditoria_no_predictor'
        if c=='target_class':return 'etiqueta_no_predictor'
        if c=='cv_fold':return 'particion_no_predictor'
        return 'identificador_no_predictor'
    profile=pd.DataFrame([{'columna':c,'tipo':str(frame[c].dtype),'rol':role(c),'faltantes':int(frame[c].isna().sum()),'faltantes_pct':float(100*frame[c].isna().mean()),'valores_distintos_observados':int(frame[c].nunique())} for c in frame])
    describe=frame[numeric].astype(float).describe(percentiles=[.01,.25,.5,.75,.95,.99]).T
    describe['asimetria']=frame[numeric].astype(float).skew();describe.index.name='variable'
    target=frame.target_class.value_counts().reindex(CLASSES).rename_axis('clase').reset_index(name='n');target['pct']=100*target.n/len(frame)
    category_rows=[]
    for c in categorical+flags:
        for value,n in frame[c].astype('string').fillna('(faltante)').value_counts().items():
            category_rows.append({'variable':c,'categoria':value,'n':int(n),'pct':100*int(n)/len(frame)})
    bool_fail=frame.target_class.eq('Fail').astype(float)
    corr_input=frame[numeric+flags].astype(float);corr_input=corr_input.loc[:,corr_input.nunique(dropna=True)>1]
    associations=[]
    for c in corr_input:
        valid=corr_input[c].notna()
        associations.append({'variable':c,'n_pares':int(valid.sum()),'spearman_fail':float(corr_input.loc[valid,c].corr(bool_fail.loc[valid],method='spearman'))})
    associations=pd.DataFrame(associations);associations['abs_spearman']=associations.spearman_fail.abs();associations=associations.sort_values('abs_spearman',ascending=False).reset_index(drop=True)
    matrix=corr_input.assign(Fail=bool_fail).corr(method='spearman')
    matrix.index.name='variable'
    redundancy=[]
    for i,a in enumerate(corr_input):
        for b in list(corr_input)[i+1:]:
            rho=matrix.loc[a,b]
            if abs(rho)>=.90:redundancy.append({'variable_a':a,'variable_b':b,'rho_spearman':float(rho)})
    median=frame.groupby('target_class',observed=True)[numeric].median().reindex(CLASSES).T;median.index.name='variable'
    missing_rows=[]
    for c in predictors:
        if not frame[c].isna().any():continue
        for absent in [False,True]:
            a=frame.loc[frame[c].isna().eq(absent)]
            missing_rows.append({'variable':c,'faltante':absent,'n':len(a),'n_fail':int(a.target_class.eq('Fail').sum()),'tasa_fail':float(a.target_class.eq('Fail').mean())})
    recorded=tasas(frame,'has_recorded_activity')
    states=np.where(~frame.has_recorded_activity.to_numpy(dtype=bool),'Sin registros hasta 56',np.where(frame.active_days_current_14d.eq(0),'Registros previos, no recientes','Registros recientes'))
    state_rates=tasas(frame.assign(estado_actividad=states),'estado_actividad')
    # Prototipos exclusivamente descriptivos; aún no se incorporan al pipeline.
    derived=pd.DataFrame({'target_class':frame.target_class,'log1p_clicks_current_14d':np.log1p(frame.clicks_current_14d.astype(float)),
        'clicks_per_active_day_14d':frame.clicks_current_14d.astype(float).div(frame.active_days_current_14d.astype(float).replace(0,np.nan))})
    candidate_rows=[]
    for c in ['log1p_clicks_current_14d','clicks_per_active_day_14d']:
        for cls in CLASSES:
            a=derived.loc[derived.target_class.eq(cls),c]
            candidate_rows.append({'variable_candidata':c,'clase':cls,'n_observado':int(a.notna().sum()),'n_faltante':int(a.isna().sum()),'mediana':float(a.median())})
    checks={
        'train_rows_match_frozen':len(frame)==int(assignments.partition.eq('train').sum()),
        'no_missing_target':not frame.target_class.isna().any(),
        'no_missing_ids':not frame[['enrollment_key','id_student','edition_key']].isna().any().any(),
        'counter_reconciliation':bool(frame.clicks_through_cutoff.eq(frame.clicks_prestart+frame.clicks_day_zero+frame.clicks_since_start).all()),
        'recency_missing_exactly_no_recorded_activity':bool(frame.recency_days.isna().eq(~frame.has_recorded_activity).all()),
        'ratio_missing_exactly_zero_previous_window':bool(frame.click_ratio_14d.isna().eq(frame.clicks_previous_14d.eq(0)).all()),
        'current_active_days_between_0_and_14':bool(frame.active_days_current_14d.between(0,14).all()),
        'recency_matches_last_day':bool(frame.loc[frame.recency_days.notna(),'recency_days'].eq(56-frame.loc[frame.recency_days.notna(),'last_activity_day']).all()),
        'no_negative_click_counters':bool(frame[[c for c in numeric if c.startswith('clicks_')]].ge(0).fillna(True).all().all()),
        'no_target_leakage_into_original_features':not any(c in contract['output_columns'] for c in ['target_class','final_result','target_fail','date_unregistration'])}
    if not all(checks.values()):raise ValueError('Falló una reconciliación EDA: '+str([k for k,v in checks.items() if not v]))
    tables={'perfil_columnas':profile,'descriptivos_numericos':describe,'categorias':pd.DataFrame(category_rows),'target':target,
            'outliers':tabla_outliers(frame,numeric),'correlacion_fail':associations,'correlaciones':matrix,'medianas_target':median,
            'faltantes_target':pd.DataFrame(missing_rows),'actividad_registrada':recorded,'estado_actividad':state_rates,
            'tasas_modulo':tasas(frame,'code_module'),'tasas_presentacion':tasas(frame,'code_presentation'),
            'balance_folds':tasas(frame,'cv_fold'),'redundancia':pd.DataFrame(redundancy,columns=['variable_a','variable_b','rho_spearman']),
            'candidatas_derivadas':pd.DataFrame(candidate_rows)}
    tables['balance_folds']=tables['balance_folds'].merge(pd.crosstab(frame.cv_fold,frame.target_class).reset_index(),on='cv_fold',validate='one_to_one')
    summary={'status':'ok','phase':'eda','partition':'train','cutoff_day':56,'rows':len(frame),'unique_students':int(frame.id_student.nunique()),'columns_loaded':len(frame.columns),'original_obt_columns':len(contract['output_columns']),
             'snapshot_id':snapshot['id'],'split_id':split['id'],'snapshot_at_utc':snapshot['identity']['snapshot_at_utc'],
             'target_counts':{str(r.clase):int(r.n) for r in target.itertuples()},'fail_prevalence':float(bool_fail.mean()),'majority_minority_ratio':float(target.n.max()/target.n.min()),
             'majority_class_accuracy_reference':float(target.n.max()/len(frame)),
             'missing_counts':{c:int(frame[c].isna().sum()) for c in frame if frame[c].isna().any()},'numeric_predictors':numeric,'categorical_predictors':categorical,'boolean_predictors':flags,
             'checks':{k:bool(v) for k,v in checks.items()},'holdout_loaded_for_analysis':False,'model_fitted':False,'preprocessing_fitted':False,'outlier_rows_removed':0,
             'correlation_method':'Spearman sobre observados por pareja; target Fail vs resto, sin codificación ordinal de las tres clases. Asociaciones exploratorias, sin p-valores ni afirmación causal.',
             'zscore_definition':'abs((x-media)/std_poblacional_ddof0)>=3; observados solamente; no definido con varianza cero.',
             'references_are_not_model_baseline_runs':True,'source_sha256':sha256(Path(__file__))}
    return {'tables':tables,'summary':summary}

def figuras(frame,result):
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10,'figure.dpi':110,'savefig.dpi':170})
    colors={'Approved':'#3366A0','Fail':'#D36A29','Withdrawn':'#7B878C'}
    tables=result['tables'];plots={}
    fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained')
    t=tables['target'];bars=ax.bar(t.clase,t.n,color=[colors[c] for c in t.clase])
    ax.bar_label(bars,labels=[f'{r.n:,}\n{r.pct:.2f} %' for r in t.itertuples()],padding=4)
    ax.set(ylim=(0,t.n.max()*1.24),ylabel='Matrículas',title='Resultados en desarrollo · día 56 · N = 16.331')
    plots['01_target']=fig
    fig,ax=plt.subplots(figsize=(9,4),layout='constrained')
    missing=tables['perfil_columnas'].query('faltantes > 0').sort_values('faltantes_pct')
    bars=ax.barh(missing.columna,missing.faltantes_pct,color='#527DA5');ax.bar_label(bars,labels=[f'{r.faltantes:,} ({r.faltantes_pct:.2f} %)' for r in missing.itertuples()],padding=4)
    ax.set(xlim=(0,missing.faltantes_pct.max()*1.45),xlabel='% de matrículas',title='Faltantes estructurales y de antecedentes · sin imputar')
    plots['02_faltantes']=fig
    selected=['clicks_through_cutoff','clicks_current_14d','active_days_current_14d','recency_days','click_ratio_14d','click_change_14d']
    fig,axes=plt.subplots(2,3,figsize=(15,8),layout='constrained')
    for ax,c in zip(axes.flat,selected):
        observed=frame[c].dropna().astype(float).to_numpy()
        if c in ['clicks_through_cutoff','clicks_current_14d','click_ratio_14d']:observed=np.log1p(observed)
        if c=='click_change_14d':observed=np.sign(observed)*np.log1p(np.abs(observed))
        bins=np.arange(-.5,15.5,1) if c=='active_days_current_14d' else np.histogram_bin_edges(observed,bins=40)
        for cls in CLASSES:
            a=frame.loc[frame.target_class.eq(cls),c].dropna().astype(float).to_numpy()
            if c in ['clicks_through_cutoff','clicks_current_14d','click_ratio_14d']:a=np.log1p(a)
            if c=='click_change_14d':a=np.sign(a)*np.log1p(np.abs(a))
            ax.hist(a,bins=bins,density=True,histtype='step',linewidth=1.6,label=cls,color=colors[cls])
        label=('log1p(x)' if c in ['clicks_through_cutoff','clicks_current_14d','click_ratio_14d'] else 'signo(x) × log1p(|x|)' if c=='click_change_14d' else 'Valor observado')
        ax.set(title=c,xlabel=label,ylabel='Densidad por clase');ax.grid(alpha=.15)
    axes[0,0].legend(fontsize=9)
    fig.suptitle('Distribuciones por resultado · transformaciones solo para visualizar',fontsize=13)
    plots['03_distribuciones']=fig
    fig,axes=plt.subplots(2,3,figsize=(15,8),layout='constrained')
    for ax,c in zip(axes.flat,selected):
        arrays=[frame.loc[frame.target_class.eq(cls),c].dropna().astype(float).to_numpy() for cls in CLASSES]
        b=ax.boxplot(arrays,tick_labels=CLASSES,patch_artist=True,showfliers=True,
                     flierprops={'markersize':2,'alpha':.2},medianprops={'color':'black'})
        for patch,cls in zip(b['boxes'],CLASSES):patch.set_facecolor(colors[cls]);patch.set_alpha(.6)
        if c in ['clicks_through_cutoff','clicks_current_14d','click_ratio_14d','click_change_14d']:
            ax.set_yscale('symlog',linthresh=1);ax.set_ylabel('Valor original · escala symlog')
        else:ax.set_ylabel('Valor original')
        ax.set_title(c);ax.tick_params(axis='x',labelsize=9);ax.grid(axis='y',alpha=.15)
    fig.suptitle('Boxplots: mediana, cuartiles, bigotes 1,5 × IQR y todos los puntos extremos',fontsize=13)
    plots['04_boxplots_iqr']=fig
    top=tables['correlacion_fail'].variable.head(10).tolist()+['Fail']
    fig,ax=plt.subplots(figsize=(12,10),layout='constrained')
    sns.heatmap(tables['correlaciones'].loc[top,top],vmin=-1,vmax=1,center=0,cmap='vlag',annot=True,fmt='.2f',annot_kws={'fontsize':8},square=True,ax=ax,cbar_kws={'shrink':.7,'label':'ρ de Spearman'})
    ax.tick_params(axis='x',rotation=45);plt.setp(ax.get_xticklabels(),ha='right');ax.set_title('Relaciones exploratorias · diez variables con mayor |ρ| frente a Fail',pad=16)
    plots['05_correlaciones_spearman']=fig
    fig,axes=plt.subplots(1,2,figsize=(13,4.5),layout='constrained')
    for ax,key,label in zip(axes,['tasas_modulo','tasas_presentacion'],['code_module','code_presentation']):
        t=tables[key];bars=ax.bar(t[label].astype(str),100*t.tasa_fail,color='#527DA5')
        ax.bar_label(bars,labels=[f'n={r.n:,}' for r in t.itertuples()],padding=3,fontsize=8)
        ax.set(ylim=(0,100),ylabel='% Fail observado',title='Desarrollo por '+('módulo' if key=='tasas_modulo' else 'presentación'));ax.grid(axis='y',alpha=.15)
    plots['06_contexto_modulo_presentacion']=fig
    fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained')
    t=tables['estado_actividad'];labels=[v.replace(', no recientes',',\nno recientes').replace(' hasta 56','\nhasta 56') for v in t.estado_actividad]
    bars=ax.bar(labels,100*t.tasa_fail,color=['#527DA5','#7B878C','#D36A29'])
    ax.bar_label(bars,labels=[f'{100*r.tasa_fail:.1f} %\nn={r.n:,}' for r in t.itertuples()],padding=4)
    ax.set(ylim=(0,100),ylabel='% Fail observado',title='Registros de actividad y resultado · asociación descriptiva')
    plots['07_estado_actividad']=fig
    for fig in plots.values():plt.close(fig)
    return plots

def hallazgos(result):
    t=result['tables'];s=result['summary'];desc=t['descriptivos_numericos'];out=t['outliers'].set_index('variable')
    recorded=t['actividad_registrada'].set_index('has_recorded_activity')
    corr=t['correlacion_fail'].set_index('variable')
    ratio=s['missing_counts']['click_ratio_14d'];imd=s['missing_counts']['imd_band'];n=s['rows']
    return [
      {'hallazgo':'Desbalance multiclase relevante para Fail',
       'evidencia':f"Approved={s['target_counts']['Approved']:,}, Fail={s['target_counts']['Fail']:,}, Withdrawn={s['target_counts']['Withdrawn']:,}; Fail={100*s['fail_prevalence']:.2f} %; razón mayor/menor={s['majority_minority_ratio']:.2f}.",
       'consecuencia':'Mantener AP para Fail y cobertura a cupo fijo; informar calibración y métricas por clase. Accuracy de mayoría es solo referencia descriptiva, no criterio de selección ni baseline ya entrenado. Comparar pesos de clase únicamente dentro de CV.'},
      {'hallazgo':'Clics con cola larga; outliers no implican errores',
       'evidencia':f"clicks_current_14d: mediana={desc.loc['clicks_current_14d','50%']:.0f}, p99={desc.loc['clicks_current_14d','99%']:.1f}, máximo={desc.loc['clicks_current_14d','max']:.0f}, asimetría={desc.loc['clicks_current_14d','asimetria']:.2f}; IQR marca {int(out.loc['clicks_current_14d','n_iqr']):,} y |Z|≥3 marca {int(out.loc['clicks_current_14d','n_z_abs_ge_3']):,} observaciones.",
       'consecuencia':'Conservar filas. Probar log1p de clics actuales en la etapa de features y comparar por ablación con los mismos folds. No aplicar log1p al cambio quincenal, que puede ser negativo. Cualquier recorte aprendido debe ajustarse solo dentro del fold.'},
      {'hallazgo':'Ausencia de registros con recencia desconocida',
       'evidencia':f"{int(recorded.loc[False,'n']):,} matrículas ({100*recorded.loc[False,'n']/n:.2f} %) sin registros; Fail={100*recorded.loc[False,'tasa_fail']:.2f} %, frente a {100*recorded.loc[True,'tasa_fail']:.2f} % con registros. Recencia falta exactamente en esos casos.",
       'consecuencia':'Preservar las matrículas y distinguir desconocido de cero. Mantener indicadores y justificar imputación dentro del Pipeline; no asignar recencia cero a ausencia de registros ni inferir actividad académica real. Evaluar estado/indicador de registros como candidato, sin interpretar causalidad.'},
      {'hallazgo':'Faltantes de razón quincenal son estructurales',
       'evidencia':f"click_ratio_14d falta en {ratio:,} matrículas ({100*ratio/n:.2f} %), exactamente cuando clicks_previous_14d=0. IMD falta en {imd:,} ({100*imd/n:.2f} %).",
       'consecuencia':'No convertir razón indefinida en cero ni borrar esas filas. Conservar indicador de denominador cero si se usa la razón. Prototipar clics por día activo con denominador positivo y NULL en ausencia de días activos; codificar IMD con política explícita dentro del fold.'},
      {'hallazgo':'Actividad reciente se asocia a Fail, sin demostrar rendimiento',
       'evidencia':f"Spearman(Fail,active_days_current_14d)={corr.loc['active_days_current_14d','spearman_fail']:.3f}; Spearman(Fail,clicks_current_14d)={corr.loc['clicks_current_14d','spearman_fail']:.3f}. Las medianas por clase y las tasas por módulo/presentación se muestran separadas.",
       'consecuencia':'Conservar comparación estático/longitudinal y evaluar intensidad normalizada por días activos como candidata. No seleccionar un ganador ni eliminar variables solo por correlación marginal. Los códigos de módulo/presentación siguen siendo contexto, no predictores automáticos.'},
      {'hallazgo':'IQR degenerado en antecedentes discretos',
       'evidencia':f"num_of_prev_attempts tiene IQR={out.loc['num_of_prev_attempts','iqr']:.0f}; la regla marca {int(out.loc['num_of_prev_attempts','n_iqr']):,} casos, aunque los valores positivos representan intentos previos registrados.",
       'consecuencia':'Informar la bandera estadística sin tratarla como error de calidad ni borrar reintentos. Z-score tampoco es un test de anomalía con normalidad demostrada. Mantener estos antecedentes hasta comparar su aporte dentro de CV.'}]

def exportar(result,plots):
    output=ROOT/'docs/eda';output.mkdir(parents=True,exist_ok=True)
    indexed={'descriptivos_numericos','correlaciones','medianas_target'}
    for name,table in result['tables'].items():table.to_csv(output/(name+'.csv'),index=name in indexed,float_format='%.8g')
    for name,fig in plots.items():fig.savefig(output/(name+'.png'),bbox_inches='tight',facecolor='white')
    result['summary']['findings']=hallazgos(result)
    result['summary']['created_at_utc']=datetime.now(timezone.utc).isoformat()
    result['summary']['artifact_files']={p.name:sha256(p) for p in sorted(output.iterdir()) if p.suffix in ['.csv','.png']}
    (output/'resumen.json').write_text(json.dumps(result['summary'],ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    return output
