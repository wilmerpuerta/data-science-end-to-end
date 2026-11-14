"""Genera evidencia de orden, detención, retry y coherencia del flujo integral."""
from pathlib import Path
from datetime import datetime,timezone
import json
BASE=Path(__file__).resolve().parents[1]

def evidence():
    folders=BASE/'output/pipeline'
    executions=[json.loads(p.read_text()) for p in folders.glob('*/execution.json')]
    # Este informe certifica el caso de retry; un SUCCESS normal posterior
    # no sustituye la evidencia del ensayo controlado.
    success=max((e for e in executions if e['state']=='SUCCESS' and e['inputs']['retry_probe']),key=lambda e:e['checked_at_utc'])
    failure=max((e for e in executions if e['state']=='FAILED' and e['inputs']['fail_after_raw']),key=lambda e:e['checked_at_utc'])
    assert not failure['inputs']['force_reload'] and failure['inputs']['source_file']=='all'
    failed_tasks={t['task_id']:t for t in failure['tasks']}
    assert set(failed_tasks)=={'raw','gate'} and failed_tasks['raw']['state']=='SUCCESS' and failed_tasks['gate']['state']=='FAILED'
    failed_folder=folders/failure['execution_id']
    assert not (failed_folder/'dbt.json').exists() and not (failed_folder/'spark.json').exists()
    failed_raw=max((json.loads(p.read_text()) for p in (BASE/'output/raw').glob(failure['raw_execution_id']+'_*.json')),key=lambda r:r['finished_at_utc'])
    assert failed_raw['status']=='ok' and len(failed_raw['files'])==5 and all(r['status']=='NOOP' for r in failed_raw['files'])
    folder=folders/success['execution_id'];v=json.loads((folder/'verification.json').read_text())
    assert v['status']=='ok' and v['execution_id']==success['execution_id']
    tasks={t['task_id']:t for t in success['tasks']}
    expected=['raw','gate','dbt','spark','verificar']
    assert [t['task_id'] for t in success['tasks']]==expected and all(t['state']=='SUCCESS' for t in tasks.values())
    assert success['inputs']['retry_probe'] and tasks['gate']['attempts']==2
    for before,after in zip(expected,expected[1:]):
        assert datetime.fromisoformat(tasks[before]['finished_at'].replace('Z','+00:00'))<=datetime.fromisoformat(tasks[after]['started_at'].replace('Z','+00:00'))
    probe=json.loads((folder/'api-probe.json').read_text())
    for worker in ['dbt','spark']:
        assert all(probe['workers'][worker][k] for k in ['health_ok','arbitrary_command_rejected','invalid_request_started_no_job','duplicate_post_reused_job'])
        assert probe['workers'][worker]['attempt']==1
    return {'checked_at_utc':datetime.now(timezone.utc).isoformat(),'status':'ok','success_execution_id':success['execution_id'],
            'failure_execution_id':failure['execution_id'],'raw_execution_id':v['raw_execution_id'],
            'task_order':expected,'gate_attempts':tasks['gate']['attempts'],'dbt_tests_passed':v['dbt_tests_passed'],
            'dbt_models_succeeded':v['dbt_models_succeeded'],'obt_rows':v['obt_rows'],'obt_columns':v['obt_columns'],
            'stopped_after_injected_failure':True,'failure_raw_all_noop':True,'no_downstream_jobs_on_failure':True,
            'worker_api_contract_verified':True,'duplicate_requests_reused_jobs':True,'calendars_enabled':False,
            'scope':'Prueba de fallo permanente y retry inyectados; una cadena completa real. No se simula una caída real del proveedor.'}

def render(data):
    folder=BASE/'output/pipeline'/data['success_execution_id']
    execution=json.loads((folder/'execution.json').read_text());v=json.loads((folder/'verification.json').read_text())
    def number(n):return f'{n:,}'.replace(',','.')
    lines=['# Resultados de orquestación integral','',
           'Generado por `python3 pset-02/scripts/resumir_pipeline.py` desde informes de ejecuciones reales.','',
           f"**Kestra SUCCESS:** `{data['success_execution_id']}`. Raw → gate → dbt → Spark → verificación, sin intervención manual entre etapas.",'',
           '| Tarea | Estado | Intentos |','|---|---|---:|']
    for task in execution['tasks']:lines.append(f"| {task['task_id']} | {task['state']} | {task['attempts']} |")
    lines += ['',
        f"Raw, subflujo `{data['raw_execution_id']}`: cinco fuentes reconciliadas, {number(v['raw_selected_rows'])} filas (todas NOOP en esta ejecución). dbt construyó/revalidó {data['dbt_models_succeeded']} modelos y aprobó **{data['dbt_tests_passed']} pruebas**. Spark publicó **{number(data['obt_rows'])} filas y {data['obt_columns']} columnas**, con población, perturbaciones y lectura completa de vuelta aprobadas.",'',
        '**Recuperación controlada:** gate falló una vez antes de dbt/Spark y pasó al segundo intento. La ejecución completa terminó correctamente. La prueba no representa una caída real de Snowflake.','',
        f"**Detención controlada:** `{data['failure_execution_id']}` terminó FAILED después de Raw y gate; dbt, Spark y verificación no se iniciaron. Raw produjo cinco NOOP y no hubo publicación OBT desde ese flujo. No se presenta ese FAILED deliberado como una ejecución productiva exitosa.",'',
        '**API interna:** ambos ejecutores rechazaron campos de comando libre con HTTP 400 sin crear trabajos. Repetir POST con la misma ejecución reutilizó el mismo job_id/intento para dbt y Spark; cada uno se ejecutó una vez en la cadena exitosa.','',
        'Los calendarios padre y Raw permanecen desactivados. Un único flujo padre puede ejecutar a la vez; las operaciones manuales también deben respetar el escritor único. La atomicidad es por carga/modelo/publicación OBT, no una transacción de toda la cadena.','',
        f"Evidencia: [resumen JSON](pipeline-pruebas.json), [cierre canónico](pipeline-verificacion.json), [ejecución exitosa](../output/pipeline/{data['success_execution_id']}/execution.json), [verificación](../output/pipeline/{data['success_execution_id']}/verification.json), [prueba API](../output/pipeline/{data['success_execution_id']}/api-probe.json), [fallo controlado](../output/pipeline/{data['failure_execution_id']}/execution.json), [guía](orquestacion-integral.md).",'',
        'Reproducción desde exportación limpia verificada: [resultados](reproduccion-resultados.md). Memo técnico generado: [fuente y exportación](memo-tecnico.md). Revisión local del paquete completada: [informe](revision-paquete.md). Pendientes: cuantificación de costo monetario y publicación GitHub. No se ha publicado el repositorio ni activado el calendario.','']
    return '\n'.join(lines)

if __name__=='__main__':
    data=evidence();(BASE/'docs/pipeline-pruebas.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (BASE/'docs/pipeline-resultados.md').write_text(render(data));print('Generados pipeline-pruebas.json y pipeline-resultados.md.')
