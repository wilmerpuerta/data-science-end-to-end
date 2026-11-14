"""Gold -> features en Spark -> Snowflake. Nunca imprime credenciales o filas."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,logging,re,sys,time
from pyspark.sql import SparkSession,functions as F
from pyspark import StorageLevel
from pyspark.sql.types import DecimalType
from features import CUTOFFS,KEYS,STATIC,ACTIVITY,OUTPUT,population,build_features

logging.disable(logging.CRITICAL)
SOURCE='net.snowflake.spark.snowflake'
OUTPUT_DIR=Path('/workspace/output');ARTIFACTS=Path('/workspace/artifacts')
MARKER='pset2.obt.v1;'

def main():
    p=argparse.ArgumentParser();p.add_argument('--run-id',required=True)
    p.add_argument('--action',choices=['check-connection','build-obt'],required=True);args=p.parse_args()
    assert re.fullmatch('[a-f0-9]{32}',args.run_id)
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'action':args.action,
            'run_id':args.run_id,'status':'failed','published':False}
    phase='initialize';started=time.monotonic();spark=None;conn=None;stage=None;private={};key_text=''
    OUTPUT_DIR.mkdir(parents=True,exist_ok=True);ARTIFACTS.mkdir(parents=True,exist_ok=True)
    def progress(name,**values):
        nonlocal phase
        phase=name
        (OUTPUT_DIR/('progress_'+args.run_id+'.json')).write_text(json.dumps({'phase':name,**values})+'\n')
    try:
        private=json.loads(Path('/run/secrets/snowflake_connection.json').read_text())
        assert private['schema_version']==1
        from cryptography.hazmat.primitives import serialization
        key=serialization.load_pem_private_key(Path('/run/secrets/snowflake_key.p8').read_bytes(),password=private['private_key_passphrase'].encode())
        pem=key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()).decode()
        key_text=''.join(line for line in pem.splitlines() if not line.startswith('---'))
        options={'sfURL':private['account']+'.snowflakecomputing.com','sfUser':'PSET2_SVC',
                 'sfRole':'PSET2_PIPELINE','sfDatabase':'PSET2_OULAD','sfSchema':'ANALYTICS',
                 'sfWarehouse':'PSET2_WH','pem_private_key':key_text,'autopushdown':'off',
                 'query_tag':'pset02_spark_'+args.run_id,'use_parquet_in_write':'true'}
        spark=SparkSession.builder.appName('pset02-obt').config('spark.sql.session.timeZone','UTC').getOrCreate()
        spark.sparkContext.setLogLevel('OFF')
        def read(query):
            df=spark.read.format(SOURCE).options(**options).option('query',query).load()
            # IDs y contadores de esta copia caben en int64; evitar Decimal al operar con días.
            return df.select(*[F.col(f.name).cast('long').alias(f.name.lower()) if isinstance(f.dataType,DecimalType) and f.dataType.scale==0
                               else F.col(f.name).alias(f.name.lower()) for f in df.schema.fields])
        progress('connection')
        context=read('SELECT CURRENT_USER() AS U,CURRENT_ROLE() AS R,CURRENT_DATABASE() AS D,CURRENT_SCHEMA() AS S,CURRENT_WAREHOUSE() AS W').first()
        assert tuple(context)==('PSET2_SVC','PSET2_PIPELINE','PSET2_OULAD','ANALYTICS','PSET2_WH')
        report.update(spark_version=spark.version,scala_version='2.12.18',spark_connector='3.2.3-spark_3.5',
                      jdbc='4.4.1',session_context_verified=True,autopushdown=False)
        if args.action=='check-connection':
            report.update(status='ok',scope='Conexión real desde Spark y contexto esperado; sin escritura de tablas.')
            return report
        import snowflake.connector
        conn=snowflake.connector.connect(account=private['account'],user='PSET2_SVC',role='PSET2_PIPELINE',
            database='PSET2_OULAD',schema='ANALYTICS',warehouse='PSET2_WH',authenticator='SNOWFLAKE_JWT',
            private_key_file='/run/secrets/snowflake_key.p8',private_key_file_pwd=private['private_key_passphrase'],
            login_timeout=30,network_timeout=120,session_parameters={'QUERY_TAG':'pset02_obt_publish_'+args.run_id,'STATEMENT_TIMEOUT_IN_SECONDS':600})
        cur=conn.cursor()
        existing=cur.execute("SELECT COMMENT FROM PSET2_OULAD.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='ANALYTICS' AND TABLE_NAME='OBT_FEATURES'").fetchone()
        if existing and not (existing[0] or '').startswith(MARKER):raise RuntimeError('unmanaged_existing_target')
        manifest=json.loads(Path('/datasets/manifest.json').read_text())
        sources=[('DIM_ENROLLMENT','SOURCE_SHA256','studentInfo.csv'),
                 ('FACT_ENROLLMENT','REGISTRATION_SOURCE_SHA256','studentRegistration.csv'),
                 ('DIM_EDITION','SOURCE_SHA256','courses.csv'),('DIM_RESOURCE','SOURCE_SHA256','vle.csv'),
                 ('FACT_ACTIVITY_DAILY','SOURCE_SHA256','studentVle.csv')]
        for table,column,filename in sources:
            version=cur.execute('SELECT COUNT(DISTINCT '+column+'),MIN('+column+'),COUNT_IF('+column+' IS NULL) FROM PSET2_OULAD.GOLD.'+table).fetchone()
            assert version[0]==1 and version[1]==manifest['files'][filename]['sha256'] and version[2]==0
        report['gold_source_sha256_verified']=True
        progress('read_gold')
        def cached(query):
            df=read(query).persist(StorageLevel.DISK_ONLY);df.count();return df
        enrollment=cached('SELECT ENROLLMENT_KEY,ID_STUDENT,EDITION_KEY,DATE_REGISTRATION FROM PSET2_OULAD.GOLD.FACT_ENROLLMENT')
        withdrawals=cached('SELECT ENROLLMENT_KEY,DATE_UNREGISTRATION FROM PSET2_OULAD.GOLD.ENROLLMENT_WITHDRAWAL')
        context=cached('SELECT ENROLLMENT_KEY,CODE_MODULE,CODE_PRESENTATION,GENDER,REGION,HIGHEST_EDUCATION,IMD_BAND,AGE_BAND,NUM_OF_PREV_ATTEMPTS,STUDIED_CREDITS,DISABILITY,IS_IMD_MISSING FROM PSET2_OULAD.GOLD.DIM_ENROLLMENT')
        editions=cached('SELECT EDITION_KEY,MODULE_PRESENTATION_LENGTH FROM PSET2_OULAD.GOLD.DIM_EDITION')
        resources=cached('SELECT RESOURCE_KEY,ACTIVITY_TYPE FROM PSET2_OULAD.GOLD.DIM_RESOURCE')
        activity=cached('SELECT ENROLLMENT_KEY,RESOURCE_KEY,ID_SITE,ACTIVITY_DAY,CLICK_COUNT FROM PSET2_OULAD.GOLD.FACT_ACTIVITY_DAILY WHERE ACTIVITY_DAY<=56')
        report['activity_rows_extracted']=activity.count()
        expected=read('''SELECT E.ENROLLMENT_KEY,D.RELATIVE_DAY AS CUTOFF_DAY
            FROM PSET2_OULAD.GOLD.FACT_ENROLLMENT E
            JOIN PSET2_OULAD.GOLD.ENROLLMENT_WITHDRAWAL W ON E.ENROLLMENT_KEY=W.ENROLLMENT_KEY
            CROSS JOIN PSET2_OULAD.GOLD.DIM_RELATIVE_DAY D
            WHERE D.IS_OBSERVATION_CUTOFF AND E.DATE_REGISTRATION<=0
              AND (W.DATE_UNREGISTRATION IS NULL OR W.DATE_UNREGISTRATION>D.RELATIVE_DAY)''').persist(StorageLevel.DISK_ONLY)
        expected.count()
        work=ARTIFACTS/'work'/args.run_id;work.mkdir(parents=True,exist_ok=True)
        metrics=[];paths=[]
        for cutoff in CUTOFFS:
            progress('cutoff',cutoff_day=cutoff)
            eligible=population(enrollment,withdrawals,cutoff).persist(StorageLevel.DISK_ONLY)
            n=eligible.count()
            assert eligible.select('enrollment_key').distinct().count()==n
            features=build_features(eligible,activity,context,editions,resources,cutoff)
            path=str(work/('features_'+str(cutoff)))
            features.write.mode('errorifexists').parquet(path);paths.append(path)
            actual=spark.read.parquet(path)
            assert actual.columns==OUTPUT and actual.count()==n
            assert actual.select(*KEYS).distinct().count()==n
            ref=expected.filter(F.col('cutoff_day')==cutoff).select(*KEYS)
            assert actual.select(*KEYS).exceptAll(ref).count()==0 and ref.exceptAll(actual.select(*KEYS)).count()==0
            assert actual.filter((F.col('last_activity_day')>cutoff) | (F.col('active_days_current_14d')>14) |
                (F.col('clicks_through_cutoff') != F.col('clicks_prestart')+F.col('clicks_day_zero')+F.col('clicks_since_start'))).count()==0
            # Modificar todas las contribuciones posteriores e insertar un evento futuro.
            future=(activity.join(F.broadcast(eligible.select('enrollment_key')),'enrollment_key','inner').limit(1)
                    .withColumn('activity_day',F.lit(cutoff+1).cast('long')).withColumn('click_count',F.lit(999999999).cast('long')))
            assert future.count()==1
            perturbed=activity.withColumn('click_count',F.when(F.col('activity_day')>cutoff,F.lit(888888888)).otherwise(F.col('click_count'))).unionByName(future)
            alternative=build_features(eligible,perturbed,context,editions,resources,cutoff).persist(StorageLevel.DISK_ONLY)
            alternative.count()
            assert actual.exceptAll(alternative).count()==0 and alternative.exceptAll(actual).count()==0
            alternative.unpersist()
            totals=actual.agg(F.count(F.when(~F.col('has_recorded_activity'),1)).alias('without_activity'),
                F.sum('clicks_through_cutoff').alias('recorded_clicks'),F.sum('clicks_current_14d').alias('window_clicks')).first()
            metrics.append({'cutoff_day':cutoff,'rows':n,'without_recorded_activity':int(totals.without_activity),
                            'recorded_clicks':int(totals.recorded_clicks),'window_clicks':int(totals.window_clicks),
                            'future_perturbation_unchanged':True})
            eligible.unpersist()
        progress('validate_obt')
        obt=spark.read.parquet(*paths).select(*OUTPUT).persist(StorageLevel.DISK_ONLY)
        n=obt.count();assert n==expected.count() and obt.select(*KEYS).distinct().count()==n
        assert obt.filter((~F.col('has_recorded_activity')) & (F.col('recency_days').isNotNull() | (F.col('clicks_through_cutoff')!=0))).count()==0
        assert obt.filter((F.col('cutoff_day')==14) & (F.col('click_change_14d').isNotNull() | F.col('clicks_previous_14d').isNotNull())).count()==0
        assert obt.filter(F.col('recency_days')<0).count()==0
        hashes=obt.withColumn('_hash',F.sha2(F.to_json(F.struct(*[F.col(c) for c in OUTPUT]),{'ignoreNullFields':'false'}),256))
        fingerprints={str(r.cutoff_day):r.fingerprint for r in hashes.groupBy('cutoff_day').agg(F.sha2(F.concat_ws('',F.sort_array(F.collect_list('_hash'))),256).alias('fingerprint')).collect()}
        progress('write_staging')
        stage='OBT_FEATURES_BUILD_'+args.run_id.upper()
        obt.repartition(4).write.format(SOURCE).options(**options).option('dbtable',stage).mode('errorifexists').save()
        cur.execute('ALTER TABLE '+stage+' SET COMMENT=%s',(MARKER+'run_id='+args.run_id,))
        progress('readback')
        back=read('SELECT '+','.join(OUTPUT)+' FROM '+stage)
        back=back.select(*[F.col(f.name).cast(f.dataType).alias(f.name) for f in obt.schema.fields]).persist(StorageLevel.DISK_ONLY)
        assert back.count()==n and back.select(*KEYS).distinct().count()==n
        assert obt.exceptAll(back).count()==0 and back.exceptAll(obt).count()==0
        progress('publish')
        if existing:
            cur.execute('ALTER TABLE '+stage+' SWAP WITH OBT_FEATURES')
            cur.execute('DROP TABLE '+stage)
        else:cur.execute('ALTER TABLE '+stage+' RENAME TO OBT_FEATURES')
        stage=None;report['published']=True
        final=cur.execute('SELECT COUNT(*),COUNT(DISTINCT ENROLLMENT_KEY,CUTOFF_DAY) FROM OBT_FEATURES').fetchone()
        assert tuple(final)==(n,n)
        report.update(status='ok',rows=n,unique_keys=n,per_cutoff=metrics,content_sha256_by_cutoff=fingerprints,
                      output_columns=OUTPUT,temporal_tests_passed=len(CUTOFFS),readback_all_columns_equal=True,
                      population_key_sets_equal=True,target_and_withdrawal_excluded=True,
                      source_manifest_sha256=hashlib.sha256(Path('/datasets/manifest.json').read_bytes()).hexdigest(),
                      destination='PSET2_OULAD.ANALYTICS.OBT_FEATURES')
        progress('done',rows=n)
        return report
    except Exception as e:
        report.update(category='spark_pipeline_error',phase=phase,error_class=type(e).__name__)
        if getattr(e,'errno',None) is not None:report['errno']=e.errno
        message=str(e)
        for value in [key_text,private.get('account',''),private.get('private_key_passphrase','')]:
            if value:message=message.replace(value,'[privado]')
        message=re.sub(r'https?://\S+|[\w.-]+\.snowflakecomputing\.com|[A-Za-z0-9+/=_-]{40,}','[omitido]',message)
        (ARTIFACTS/('diagnostic_'+args.run_id+'.txt')).write_text(message)
        return report
    finally:
        if conn:
            if stage:
                try:conn.cursor().execute('DROP TABLE IF EXISTS '+stage)
                except Exception:pass
            conn.close()
        if spark:spark.stop()
        report['elapsed_seconds']=round(time.monotonic()-started,2)
        report['finished_at_utc']=datetime.now(timezone.utc).isoformat()
        (OUTPUT_DIR/(args.run_id+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    result=main();print(json.dumps(result,ensure_ascii=False))
    if result['status']!='ok':sys.exit(1)
