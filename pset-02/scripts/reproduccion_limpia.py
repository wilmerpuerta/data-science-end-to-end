"""Exporta código sin estado local y reproduce la cadena en Compose aislado."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,shutil,socket,subprocess,sys,uuid
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'pset-02'
PRIVATE=BASE/'.local/reproduction'
def utc():return datetime.now(timezone.utc).isoformat()
def state_path(run):
    assert re.fullmatch('[a-f0-9]{12}',run)
    return PRIVATE/(run+'.json')
def save(state):
    PRIVATE.mkdir(parents=True,exist_ok=True)
    p=state_path(state['run_id']);p.write_text(json.dumps(state,indent=2)+'\n');p.chmod(0o600)
def is_code(name):
    return name.startswith(('pset-02/scripts/','pset-02/orchestration/','pset-02/ingestion/','pset-02/dbt/','pset-02/spark/')) or name in ['pset-02/docker-compose.yml','pset-02/docker-compose.cloud.yml']
def aggregate_hash(items):return hashlib.sha256(json.dumps(items,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def files_to_export():
    names=subprocess.run(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT,capture_output=True,check=True).stdout.decode().split('\0')
    result=[]
    for name in sorted(set(n for n in names if n)):
        p=Path(name)
        assert not any(x in p.parts for x in ['.git','.venv','.local','.secrets','secrets','.retry-probes'])
        assert not (p.name.startswith('.env') and p.name!='.env.example')
        assert p.suffix not in ['.pem','.p8','.key','.pub','.jar']
        if name.startswith('pset-02/output/'):continue
        assert not (name.startswith('datasets/') and p.suffix=='.csv')
        assert not (ROOT/p).is_symlink()
        if (ROOT/p).is_file():result.append(name)
    return result
def prepare(args):
    assert (BASE/'.env.cloud').is_file(),'Preparar primero configuración privada externa.'
    data=args.data_dir.resolve();manifest=json.loads((data/'manifest.json').read_text())
    for name,meta in manifest['files'].items():
        assert Path(name).name==name
        path=data/name;digest=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(8*1024*1024),b''):digest.update(chunk)
        assert path.stat().st_size==meta['bytes'] and digest.hexdigest()==meta['sha256']
    for port in [args.port,args.port+1]:
        with socket.socket() as sock:sock.bind(('127.0.0.1',port))
    run=uuid.uuid4().hex[:12];destination=ROOT/'tmp'/('reproduccion-'+run)/'repo'
    assert not destination.exists();destination.mkdir(parents=True)
    hashes={}
    for name in files_to_export():
        target=destination/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,target);hashes[name]=hashlib.sha256(target.read_bytes()).hexdigest()
    absent=['.venv','pset-02/.venv','pset-02/.local','pset-02/.env.infra','pset-02/.env.cloud','pset-02/output']
    assert all(not (destination/name).exists() for name in absent)
    subprocess.run([sys.executable,str(destination/'pset-02/scripts/infra.py'),'prepare'],cwd=destination,check=True)
    # El archivo cloud existente contiene únicamente referencias, no cuenta/frase.
    pointers={}
    for line in (BASE/'.env.cloud').read_text().splitlines():
        if not line or line.startswith('#'):continue
        key,value=line.split('=',1);assert key in ['SNOWFLAKE_CONNECTION_HOST_PATH','SNOWFLAKE_PRIVATE_KEY_HOST_PATH']
        path=Path(json.loads(value));assert path.is_absolute() and path.is_file() and ROOT not in path.parents
        pointers[key]=path
    assert len(pointers)==2
    cloud=destination/'pset-02/.env.cloud'
    cloud.write_text(''.join(k+'='+json.dumps(str(v),ensure_ascii=False)+'\n' for k,v in pointers.items()));cloud.chmod(0o600)
    project='pset2repro_'+run
    assert not any(c in str(data) for c in ['$','\n','\r'])
    with (destination/'pset-02/.env.infra').open('a') as f:
        f.write(f'PSET2_COMPOSE_PROJECT_NAME={project}\nPSET2_KESTRA_PORT={args.port}\nPSET2_KESTRA_MANAGEMENT_PORT={args.port+1}\n')
        f.write('OULAD_DATA_DIR='+json.dumps(str(data),ensure_ascii=False)+'\n')
    for folder in ['output/raw','output/spark','output/pipeline']:(destination/'pset-02'/folder).mkdir(parents=True,exist_ok=True)
    state={'run_id':run,'created_at_utc':utc(),'destination':str(destination),'project_name':project,'port':args.port,
           'state':'PREPARED','exported_files':len(hashes),'export_sha256':aggregate_hash(hashes),
           'code_sha256':aggregate_hash({k:v for k,v in hashes.items() if is_code(k)}),'file_hashes':hashes,
           'initial_runtime_paths_absent':absent,'dataset_manifest_sha256':hashlib.sha256((data/'manifest.json').read_bytes()).hexdigest()}
    save(state);print(json.dumps({k:state[k] for k in ['run_id','state','project_name','port','exported_files','export_sha256','code_sha256']}))
def step(state,name,args,cwd=None,env=None):
    log=PRIVATE/(state['run_id']+'-'+name+'.log')
    with log.open('w') as f:
        log.chmod(0o600);code=subprocess.run(args,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT).returncode
    state.setdefault('steps',[]).append({'step':name,'finished_at_utc':utc(),'returncode':code});save(state)
    print(json.dumps({'step':name,'returncode':code}),flush=True)
    if code:raise RuntimeError(name)
def run_test(state):
    destination=Path(state['destination']);env=os.environ.copy();env['COMPOSE_PROJECT_NAME']=state['project_name']
    root_infra=[sys.executable,str(BASE/'scripts/infra.py')]
    state['state']='RUNNING';state['started_at_utc']=utc();save(state)
    try:
        step(state,'stop_original',root_infra+['stop','--cloud'],cwd=ROOT)
        infra=[sys.executable,str(destination/'pset-02/scripts/infra.py')]
        step(state,'validate',infra+['validate','--cloud'],cwd=destination,env=env)
        step(state,'pull',infra+['pull','--cloud'],cwd=destination,env=env)
        step(state,'build_no_cache',infra+['build','--cloud','--no-cache'],cwd=destination,env=env)
        step(state,'up_new_volumes',infra+['up','--cloud'],cwd=destination,env=env)
        step(state,'smoke_seed',[sys.executable,str(destination/'pset-02/scripts/comprobar_kestra.py'),'--seed'],cwd=destination,env=env)
        step(state,'smoke_auth',[sys.executable,str(destination/'pset-02/scripts/comprobar_kestra.py'),'--execute','--check-auth'],cwd=destination,env=env)
        step(state,'deploy',[sys.executable,str(destination/'pset-02/scripts/ejecutar_pipeline.py'),'--deploy'],cwd=destination,env=env)
        # Releer CSV originales y volver a publicar Raw, no aprovechar cinco NOOP.
        step(state,'pipeline_force_reload',[sys.executable,str(destination/'pset-02/scripts/ejecutar_pipeline.py'),'--force-reload'],cwd=destination,env=env)
        state['state']='SUCCESS';state['finished_at_utc']=utc();save(state)
    except Exception as e:
        state['state']='FAILED';state['error_class']=type(e).__name__;state['failed_step']=str(e) if isinstance(e,RuntimeError) else 'local_error';save(state)
        raise
    finally:
        # Apagar solo la prueba; conservar sus volúmenes y evidencia para revisión.
        try:step(state,'stop_reproduction',[sys.executable,str(destination/'pset-02/scripts/infra.py'),'stop','--cloud'],cwd=destination,env=env)
        finally:step(state,'restore_original',root_infra+['up','--cloud'],cwd=ROOT)
def collect(state):
    assert state['state']=='SUCCESS'
    assert all(s['returncode']==0 for s in state['steps'])
    assert [s['step'] for s in state['steps'][-2:]]==['stop_reproduction','restore_original']
    destination=Path(state['destination']);source=destination/'pset-02/output/pipeline'
    executions=[json.loads(p.read_text()) for p in source.glob('*/execution.json')]
    execution=max((r for r in executions if r['state']=='SUCCESS'),key=lambda r:r['checked_at_utc'])
    folder=source/execution['execution_id'];verify=json.loads((folder/'verification.json').read_text())
    dbt=json.loads((folder/'dbt.json').read_text());spark=json.loads((folder/'spark.json').read_text())
    assert verify['status']=='ok' and execution['inputs']['force_reload'] and not execution['inputs']['retry_probe']
    assert len(verify['raw_files'])==5 and all(r['status']=='LOADED' for r in verify['raw_files'])
    assert verify['raw_selected_rows']==10726852 and verify['dbt_tests_passed']==168 and verify['obt_rows']==108277
    previous=json.loads((BASE/'docs/obt-verificacion.json').read_text())
    assert previous['content_sha256_by_cutoff']==spark['content_sha256_by_cutoff']
    all_copied_hashes={k:hashlib.sha256((destination/k).read_bytes()).hexdigest() for k in state['file_hashes']}
    assert aggregate_hash(all_copied_hashes)==state['export_sha256']
    copied_hashes={k:v for k,v in all_copied_hashes.items() if is_code(k)}
    # Archivos ejecutables copiados intactos; las salidas y configuración privada se generan aparte.
    assert aggregate_hash(copied_hashes)==state['code_sha256']
    evidence=BASE/'output/reproduction'/state['run_id'];evidence.mkdir(parents=True,exist_ok=True)
    for name in ['execution.json','verification.json','dbt.json','spark.json']:shutil.copy2(folder/name,evidence/name)
    raw_paths=list((destination/'pset-02/output/raw').glob(verify['raw_execution_id']+'_*.json'))
    raw=max((json.loads(p.read_text()) for p in raw_paths),key=lambda d:d['finished_at_utc'])
    assert raw['status']=='ok' and len(raw['files'])==5 and all(f['status']=='LOADED' for f in raw['files'])
    (evidence/'raw.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
    (evidence/'export-manifest.json').write_text(json.dumps({'export_sha256':state['export_sha256'],
        'code_sha256':state['code_sha256'],'files':state['file_hashes']},indent=2)+'\n')
    health_log=PRIVATE/(state['run_id']+'-up_new_volumes.log')
    text=health_log.read_text()
    assert state['project_name']+'-postgres-1' in text
    report={'checked_at_utc':utc(),'status':'ok','run_id':state['run_id'],'project_name':state['project_name'],
            'source_mode':'Exportación limpia de archivos versionables desde el árbol de trabajo; no es un clon remoto.',
            'exported_files':state['exported_files'],'export_sha256':state['export_sha256'],'code_sha256':state['code_sha256'],
            'separate_working_directory':True,'export_files_unchanged':True,'initial_runtime_paths_absent':state['initial_runtime_paths_absent'],
            'fresh_local_passwords':True,'external_credentials_referenced_only':True,
            'new_compose_project_and_volumes':True,'kestra_port':state['port'],'management_port':state['port']+1,
            'own_images_rebuilt_without_layer_cache':True,'base_images_pinned_and_reused':True,
            'snowflake_resources_reused':True,'raw_force_reloaded':True,'raw_rows':verify['raw_selected_rows'],
            'execution_id':execution['execution_id'],'dbt_models_succeeded':dbt['models_succeeded'],'dbt_tests_passed':dbt['tests_passed'],
            'obt_rows':spark['rows'],'obt_columns':len(spark['output_columns']),'content_sha256_matches_previous':True,
            'future_perturbation_tests_passed':spark['temporal_tests_passed'],'readback_all_columns_equal':spark['readback_all_columns_equal'],
            'steps':state['steps'],'reproduction_stopped':True,'original_stack_restored':True,
            'scope':'Directorio, estado Kestra/PostgreSQL, volúmenes y contraseñas locales nuevos. CSV y secretos externos identificados; cuenta/rol/warehouse/esquemas Snowflake existentes. No prueba alta de cuenta nueva ni clon remoto.'}
    (BASE/'docs/reproduccion-limpia.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['steps','initial_runtime_paths_absent']},ensure_ascii=False))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','run','collect'])
    p.add_argument('--run-id');p.add_argument('--data-dir',type=Path,default=ROOT/'datasets');p.add_argument('--port',type=int,default=18080)
    args=p.parse_args()
    if not 1024<=args.port<65535:p.error('--port debe dejar dos puertos válidos, desde 1024 hasta 65535')
    if args.action=='prepare':return prepare(args)
    if not args.run_id:p.error('--run-id requerido')
    state=json.loads(state_path(args.run_id).read_text())
    if args.action=='run':
        assert state['state']=='PREPARED','Una prueba iniciada no se relanza silenciosamente.'
        return run_test(state)
    collect(state)
if __name__=='__main__':main()
