"""Auditoría de fuentes y ejecución independiente de los notebooks de entrega.

No entrena modelos, no cambia aliases y no consume API externas.
"""
from pathlib import Path
import argparse
import json
import os
from .datos import ROOT, sha256, leer_bundle


def evidencia():
    return json.loads((ROOT / 'docs/evidencia_modelado.json').read_text())


def desarrollo():
    """Recupera el desarrollo del día 56 sin generar nuevas particiones."""
    import pandas as pd
    local = Path(os.environ.get('PSET4_MODELADO_DIR', ROOT / '.local/modelado'))
    folder, manifest = leer_bundle(local)
    splits, split = leer_bundle(local, 'splits-current.json')
    assert split['identity']['snapshot_id'] == manifest['id']
    assignments = pd.read_csv(splits / 'assignments.csv')
    keys = assignments.loc[assignments.partition.eq('train')]
    features = pd.read_parquet(folder / 'features.parquet')
    x = features.loc[features.cutoff_day.eq(56)].merge(keys, on=['enrollment_key', 'id_student'], validate='one_to_one')
    labels = pd.read_parquet(folder / 'outcomes.parquet')
    x = x.merge(labels, on='enrollment_key', validate='one_to_one')
    # La partición histórica del día 56 purga las personas elegibles a ese corte.
    # La preparación temprana usa una purga propia y una población diferente.
    prueba = features.loc[features.cutoff_day.eq(56) & features.code_presentation.eq('2014J')]
    assert not set(x.id_student) & set(prueba.id_student)
    assert len(x) == len(keys) and set(x.cv_fold) == set(range(5))
    assert x.groupby('id_student').cv_fold.nunique().max() == 1
    return x.sort_values('enrollment_key').reset_index(drop=True), manifest, split


def auditar_pset1(data=None):
    """Relee los cinco originales en bloques y contrasta con PSet1 sin sobrescribirlo.

    Los duplicados de actividad se cuentan dentro de cada bloque, no globalmente.
    Los nulos en fechas no se imputan. No devuelve identificadores individuales.
    """
    import pandas as pd
    data = Path(data or os.environ.get('PSET4_DATA_DIR', ROOT / '.local/datos'))
    historical = evidencia()['auditoria_pset1']
    names = ['studentInfo', 'studentRegistration', 'courses', 'vle', 'studentVle']
    files = {}
    for name in names:
        p = data / (name + '.csv')
        expected = historical['manifest']['files'][p.name]
        files[p.name] = {'sha256': sha256(p), 'bytes': p.stat().st_size}
        assert files[p.name]['sha256'] == expected['sha256'], 'Contenido diferente: ' + p.name
        assert files[p.name]['bytes'] == expected['bytes']
    key = ['code_module', 'code_presentation', 'id_student']
    tables = {n: pd.read_csv(data / (n + '.csv')) for n in names[:-1]}
    checks = {}
    nulls = {}
    for name, table in tables.items():
        cols = key if name.startswith('student') else ['code_module', 'code_presentation'] + (['id_site'] if name == 'vle' else [])
        checks[name] = {'rows': len(table), 'duplicate_keys': int(table.duplicated(cols).sum()), 'missing_key_values': int(table[cols].isna().any(axis=1).sum())}
        assert checks[name] == historical['checks'][name]
        nulls[name] = {c: int(v) for c, v in table.isna().sum().items()}
    info = tables['studentInfo']; reg = tables['studentRegistration']
    joined = info.merge(reg, on=key, validate='one_to_one', indicator=True)
    assert len(joined) == len(info) == len(reg) and joined['_merge'].eq('both').all()
    enrollment_keys = pd.MultiIndex.from_frame(info[key])
    site_keys = pd.MultiIndex.from_frame(tables['vle'][['code_module', 'code_presentation', 'id_site']])
    course_keys = pd.MultiIndex.from_frame(tables['courses'][['code_module', 'code_presentation']])
    assert pd.MultiIndex.from_frame(info[['code_module', 'code_presentation']]).isin(course_keys).all()
    active = {d: set() for d in [14, 28, 42, 56]}
    rows = orphan = orphan_site = negative = duplicates = clicks = 0
    low = 10**9; high = -10**9; nulls['studentVle'] = {}
    editions = {}
    for chunk in pd.read_csv(data / 'studentVle.csv', chunksize=300000):
        rows += len(chunk)
        orphan += int((~pd.MultiIndex.from_frame(chunk[key]).isin(enrollment_keys)).sum())
        orphan_site += int((~pd.MultiIndex.from_frame(chunk[['code_module', 'code_presentation', 'id_site']]).isin(site_keys)).sum())
        negative += int(chunk.sum_click.lt(0).sum()); clicks += int(chunk.sum_click.sum())
        duplicates += int(chunk.duplicated(key + ['id_site', 'date']).sum())
        low = min(low, int(chunk.date.min())); high = max(high, int(chunk.date.max()))
        for c, value in chunk.isna().sum().items(): nulls['studentVle'][c] = nulls['studentVle'].get(c, 0) + int(value)
        for d in active: active[d].update(chunk.loc[chunk.date.le(d), key].itertuples(index=False, name=None))
        for k, v in chunk.groupby(['code_module', 'code_presentation']).size().items(): editions['/'.join(k)] = editions.get('/'.join(k), 0) + int(v)
    checks['studentVle'] = {'rows': rows, 'orphan_enrollment_rows': orphan, 'orphan_resource_rows': orphan_site, 'negative_click_rows': negative, 'date_min': low, 'date_max': high, 'duplicate_keys_within_chunks': duplicates}
    for k, v in checks['studentVle'].items(): assert v == historical['checks']['studentVle'][k], k
    assert nulls == historical['missing_values'] and editions == historical['activity_rows_by_edition']
    initial = joined.loc[joined.date_registration.notna() & joined.date_registration.le(0)]
    def counts(frame):
        return {'N': len(frame), 'Fail': int(frame.final_result.eq('Fail').sum()), 'Withdrawn': int(frame.final_result.eq('Withdrawn').sum()), 'Approved': int(frame.final_result.isin(['Pass', 'Distinction']).sum())}
    populations = {'original': counts(info), 'initial': counts(initial), 'unique_students': int(info.id_student.nunique()), 'late_registration': int(joined.date_registration.gt(0).sum()), 'missing_registration_date': int(joined.date_registration.isna().sum()), 'cuts': {}}
    for d in active:
        eligible = initial.loc[initial.date_unregistration.isna() | initial.date_unregistration.gt(d)]
        c = counts(eligible)
        c.update(K_sum_by_edition=sum(len(g)//10 for _, g in eligible.groupby(['code_module', 'code_presentation'])), without_recorded_activity=sum(k not in active[d] for k in eligible[key].itertuples(index=False, name=None)), withdrawn_by_cut=len(initial)-len(eligible))
        populations['cuts'][str(d)] = c
    assert populations == historical['populations']
    return {'estado': 'verificado', 'archivos': files, 'checks': checks, 'poblaciones': populations, 'faltantes': nulls, 'clics_totales': clicks, 'alcance': 'Relectura completa; fuentes y cifras PSet1 coinciden. Duplicados dentro de bloques no equivalen a duplicados globales. No se modificaron archivos históricos.'}


def ejecutar():
    import sys
    import nbformat
    from nbclient import NotebookClient
    from jupyter_client import KernelManager
    report = []
    for path in sorted((ROOT / 'notebooks').glob('0*.ipynb')):
        book = nbformat.read(path, as_version=4)
        kernel = KernelManager(kernel_name='python3')
        kernel.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
        NotebookClient(book, timeout=900, km=kernel, resources={'metadata': {'path': str(ROOT)}}).execute(cleanup_kc=True)
        nbformat.write(book, path)
        cells = [c for c in book.cells if c.cell_type == 'code']
        assert all(c.execution_count is not None for c in cells)
        report.append({'notebook': path.name, 'celdas_codigo': len(cells), 'errores': 0, 'sha256': sha256(path)})
        print(path.name, 'OK', flush=True)
    (ROOT / 'docs/verificacion_notebooks.json').write_text(json.dumps({'fecha': '2026-11-24', 'modo': 'Kernel nuevo por notebook, ejecución secuencial completa; sin servicios externos ni ajuste de clasificadores.', 'notebooks': report}, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ejecutar', action='store_true', required=True)
    parser.parse_args()
    ejecutar()
