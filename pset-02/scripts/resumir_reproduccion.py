"""Genera Markdown de reproducción desde evidencia curada de la copia aislada."""
from pathlib import Path
import json
BASE=Path(__file__).resolve().parents[1]
def render():
    r=json.loads((BASE/'docs/reproduccion-limpia.json').read_text());assert r['status']=='ok'
    folder=BASE/'output/reproduction'/r['run_id']
    execution=json.loads((folder/'execution.json').read_text());v=json.loads((folder/'verification.json').read_text())
    assert execution['state']=='SUCCESS' and v['status']=='ok'
    assert execution['inputs']['force_reload'] and not execution['inputs']['retry_probe'] and not execution['inputs']['fail_after_raw']
    assert all(f['status']=='LOADED' for f in v['raw_files'])
    assert r['original_stack_restored'] and r['reproduction_stopped'] and all(s['returncode']==0 for s in r['steps'])
    assert r['export_files_unchanged']
    def n(x):return f'{x:,}'.replace(',','.')
    lines=['# Resultados de reproducción limpia','',
        'Generado por `python3 pset-02/scripts/resumir_reproduccion.py` desde informes reales.','',
        f"**SUCCESS** en el proyecto aislado `{r['project_name']}`, ejecución `{r['execution_id']}`. Fecha de comprobación UTC: {r['checked_at_utc']}.",'',
        '## Entorno comprobado','',
        f"Se exportaron {r['exported_files']} archivos versionables a otra carpeta. No se copiaron entornos, .local, secretos ni salidas de ejecución del PSet 2. Se generaron contraseñas locales nuevas y se usaron puertos {r['kestra_port']}/{r['management_port']}, volúmenes PostgreSQL/Kestra nuevos y estado de flujos nuevo.",'',
        'Las tres imágenes propias se reconstruyeron con --no-cache. Se conservaron las capas base Docker fijadas por digest. Los cinco CSV y los archivos privados Snowflake se referenciaron externamente; las claves y la frase no se copiaron al árbol exportado. La cuenta, rol, warehouse y esquemas Snowflake existentes se reutilizaron.','',
        '## Resultado de la cadena','',
        '| Etapa | Evidencia |','|---|---|',
        f"| Raw | Cinco fuentes LOADED: {n(r['raw_rows'])} filas reconciliadas; recarga real, no NOOP |",
        f"| dbt | {r['dbt_models_succeeded']} modelos y {r['dbt_tests_passed']} pruebas aprobadas |",
        f"| Spark/OBT | {n(r['obt_rows'])} filas y {r['obt_columns']} columnas publicadas |",
        f"| Tiempo y joins | Cuatro cortes, {r['future_perturbation_tests_passed']} perturbaciones futuras y lectura de vuelta completa aprobadas |",
        '| Comparación | Las cuatro huellas de contenido coinciden con la ejecución anterior |',
        '| Cierre local | Reproducción detenida y stack principal restaurado con espera de salud |','',
        '| Corte | Filas OBT | Sin actividad registrada |','|---|---:|---:|']
    for part in v['per_cutoff']:lines.append(f"| {part['cutoff_day']} | {n(part['rows'])} | {n(part['without_recorded_activity'])} |")
    lines += ['',
        'No se inyectaron fallos en esta reproducción: se ejecutó el camino normal con force_reload=true. Las pruebas de detención y retry permanecen documentadas en la ejecución integral anterior. Los datos de la instancia original de Kestra se conservaron en sus volúmenes.','',
        '## Huellas y alcance','',
        f"Exportación: `{r['export_sha256']}`. Código de la instantánea: `{r['code_sha256']}`.",'',
        'La prueba es una exportación limpia desde el árbol de trabajo, no un clon remoto. No se inició una cuenta Snowflake vacía ni un daemon Docker sin imágenes base. Las huellas identifican la instantánea probada; los informes y documentación de cierre se agregan después. No se afirma compatibilidad ARM, exactitud externa del dataset ni costo monetario medido.','',
        f"Evidencia: [resumen JSON](reproduccion-limpia.json), [manifiesto de exportación](../output/reproduction/{r['run_id']}/export-manifest.json), [ejecución](../output/reproduction/{r['run_id']}/execution.json), [Raw](../output/reproduction/{r['run_id']}/raw.json), [verificación](../output/reproduction/{r['run_id']}/verification.json), [dbt](../output/reproduction/{r['run_id']}/dbt.json), [Spark](../output/reproduction/{r['run_id']}/spark.json), [procedimiento](reproduccion-limpia.md).",'',
        'Memo técnico generado: [fuente y exportación](memo-tecnico.md), posterior a la instantánea probada. Revisión local del paquete completada: [informe](revision-paquete.md). Publicación GitHub pendiente de indicación del autor. El consumo monetario continúa sin cuantificar. No hubo entrenamiento ni cambios de alcance metodológico del PSet 1.','']
    return '\n'.join(lines)
if __name__=='__main__':
    out=BASE/'docs/reproduccion-resultados.md';out.write_text(render());print('Generado docs/reproduccion-resultados.md')
