"""Referencia de entrenamiento, monitoreo por evento y tablero operativo."""
from contextlib import closing
from pathlib import Path
import argparse
import csv
import json
import os
import sqlite3
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, chi2_contingency
from sklearn.metrics import average_precision_score
from src.datos import ROOT, identidad, sha256, desarrollo_temprano, PLAN_CONTROL, PLAN_DERIVA
from monitoreo.alertas import PROTOCOLO_MONITOREO as PROTOCOLO, diagnostico, evaluar_alertas

REFERENCIA = ROOT/'tests/fixtures/referencia_monitoreo.json'
CATEGORICAS = ['gender','region','highest_education','imd_band','age_band','disability']
FALTANTE, NUEVA = '__FALTANTE__', '__NUEVA__'


def conteos_numeric(values, cortes):
    values = np.asarray(values, dtype=float)
    presentes = values[np.isfinite(values)]
    counts = np.histogram(presentes, bins=[-np.inf, *cortes, np.inf])[0].tolist()
    return counts+[int((~np.isfinite(values)).sum())]


def perfil_entrenamiento(frame, names):
    resultado = {}
    for name in names:
        serie = frame[name]
        if name in CATEGORICAS:
            values = serie.astype(object).where(serie.notna(), FALTANTE).astype(str)
            categorias = sorted(set(values)-{FALTANTE, NUEVA})+[FALTANTE,NUEVA]
            resultado[name] = {'tipo':'categorica','categorias':categorias,'conteos':[int((values==v).sum()) for v in categorias]}
        else:
            values = pd.to_numeric(serie).to_numpy(dtype=float, na_value=np.nan)
            x = values[np.isfinite(values)]
            if len(x):
                unicos=np.unique(x)
                cortes=np.r_[unicos[0],(unicos[:-1]+unicos[1:])/2,unicos[-1]] if len(unicos)<=10 else np.unique(np.quantile(x,np.linspace(0,1,11)))
                if len(cortes)==1: cortes=np.array([cortes[0],np.nextafter(cortes[0],np.inf)])
                else: cortes[-1]=np.nextafter(cortes[-1],np.inf)
                muestra = np.random.default_rng(5041).choice(x,size=min(1000,len(x)),replace=False).tolist()
            else: cortes=np.array([0.,1.]);muestra=[]
            resultado[name] = {'tipo':'numerica','cortes':cortes.tolist(),'conteos':conteos_numeric(values,cortes),
                'min':float(x.min()) if len(x) else None,'max':float(x.max()) if len(x) else None,'ks_muestra':muestra}
    return resultado


def preparar_referencia(local):
    """Reutiliza OOF y folds históricos, sin estimar modelos ni mirar targets 2014J."""
    local = Path(local)
    meta = json.loads((ROOT/'tests/fixtures/referencia.json').read_text())
    names = [v['name'] for v in json.loads(meta['modelos']['14']['signature']['inputs'])]
    assignments = pd.read_csv(local/'anticipacion/assignments.csv')[['enrollment_key','cv_fold']]
    referencia = {'protocolo':PROTOCOLO,'snapshot_id':meta['modelos']['14']['snapshot_id'],
                  'assignments_sha256':sha256(local/'anticipacion/assignments.csv'),'cortes':{}}
    for cut in [14,28]:
        frame,manifest=desarrollo_temprano(local,cut)
        if manifest['id']!=referencia['snapshot_id']:raise ValueError('Snapshot de referencia distinto')
        path=local/'anticipacion'/f'boosting-{cut}-longitudinal-oof.parquet'
        frame=frame.merge(pd.read_parquet(path),on='enrollment_key',validate='one_to_one').merge(assignments,on='enrollment_key',validate='one_to_one')
        modulos=sorted(frame.code_module.unique())
        info={'source_run_id':meta['modelos'][str(cut)]['run_id'],'oof_sha256':sha256(path),'global':None,'ondas':{}}
        for onda in [0,1,2,3,4]:
            subset=frame if onda==0 else frame.loc[frame.code_module.isin(modulos[onda-1::4])]
            metrics=[float(average_precision_score(f.target_class.eq('Fail'),f.p_fail)) for _,f in subset.groupby('cv_fold')]
            ref={'n':len(subset),'modulos':sorted(subset.code_module.unique()),'datos':perfil_entrenamiento(subset,names),
                 'cv_ap_fold':metrics,'cv_ap_mean':float(np.mean(metrics)),'cv_ap_std':float(np.std(metrics,ddof=1)),
                 'prevalencia_fail':float(subset.target_class.eq('Fail').mean())}
            if onda==0:
                assert np.isclose(ref['cv_ap_mean'],meta['modelos'][str(cut)]['cv_ap_fail_mean'],atol=1e-12)
                assert np.isclose(ref['cv_ap_std'],meta['modelos'][str(cut)]['cv_ap_fail_std'],atol=1e-12)
                info['global']=ref
            else:info['ondas'][str(onda)]=ref
        referencia['cortes'][str(cut)]=info
    referencia['id']=identidad(referencia)
    REFERENCIA.write_text(json.dumps(referencia,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
    return {'referencia_id':referencia['id'],'targets_2014j_consultados':False,'nuevos_entrenamientos':0}


def psi(esperado,observado):
    a,b=np.asarray(esperado,dtype=float),np.asarray(observado,dtype=float)
    if len(a)!=len(b) or (a<0).any() or (b<0).any():raise ValueError('Conteos PSI incompatibles')
    alpha=PROTOCOLO['pseudoconteo']
    a=(a+alpha)/(a.sum()+alpha*len(a));b=(b+alpha)/(b.sum()+alpha*len(b))
    return float(np.sum((b-a)*np.log(b/a)))


def calidad_y_deriva(features,referencia):
    resultados={}
    for campo,ref in referencia.items():
        values=features[campo];missing=values.isna();n=len(values)
        datos={'faltantes':float(missing.mean()),'categorias_nuevas':0.,'fuera_contrato':0.,'fuera_soporte':0.,'p_respaldo':None,'prueba':None}
        if ref['tipo']=='categorica':
            values=values.astype(object).where(~missing,FALTANTE).astype(str)
            unknown=(~values.isin(ref['categorias'])) & values.ne(FALTANTE)
            datos['categorias_nuevas']=float(unknown.mean())
            values=values.where(~unknown,NUEVA)
            counts=np.array([int((values==v).sum()) for v in ref['categorias']])
            table=np.array([ref['conteos'],counts],dtype=float)
            table=table[:,table.sum(axis=0)>0]
            if table.shape[1]>1:
                expected=table.sum(axis=1)[:,None]*table.sum(axis=0)[None,:]/table.sum()
                rare=(expected<5).any(axis=0)
                if rare.any():table=np.column_stack([table[:,~rare],table[:,rare].sum(axis=1)])
                if table.shape[1]>1 and (table.sum(axis=0)>0).all():
                    test=chi2_contingency(table,correction=False)
                    if (test.expected_freq>=5).all():datos.update(p_respaldo=float(test.pvalue),prueba='chi2; categorías escasas agrupadas')
            datos['prueba']=datos['prueba'] or 'chi2 no concluyente por soporte escaso/constante'
        else:
            x=pd.to_numeric(values,errors='coerce').to_numpy(dtype=float,na_value=np.nan)
            valid=np.isfinite(x);v=x[valid];counts=conteos_numeric(x,ref['cortes'])
            invalid=(~valid)&~missing.to_numpy()
            if campo not in ['registration_days_before_start','click_change_14d']:invalid|=valid&(x<0)
            if campo in ['is_imd_missing','has_recorded_activity']:invalid|=valid&~np.isin(x,[0,1])
            if campo=='module_presentation_length':invalid|=valid&(x<=0)
            if campo=='active_days_current_14d':invalid|=valid&(x>14)
            datos['fuera_contrato']=float(invalid.mean())
            if ref['min'] is not None:datos['fuera_soporte']=float(((x<ref['min'])|(x>ref['max'])).mean())
            if len(v) and ref['ks_muestra']:
                test=ks_2samp(ref['ks_muestra'],v,method='asymp')
                datos.update(p_respaldo=float(test.pvalue),prueba='KS asintótico; empates/discretización limitan su interpretación')
        datos['psi']=psi(ref['conteos'],counts)
        datos['psi_accionable']=campo not in PROTOCOLO['psi_no_accionable']
        resultados[campo]=datos
    return resultados


def resumen_sistema(ruta,plan_id,lote_id,latencias):
    with closing(sqlite3.connect(ruta)) as db:
        campos={r[1] for r in db.execute('PRAGMA table_info(peticiones)')}
        rows=db.execute('SELECT codigo,latencia_ms FROM peticiones WHERE plan_id=? AND lote_id=?',(plan_id,lote_id)).fetchall() if 'plan_id' in campos else []
    n=len(rows)
    vals=[r[1] for r in rows] if rows else list(set(latencias))
    return {'solicitudes_atribuidas':n,'solicitudes_exitosas_conciliadas':1,
        'cobertura':'peticiones con cabecera operativa' if n else 'histórico sin atribución: latencia de respuesta conciliada; errores del lote desconocidos',
        'latencia_p50_ms':float(np.percentile(vals,50)) if vals else None,'latencia_p95_ms':float(np.percentile(vals,95)) if vals else None,
        'errores_4xx':sum(400<=r[0]<500 for r in rows) if n else None,'errores_5xx':sum(r[0]>=500 for r in rows) if n else None,
        'tasa_4xx':sum(400<=r[0]<500 for r in rows)/n if n else None,'tasa_5xx':sum(r[0]>=500 for r in rows)/n if n else None,
        'slo_evaluable':n>=PROTOCOLO['min_solicitudes_slo']}


def evaluar_lote(lote,predicciones,labels,referencia,sistema,dia):
    """Labels es únicamente el subconjunto ya disponible al día de revisión."""
    frame=pd.DataFrame([r['ENTRADAS'] for r in predicciones])
    completos=set(lote['manifiesto']['base'])<=set(labels)
    y=[labels.get(r['MATRICULA'])=='Fail' for r in predicciones]
    nfail=sum(y);n=len(y)
    evaluable=completos and nfail>=PROTOCOLO['min_fail'] and n-nfail>=PROTOCOLO['min_no_fail']
    ap=float(average_precision_score(y,[r['SALIDA']['riesgo_fail'] for r in predicciones])) if evaluable else None
    umbral=max(0.,referencia['cv_ap_mean']-PROTOCOLO['sigmas_ap']*referencia['cv_ap_std'])
    datos=calidad_y_deriva(frame,referencia['datos'])
    cambio=bool(n>=PROTOCOLO['min_lote'] and any(d['psi']>PROTOCOLO['psi_alta'] and d['psi_accionable'] for d in datos.values()))
    caida=bool(evaluable and ap<umbral)
    diag,accion=diagnostico(cambio,caida,evaluable)
    nuevas=[r for r in predicciones if r['SALIDA']['consume_cupo_nuevo']]
    tp=sum(labels.get(r['MATRICULA'])=='Fail' for r in nuevas) if completos else None
    result={'plan_id':lote['plan_id'],'lote_id':lote['lote_id'],'corte':lote['corte'],'dia_prediccion':lote['dia'],'dia_revision':dia,
        'n':n,'alterado':bool(lote.get('alterado',False)),'n_etiquetas':sum(r['MATRICULA'] in labels for r in predicciones),
        'etiquetas_completas':completos,'desempeno_evaluable':evaluable,'ap_fail':ap,'ap_cv_mean':referencia['cv_ap_mean'],
        'ap_cv_std':referencia['cv_ap_std'],'umbral_ap':umbral,'caida_ap':caida,'datos_cambian':cambio,
        'prevalencia_fail':nfail/n if completos else None,'prevalencia_referencia':referencia['prevalencia_fail'],
        'nuevas_propuestas':len(nuevas),'tp_nuevos':tp,'fp_nuevos':len(nuevas)-tp if completos else None,
        'precision_nuevas':tp/len(nuevas) if completos and nuevas else None,
        'scores':dict(zip(['min','p25','p50','p75','max'],[float(v) for v in np.quantile([r['SALIDA']['riesgo_fail'] for r in predicciones],[0,.25,.5,.75,1])])),
        'tasas_decision':pd.Series([r['SALIDA']['decision'] for r in predicciones]).value_counts(normalize=True).to_dict(),
        'versiones_modelo':sorted({str(r['VERSION_MODELO']) for r in predicciones}),'run_ids':sorted({r['RUN_ID'] for r in predicciones}),
        'respaldo_n':sum(r['RESPALDO'] for r in predicciones),'datos':datos,'sistema':sistema,'diagnostico':diag,'accion':accion}
    return result


def registrar_contratos():
    from src.datos import TABLAS_OPERACION, CLAVES_OPERACION
    TABLAS_OPERACION.update({
        'MONITOREO': {'ID_MONITOREO':'VARCHAR','PLAN_ID':'VARCHAR','LOTE_ID':'VARCHAR','DIA_REVISION':'NUMBER','CONTENIDO':'VARIANT','HUELLA':'VARCHAR'},
        'ALERTAS': {'ID_ALERTA':'VARCHAR','ID_MONITOREO':'VARCHAR','PLAN_ID':'VARCHAR','LOTE_ID':'VARCHAR','CONTENIDO':'VARIANT','HUELLA':'VARCHAR'},
    })
    CLAVES_OPERACION.update({'MONITOREO':['ID_MONITOREO'],'ALERTAS':['ID_ALERTA']})


def leer_predicciones(repo,plan_id,cohorte_id=None,corte=None,lote_id=None):
    from src.datos import ESQUEMA_OPERACION
    filtros=['PLAN_ID=%s'];params=[plan_id]
    for columna,valor in [('COHORTE_ID',cohorte_id),('LOTE_ID',lote_id)]:
        if valor is not None:filtros.append(columna+'=%s');params.append(valor)
    if corte is not None:filtros.append('CORTE<=%s');params.append(corte)
    with repo.conn.cursor() as cur:
        cur.execute('SELECT ID_PREDICCION,MATRICULA,ENTRADAS,SALIDA,LATENCIA_MS,VERSION_MODELO,RUN_ID,RESPALDO FROM '+ESQUEMA_OPERACION+'.PREDICCIONES WHERE '+' AND '.join(filtros)+' ORDER BY ID_PREDICCION',tuple(params))
        names=[r[0] for r in cur.description]
        rows=[dict(zip(names,row)) for row in cur.fetchall()]
    for row in rows:
        for k in ['ENTRADAS','SALIDA']:
            if isinstance(row[k],str):row[k]=json.loads(row[k])
    return rows


def monitorear(repo,plan_id,lote_id,fase,local):
    from src.datos import ESQUEMA_OPERACION
    ref=json.loads(REFERENCIA.read_text())
    if ref['id']!=identidad({k:v for k,v in ref.items() if k!='id'}) or ref['protocolo']!=PROTOCOLO:
        raise ValueError('Referencia o protocolo de monitoreo alterados')
    lote=repo.contenido('LOTES_ENTRADA',plan_id,lote_id)
    if lote is None or repo.contenido('LOTES_PROCESADOS',plan_id,lote_id) is None:
        raise ValueError('Lote aún no conciliado')
    limite=max(v['fin_periodo'] for v in lote['fuentes'].values())+14
    dia=lote['dia'] if fase=='prediccion' else limite
    if dia>repo.reloj(plan_id):raise ValueError('El reloj todavía no permite esta revisión')
    ident=identidad([plan_id,lote_id,dia,ref['id']])
    with repo.conn.cursor() as cur:
        previo=cur.execute(f'SELECT CONTENIDO FROM {ESQUEMA_OPERACION}.MONITOREO WHERE ID_MONITOREO=%s',(ident,)).fetchall()
    if len(previo)>1:raise ValueError('Evento de monitoreo duplicado')
    if previo:
        result=json.loads(previo[0][0]);return {'id_monitoreo':ident,'repeticion':True,'alertas':result['alertas'],'diagnostico':result['diagnostico']}
    pred=leer_predicciones(repo,plan_id,lote_id=lote_id)
    if len(pred)!=len(lote['solicitud']['matriculas']):raise ValueError('Predicciones incompletas')
    with repo.conn.cursor() as cur:
        labels=dict(cur.execute(f'SELECT MATRICULA,TARGET_CLASS FROM {ESQUEMA_OPERACION}.ETIQUETAS WHERE PLAN_ID=%s AND DIA_DISPONIBLE<=%s',(plan_id,dia)).fetchall())
        historia=[json.loads(row[0]) for row in cur.execute(f'SELECT CONTENIDO FROM {ESQUEMA_OPERACION}.MONITOREO WHERE PLAN_ID=%s AND DIA_REVISION<=%s',(plan_id,dia)).fetchall()]
    onda=str((lote['orden']-1)%4+1)
    referencia=ref['cortes'][str(lote['corte'])]['ondas'][onda]
    db=Path(local)/('deriva/operacion.sqlite' if plan_id==PLAN_DERIVA else 'operacion.sqlite')
    sistema=resumen_sistema(db,plan_id,lote_id,[float(r['LATENCIA_MS']) for r in pred])
    result=evaluar_lote(lote,pred,labels,referencia,sistema,dia)
    result.update(id_monitoreo=ident,referencia_id=ref['id'],protocolo_version=PROTOCOLO['version'],
                  ap_cv_global=ref['cortes'][str(lote['corte'])]['global']['cv_ap_mean'],
                  revision_retrospectiva=True)
    historial=leer_predicciones(repo,plan_id,cohorte_id=lote['cohorte_id'],corte=lote['corte'])
    propuestas={r['MATRICULA']:r for r in historial if r['SALIDA']['consume_cupo_nuevo']}
    result['propuestas_acumuladas']=len(propuestas)
    result['personas_unicas_propuestas']=len({r['SALIDA']['persona'] for r in propuestas.values()})
    if result['etiquetas_completas']:
        fail=sum(labels[k]=='Fail' for k in lote['manifiesto']['base'])
        tp=sum(labels[k]=='Fail' for k in propuestas)
        result.update(fail_cohorte_base=fail,tp_acumulados=tp,cobertura_acumulada=tp/fail if fail else None)
    else:result.update(fail_cohorte_base=None,tp_acumulados=None,cobertura_acumulada=None)
    alerts,trigger=evaluar_alertas(result,historia)
    result.update(alertas=alerts,reentrenamiento_propuesto=trigger)
    # Alertas antes del evento: un fallo intermedio se recupera con IDs deterministas.
    repo.insertar('ALERTAS',[{'ID_ALERTA':identidad([ident,a['tipo'],a['metrica']]),'ID_MONITOREO':ident,'PLAN_ID':plan_id,'LOTE_ID':lote_id,'CONTENIDO':a} for a in alerts])
    repo.insertar('MONITOREO',[{'ID_MONITOREO':ident,'PLAN_ID':plan_id,'LOTE_ID':lote_id,'DIA_REVISION':dia,'CONTENIDO':result}])
    return {'id_monitoreo':ident,'plan_id':plan_id,'lote_id':lote_id,'dia_revision':dia,'diagnostico':result['diagnostico'],
            'reentrenamiento_propuesto':trigger,'alertas':alerts}


def _ejecutar_monitoreo(plan_id,lote_id='todos',fase='prediccion',local=None):
    from src.datos import conectar_snowflake,RepositorioSnowflake
    if plan_id not in [PLAN_CONTROL,PLAN_DERIVA] or fase not in ['prediccion','maduro'] or lote_id not in ['todos',*[f'L{i:02}' for i in range(1,9)]]:
        raise ValueError('Solicitud de monitoreo inválida')
    registrar_contratos()
    with conectar_snowflake() as conn:
        repo=RepositorioSnowflake(conn);repo.asegurar()
        if lote_id=='todos':
            plan=repo.contenido('PLANES',plan_id)
            ids=[r['lote_id'] for r in plan['lotes']]
            if fase=='maduro':
                lotes=[repo.contenido('LOTES_ENTRADA',plan_id,i) for i in ids]
                ids=[r['lote_id'] for r in sorted(lotes,key=lambda r:(max(v['fin_periodo'] for v in r['fuentes'].values())+14,r['dia']))]
            return {'eventos':[monitorear(repo,plan_id,i,fase,local or ROOT/'.local') for i in ids]}
        return monitorear(repo,plan_id,lote_id,fase,local or ROOT/'.local')


def ejecutar_monitoreo(plan_id,lote_id='todos',fase='prediccion',local=None):
    import fcntl
    base=Path(local or ROOT/'.local');base.mkdir(parents=True,exist_ok=True)
    with (base/'escritor-snowflake.lock').open('a') as gate:
        fcntl.flock(gate,fcntl.LOCK_EX)
        return _ejecutar_monitoreo(plan_id,lote_id,fase,base)


def exportar_evidencia(repo,destino):
    from src.datos import ESQUEMA_OPERACION
    destino=Path(destino);destino.mkdir(parents=True,exist_ok=True)
    with repo.conn.cursor() as cur:
        rows=cur.execute(f'SELECT CONTENIDO FROM {ESQUEMA_OPERACION}.MONITOREO ORDER BY PLAN_ID,DIA_REVISION,LOTE_ID').fetchall()
    datos=[json.loads(r[0]) for r in rows]
    if not datos:raise ValueError('Sin monitoreo para exportar')
    columns=list(datos[0]);tmp=destino/'monitoreo.csv.tmp'
    with tmp.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator='\n');writer.writeheader()
        for row in datos:
            writer.writerow({k:json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False) if isinstance(v,(dict,list)) else v for k,v in row.items()})
    tmp.replace(destino/'monitoreo.csv')
    cols=['plan_id','lote_id','dia_revision','id_monitoreo','tipo','metrica','valor','umbral','ventana','severidad','receptor','accion']
    tmp=destino/'alertas.csv.tmp'
    with tmp.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');writer.writeheader()
        for row in datos:
            for alerta in row['alertas']:writer.writerow({**{k:row[k] for k in cols[:4]},**alerta})
    tmp.replace(destino/'alertas.csv')
    return {'monitoreos':len(datos),'alertas':sum(len(d['alertas']) for d in datos)}


def servir():
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    from threading import RLock
    lock=RLock()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send(self,status,body):
            data=json.dumps(body,ensure_ascii=False,allow_nan=False).encode()
            self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        def do_GET(self):
            self.send(200,{'estado':'ok'}) if self.path=='/salud' else self.send(404,{'error':'ruta_desconocida'})
        def do_POST(self):
            if self.path not in ['/monitorear','/reentrenar']:return self.send(404,{'error':'ruta_desconocida'})
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=(8192 if self.path=='/reentrenar' else 1024):raise ValueError('Tamaño inválido')
                data=json.loads(self.rfile.read(size))
                if self.path=='/monitorear':
                    if set(data)!={'plan_id','lote_id','fase'}:raise ValueError('Campos inválidos')
                    with lock:result=ejecutar_monitoreo(**data)
                else:
                    if set(data)!={'operacion','execution_id','decision','motivo','responsable'}:raise ValueError('Campos inválidos')
                    from src.reentrenar import trabajar
                    with lock:result=trabajar(**data)
                self.send(200,result)
            except Exception as exc:
                self.send(422 if isinstance(exc,ValueError) else 500,{'error_class':type(exc).__name__})
    ThreadingHTTPServer(('0.0.0.0',8090),Handler).serve_forever()


def tablero():
    import streamlit as st
    import altair as alt
    st.set_page_config(page_title='Apoyo académico preventivo',page_icon='📊',layout='wide')
    st.title('Apoyo académico preventivo')
    st.caption('Operación simulada · semanas 2 y 4 · decisiones sujetas a revisión humana')
    st.info('Los escenarios se analizan por separado. Las propuestas no equivalen a tutorías realizadas ni a reprobaciones evitadas.')
    directory=Path(os.environ.get('PSET4_DOCS',ROOT/'docs'))
    if not (directory/'monitoreo.csv').exists():
        st.warning('Aún no se exportaron eventos de monitoreo.');return
    frame=pd.read_csv(directory/'monitoreo.csv')
    plan=st.selectbox('Escenario',sorted(frame.plan_id.unique()))
    datos=frame.loc[frame.plan_id.eq(plan)].copy()
    maduros=datos.loc[datos.etiquetas_completas.eq(True)].sort_values('dia_revision').drop_duplicates('lote_id',keep='last')
    visible=maduros if len(maduros) else datos.sort_values('dia_revision').drop_duplicates('lote_id',keep='last')
    a,b,c,d=st.columns(4)
    a.metric('Predicciones',f'{int(visible.n.sum()):,}')
    b.metric('Propuestas nuevas',int(visible.nuevas_propuestas.sum()))
    c.metric('Lotes con resultados completos',len(maduros))
    d.metric('Alertas para revisión',sum(len(json.loads(v)) for v in visible.alertas))
    st.caption('2014J es un benchmark histórico ya examinado. La separación por escenario evita sumar dos presupuestos sobre las mismas matrículas.')
    progreso=datos[['lote_id','dia_prediccion','dia_revision','n_etiquetas','etiquetas_completas','diagnostico']].copy()
    with st.expander('Disponibilidad de resultados y diagnóstico',expanded=False):st.dataframe(progreso,hide_index=True)
    left,right=st.columns(2)
    with left:
        st.subheader('Capacidad de focalización')
        line=visible[['lote_id','ap_fail','umbral_ap']].melt('lote_id',var_name='serie',value_name='valor')
        st.altair_chart(alt.Chart(line).mark_line(point=True).encode(x='lote_id:O',y=alt.Y('valor:Q',title='AP de Fail'),color='serie:N',tooltip=['lote_id','serie','valor']),width='stretch')
        st.caption('Una caída exige revisión de datos y resultados. Dos caídas consecutivas del mismo corte proponen evaluar un challenger; no lo promueven.')
    with right:
        st.subheader('Atención propuesta y error de focalización')
        bar=visible[['lote_id','tp_nuevos','fp_nuevos']].melt('lote_id',var_name='resultado',value_name='matriculas')
        st.altair_chart(alt.Chart(bar).mark_bar().encode(x='lote_id:O',y='matriculas:Q',color='resultado:N',tooltip=['lote_id','resultado','matriculas']),width='stretch')
        st.caption('TP y FP usan únicamente resultados ya disponibles. El beneficio causal de una tutoría no se observa en esta simulación.')
    st.subheader('Lectura de negocio por lote')
    st.dataframe(visible[['lote_id','corte','nuevas_propuestas','tp_nuevos','fp_nuevos','precision_nuevas','cobertura_acumulada','personas_unicas_propuestas']],hide_index=True)
    st.caption('La cobertura acumulada usa los Fail de la cohorte base de cada onda. Los cupos se cuentan por matrícula-asignatura; las personas únicas se muestran aparte.')
    st.subheader('Cambios en los datos')
    cells=[]
    for _,row in visible.iterrows():
        for name,value in json.loads(row.datos).items():cells.append({'lote':row.lote_id,'feature':name,'PSI':value['psi'],'accionable':value['psi_accionable']})
    st.altair_chart(alt.Chart(pd.DataFrame(cells)).mark_rect().encode(x='lote:O',y='feature:N',color=alt.Color('PSI:Q',scale=alt.Scale(scheme='yelloworangered',domain=[0,.25])),tooltip=['lote','feature','PSI','accionable']),width='stretch')
    st.caption('PSI >0,25 genera revisión en features accionables. La duración curricular se muestra como contexto y no activa por sí sola una alerta de comportamiento.')
    st.subheader('Salud del servicio')
    sistema=pd.DataFrame([{'lote_id':r.lote_id,**json.loads(r.sistema)} for _,r in visible.iterrows()])
    st.dataframe(sistema,hide_index=True)
    st.caption('Sin atribución histórica, las tasas de error del lote son desconocidas. Un lote tiene una solicitud batch: p50/p95 individuales no estiman un SLA; se requieren 20 solicitudes para evaluarlo.')
    st.subheader('Alertas y versiones')
    alertas=pd.read_csv(directory/'alertas.csv')
    st.dataframe(alertas.loc[alertas.plan_id.eq(plan)] if len(alertas) else alertas,hide_index=True)
    st.dataframe(visible[['lote_id','versiones_modelo','run_ids','reentrenamiento_propuesto','accion']],hide_index=True)
    ruta=directory/'reentrenamientos.csv'
    if ruta.exists():st.dataframe(pd.read_csv(ruta),hide_index=True)
    else:st.caption('Todavía no hay reentrenamientos registrados: una alerta representa una propuesta pendiente de revisión.')


def main():
    if os.environ.get('PSET4_TABLERO')=='1':return tablero()
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--preparar-referencia',type=Path)
    group.add_argument('--servir',action='store_true')
    group.add_argument('--exportar',type=Path)
    group.add_argument('--plan',choices=[PLAN_CONTROL,PLAN_DERIVA])
    parser.add_argument('--lote',default='todos')
    parser.add_argument('--fase',choices=['prediccion','maduro'],default='prediccion')
    args=parser.parse_args()
    if args.preparar_referencia:result=preparar_referencia(args.preparar_referencia)
    elif args.servir:return servir()
    elif args.plan:result=ejecutar_monitoreo(args.plan,args.lote,args.fase)
    else:
        from src.datos import conectar_snowflake,RepositorioSnowflake
        with conectar_snowflake() as conn:result=exportar_evidencia(RepositorioSnowflake(conn),args.exportar)
    print(json.dumps(result,ensure_ascii=False,allow_nan=False))


if __name__=='__main__':
    main()
