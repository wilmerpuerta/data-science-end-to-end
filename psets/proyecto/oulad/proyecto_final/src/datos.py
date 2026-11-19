"""Datos verificados y registro transaccional privado de cohortes y predicciones."""
from contextlib import contextmanager, closing
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import os
import sqlite3

ROOT = Path(__file__).resolve().parents[1]


def ahora():
    return datetime.now(timezone.utc).isoformat()


def identidad(objeto):
    return hashlib.sha256(json.dumps(objeto, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for bloque in iter(lambda: source.read(8 * 1024 * 1024), b''):
            h.update(bloque)
    return h.hexdigest()


def leer_bundle(local, puntero='snapshot-current.json'):
    local = Path(local).resolve()
    ref = json.loads((local / puntero).read_text())
    folder = (local / ref['directory']).resolve()
    if local not in folder.parents:
        raise ValueError('El bundle debe permanecer en su directorio privado')
    manifest = json.loads((folder / 'manifest.json').read_text())
    if identidad(manifest['identity']) != manifest['id'] or ref['id'] != manifest['id']:
        raise ValueError('Identidad del snapshot inválida')
    for name, entry in manifest['identity']['files'].items():
        if Path(name).name != name or sha256(folder / name) != entry['sha256']:
            raise ValueError('Contenido del snapshot alterado: ' + name)
    return folder, manifest


def desarrollo_temprano(local, corte):
    """Solo etiquetas de desarrollo; purga estudiantes presentes en 2014J."""
    import pandas as pd
    folder, manifest = leer_bundle(local)
    features = pd.read_parquet(folder / 'features.parquet')
    ids_prueba = set(features.loc[features.code_presentation.eq('2014J'), 'id_student'])
    dev = features.loc[features.code_presentation.isin(['2013B', '2013J', '2014B']) & ~features.id_student.isin(ids_prueba)]
    frame = dev.loc[dev.cutoff_day.eq(corte)].copy()
    labels = pd.read_parquet(folder / 'outcomes.parquet')
    labels = labels.loc[labels.enrollment_key.isin(frame.enrollment_key)]
    frame = frame.merge(labels, on='enrollment_key', validate='one_to_one').sort_values('enrollment_key').reset_index(drop=True)
    if frame.target_class.isna().any() or set(frame.id_student) & ids_prueba:
        raise ValueError('Desarrollo incompleto o contaminado')
    return frame, manifest


class Almacen:
    """SQLite actúa como registro durable y outbox; la carga Snowflake es posterior."""
    def __init__(self, ruta):
        self.ruta = Path(ruta)
        self.ruta.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with closing(self.conexion()) as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.executescript('''
                CREATE TABLE IF NOT EXISTS cohortes (
                    cohorte_id TEXT PRIMARY KEY, contenido TEXT NOT NULL, huella TEXT NOT NULL UNIQUE);
                CREATE UNIQUE INDEX IF NOT EXISTS cohortes_contenido ON cohortes(huella);
                CREATE TABLE IF NOT EXISTS lotes (
                    cohorte_id TEXT NOT NULL, corte INTEGER NOT NULL, huella TEXT NOT NULL,
                    respuesta TEXT NOT NULL, PRIMARY KEY(cohorte_id,corte));
                CREATE TABLE IF NOT EXISTS predicciones (
                    id_prediccion TEXT PRIMARY KEY, cohorte_id TEXT NOT NULL, corte INTEGER NOT NULL,
                    matricula TEXT NOT NULL, momento TEXT NOT NULL, entradas TEXT NOT NULL,
                    salida TEXT NOT NULL, modelo TEXT NOT NULL, latencia_ms REAL NOT NULL,
                    UNIQUE(cohorte_id,corte,matricula));
                CREATE TABLE IF NOT EXISTS peticiones (
                    id INTEGER PRIMARY KEY, momento TEXT NOT NULL, codigo INTEGER NOT NULL,
                    latencia_ms REAL NOT NULL);
            ''')
        os.chmod(self.ruta, 0o600)

    def conexion(self):
        db = sqlite3.connect(self.ruta, timeout=60, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA busy_timeout=60000')
        return db

    @contextmanager
    def transaccion(self):
        db = self.conexion()
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def registrar_cohorte(self, contenido):
        """Operación administrativa local; la API pública no admite manifiestos."""
        if set(contenido) != {'cohorte_id', 'base', 'elegibles', 'personas'}:
            raise ValueError('Manifiesto de cohorte inválido')
        base = contenido['base']
        if not base or contenido['elegibles'].get('14') != base or set(contenido['elegibles']) != {'14', '28'}:
            raise ValueError('Se requieren la base completa del día 14 y los dos cortes')
        if set(contenido['personas']) != set(base):
            raise ValueError('Faltan identificadores de persona')
        if any(k not in base or base[k] != v for k, v in contenido['elegibles']['28'].items()):
            raise ValueError('La elegibilidad de día 28 debe pertenecer a la cohorte base')
        huella = identidad({k: v for k, v in contenido.items() if k != 'cohorte_id'})
        with self.transaccion() as db:
            previo = db.execute('SELECT huella FROM cohortes WHERE cohorte_id=?', (contenido['cohorte_id'],)).fetchone()
            if previo and previo['huella'] != huella:
                raise ValueError('No se reemplaza un manifiesto registrado')
            duplicado = db.execute('SELECT cohorte_id FROM cohortes WHERE huella=?', (huella,)).fetchone()
            if duplicado and duplicado['cohorte_id'] != contenido['cohorte_id']:
                raise ValueError('La misma cohorte no obtiene un presupuesto nuevo con otro identificador')
            db.execute('INSERT OR IGNORE INTO cohortes VALUES (?,?,?)', (contenido['cohorte_id'], json.dumps(contenido), huella))

    def registrar_peticion(self, codigo, latencia):
        with self.transaccion() as db:
            db.execute('INSERT INTO peticiones(momento,codigo,latencia_ms) VALUES (?,?,?)', (ahora(), codigo, latencia))

    def metricas(self):
        import numpy as np
        with closing(self.conexion()) as db:
            rows = db.execute('SELECT codigo,latencia_ms FROM peticiones').fetchall()
            volumen = db.execute('SELECT COUNT(*) FROM predicciones').fetchone()[0]
        n = len(rows)
        return {'solicitudes': n, 'predicciones_registradas': volumen,
                'errores_4xx': sum(400 <= r['codigo'] < 500 for r in rows),
                'errores_5xx': sum(r['codigo'] >= 500 for r in rows),
                'tasa_4xx': sum(400 <= r['codigo'] < 500 for r in rows) / n if n else 0,
                'tasa_5xx': sum(r['codigo'] >= 500 for r in rows) / n if n else 0,
                'latencia_p50_ms': float(np.percentile([r['latencia_ms'] for r in rows], 50)) if n else None,
                'latencia_p95_ms': float(np.percentile([r['latencia_ms'] for r in rows], 95)) if n else None}


def generar_ejemplo(carpeta, almacen, cohorte_id='ejemplo-api'):
    """Solo datos sintéticos derivados de una fixture, sin IDs reales ni targets."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True, mode=0o700)
    base = {f'{cohorte_id}-M{i:03}': f'{cohorte_id}-edicion' for i in range(40)}
    personas = {key: key.replace('-M', '-P') for key in base}
    manifest = {'cohorte_id': cohorte_id, 'base': base, 'elegibles': {'14': base, '28': base}, 'personas': personas}
    almacen.registrar_cohorte(manifest)
    (carpeta/'cohorte.json').write_text(json.dumps(manifest, indent=2)+'\n')
    for cut in [14, 28]:
        sample = json.loads((ROOT/'tests/fixtures'/f'muestra_semana{cut//7}.json').read_text())['rows'][0]['features']
        payload = {'cohorte_id': cohorte_id, 'corte_dias': cut,
                   'matriculas': [{'matricula': key, 'edicion': edition, 'persona': personas[key], 'features': sample} for key, edition in base.items()]}
        (carpeta/f'semana{cut//7}.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    print('Ejemplo sintético preparado y cohorte registrada; 40 matrículas, sin etiquetas en las solicitudes.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--registrar-cohorte', type=Path)
    group.add_argument('--ejemplo', type=Path)
    parser.add_argument('--cohorte-id', default='ejemplo-api')
    parser.add_argument('--base-local', type=Path, default=ROOT / '.local/operacion.sqlite')
    args = parser.parse_args()
    almacen = Almacen(args.base_local)
    if args.ejemplo:
        generar_ejemplo(args.ejemplo, almacen, args.cohorte_id)
    else:
        almacen.registrar_cohorte(json.loads(args.registrar_cohorte.read_text()))
        print('Manifiesto registrado; sin llamadas a Snowflake ni predicciones nuevas.')
