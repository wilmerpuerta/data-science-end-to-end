"""Revisa los archivos que Git incluiría, sin add, commit, push ni cargas cloud.

Usar el entorno de pset-01/scripts/requirements.txt. --entregables ejecuta sus
verificadores; --infra consulta Compose sin crear o reiniciar servicios.
Los hallazgos contienen ubicación y categoría, nunca el valor detectado.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'pset-02'
REPORT = BASE / 'docs/paquete-verificacion.json'
SELF_REPORTS = {'pset-02/docs/paquete-verificacion.json', 'pset-01/docs/entregables-manifest.json'}
PATTERNS = {
    'private_key_material': r'-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----',
    'github_token': r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b',
    'cloud_access_key': r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'api_key': r'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b',
    'credential_url': r'(?i)https?://[^\s/:]+:[^\s/@]+@',
    'jwt': r'\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\b',
    'personal_path': r'/(?:Users|home)/[^\s"\x27<>]+',
    'account_endpoint': r'(?i)\b[a-z0-9][a-z0-9.-]{3,}\.snowflakecomputing\.com\b',
}
PRIVATE_PARTS = {'.git', '.venv', '.local', '.secrets', 'secrets', '.retry-probes', 'node_modules', '__pycache__'}
PRIVATE_SUFFIXES = {'.pem', '.p8', '.key', '.pub', '.p12', '.pfx', '.jks', '.keystore', '.der'}


def git(*args, **kwargs):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, **kwargs)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_path(name):
    return name.startswith(('pset-02/ingestion/', 'pset-02/dbt/', 'pset-02/spark/', 'pset-02/orchestration/')) or name in {
        'pset-02/docker-compose.yml', 'pset-02/docker-compose.cloud.yml',
        'pset-02/scripts/infra.py', 'pset-02/scripts/ejecutar_raw.py',
        'pset-02/scripts/ejecutar_dbt.py', 'pset-02/scripts/ejecutar_spark.py',
        'pset-02/scripts/ejecutar_pipeline.py',
    }


def content(path):
    if path.suffix == '.pdf':
        import pymupdf
        with pymupdf.open(path) as doc:
            return '\n'.join(p.get_text() for p in doc)
    if path.suffix == '.pptx':
        with zipfile.ZipFile(path) as archive:
            return '\n'.join(archive.read(n).decode() for n in archive.namelist() if n.endswith('.xml'))
    if path.suffix == '.ppt':
        data = path.read_bytes()
        # Comprobar cadenas legibles, además del verificador PowerPoint existente.
        return data.decode('latin1') + '\n' + data.decode('utf-16-le', errors='ignore')
    return path.read_text(encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entregables', action='store_true')
    parser.add_argument('--infra', action='store_true')
    args = parser.parse_args()
    REPORT.write_text('{"status":"running","scope":"Revisión aún no terminada."}\n')
    checks, findings, examples, links = {}, [], [], []
    def check(name, value):
        checks[name] = bool(value)
    subprocess_checks = {}
    if args.entregables:
        for name,script in [('memo_pset2','pset-02/scripts/verificar_memo.py'),('pset1','pset-01/scripts/verificar_entregables.py')]:
            result = subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,capture_output=True,text=True)
            subprocess_checks[name] = {'returncode':result.returncode}
            check(name+'_verifier_passed',result.returncode==0)
    services = []
    if args.infra:
        for action in ['validate','status']:
            result = subprocess.run([sys.executable,str(BASE/'scripts/infra.py'),action,'--cloud'],cwd=ROOT,capture_output=True,text=True)
            check('compose_'+action+'_passed',result.returncode==0)
            if action=='status' and result.returncode==0:
                services = json.loads(result.stdout)
                check('five_services_healthy',len(services)==5 and all(s['state']=='running' and s['health']=='healthy' for s in services))

    listed = git('ls-files','--cached','--others','--exclude-standard','-z')
    listed.check_returncode()
    names = sorted(set(n for n in listed.stdout.decode().split('\0') if n) - SELF_REPORTS)
    files = [ROOT/name for name in names]
    check('candidate_files_exist_and_are_not_symlinks',all(p.is_file() and not p.is_symlink() for p in files))
    check('no_private_paths_or_raw_csv_candidates',not any(
        set(p.parts)&PRIVATE_PARTS or p.suffix in PRIVATE_SUFFIXES or
        (p.name.startswith('.env') and p.name!='.env.example') or p.name.endswith('.local.sql') or
        (name.startswith('datasets/') and p.suffix=='.csv') or
        name.startswith(('tmp/','backups/','pset-02/dbt/target/','pset-02/dbt/logs/'))
        for name in names for p in [Path(name)]))
    check('no_file_over_50_mib',all(p.stat().st_size<50*1024*1024 for p in files))
    fixtures = ['.env','pset-02/.env.infra','pset-02/.env.cloud','pset-02/.venv/pyvenv.cfg',
                'datasets/studentInfo.csv','datasets/studentVle.csv','datasets/studentAssessment.csv',
                'pset-02/.local/log.txt','tmp/revision.txt','backups/original.md','clave.p8','clave.pem',
                'registrar_usuario.local.sql','pset-02/dbt/target/run_results.json']
    ignored = git('check-ignore','--no-index','--stdin','-z',input=('\0'.join(fixtures)+'\0').encode())
    ignored_names = set(ignored.stdout.decode().split('\0'))
    check('sensitive_path_exclusion_rules',all(name in ignored_names for name in fixtures))

    parsed_json, parsed_python = 0, 0
    for name,path in zip(names,files):
        text = content(path)
        if path.suffix in {'.json','.ipynb'}:
            json.loads(text)
            parsed_json += 1
        if path.suffix=='.py':
            ast.parse(text,filename=name)
            parsed_python += 1
        for category,pattern in PATTERNS.items():
            for match in re.finditer(pattern,text):
                line = text[:match.start()].count('\n')+1
                # Ejemplo literal de una prohibición del encargo, no ruta usada.
                source_line = text.splitlines()[line-1]
                if category=='personal_path' and name=='prompt-codex-psets.md' and 'Nunca codifiques' in source_line and '/...' in source_line:
                    examples.append({'file':name,'line':line,'classification':'Ejemplo de ruta prohibida en el encargo; no dependencia ni credencial.'})
                    continue
                findings.append({'file':name,'line':line,'category':category})
        if path.suffix=='.md':
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',text):
                target = target.strip('<>')
                if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:|#',target):
                    continue
                resolved = (path.parent/target.split('#')[0]).resolve()
                if resolved != REPORT and not resolved.exists():
                    links.append({'file':name,'target':target})
    check('no_secret_or_personal_path_pattern_findings',not findings)
    check('all_local_markdown_links_exist',not links)
    check('public_json_and_python_parse',parsed_json>0 and parsed_python>0)
    template = (BASE/'.env.example').read_text()
    passwords = re.findall(r'^\w*PASSWORD=(.*)$',template,re.M)
    check('env_password_examples_are_placeholders',len(passwords)==2 and all(v=='EJEMPLO_NO_UTILIZAR' for v in passwords))

    models = list((BASE/'dbt/models').rglob('*.sql'))
    model_names = {p.stem for p in models}
    check('23_unique_dbt_models',len(models)==len(model_names)==23)
    source = json.loads((BASE/'dbt/models/sources.yml').read_text())
    sources = {(s['name'],t['name']) for s in source['sources'] for t in s['tables']}
    all_sql = list((BASE/'dbt').rglob('*.sql'))
    all_sql = [p for p in all_sql if not set(p.parts)&{'target','dbt_packages','logs'}]
    refs = {ref for p in all_sql for ref in re.findall(r"ref\(\s*['\"]([^'\"]+)['\"]\s*\)",p.read_text())}
    source_refs = {tuple(r) for p in all_sql for r in re.findall(r"source\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)",p.read_text())}
    check('dbt_literal_refs_resolve',refs<=model_names and source_refs<=sources and len(source_refs)==5)
    graph = {p.stem:set(re.findall(r"ref\(\s*['\"]([^'\"]+)['\"]\s*\)",p.read_text())) for p in models}
    done,active = set(),set()
    def visit(node):
        if node in active:
            return False
        if node in done:
            return True
        active.add(node)
        if not all(visit(n) for n in graph.get(node,set())):
            return False
        active.remove(node)
        done.add(node)
        return True
    check('dbt_model_graph_acyclic',all(visit(n) for n in graph))
    dockerfiles = [BASE/folder/'Dockerfile' for folder in ['ingestion','dbt','spark']]
    check('docker_bases_pinned_by_digest',all(re.search(r'^FROM \S+@sha256:[a-f0-9]{64}$',p.read_text(),re.M) for p in dockerfiles))
    check('docker_python_dependencies_require_hashes',all('--require-hashes' in p.read_text() for p in dockerfiles))
    check('docker_build_contexts_allowlist_only',all((p.parent/'.dockerignore').read_text().startswith('*\n!Dockerfile\n!requirements.txt') for p in dockerfiles))
    jars = json.loads((BASE/'spark/jars.lock.json').read_text())['artifacts']
    check('four_jars_have_https_urls_sizes_and_sha256',len(jars)==4 and all(
        a['url'].startswith('https://repo.maven.apache.org/') and a['bytes']>0 and
        re.fullmatch('[a-f0-9]{64}',a['sha256']) for a in jars))
    snapshot = json.loads((BASE/'output/reproduction/849681d33298/export-manifest.json').read_text())
    runtime = {name:digest for name,digest in snapshot['files'].items() if runtime_path(name)}
    changed_runtime = [name for name,digest in runtime.items() if not (ROOT/name).is_file() or sha(ROOT/name)!=digest]
    check('tested_pipeline_runtime_unchanged',not changed_runtime)
    required = ['README.md','datasets/README.md','datasets/manifest.json','pset-01/README.md','pset-02/README.md',
                'pset-02/enunciado.md','pset-02/rubrica.md','pset-02/memo-pset2.md',
                'pset-02/output/pdf/PSet2_memo_Puerta_Wilmer.pdf','pset-02/docker-compose.yml','pset-02/docker-compose.cloud.yml']
    check('required_deliverables_present',all(name in names for name in required))
    history = git('rev-parse','--verify','HEAD').returncode==0
    remote_count = len(git('remote').stdout.decode().splitlines())
    # Una primera revisión sin commits no puede certificar un historial futuro.
    history_scope = 'No hay commits que inspeccionar.' if not history else 'Hay commits: esta revisión cubre candidatos actuales, no todo el historial.'
    hashes = {name:sha(ROOT/name) for name in names}
    package_hash = hashlib.sha256(json.dumps(hashes,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    result = {
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),
        'status':'ok' if all(checks.values()) else 'failed',
        'checks':checks,'reviewed_files':len(files),'reviewed_bytes':sum(p.stat().st_size for p in files),
        'package_sha256':package_hash,'file_sha256':hashes,
        'fingerprint_exclusions':sorted(SELF_REPORTS),'python_files_parsed':parsed_python,'json_files_parsed':parsed_json,
        'findings_metadata_only':findings,'instructional_examples':examples,'broken_markdown_links':links,
        'pipeline_runtime_files_compared':len(runtime),'pipeline_runtime_changed':changed_runtime,
        'git_has_commits':history,'git_remote_count':remote_count,'history_scope':history_scope,
        'services':services,'subprocess_verifiers':subprocess_checks,
        'scope':'Archivos candidatos según Git, contenido textual y cadenas legibles de PPT; sin leer archivos privados excluidos. Reglas de patrones, no garantía absoluta de ausencia de cualquier secreto. No se repitieron cargas ni builds cloud. No se hace add, commit, push ni despliegue.',
        'documented_limits':['Costo monetario sin cuantificar.','Timeout del warehouse sin evidencia específica.','Calendarios desactivados; backfill por fichero.','Recursos Snowflake reutilizados en reproducción limpia.','Cobertura y exactitud externa sin acreditar; sin entrenamiento.','Colab de PSet 1 pendiente de sincronización.'],
    }
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    # El inventario general incluye este informe ya cerrado. El hash del paquete
    # excluye el inventario, de modo que no existe dependencia circular.
    if args.entregables:
        sys.path.insert(0,str(ROOT/'pset-01/scripts'))
        from verificar_entregables import actualizar_inventario
        actualizar_inventario()
    failed = [k for k,v in checks.items() if not v]
    print(json.dumps({'status':result['status'],'checks':len(checks),'failed_checks':failed,
                      'reviewed_files':len(files),'reviewed_bytes':result['reviewed_bytes'],
                      'findings':len(findings),'broken_links':len(links),'report':'pset-02/docs/paquete-verificacion.json'},ensure_ascii=False))
    return 0 if not failed else 1


if __name__=='__main__':
    raise SystemExit(main())
