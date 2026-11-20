"""Verifica cron activo y una ejecución Schedule real; no crea ejecuciones ni backfills."""
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import argparse, base64, hashlib, json, re, shlex, urllib.request, urllib.error

BASE = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execution-id', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', args.execution_id):
        parser.error('Identificador de ejecución inválido.')
    settings = dict(line.split('=', 1) for line in (BASE / '.env.infra').read_text().splitlines()
                    if line and not line.startswith('#'))
    password = shlex.split(settings['PSET2_KESTRA_PASSWORD'])[0]
    auth = base64.b64encode(('admin@psets.local:' + password).encode()).decode()
    port = int(settings.get('PSET2_KESTRA_PORT', '18090'))
    assert 1024 <= port <= 65535

    def request(path):
        req = urllib.request.Request(f'http://127.0.0.1:{port}/api/v1/main' + path,
                                     headers={'Authorization': 'Basic ' + auth})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read())

    flow = request('/flows/pset2.oulad/oulad_pipeline')
    parent = next(t for t in flow['triggers'] if t['id'] == 'revision_integral')
    assert parent['type'] == 'io.kestra.plugin.core.trigger.Schedule'
    assert parent['cron'] == '0 9 1,15 * *' and parent['timezone'] == 'America/Guayaquil'
    assert not flow.get('disabled', False) and not parent.get('disabled', False)
    raw = request('/flows/pset2.oulad/oulad_raw')
    assert all(t.get('disabled', False) for t in raw.get('triggers', []))
    trigger = next(t for t in request('/triggers/pset2.oulad/oulad_pipeline')['results']
                   if t['triggerId'] == 'revision_integral')
    assert not trigger.get('disabled', False)
    execution = request('/executions/' + args.execution_id)
    assert execution['namespace'] == 'pset2.oulad' and execution['flowId'] == 'oulad_pipeline'
    assert execution['state']['current'] == 'SUCCESS', 'Esperar SUCCESS antes de cerrar la evidencia.'
    origin = execution.get('trigger') or {}
    assert origin.get('id') == 'revision_integral' and origin.get('type') == parent['type']
    variables = origin['variables']
    def parse(s): return datetime.fromisoformat(s.replace('Z', '+00:00'))
    scheduled = parse(variables['date']).astimezone(ZoneInfo('America/Guayaquil'))
    assert scheduled.day in {1, 15} and (scheduled.hour, scheduled.minute, scheduled.second) == (9, 0, 0)
    upcoming = parse(trigger['nextExecutionDate']).astimezone(ZoneInfo('America/Guayaquil'))
    assert upcoming.day in {1, 15} and (upcoming.hour, upcoming.minute) == (9, 0)
    assert upcoming > datetime.now(timezone.utc), 'La siguiente fecha debe estar en el futuro.'
    labels = {x['key']: x['value'] for x in execution.get('labels', [])}
    is_backfill = labels.get('tipo_prueba') == 'recuperacion_calendario'
    folder = BASE / 'docs/evidencia/pipeline' / args.execution_id
    verification = json.loads((folder / 'verification.json').read_text())
    assert verification['status'] == 'ok' and verification['execution_id'] == args.execution_id
    assert verification['dbt_models_succeeded'] == 23 and verification['dbt_tests_passed'] == 168
    assert verification['obt_rows'] == 108277 and verification['obt_columns'] == 35
    assert verification['stage_order_verified'] and verification['temporal_tests_passed'] == 4
    tasks = [{'task_id': t['taskId'], 'state': t['state']['current'],
              'attempts': len(t.get('attempts', []))} for t in execution['taskRunList']]
    assert [t['task_id'] for t in tasks] == ['raw', 'gate', 'dbt', 'spark', 'verificar']
    assert all(t['state'] == 'SUCCESS' for t in tasks)
    report = {'status': 'ok', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'flow': 'pset2.oulad/oulad_pipeline', 'flow_revision': flow['revision'],
              'execution_flow_revision': execution['flowRevision'],
              'trigger_id': 'revision_integral', 'trigger_type': parent['type'],
              'cron': parent['cron'], 'timezone': parent['timezone'], 'enabled': True,
              'raw_independent_schedule_enabled': False,
              'execution_id': args.execution_id, 'state': execution['state']['current'],
              'scheduled_date': scheduled.isoformat(),
              'actual_start_utc': execution['state']['startDate'],
              'actual_end_utc': execution['state']['endDate'],
              'next_execution_date': upcoming.isoformat(), 'backfill_calendar': is_backfill,
              'trigger_variables': {k: variables[k] for k in ['date', 'previous', 'next']},
              'tasks': tasks, 'raw_selected_rows': verification['raw_selected_rows'],
              'dbt_models_succeeded': verification['dbt_models_succeeded'],
              'dbt_tests_passed': verification['dbt_tests_passed'],
              'obt_rows': verification['obt_rows'], 'obt_columns': verification['obt_columns'],
              'obt_hashes_match_previous': verification['content_sha256_by_cutoff'] ==
                  json.loads((BASE / 'docs/obt-verificacion.json').read_text())['content_sha256_by_cutoff'],
              'pipeline_source_sha256': hashlib.sha256((BASE / 'kestra/oulad_pipeline.yml').read_bytes()).hexdigest(),
              'scope': 'Ejecución real creada por Schedule al recuperar la fecha del calendario mediante backfill; '
                       'no se afirma que el equipo estuviera encendido en esa fecha ni que se observara su llegada en tiempo real.'
                       if is_backfill else 'Ejecución real creada por Schedule; origen conservado desde la API.',
              'next_run_requires': 'Equipo, Docker, Kestra y credenciales/recursos cloud disponibles.',
              'api_base': f'http://localhost:{port}',
              'evidence': f'docs/evidencia/pipeline/{args.execution_id}/verification.json'}
    assert report['obt_hashes_match_previous']
    previous = folder / 'antes-reintento-execution.json'
    if previous.is_file():
        failed = json.loads(previous.read_text())
        assert failed['state'] == 'FAILED' and tasks[-1]['attempts'] == 2
        assert all(t['attempts'] == 1 for t in tasks[:-1])
        report['recovery'] = {'initial_state': failed['state'],
                              'initial_failed_task': 'verificar', 'error_class': 'OSError EIO',
                              'action': 'Referencia audit.json repuesta con bytes idénticos a Git; remonte de Kestra y restart de la tarea fallida.',
                              'manual_restart': True, 'upstream_tasks_repeated': False,
                              'evidence': f'docs/evidencia/pipeline/{args.execution_id}/antes-reintento-execution.json'}
    (BASE / 'docs/calendario-verificacion.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'cron', 'enabled', 'execution_id',
                                            'scheduled_date', 'backfill_calendar', 'next_execution_date']}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as error:
        raise SystemExit(f'Kestra HTTP {error.code}; no se imprime la respuesta ni la autenticación.')
    except urllib.error.URLError:
        raise SystemExit('Kestra no disponible. Revisar infraestructura antes de verificar el calendario.')
