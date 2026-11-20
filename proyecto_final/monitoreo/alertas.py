"""Protocolo operativo previo a observar el monitoreo; sin promoción automática."""
PROTOCOLO_MONITOREO = {
    'version': 'monitoreo-1', 'psi_aviso': 0.10, 'psi_alta': 0.25, 'pseudoconteo': 0.5,
    'min_lote': 200, 'min_fail': 20, 'min_no_fail': 20, 'sigmas_ap': 2,
    'lotes_consecutivos': 2, 'p95_ms': 10000, 'min_solicitudes_slo': 20,
    'tasa_5xx': 0.01, 'tasa_4xx': 0.05, 'alpha_respaldo': 0.05,
    'psi_no_accionable': ['module_presentation_length'],
    'razon_excepcion': 'Duración curricular conocida de cada edición: se calcula PSI y rango, pero el calendario por sí solo no implica incidente de comportamiento.',
    'referencia': 'Entrenamiento del corte, condicionado a los módulos de la onda; global conservado como diagnóstico. KS con muestra determinista de hasta 1000 valores por feature.',
    'limitacion': 'Umbrales operativos de demostración, no SLA institucional ni intervalos de confianza. La mezcla y prevalencia pueden cambiar AP sin demostrar deriva conceptual.',
    'induccion': {
        'version': 'permutacion-creditos-1', 'lotes': ['L06', 'L07'], 'seed': 5041,
        'desplazamiento_creditos': 120.0,
        'metodo': 'Permutar vectores completos de features dentro de edición, ordenando por matrícula, semilla 5041+orden; sumar 120 créditos. No se usan ni cambian targets.',
        'aislamiento': 'Plan y SQLite propios; mismas matrículas y cupos, resultados de escenarios separados. L01-L05 y L08 sin alteración.',
        'limitacion': 'Escenario sintético que rompe asociaciones; sus demografías permutadas no representan personas reales para análisis de equidad.',
    },
}


def diagnostico(cambio, caida, etiquetas):
    if not etiquetas:
        return 'pendiente_etiquetas', 'Vigilar datos y esperar resultados; no reentrenar.'
    if cambio and caida:
        return 'datos_con_impacto', 'Investigar fuente y etiquetado; evaluar reentrenamiento si la caída persiste.'
    if cambio:
        return 'datos_sin_impacto', 'Revisar cambios de fuente; mantener el modelo y no reentrenar por PSI solo.'
    if caida:
        return 'posible_deriva_conceptual', 'Revisar prevalencia y calidad del target; evaluar reentrenamiento si persiste.'
    return 'sin_evidencia_de_cambio', 'Continuar vigilancia.'


def evaluar_alertas(metricas, historia=()):
    """Las etiquetas gobiernan el desempeño; PSI solo nunca activa reentrenamiento."""
    p = PROTOCOLO_MONITOREO
    alertas = []
    def add(tipo, metrica, valor, umbral, ventana, severidad, receptor, accion):
        alertas.append(dict(tipo=tipo, metrica=metrica, valor=valor, umbral=umbral,
                            ventana=ventana, severidad=severidad, receptor=receptor, accion=accion))
    for campo, datos in metricas['datos'].items():
        if datos['psi'] > p['psi_alta'] and campo not in p['psi_no_accionable'] and metricas['n'] >= p['min_lote']:
            add('datos', 'psi:'+campo, datos['psi'], p['psi_alta'], '1 lote', 'alta', 'equipo de datos', 'Revisar fuente, composición y respaldo estadístico; PSI solo no dispara entrenamiento.')
        if datos['fuera_contrato'] > 0 or datos['categorias_nuevas'] > 0:
            add('calidad', 'contrato:'+campo, max(datos['fuera_contrato'],datos['categorias_nuevas']), 0, '1 lote', 'alta', 'equipo de datos', 'Detener uso del lote y corregir la fuente; supervisión humana.')
    if metricas['caida_ap']:
        add('desempeno', 'ap_fail', metricas['ap_fail'], metricas['umbral_ap'], '1 lote etiquetado', 'alta', 'responsable del modelo', 'Investigar; mantener la comparación con datos no vistos.')
    anteriores = sorted([m for m in historia if m['corte']==metricas['corte'] and m['etiquetas_completas'] and m['lote_id']!=metricas['lote_id']], key=lambda m:(m['dia_revision'],m['dia_prediccion']))
    previos = [m for m in anteriores if (m['dia_revision'],m['dia_prediccion']) < (metricas['dia_revision'],metricas['dia_prediccion'])]
    disparar = bool(metricas['caida_ap'] and previos and previos[-1]['caida_ap'])
    if disparar:
        add('reentrenamiento_propuesto', 'caida_ap_consecutiva', 2, 2, '2 lotes etiquetados consecutivos del mismo corte', 'alta', 'responsable del modelo', 'Preparar challenger sin repetir tuning; reservar el último lote etiquetado y exigir aprobación humana.')
    sistema = metricas['sistema']
    if sistema['solicitudes_atribuidas'] >= p['min_solicitudes_slo']:
        for campo, limite in [('latencia_p95_ms',p['p95_ms']),('tasa_5xx',p['tasa_5xx']),('tasa_4xx',p['tasa_4xx'])]:
            if sistema[campo] is not None and sistema[campo] > limite:
                add('sistema',campo,sistema[campo],limite,'mínimo 20 solicitudes del lote','alta','operación de la plataforma','Revisar disponibilidad, capacidad y errores; evaluar respaldo.')
    return alertas, disparar


# Protocolo independiente: no altera las referencias históricas monitoreo-1.
PROTOCOLO_ETICA = {
    'version': 'etica-operativa-1', 'plan': 'oulad-2014j-control-v1',
    'atributo': 'disability', 'grupos': ['N', 'Y', 'sin_dato'],
    'min_n': 200, 'min_fail': 20, 'min_no_fail': 20,
    'brecha_cobertura': 0.05, 'brecha_fpr': 0.03, 'lotes_consecutivos': 2,
    'comparacion': 'Diferencias absolutas Y-N a igual política, sobre cohortes base del día 14; denominadores completos y cupos por edición.',
    'interpretacion': 'Umbrales de revisión de prototipo, no límites legales ni aprobación institucional. Cinco puntos de cobertura son cinco Fail adicionales sin propuesta por cada cien Fail; tres de FPR son tres propuestas adicionales por cada cien no-Fail.',
    'limitacion': 'Resultados descriptivos del benchmark 2014J ya inspeccionado; sin intervalos de confianza ni inferencia causal. Matrículas de una persona no son independientes. Diferencias pueden reflejar prevalencia y composición de módulos.',
    'supervision': 'Tutor revisa necesidades, accesibilidad, información insuficiente y contactos previos. Estudiante conserva canales de apoyo y puede solicitar revisión. No sanciones ni exclusión por falta de actividad o por grupo.',
}


def evaluar_retirada(evento, historia=()):
    """Recomendaciones auditables; solo el fallo de carga activa el respaldo local.

    La suspensión por desempeño/equidad requiere decisión del responsable y
    operar el interruptor. No cambia aliases ni modifica eventos históricos.
    """
    p=PROTOCOLO_ETICA;out=[]
    def add(regla,accion,responsable):
        out.append({'regla':regla,'accion':accion,'responsable':responsable,'requiere_revision_humana':True})
    if evento.get('errores_contrato',0)>0:
        add('calidad','Bloquear el lote inválido y corregir fuente; no inferir ni usar el respaldo para eludir el contrato.','equipo de datos')
    if evento.get('modelo_disponible') is False or evento.get('artefacto_integro') is False:
        add('integridad_disponibilidad','Usar respaldo administrativo marcado y revisión humana; revisar Registry, firma e integridad antes de reactivar.','responsable del modelo y operación')
    clave=lambda e:(e['dia_revision'],e['dia_prediccion'],e['lote_id'])
    anteriores=sorted([e for e in historia if e['corte']==evento['corte'] and e['cohorte_id']!=evento['cohorte_id'] and clave(e)<clave(evento)],key=clave)
    previo=anteriores[-1] if anteriores else None
    def brecha(e):
        return (e.get('equidad_evaluable') is True and
                (abs(e['brecha_cobertura'])>p['brecha_cobertura']+1e-12 or abs(e['brecha_fpr'])>p['brecha_fpr']+1e-12))
    if brecha(evento):
        if previo and brecha(previo):
            add('equidad_persistente','Suspender priorización automática en lotes nuevos y pasar a revisión administrativa; investigar accesibilidad, composición y errores antes de reactivar.','responsable académico y equipo del modelo')
        else:add('equidad_revision','Revisar diferencias por edición, necesidades y accesibilidad; no ajustar umbrales con este mismo benchmark.','responsable académico')
    def inferior(e):
        a,b=e.get('tp_modelo'),e.get('tp_estatico')
        k,j=e.get('cupos_modelo'),e.get('cupos_estatico')
        f,g=e.get('fail_base_modelo'),e.get('fail_base_estatico')
        comparables=all(type(v) is int and v>=0 for v in [a,b,k,j,f,g])
        return (comparables and f==g and f>0 and k==j and max(a,b)<=min(k,f)
                and e.get('etiquetas_completas') is True and e.get('reentrenamiento_evaluado') is True and a<b)
    if inferior(evento) and previo and inferior(previo):
        add('negocio_inferior','Retirar ranking del modelo de lotes nuevos y operar respaldo con revisión humana; revisar utilidad frente al estático.','responsable académico y del modelo')
    def error_sistema(e):
        return e.get('solicitudes',0)>=20 and e.get('tasa_5xx') is not None and e['tasa_5xx']>0.01
    if error_sistema(evento) and previo and error_sistema(previo):
        add('sistema_persistente','Restaurar servicio y evaluar respaldo; si la API no está disponible, pausar despachos y realizar revisión manual fuera del servicio.','operación de la plataforma')
    return out
