"""Valida fuente, PDF, evidencias y sincronía de los Markdown derivados.

--render genera PNG por página para revisión visual, sin red ni credenciales.
"""
from pathlib import Path
import argparse
import hashlib
import importlib
import json
import re

import pymupdf
from generar_memo import BASE, SOURCE, OUTPUT, blocks, graph, plain

ROOT = BASE.parent
REPORT = BASE / 'docs/memo-verificacion.json'


def compact(text):
    return ''.join(c for c in text.casefold() if c.isalnum())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads((BASE/path).read_text())


def format_number(n):
    return f'{n:,}'.replace(',','.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render',action='store_true')
    args = parser.parse_args()
    checks = {}
    def check(name, value):
        checks[name] = bool(value)
        if not value:
            raise AssertionError(name)

    source = SOURCE.read_text()
    sections = source.split('<!-- pagebreak -->')
    pdf = pymupdf.open(OUTPUT)
    check('six_pages_and_six_source_sections',len(pdf)==len(sections)==6)
    check('pdf_metadata_matches_source_sha256',pdf.metadata['subject']=='Fuente SHA-256: '+sha(SOURCE))
    missing = []
    spans = []
    diagram_counts = []
    for i,(section,page) in enumerate(zip(sections,pdf),1):
        extracted = compact(page.get_text())
        for kind,body in blocks(section):
            if kind=='mermaid':
                nodes,edges = graph(body)
                fragments = [label for value in nodes.values() for label in value.split('<br/>')]
                diagram_counts.append({'page':i,'nodes':len(nodes),'edges':len(edges)})
            elif kind=='table':
                fragments = [cell for row in body for cell in row]
            elif kind=='bash':
                fragments = body.splitlines()
            else:
                fragments = [plain(body)]
            for fragment in fragments:
                if compact(fragment) not in extracted:
                    missing.append({'page':i,'text':fragment})
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                spans += [dict(s,page=i) for s in line['spans']]
    check('every_source_fragment_on_corresponding_pdf_page',not missing)
    check('literal_cron_preserved','0 9 1,15 * *' in ' '.join(pdf[1].get_text().split()))
    check('two_vector_diagrams',len(diagram_counts)==2 and diagram_counts[0]['edges']==11 and diagram_counts[1]['edges']==8 and sum(len(p.get_images()) for p in pdf)==0)
    check('text_inside_page',all(s['bbox'][0]>=35 and s['bbox'][1]>=15 and s['bbox'][2]<=pdf[0].rect.width-35 and s['bbox'][3]<=pdf[0].rect.height-15 for s in spans))
    check('minimum_font_8pt',all(s['size']>=7.99 for s in spans))
    check('no_replacement_or_black_square_glyphs',all('\ufffd' not in s['text'] and '\u25a0' not in s['text'] for s in spans))
    check('no_personal_paths_or_private_material_in_memo',not any(s in source for s in ['/Users/','BEGIN PRIVATE KEY','BEGIN ENCRYPTED PRIVATE KEY','SNOWFLAKE_PASSWORD=','token=']))

    repro = read('docs/reproduccion-limpia.json')
    obt = read('docs/obt-verificacion.json')
    silver = read('docs/calidad-silver.json')
    gold = read('docs/calidad-gold.json')
    dbt = read('docs/dbt-build-gold.json')
    pipeline = read('docs/pipeline-pruebas.json')
    synthetic = read('docs/spark-pruebas.json')
    manifest = json.loads((ROOT/'datasets/manifest.json').read_text())
    sm = {(m['dataset'],m['metric']):m['value'] for m in silver['metrics']}
    gm = {(m['dataset'],m['metric']):m['value'] for m in gold['metrics']}
    check('evidence_reports_success',all(r['status']=='ok' for r in [repro,obt,silver,gold,dbt,pipeline,synthetic]))
    models = [r for r in dbt['results'] if r['unique_id'].startswith('model.')]
    tests = [r for r in dbt['results'] if r['unique_id'].startswith('test.')]
    check('23_models_and_168_tests_match_real_build',len(models)==repro['dbt_models_succeeded']==23 and all(r['status']=='success' for r in models) and len(tests)==repro['dbt_tests_passed']==168 and all(r['status']=='pass' for r in tests))
    check('raw_file_counts_match_manifest',sum(manifest['files'][n]['rows'] for n in ['studentInfo.csv','studentRegistration.csv','courses.csv','vle.csv','studentVle.csv'])==repro['raw_rows']==10726852)
    check('silver_gold_counts_and_clicks_reconciled',sm['activity_daily','rows']==gm['fact_activity_daily','rows']==8459320 and sm['activity_daily','clicks']==gm['fact_activity_daily','clicks']==39605099)
    check('obt_shape_matches_reproduction',obt['rows']==obt['unique_keys']==repro['obt_rows']==108277 and len(obt['output_columns'])==repro['obt_columns']==35)
    check('temporal_and_readback_evidence',synthetic['cases_passed']==7 and obt['temporal_tests_passed']==repro['future_perturbation_tests_passed']==4 and obt['readback_all_columns_equal'] and repro['readback_all_columns_equal'] and repro['content_sha256_matches_previous'])
    check('controlled_failure_scope',pipeline['stopped_after_injected_failure'] and pipeline['no_downstream_jobs_on_failure'] and pipeline['gate_attempts']==2 and not pipeline['calendars_enabled'])
    check('clean_reproduction_scope',repro['exported_files']==214 and repro['new_compose_project_and_volumes'] and repro['own_images_rebuilt_without_layer_cache'] and repro['snowflake_resources_reused'] and repro['original_stack_restored'])
    # Comparar cada cifra relevante en su sección correspondiente.
    expected = {
        1:[repro['raw_rows'],sm['activity_daily','rows'],obt['rows']],
        2:[manifest['files'][name]['rows'] for name in ['studentInfo.csv','studentRegistration.csv','courses.csv','vle.csv','studentVle.csv']],
        3:[sm['enrollments','missing_imd'],sm['registration','missing_registration'],sm['registration','late_registration'],sm['resources','unknown_schedule'],sm['outcomes','withdrawn_without_date'],sm['outcomes','other_outcome_with_date'],sm['activity_daily','natural_key_excess'],sm['activity_daily','exact_value_excess'],sm['activity_daily','clicks'],sm['sensitivity','clicks_if_exact_deduplicated'],sm['enrollments','without_activity']],
        4:[gm['dim_student','rows'],gm['dim_edition','rows'],gm['dim_enrollment','rows'],gm['dim_resource','rows'],gm['dim_relative_day','rows'],gm['fact_activity_daily','rows'],gm['fact_activity_daily','clicks']],
        5:[obt['rows'],obt['activity_rows_extracted']]+[p[k] for p in obt['per_cutoff'] for k in ['rows','without_recorded_activity']],
        6:[repro['exported_files']],
    }
    for page,values in expected.items():
        check(f'page_{page}_metrics_match_json',all(re.search(r'(?<![\d.])'+re.escape(format_number(v))+r'(?![\d.])',sections[page-1]) for v in values))
    check('reproduction_ports_match_json',f"{repro['kestra_port']}/{repro['management_port']}" in sections[5])
    for module,filename in [('resumir_bronze','calidad-bronze-resultados.md'),('resumir_silver','silver-resultados.md'),('resumir_gold','gold-resultados.md'),('resumir_obt','obt-resultados.md'),('resumir_reproduccion','reproduccion-resultados.md')]:
        check(filename+'_matches_generator',importlib.import_module(module).render()==(BASE/'docs'/filename).read_text())
    check('pipeline_markdown_matches_json',importlib.import_module('resumir_pipeline').render(pipeline)==(BASE/'docs/pipeline-resultados.md').read_text())

    links = []
    for filename in [ROOT/'README.md',BASE/'README.md',BASE/'docs/memo-tecnico.md']:
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',filename.read_text()):
            if re.match(r'https?://|#',target):
                continue
            resolved = (filename.parent/target.split('#')[0]).resolve()
            # El enlace al informe se materializa al terminar esta verificación.
            if resolved != REPORT and not resolved.exists():
                links.append(target)
    check('readme_and_memo_guide_links_exist',not links)
    referenced = ['docs/ingesta-raw-verificacion.json','docs/calidad-bronze.json','docs/calidad-silver.json','docs/calidad-gold.json','docs/obt-verificacion.json','spark/feature-contract.json','docs/pipeline-pruebas.json','docs/reproduccion-limpia.json','README.md']
    result = {'status':'ok','pages':len(pdf),'checks':checks,'source_sha256':sha(SOURCE),'pdf_sha256':sha(OUTPUT),'generator_sha256':sha(BASE/'scripts/generar_memo.py'),'evidence_sha256':{p:sha(BASE/p) for p in referenced},'minimum_font_pt':round(min(s['size'] for s in spans),2),'diagrams':diagram_counts,'missing_fragments':missing,'scope':'Coherencia textual por página, cifras contra JSON, geometría y Markdown derivados. La legibilidad de diagramas requiere además revisión visual de las seis páginas.'}
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if args.render:
        folder = ROOT/'tmp/pdfs/pset2-memo'
        folder.mkdir(parents=True,exist_ok=True)
        for number,page in enumerate(pdf,1):
            page.get_pixmap(matrix=pymupdf.Matrix(1.65,1.65),alpha=False).save(folder/f'pagina-{number}.png')
        print('Renderizadas 6 páginas en tmp/pdfs/pset2-memo (PyMuPDF).')
    print(f'OK: {len(checks)} verificaciones; 6 páginas; fuente y PDF sincronizados.')


if __name__=='__main__':
    main()
