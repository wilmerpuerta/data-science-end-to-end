"""OULAD a Raw. Ejecutar dentro de Kestra; nunca imprime credenciales o filas."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,csv,gzip,hashlib,json,logging,os,re,shutil,sys,tempfile,uuid

DATA=Path('/datasets')
OUTPUT=Path('/workspace/output')
TABLES={'studentInfo.csv':'STUDENTINFO','studentRegistration.csv':'STUDENTREGISTRATION',
        'courses.csv':'COURSES','vle.csv':'VLE','studentVle.csv':'STUDENTVLE'}
CTX=('PSET2_SVC','PSET2_PIPELINE','PSET2_OULAD','RAW','PSET2_WH')

def connect():
    import snowflake.connector
    with open('/run/secrets/snowflake_connection.json') as f: config=json.load(f)
    if config.get('schema_version')!=1:raise RuntimeError('private_config_version')
    return snowflake.connector.connect(account=config['account'],user=CTX[0],role=CTX[1],
        database=CTX[2],schema=CTX[3],warehouse=CTX[4],authenticator='SNOWFLAKE_JWT',
        private_key_file='/run/secrets/snowflake_key.p8',private_key_file_pwd=config['private_key_passphrase'],
        login_timeout=30,network_timeout=120,
        session_parameters={'QUERY_TAG':'pset02_raw_ingestion','STATEMENT_TIMEOUT_IN_SECONDS':600})

def verified_files(selected):
    manifest=json.loads((DATA/'manifest.json').read_text())
    names=list(TABLES) if selected=='all' else [selected]
    result=[]
    for name in names:
        meta=manifest['files'][name];path=DATA/name;h=hashlib.sha256()
        with path.open('rb') as f:
            for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
        if h.hexdigest()!=meta['sha256'] or path.stat().st_size!=meta['bytes']:
            raise RuntimeError('input_checksum_mismatch')
        with path.open(newline='',encoding='utf-8-sig') as f:
            reader=csv.reader(f);columns=next(reader);count=0
            for row in reader:
                if len(row)!=len(columns):raise RuntimeError('source_column_count_mismatch')
                count+=1
            if count!=meta['rows']:raise RuntimeError('source_row_count_mismatch')
        if not columns or len(set(columns))!=len(columns) or not all(re.fullmatch(r'[a-z][a-z0-9_]*',c) for c in columns):
            raise RuntimeError('invalid_source_columns')
        result.append((name,meta,columns))
    return result

def ensure_managed(cur,table,definition,marker):
    cur.execute(f"CREATE TABLE IF NOT EXISTS {table} ({definition}) COMMENT='{marker}'")
    row=cur.execute("SELECT COMMENT FROM PSET2_OULAD.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='RAW' AND TABLE_NAME=%s",(table,)).fetchone()
    if not row or row[0]!=marker:raise RuntimeError('unmanaged_existing_table')

def target_counts(cur,table,checksum):
    row=cur.execute(f'''SELECT COUNT(*), COUNT(DISTINCT SOURCE_ROW_NUMBER),
        COUNT_IF(SOURCE_SHA256 IS NULL OR SOURCE_SHA256 <> %s)
        FROM {table}''',(checksum,)).fetchone()
    return {'rows':int(row[0]),'unique_source_rows':int(row[1]),'other_checksums':int(row[2] or 0)}

def audit(cur,name,checksum,run_id,attempt,status,expected,rows):
    cur.execute('''INSERT INTO INGESTION_LOG
        (SOURCE_FILE,SOURCE_SHA256,RUN_ID,ATTEMPT_ID,STATUS,EXPECTED_ROWS,ACTUAL_ROWS,RECORDED_AT)
        VALUES (%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP())''',
        (name,checksum,run_id,attempt,status,expected,rows))

def verify_source_values(conn):
    """Reconciliar clases y valores vacíos con la auditoría de esta copia."""
    with conn.cursor() as cur:
        classes=cur.execute("SELECT COUNT_IF(FINAL_RESULT='Fail'),COUNT_IF(FINAL_RESULT='Withdrawn'),COUNT_IF(FINAL_RESULT IN ('Pass','Distinction')),COUNT_IF(IMD_BAND=''),COUNT_IF(IMD_BAND IS NULL) FROM STUDENTINFO").fetchone()
        registration=cur.execute("SELECT COUNT_IF(DATE_REGISTRATION=''),COUNT_IF(DATE_UNREGISTRATION=''),COUNT_IF(DATE_UNREGISTRATION IS NULL) FROM STUDENTREGISTRATION").fetchone()
        resources=cur.execute("SELECT COUNT_IF(WEEK_FROM=''),COUNT_IF(WEEK_TO='') FROM VLE").fetchone()
    if tuple(classes)!=(7052,10156,15385,1111,0) or tuple(registration)!=(45,22521,0) or tuple(resources)!=(5243,5243):
        raise RuntimeError('source_value_reconciliation_failed')
    return {'Fail':int(classes[0]),'Withdrawn':int(classes[1]),'Approved':int(classes[2]),
            'empty_imd_band':int(classes[3]),'empty_registration_date':int(registration[0]),
            'empty_unregistration_date':int(registration[1]),'empty_week_from':int(resources[0]),
            'empty_week_to':int(resources[1]),'source_empty_values_preserved':True}

def load_file(conn,name,meta,columns,run_id,attempt,force=False,progress=None):
    table=TABLES[name];checksum=meta['sha256'];expected=meta['rows']
    cols=', '.join(c.upper()+' VARCHAR' for c in columns)
    technical='SOURCE_SHA256 VARCHAR, SOURCE_ROW_NUMBER NUMBER, LOAD_RUN_ID VARCHAR, LOADED_AT TIMESTAMP_LTZ'
    with conn.cursor() as cur:
        if progress is not None:progress['phase']='target_contract'
        ensure_managed(cur,table,cols+', '+technical,'pset2.raw.v1:'+name)
        # No se modifica una tabla con un contrato diferente aunque tuviera el comentario.
        actual=[r[0] for r in cur.execute(f'DESC TABLE {table}').fetchall()]
        if actual!=[c.upper() for c in columns]+['SOURCE_SHA256','SOURCE_ROW_NUMBER','LOAD_RUN_ID','LOADED_AT']:
            raise RuntimeError('target_schema_mismatch')
        current=target_counts(cur,table,checksum)
        if current=={'rows':expected,'unique_source_rows':expected,'other_checksums':0} and not force:
            audit(cur,name,checksum,run_id,attempt,'NOOP',expected,expected)
            return {'file':name,'status':'NOOP',**current}
        temp='TMP_'+table+'_'+uuid.uuid4().hex[:12].upper()
        if progress is not None:progress['phase']='temporary_table'
        cur.execute(f'CREATE TEMPORARY TABLE {temp} LIKE {table}')
        # Compresión determinista, sin modificar el original; temporales solo dentro del contenedor.
        with tempfile.TemporaryDirectory(prefix='oulad-raw-') as work:
            gzpath=Path(work)/(name+'.gz')
            with (DATA/name).open('rb') as source,gzpath.open('wb') as target:
                with gzip.GzipFile(filename='',fileobj=target,mode='wb',compresslevel=3,mtime=0) as compressed:
                    shutil.copyfileobj(source,compressed,8*1024*1024)
            stage_path=f'@OULAD_FILES/{table}/{checksum}'
            if progress is not None:progress['phase']='stage_upload'
            cur.execute(f"PUT 'file://{gzpath}' {stage_path} AUTO_COMPRESS=FALSE SOURCE_COMPRESSION=GZIP OVERWRITE=FALSE PARALLEL=2")
            put=cur.fetchall()
            if not put or any(str(row[6]).upper() not in ['UPLOADED','SKIPPED'] for row in put):
                raise RuntimeError('stage_upload_incomplete')
            selection=', '.join(f'${i}::VARCHAR' for i in range(1,len(columns)+1))
            if progress is not None:progress['phase']='copy_to_temporary'
            cur.execute(f'''COPY INTO {temp} FROM (
                SELECT {selection}, '{checksum}', METADATA$FILE_ROW_NUMBER,
                    '{run_id}', CURRENT_TIMESTAMP()
                FROM {stage_path}/{name}.gz)
                FILE_FORMAT=(FORMAT_NAME='PSET2_OULAD.RAW.OULAD_CSV_V1')
                ON_ERROR='ABORT_STATEMENT' FORCE=TRUE''')
        copied=target_counts(cur,temp,checksum)
        if copied!={'rows':expected,'unique_source_rows':expected,'other_checksums':0}:
            raise RuntimeError('copy_reconciliation_failed')
        # DDL y COPY terminan antes de la transacción. Solo se publica un fichero
        # entero validado; no hay truncado ni eliminación de tablas originales.
        try:
            if progress is not None:progress['phase']='publish_transaction'
            cur.execute('BEGIN')
            cur.execute(f'DELETE FROM {table}')
            cur.execute(f'INSERT INTO {table} SELECT * FROM {temp}')
            audit(cur,name,checksum,run_id,attempt,'LOADED',expected,expected)
            cur.execute('COMMIT')
        except Exception:
            cur.execute('ROLLBACK');raise
        finally:
            cur.execute(f'DROP TABLE IF EXISTS {temp}')
        final=target_counts(cur,table,checksum)
        if final!=copied:raise RuntimeError('published_reconciliation_failed')
        return {'file':name,'status':'LOADED',**final}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check-connection',action='store_true')
    p.add_argument('--retry-probe',action='store_true',help='Fallo controlado una vez, solo para prueba de conexión y retries.')
    p.add_argument('--file',choices=['all',*TABLES],default='all')
    p.add_argument('--run-id',default='manual_'+uuid.uuid4().hex)
    p.add_argument('--force-reload',action='store_true',help='Backfill explícito del fichero completo, con publicación transaccional.')
    args=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',args.run_id):raise SystemExit('run_id inválido')
    logging.disable(logging.CRITICAL)
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'run_id':args.run_id,
            'attempt_id':uuid.uuid4().hex,'status':'failed','files':[],
            'mode':'connection' if args.check_connection else 'load','source_partition':args.file}
    try:
        report['phase']='connect'
        if args.retry_probe:
            if not args.check_connection:raise RuntimeError('retry_probe_requires_connection_mode')
            report['retry_probe']=True
            markers=OUTPUT/'.retry-probes';markers.mkdir(parents=True,exist_ok=True)
            try:fd=os.open(markers/args.run_id,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            except FileExistsError:pass
            else:
                os.close(fd)
                raise RuntimeError('retry_probe_first_attempt')
        with connect() as conn:
            with conn.cursor() as cur:
                row=cur.execute('SELECT CURRENT_USER(),CURRENT_ROLE(),CURRENT_DATABASE(),CURRENT_SCHEMA(),CURRENT_WAREHOUSE()').fetchone()
                if tuple(row)!=CTX:raise RuntimeError('unexpected_session_context')
            if args.check_connection:
                report['expected_session_context_verified']=True
            else:
                if not os.statvfs(DATA).f_flag & os.ST_RDONLY:raise RuntimeError('source_not_read_only')
                report['phase']='verify_source';files=verified_files(args.file)
                with conn.cursor() as cur:
                    report['phase']='raw_control_objects'
                    ensure_managed(cur,'INGESTION_LOG',
                        'SOURCE_FILE VARCHAR, SOURCE_SHA256 VARCHAR, RUN_ID VARCHAR, ATTEMPT_ID VARCHAR, STATUS VARCHAR, EXPECTED_ROWS NUMBER, ACTUAL_ROWS NUMBER, RECORDED_AT TIMESTAMP_LTZ',
                        'pset2.raw.ingestion-log.v1')
                    cur.execute("CREATE STAGE IF NOT EXISTS OULAD_FILES COMMENT='pset2.raw.stage.v1'")
                    cur.execute('''CREATE FILE FORMAT IF NOT EXISTS OULAD_CSV_V1
                        TYPE=CSV COMPRESSION=AUTO SKIP_HEADER=1 FIELD_OPTIONALLY_ENCLOSED_BY='"'
                        EMPTY_FIELD_AS_NULL=FALSE NULL_IF=() ERROR_ON_COLUMN_COUNT_MISMATCH=FALSE ENCODING='UTF8' ''')
                for name,meta,columns in files:
                    report['active_file']=name
                    result=load_file(conn,name,meta,columns,args.run_id,report['attempt_id'],args.force_reload,report)
                    report['files'].append(result)
                    print(json.dumps({'file':name,**result}),flush=True)
                report['datasets_read_only']=True
                if args.file=='all':report['source_value_checks']=verify_source_values(conn)
            report['status']='ok'
            report['phase']='completed'
    except Exception as exc:
        import snowflake.connector
        report['category']='connector_error' if isinstance(exc,snowflake.connector.errors.Error) else 'local_validation_error'
        if report['category']=='connector_error':
            report['errno']=exc.errno if isinstance(exc.errno,int) else None
            report['sqlstate']=exc.sqlstate if isinstance(exc.sqlstate,str) and len(exc.sqlstate)==5 and exc.sqlstate.isalnum() else None
        elif isinstance(exc,RuntimeError):
            # Solo códigos conocidos y sin contenido de entradas o de excepciones externas.
            allowed={'private_config_version','input_checksum_mismatch','invalid_source_columns','source_column_count_mismatch','source_row_count_mismatch','source_value_reconciliation_failed','unmanaged_existing_table','target_schema_mismatch','stage_upload_incomplete','copy_reconciliation_failed','published_reconciliation_failed','source_not_read_only','unexpected_session_context','retry_probe_requires_connection_mode','retry_probe_first_attempt'}
            if str(exc) in allowed:report['validation_code']=str(exc)
            if str(exc)=='retry_probe_first_attempt':report['category']='injected_transient_failure'
    report['finished_at_utc']=datetime.now(timezone.utc).isoformat()
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/(args.run_id+'_'+report['attempt_id']+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False),flush=True)
    return 0 if report['status']=='ok' else 1
if __name__=='__main__':raise SystemExit(main())
