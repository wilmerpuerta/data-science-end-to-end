"""Genera el resumen Markdown desde los informes agregados de dbt y calidad."""
from pathlib import Path
import json
BASE=Path(__file__).resolve().parents[1]

def render():
    build=json.loads((BASE/'docs/dbt-build-bronze.json').read_text())
    quality=json.loads((BASE/'docs/calidad-bronze.json').read_text())
    assert build['status']==quality['status']=='ok'
    nodes=build['results'];tests=[n for n in nodes if n['unique_id'].startswith('test.')]
    assert tests and all(n['status']=='pass' and n['failures']==0 for n in tests)
    m={(x['dataset'],x['metric']):x for x in quality['metrics']}
    def number(n):return f'{n:,}'.replace(',','.')
    def value(d,k):return number(m[d,k]['value'])
    def ratio(d,k):
        r=m[d,k];return value(d,k)+' / '+number(r['denominator'])+f" ({100*r['value']/r['denominator']:.2f} %)".replace('.',',')
    lines=['# Resultados de calidad y Bronze', '',
        'Archivo generado por `python3 pset-02/scripts/resumir_bronze.py`; no editar cifras manualmente.', '',
        f"Build: {build['checked_at_utc']}. Exportación de métricas: {quality['checked_at_utc']}. Ambos en UTC.", '',
        f"Resultado: cinco vistas Staging y una tabla agregada construidas; **{len(tests)} tests aprobados, cero fallos**. Duración dbt: {build['elapsed_seconds']:.2f} s, excluye arranque del contenedor y exportación. Raw no se modificó.", '',
        '| Fuente / vista | Filas conservadas |', '|---|---:|']
    for d,label in [('student_info','studentInfo'),('registration','studentRegistration'),('courses','courses'),('vle','vle'),('student_vle','studentVle')]:
        lines.append(f"| {label} | {value(d,'rows')} |")
    lines += ['',f"Las {value('student_info','rows')} matrículas corresponden a {value('student_info','unique_people')} personas distintas. Total de clics: **{value('student_vle','total_clicks')}**. Las claves de matrícula y recurso son únicas en sus tablas maestras; no hay huérfanos en las relaciones probadas ni errores de conversión.", '',
        '| Problema o condición | Evidencia | Acción en esta etapa | Justificación / siguiente decisión |', '|---|---|---|---|',
        f"| IMD vacío | {ratio('student_info','missing_imd')} | NULL en Bronze, sin imputación | Es un atributo desconocido; una imputación aprendida se ajustará solo con entrenamiento. |",
        f"| Registro sin fecha | {ratio('registration','missing_registration')} | Conservar matrícula y marcar ausencia | El contrato posterior exige registro conocido <= 0 para población inicial; la exclusión se contará al construir elegibilidad. |",
        f"| Registro posterior al inicio | {ratio('registration','late_registration')} | Conservar fecha | No es error de tipo; queda fuera de población inicial por la regla del proyecto. |",
        f"| Sin fecha de retiro registrada | {ratio('registration','no_recorded_withdrawal')} | Conservar NULL | No equivale a un faltante genérico ni prueba que nunca hubo retiro. No inventar una fecha. |",
        f"| Resultado Withdrawn sin fecha de retiro | {ratio('outcomes','withdrawn_without_date')} | Señalar inconsistencia; no inferir fecha con la etiqueta | Limita la reconstrucción de elegibilidad histórica. Tratamiento y sensibilidad deben documentarse; no usar resultado futuro como predictor. |",
        f"| Otro resultado con fecha de retiro | {ratio('outcomes','other_outcome_with_date')} | Conservar ambos datos y señalar conflicto | No podemos corregir el registro institucional desde estos CSV. |",
        f"| Semanas del recurso ausentes | week_from: {ratio('vle','missing_week_from')}; week_to: {ratio('vle','missing_week_to')} | Mantener NULL | No usar estas semanas como prueba de cobertura ni sustituir por semana cero. |",
        f"| Clave matrícula–recurso–día repetida | {ratio('student_vle','repeated_natural_key_excess')} filas adicionales respecto de claves distintas | Conservar todas las filas | La futura agregación diaria debe reconciliar clics; repetición no demuestra por sí sola error de captura. |",
        f"| Valores de evento idénticos, incluido sum_click | {ratio('student_vle','repeated_exact_value_excess')} filas adicionales respecto de valores distintos | Sin deduplicación automática | No hay identificador del evento original ni evidencia para afirmar cuál copia sobra. |",
        f"| Actividad anterior al inicio | {ratio('student_vle','prestart_rows')}; días {value('student_vle','min_day')} a {value('student_vle','max_day')} en el conjunto | Conservar días negativos | Se tratará como antecedente separado de ventanas quincenales. |", '',
        'Se observaron cero clics negativos, cero filas con sum_click=0, cero retiros anteriores al registro conocido, cero intervalos de semanas invertidos y cero duraciones no positivas. Ausencia de estos problemas no acredita exactitud externa.', '',
        'La auditoría global encuentra **2.195.960** filas adicionales por clave diaria. El PSet 1 comunicó una cota inferior de 2.195.910 dentro de bloques; los 50 casos adicionales proceden de comprobar el archivo completo. Se conserva el informe histórico del PSet 1 como evidencia de su alcance.', '',
        'Los tests validan reglas declaradas, no que todos los problemas de negocio estén resueltos. Las anomalías anteriores se conservan explícitamente en Bronze; la consolidación y las banderas Silver se documentan en [silver.md](silver.md). Gold se documenta en [gold.md](gold.md). La OBT se documenta en [obt-spark.md](obt-spark.md). La orquestación se documenta en [orquestacion-integral.md](orquestacion-integral.md). No hay entrenamiento.', '',
        'Fuentes reproducibles: [build dbt](dbt-build-bronze.json), [métricas agregadas](calidad-bronze.json), [guía y comandos](calidad-bronze.md).', '']
    # La comparación histórica es específica de la versión auditada.
    assert m['student_vle','repeated_natural_key_excess']['value']==2195960
    return '\n'.join(lines)

if __name__=='__main__':
    out=BASE/'docs/calidad-bronze-resultados.md';out.write_text(render());print('Generado '+str(out.relative_to(BASE)))
