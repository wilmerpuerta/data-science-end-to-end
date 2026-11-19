"""Actualiza evidencia canónica únicamente desde un flujo integral SUCCESS verificado."""
from pathlib import Path
import argparse,json,re
BASE=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('execution_id');a=p.parse_args()
    assert re.fullmatch('[A-Za-z0-9_-]{1,100}',a.execution_id)
    folder=BASE/'output/pipeline'/a.execution_id
    execution=json.loads((folder/'execution.json').read_text());verification=json.loads((folder/'verification.json').read_text())
    assert execution['state']=='SUCCESS' and verification['status']=='ok'
    assert verification['execution_id']==execution['execution_id']==a.execution_id
    dbt=json.loads((folder/'dbt.json').read_text());spark=json.loads((folder/'spark.json').read_text())
    assert dbt['status']==spark['status']=='ok' and spark['published']
    report={'checked_at_utc':dbt['build_checked_at_utc'],'action':'build-gold','status':'ok','returncode':0,
            'dbt_core':'1.10.13','dbt_snowflake':'1.10.2','scope':'Bronze, Silver y Gold desde Kestra',
            'pipeline_execution_id':a.execution_id,
            **{k:dbt[k] for k in ['elapsed_seconds','results','models_succeeded','tests_passed']}}
    def write(name,value):(BASE/'docs'/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    write('dbt-build-gold.json',report)
    for layer in ['bronze','silver','gold']:
        write('calidad-'+layer+'.json',{'checked_at_utc':dbt['quality_checked_at_utc'][layer],
              'action':'quality-export' if layer=='bronze' else 'quality-export-'+layer,'status':'ok','returncode':0,
              'dbt_core':'1.10.13','dbt_snowflake':'1.10.2','pipeline_execution_id':a.execution_id,'metrics':dbt['quality'][layer]})
    write('obt-verificacion.json',spark)
    write('pipeline-verificacion.json',{'execution':execution,'verification':verification})
    print('Evidencia canónica actualizada desde '+a.execution_id+'; regenerar resúmenes Markdown.')
if __name__=='__main__':main()
