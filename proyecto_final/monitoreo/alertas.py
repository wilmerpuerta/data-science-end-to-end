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
