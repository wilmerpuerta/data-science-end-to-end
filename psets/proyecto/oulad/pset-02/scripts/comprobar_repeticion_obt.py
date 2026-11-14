"""Compara contenido canónico y población de dos construcciones OBT reales."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json
BASE=Path(__file__).resolve().parents[1]
CHECKPOINT=BASE/'output/spark/repetition-baseline.json'
def current():
    r=json.loads((BASE/'docs/obt-verificacion.json').read_text())
    assert r['status']=='ok' and r['published'] and r['readback_all_columns_equal']
    assert r['population_key_sets_equal'] and r['temporal_tests_passed']==4
    return {k:r[k] for k in ['run_id','checked_at_utc','rows','unique_keys','per_cutoff',
                            'content_sha256_by_cutoff','output_columns','source_manifest_sha256']}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['checkpoint','verify']);a=p.parse_args()
    now=current()
    if a.action=='checkpoint':
        CHECKPOINT.parent.mkdir(parents=True,exist_ok=True);CHECKPOINT.write_text(json.dumps(now,indent=2)+'\n')
        print('Checkpoint OBT guardado. Repetir build-obt antes de verify.');return
    before=json.loads(CHECKPOINT.read_text())
    assert before['run_id']!=now['run_id'] and before['checked_at_utc']<now['checked_at_utc']
    checks={k:before[k]==now[k] for k in ['rows','unique_keys','per_cutoff','content_sha256_by_cutoff','output_columns','source_manifest_sha256']}
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'status':'ok' if all(checks.values()) else 'failed',
            'first_run_id':before['run_id'],'second_run_id':now['run_id'],'checks':checks,
            'rows_per_run':now['rows'],'cutoff_fingerprints_compared':len(now['content_sha256_by_cutoff']),
            'scope':'SHA-256 por corte de filas JSON canónicas ordenadas, esquema, población y métricas iguales; lectura de vuelta completa en ambos runs.'}
    (BASE/'docs/repeticion-obt.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False));assert report['status']=='ok'
if __name__=='__main__':main()
