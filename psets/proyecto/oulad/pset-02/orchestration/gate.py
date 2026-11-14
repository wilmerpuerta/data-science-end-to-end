"""Prueba controlada después de Raw y antes de cualquier transformación."""
import argparse,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--execution-id',required=True)
p.add_argument('--retry-probe',action='store_true');p.add_argument('--fail-after-raw',action='store_true');a=p.parse_args()
assert re.fullmatch('[A-Za-z0-9_-]{1,100}',a.execution_id)
if a.fail_after_raw:raise SystemExit('Fallo permanente inyectado después de Raw; no iniciar dbt/Spark.')
if a.retry_probe:
    marker=Path('/workspace/pipeline/.retry-probes')/a.execution_id;marker.parent.mkdir(parents=True,exist_ok=True)
    try:
        with marker.open('x') as f:f.write('controlled_failure\n')
    except FileExistsError:pass
    else:raise SystemExit('Fallo transitorio inyectado una vez antes de dbt/Spark.')
print('Gate OK; transformaciones autorizadas por flujo.')
