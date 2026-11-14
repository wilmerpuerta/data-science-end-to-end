"""Cierre Kestra: reconcilia exclusivamente informes agregados de esta ejecución."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re
p=argparse.ArgumentParser();p.add_argument('--execution-id',required=True);p.add_argument('--raw-execution-id',required=True)
p.add_argument('--source-file',required=True);a=p.parse_args()
assert all(re.fullmatch('[A-Za-z0-9_-]{1,100}',v) for v in [a.execution_id,a.raw_execution_id])
folder=Path('/workspace/pipeline')/a.execution_id;folder.mkdir(parents=True,exist_ok=True)
report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'execution_id':a.execution_id,'status':'failed'}
try:
    manifest=json.loads(Path('/datasets/manifest.json').read_text())
    assert a.source_file=='all' or a.source_file in manifest['files']
    paths=list(Path('/workspace/output').glob(a.raw_execution_id+'_*.json'))
    raw=max((json.loads(f.read_text()) for f in paths),key=lambda r:r['finished_at_utc'])
    assert raw['run_id']==a.raw_execution_id and raw['status']=='ok' and raw['mode']=='load'
    selected=list(manifest['files']) if a.source_file=='all' else [a.source_file]
    assert {r['file'] for r in raw['files']}==set(selected)
    for r in raw['files']:
        assert r['status'] in ['NOOP','LOADED']
        assert r['rows']==r['unique_source_rows']==manifest['files'][r['file']]['rows'] and r['other_checksums']==0
    dbt=json.loads((folder/'dbt.json').read_text());spark=json.loads((folder/'spark.json').read_text())
    assert dbt['execution_id']==spark['execution_id']==a.execution_id
    assert dbt['status']==spark['status']=='ok'
    assert dbt['results'] and all(r['status'] in ['success','pass'] for r in dbt['results'])
    assert dbt['models_succeeded']==23 and dbt['tests_passed']==168
    assert raw['finished_at_utc']<=dbt['started_at_utc']<dbt['finished_at_utc']<=spark['started_at_utc']<spark['finished_at_utc']
    assert spark['published'] and spark['population_key_sets_equal'] and spark['readback_all_columns_equal']
    assert spark['gold_source_sha256_verified'] and spark['temporal_tests_passed']==4
    assert spark['source_manifest_sha256']==hashlib.sha256(Path('/datasets/manifest.json').read_bytes()).hexdigest()
    contract=json.loads(Path('/workspace/reference/feature-contract.json').read_text())
    assert spark['output_columns']==contract['output_columns']
    assert not set(contract['forbidden_columns']) & set(spark['output_columns'])
    assert spark['rows']==spark['unique_keys']==sum(r['rows'] for r in spark['per_cutoff'])
    golden={(r['dataset'],r['metric']):r['value'] for r in dbt['quality']['gold']}
    audit=json.loads(Path('/workspace/reference/audit.json').read_text())['populations']['cuts']
    for r in spark['per_cutoff']:
        day=r['cutoff_day'];assert r['future_perturbation_unchanged']
        assert r['rows']==golden[f'eligibility_day_{day}','expected_enrollments']==audit[str(day)]['N']
        assert r['without_recorded_activity']==audit[str(day)]['without_recorded_activity']
    report.update(status='ok',raw_execution_id=a.raw_execution_id,raw_files=[{'file':r['file'],'status':r['status'],'rows':r['rows']} for r in raw['files']],
        raw_selected_rows=sum(r['rows'] for r in raw['files']),dbt_tests_passed=dbt['tests_passed'],dbt_models_succeeded=dbt['models_succeeded'],
        spark_run_id=spark['run_id'],obt_rows=spark['rows'],obt_columns=len(spark['output_columns']),
        obt_unique_keys=spark['unique_keys'],stage_order_verified=True,temporal_tests_passed=4,readback_all_columns_equal=True,
        content_sha256_by_cutoff=spark['content_sha256_by_cutoff'],per_cutoff=spark['per_cutoff'])
except Exception as e:report.update(error_class=type(e).__name__)
(folder/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['raw_files','content_sha256_by_cutoff','per_cutoff']},ensure_ascii=False))
if report['status']!='ok':raise SystemExit(1)
