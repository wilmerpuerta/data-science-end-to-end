"""Valida exclusivamente la entrega pública; --infra comprueba Compose sin desplegar."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,hashlib,json,re,subprocess
from paquete import BASE,public_files,sha
PATTERNS={'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----','github_token':r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b','openai_key':r'\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b','personal_path':r'/(?:Users|home)/[A-Za-z0-9_.-]+/'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--infra',action='store_true');args=p.parse_args();checks={};findings=[];broken=[];files=public_files()
 def check(n,v):checks[n]=bool(v)
 required=['docker-compose.yml','.env.example','README.md','kestra/oulad_pipeline.yml','kestra/oulad_raw.yml','kestra/ingestion/load_raw.py','kestra/orchestration/runner_service.py','kestra/docker-compose.cloud.yml','dbt/dbt_project.yml','spark/build_obt.py','docs/PSet2_memo_Puerta_Wilmer.pdf']
 check('required_structure',all((BASE/n).is_file() for n in required))
 check('public_root_matches_required_layout',all(x.name in {'docker-compose.yml','.env.example','.gitignore','README.md','kestra','dbt','spark','docs'} for x in BASE.iterdir() if not x.name.startswith('.') ))
 check('public_files_no_symlinks_or_large_files',all(not q.is_symlink() and q.stat().st_size<50*1024*1024 for q in files))
 python_count=json_count=0
 for q in files:
  if q.suffix not in {'.py','.json','.md','.yml','.txt','.example'} and q.name not in {'Dockerfile','.dockerignore','.gitignore'}:continue
  s=q.read_text();name=q.relative_to(BASE).as_posix()
  if q.suffix=='.py':ast.parse(s,filename=name);python_count+=1
  if q.suffix=='.json':json.loads(s);json_count+=1
  for kind,pattern in PATTERNS.items():
   for m in re.finditer(pattern,s):findings.append({'file':name,'category':kind,'line':s[:m.start()].count('\n')+1})
  if q.suffix=='.md' and name!='docs/memo-pset2.md':
   for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',s):
    if re.match(r'[A-Za-z][A-Za-z0-9+.-]*:|#',target):continue
    resolved=(q.parent/target.strip('<>').split('#')[0]).resolve()
    if not resolved.exists() and resolved not in {BASE/'docs/paquete-verificacion.json',BASE/'docs/validacion-entrega.md'}:broken.append({'file':name,'target':target})
 check('secret_and_personal_path_patterns_absent',not findings);check('active_markdown_links_resolve',not broken)
 models=list((BASE/'dbt/models').rglob('*.sql'));names={q.stem for q in models};check('23_unique_models',len(models)==len(names)==23)
 sql=[q for q in (BASE/'dbt').rglob('*.sql') if not {'target','logs','dbt_packages','snowflake'}&set(q.relative_to(BASE).parts)]
 sources=json.loads((BASE/'dbt/models/sources.yml').read_text());source_names={(s['name'],t['name']) for s in sources['sources'] for t in s['tables']}
 refs={x for q in sql for x in re.findall(r"ref\(\s*['\"]([^'\"]+)['\"]\s*\)",q.read_text())};source_refs={tuple(x) for q in sql for x in re.findall(r"source\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)",q.read_text())};check('dbt_references_resolve',refs<=names and source_refs<=source_names and len(source_refs)==5)
 graph={q.stem:set(re.findall(r"ref\(\s*['\"]([^'\"]+)['\"]\s*\)",q.read_text())) for q in models};active=set();done=set()
 def visit(n):
  if n in active:return False
  if n in done:return True
  active.add(n)
  if not all(visit(x) for x in graph[n]):return False
  active.remove(n);done.add(n);return True
 check('dbt_graph_acyclic',all(visit(n) for n in graph))
 check('docker_images_and_dependencies_pinned',all(re.search(r'^FROM \S+@sha256:[a-f0-9]{64}$',(BASE/f/'Dockerfile').read_text(),re.M) and '--require-hashes' in (BASE/f/'Dockerfile').read_text() for f in ['kestra/ingestion','dbt','spark']))
 template=(BASE/'.env.example').read_text();passwords=re.findall(r'^\w*PASSWORD=(.*)$',template,re.M);check('password_examples_are_placeholders',len(passwords)==2 and all(x=='EJEMPLO_NO_UTILIZAR' for x in passwords))
 migration=json.loads((BASE/'docs/reestructuracion.json').read_text());pdf=next(x for x in migration['files'] if x['after']=='docs/PSet2_memo_Puerta_Wilmer.pdf')
 preserved=sha(BASE/pdf['after'])==pdf['before_sha256']
 revision=BASE/'docs/memo-revision-calendario.json'
 if not preserved and revision.is_file():
  r=json.loads(revision.read_text());calendar=json.loads((BASE/'docs/calendario-verificacion.json').read_text())
  preserved=(r['previous_pdf_sha256']==pdf['before_sha256']==sha(BASE/r['previous_pdf']) and r['pdf_sha256']==sha(BASE/pdf['after']) and r['source_md_sha256']==sha(BASE/'docs/memo-pset2.md') and calendar['status']=='ok' and calendar['enabled'])
 check('approved_pdf_preserved_or_documented_revision',preserved)
 if args.infra:
  for mode in ['--local-only','--cloud']:
   r=subprocess.run(['python3',str(BASE/'kestra/scripts/infra.py'),'validate',mode],capture_output=True,text=True);check('compose_'+mode[2:],r.returncode==0)
 report={'status':'ok' if all(checks.values()) else 'failed','checked_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'files':len(files),'python_files_parsed':python_count,'json_files_parsed':json_count,'findings_metadata_only':findings,'broken_links':broken,'cloud_execution_repeated':False,'scope':'Public files in pset_2; metadata-only pattern scan, active links, syntax, dependencies and structure. Historical memo source retains original paths; use docs/rutas-entrega.md. No full-history secret audit or Snowflake execution.'}
 (BASE/'docs/paquete-verificacion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[k for k,v in checks.items() if not v],'findings':findings,'broken_links':broken},ensure_ascii=False))
 return 0 if report['status']=='ok' else 1
if __name__=='__main__':raise SystemExit(main())
