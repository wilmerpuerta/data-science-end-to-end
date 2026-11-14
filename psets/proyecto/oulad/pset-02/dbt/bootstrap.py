"""Entrypoint interno: secretos en memoria; artefactos completos solo en .local."""
import json, logging, os, subprocess, sys
from pathlib import Path
logging.disable(logging.CRITICAL)

def main():
    private=json.loads(Path('/run/secrets/snowflake_connection.json').read_text())
    if private.get('schema_version')!=1:raise ValueError('config_version')
    os.environ['DBT_ENV_SECRET_ACCOUNT']=private['account']
    os.environ['DBT_ENV_SECRET_PRIVATE_KEY_PASSPHRASE']=private['private_key_passphrase']
    os.environ['DBT_LOG_PATH']='/workspace/artifacts/logs'
    os.environ['DBT_TARGET_PATH']='/workspace/artifacts/target'
    os.environ['DBT_SEND_ANONYMOUS_USAGE_STATS']='false'
    exports={'quality-export':('BRONZE','DQ_BRONZE_PROFILE'),
             'quality-export-silver':('SILVER','DQ_SILVER_PROFILE'),
             'quality-export-gold':('GOLD','DQ_GOLD_PROFILE')}
    if len(sys.argv)==2 and sys.argv[1] in exports:
        schema,profile=exports[sys.argv[1]]
        import snowflake.connector
        with snowflake.connector.connect(account=private['account'], user='PSET2_SVC',
            role='PSET2_PIPELINE', database='PSET2_OULAD', schema=schema, warehouse='PSET2_WH',
            authenticator='SNOWFLAKE_JWT', private_key_file='/run/secrets/snowflake_key.p8',
            private_key_file_pwd=private['private_key_passphrase'],login_timeout=30,network_timeout=120,
            session_parameters={'QUERY_TAG':'pset02_dq_export','STATEMENT_TIMEOUT_IN_SECONDS':600}) as conn:
            rows=conn.cursor().execute('SELECT DATASET, METRIC, VALUE, DENOMINATOR FROM '+profile+' ORDER BY DATASET, METRIC').fetchall()
        print(json.dumps([{'dataset':r[0], 'metric':r[1], 'value':int(r[2]),
                          'denominator':None if r[3] is None else int(r[3])} for r in rows]))
        return 0
    allowed={'debug':['debug','--connection'], 'parse':['parse'],
             'build-bronze':['build','--select','tag:bronze'],
             'test-bronze':['test','--select','tag:bronze'],
             'build-silver':['build','--select','tag:bronze','tag:silver'],
             'test-silver':['test','--select','tag:silver'],
             'build-gold':['build','--select','tag:bronze','tag:silver','tag:gold'],
             'test-gold':['test','--select','tag:gold']}
    if len(sys.argv)!=2 or sys.argv[1] not in allowed:raise ValueError('unknown_command')
    return subprocess.call(['dbt','--no-use-colors','--no-partial-parse']+allowed[sys.argv[1]])

if __name__=='__main__':
    try:sys.exit(main())
    except Exception:sys.exit('Error de cliente; no se imprimen mensajes con datos privados.')
