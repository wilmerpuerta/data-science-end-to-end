"""Compara invariantes agregados de dos builds Silver reales y sus tests."""
from pathlib import Path
from datetime import datetime, timezone
import argparse,json
BASE=Path(__file__).resolve().parents[1]
CHECKPOINT=BASE/'output/silver/repetition-baseline.json'

def snapshot():
    build=json.loads((BASE/'docs/dbt-build-silver.json').read_text())
    quality=json.loads((BASE/'docs/calidad-silver.json').read_text())
    assert build['status']==quality['status']=='ok'
    assert build['action']=='build-silver'
    assert build['checked_at_utc'] < quality['checked_at_utc']
    assert build['tests_passed']>0
    assert all(r['status'] in ['success','pass'] for r in build['results'])
    return {'build_checked_at_utc':build['checked_at_utc'],'quality_checked_at_utc':quality['checked_at_utc'],
            'tests_passed':build['tests_passed'],'models_succeeded':build['models_succeeded'],
            'metrics':sorted(quality['metrics'],key=lambda x:(x['dataset'],x['metric']))}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['checkpoint','verify']);a=p.parse_args()
    current=snapshot()
    if a.action=='checkpoint':
        CHECKPOINT.parent.mkdir(parents=True,exist_ok=True)
        CHECKPOINT.write_text(json.dumps(current,indent=2)+'\n')
        print('Checkpoint agregado guardado. Repetir build-silver y quality-export-silver antes de verificar.');return
    before=json.loads(CHECKPOINT.read_text())
    assert before['build_checked_at_utc'] < current['build_checked_at_utc'],'Se requieren dos builds distintos.'
    checks={
        'aggregate_metrics_identical':before['metrics']==current['metrics'],
        'same_model_count':before['models_succeeded']==current['models_succeeded'],
        'same_passed_test_count':before['tests_passed']==current['tests_passed']}
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),
            'status':'ok' if all(checks.values()) else 'failed','checks':checks,
            'first_build_checked_at_utc':before['build_checked_at_utc'],
            'second_build_checked_at_utc':current['build_checked_at_utc'],
            'compared_metric_count':len(current['metrics']),
            'tests_passed_per_build':current['tests_passed'],
            'scope':'Invariantes agregados idénticos; tests de claves y reconciliación aprobados en ambos builds.'}
    (BASE/'docs/repeticion-silver.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
    assert report['status']=='ok'

if __name__=='__main__':main()
