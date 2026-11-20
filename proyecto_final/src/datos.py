"""Datos verificados y registro transaccional privado de cohortes y predicciones."""
from contextlib import contextmanager, closing
from datetime import datetime, timezone
from pathlib import Path
import argparse
import csv
import gzip
import shutil
import tempfile
import uuid
import hashlib
import json
import os
import sqlite3
import re
import urllib.request
from decimal import Decimal

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
            campos = {r[1] for r in db.execute('PRAGMA table_info(peticiones)')}
            for campo in ['plan_id', 'lote_id', 'execution_id']:
                if campo not in campos:
                    db.execute(f'ALTER TABLE peticiones ADD COLUMN {campo} TEXT')
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

    def registrar_peticion(self, codigo, latencia, plan_id=None, lote_id=None, execution_id=None):
        with self.transaccion() as db:
            db.execute('INSERT INTO peticiones(momento,codigo,latencia_ms,plan_id,lote_id,execution_id) VALUES (?,?,?,?,?,?)', (ahora(), codigo, latencia, plan_id, lote_id, execution_id))

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


PLAN_CONTROL = 'oulad-2014j-control-v1'
PLAN_DERIVA = 'oulad-2014j-deriva-v1'
ESQUEMA_OPERACION = 'PSET2_OULAD.ANALYTICS'
MARCA_OPERACION = 'oulad.pset4.operacion.v1'
PROTOCOLO_LOTES = {
    'version': 'control-retrospectivo-1', 'presentacion': '2014J',
    'cortes': [14, 28], 'ondas_por_corte': 4, 'demora_maxima_despacho_dias': 3,
    'demora_etiqueta_dias': 14, 'reloj': 'dias relativos simulados; origen 0 sin fecha calendario afirmada',
    'grano': 'matricula-asignatura; ediciones completas y presupuesto compartido entre cortes',
    'asignacion': 'modulos ordenados alfabeticamente, distribuidos circularmente entre cuatro ondas',
    'limitacion': 'Una presentacion historica, no ocho semestres independientes. Holdout ya examinado en PSet 03.',
    'etiquetas': 'Disponibilidad supuesta al fin del modulo mas 14 dias; OULAD no informa fecha de publicacion.',
    'features': 'Congeladas en dia 14 o 28; retraso de despacho 0..3 dias, sin incorporar actividad posterior.',
    'escenario': 'control original, sin deriva inducida; no mide efecto causal de tutorias',
}


def normalizar(valor):
    """JSON finito sin convertir categorías ni nulos en cadenas."""
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, dict):
        return {k: normalizar(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [normalizar(v) for v in valor]
    return valor


def construir_lotes(registros, plan_id=PLAN_CONTROL):
    """Solo features: cuatro ondas de ediciones completas por cada corte."""
    if not re.fullmatch(r'[a-z0-9-]{1,80}', plan_id):
        raise ValueError('Identificador de plan inválido')
    firma = json.loads(json.loads((ROOT/'tests/fixtures/referencia.json').read_text())['modelos']['14']['signature']['inputs'])
    numericas = {f['name'] for f in firma if f['type'] == 'double'}
    nombres = {f['name'] for f in firma}
    filas = [normalizar(dict(r)) for r in registros]
    permitidos = nombres | {'enrollment_key', 'cutoff_day', 'id_student', 'edition_key', 'code_module', 'code_presentation'}
    if not filas or any(set(r) != permitidos or r['code_presentation'] != '2014J' or r['cutoff_day'] not in [14, 28] for r in filas):
        raise ValueError('Fuente incompatible o con columnas adicionales; no se admiten targets')
    pares = [(r['enrollment_key'], int(r['cutoff_day'])) for r in filas]
    if len(pares) != len(set(pares)):
        raise ValueError('Clave matrícula-corte duplicada')
    modulos = sorted({r['code_module'] for r in filas})
    if len(modulos) < 4:
        raise ValueError('Se necesitan al menos cuatro grupos de ediciones completas')
    ondas = [modulos[i::4] for i in range(4)]
    lotes = []
    for onda, modules in enumerate(ondas):
        subset = [r for r in filas if r['code_module'] in modules]
        por_corte = {cut: sorted([r for r in subset if r['cutoff_day'] == cut], key=lambda r: r['enrollment_key']) for cut in [14, 28]}
        if not all(por_corte.values()):
            raise ValueError('Onda sin datos en uno de los cortes')
        def clave(r): return 'm_' + identidad(str(r['enrollment_key']))[:40]
        base = {clave(r): str(r['edition_key']) for r in por_corte[14]}
        personas = {clave(r): 'p_' + identidad(str(r['id_student']))[:40] for r in por_corte[14]}
        elegibles = {str(cut): {clave(r): str(r['edition_key']) for r in rows} for cut, rows in por_corte.items()}
        if not set(elegibles['28']) <= set(base):
            raise ValueError('La ronda 28 contiene matrículas ajenas a la base del día 14')
        cohorte_id = f'{plan_id}-onda{onda+1}'
        manifiesto = {'cohorte_id': cohorte_id, 'base': base, 'elegibles': elegibles, 'personas': personas}
        for cut, rows in por_corte.items():
            matriculas = []
            fuentes = {}
            for r in rows:
                f = {n: float(r[n]) if n in numericas and r[n] is not None else r[n] for n in nombres}
                key = clave(r)
                matriculas.append({'matricula': key, 'edicion': str(r['edition_key']), 'persona': personas[key], 'features': f})
                fuentes[key] = {'enrollment_key': str(r['enrollment_key']), 'fin_periodo': int(r['module_presentation_length'])}
            orden = onda + 1 + (4 if cut == 28 else 0)
            lote = {'plan_id': plan_id, 'lote_id': f'L{orden:02}', 'orden': orden, 'dia': cut+onda,
                    'corte': cut, 'cohorte_id': cohorte_id, 'modulos': modules,
                    'manifiesto': manifiesto, 'fuentes': fuentes,
                    'solicitud': {'cohorte_id': cohorte_id, 'corte_dias': cut, 'matriculas': matriculas}}
            identidad(lote)  # Rechaza NaN antes de persistir.
            lotes.append(lote)
    return sorted(lotes, key=lambda r: r['orden'])


# Contratos explícitos. No se reutilizan ni reemplazan tablas Raw, Gold u OBT.
TABLAS_OPERACION = {
    'PLANES': {'PLAN_ID': 'VARCHAR', 'CONTENIDO': 'VARIANT', 'HUELLA': 'VARCHAR'},
    'LOTES_ENTRADA': {'PLAN_ID': 'VARCHAR', 'LOTE_ID': 'VARCHAR', 'ORDEN': 'NUMBER', 'DIA': 'NUMBER', 'CORTE': 'NUMBER', 'COHORTE_ID': 'VARCHAR', 'CONTENIDO': 'VARIANT', 'HUELLA': 'VARCHAR'},
    'PREDICCIONES': {'ID_PREDICCION': 'VARCHAR', 'PLAN_ID': 'VARCHAR', 'LOTE_ID': 'VARCHAR', 'COHORTE_ID': 'VARCHAR', 'MATRICULA': 'VARCHAR', 'CORTE': 'NUMBER', 'DIA_SIMULADO': 'NUMBER',
                     'TIMESTAMP': 'TIMESTAMP_TZ', 'ENTRADAS': 'VARIANT', 'SALIDA': 'VARIANT', 'MODELO': 'VARCHAR', 'VERSION_MODELO': 'VARCHAR', 'RUN_ID': 'VARCHAR',
                     'SNAPSHOT_ID': 'VARCHAR', 'SPLIT_ID': 'VARCHAR', 'GOLD': 'VARCHAR', 'POLITICA_ID': 'VARCHAR', 'RESPALDO': 'BOOLEAN', 'LATENCIA_MS': 'FLOAT', 'HUELLA': 'VARCHAR'},
    'LOTES_PROCESADOS': {'PLAN_ID': 'VARCHAR', 'LOTE_ID': 'VARCHAR', 'CONTENIDO': 'VARIANT', 'HUELLA': 'VARCHAR'},
    'ETIQUETAS': {'PLAN_ID': 'VARCHAR', 'MATRICULA': 'VARCHAR', 'TARGET_CLASS': 'VARCHAR', 'DIA_DISPONIBLE': 'NUMBER', 'HUELLA': 'VARCHAR'},
}
CLAVES_OPERACION = {'PLANES': ['PLAN_ID'], 'LOTES_ENTRADA': ['PLAN_ID', 'LOTE_ID'],
                    'PREDICCIONES': ['ID_PREDICCION'], 'LOTES_PROCESADOS': ['PLAN_ID', 'LOTE_ID'], 'ETIQUETAS': ['PLAN_ID', 'MATRICULA']}


class RepositorioSnowflake:
    """Un escritor Kestra, inserciones inmutables y conciliación antes de completar."""
    def __init__(self, conexion):
        self.conn = conexion

    def asegurar(self):
        with self.conn.cursor() as cur:
            # ANALYTICS ya está autorizado para el servicio; no se amplían permisos ni se altera su OBT.
            for tabla, columnas in TABLAS_OPERACION.items():
                definicion = ','.join(f'"{n}" {t}' for n, t in columnas.items())
                cur.execute(f"CREATE TABLE IF NOT EXISTS {ESQUEMA_OPERACION}.{tabla} ({definicion}) COMMENT='{MARCA_OPERACION}:{tabla}'")
                row = cur.execute("SELECT COMMENT FROM PSET2_OULAD.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='ANALYTICS' AND TABLE_NAME=%s", (tabla,)).fetchone()
                if not row or row[0] != MARCA_OPERACION+':'+tabla:
                    raise ValueError('Tabla existente ajena a este contrato')
                actual = cur.execute(f'DESC TABLE {ESQUEMA_OPERACION}.{tabla}').fetchall()
                if [r[0] for r in actual] != list(columnas) or any(not row[1].startswith(tipo) for row, tipo in zip(actual, columnas.values())):
                    raise ValueError('Columnas de operación incompatibles')
            cur.execute(f"CREATE TABLE IF NOT EXISTS {ESQUEMA_OPERACION}.RELOJ (PLAN_ID VARCHAR, DIA NUMBER) COMMENT='{MARCA_OPERACION}:RELOJ'")
            row = cur.execute("SELECT COMMENT FROM PSET2_OULAD.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='ANALYTICS' AND TABLE_NAME='RELOJ'").fetchone()
            if not row or row[0] != MARCA_OPERACION+':RELOJ':
                raise ValueError('Reloj existente ajeno al contrato')

    def insertar(self, tabla, filas):
        """Staging temporal antes de BEGIN: el DDL nunca corta la transacción DML."""
        columnas = TABLAS_OPERACION[tabla]
        filas = [normalizar(r) for r in filas]
        if not filas:
            return 0
        claves = CLAVES_OPERACION[tabla]
        seen = set()
        for r in filas:
            if set(r) != set(columnas) - {'HUELLA'}:
                raise ValueError('Registro incompleto')
            key = tuple(r[n] for n in claves)
            if key in seen:
                raise ValueError('Clave de carga duplicada')
            seen.add(key)
            r['HUELLA'] = identidad(r)
        with self.conn.cursor() as cur:
            cur.execute('CREATE OR REPLACE TEMPORARY TABLE PSET4_CARGA_JSON (RAW VARCHAR)')
            for offset in range(0, len(filas), 500):
                cur.executemany('INSERT INTO PSET4_CARGA_JSON VALUES (%s)', [(json.dumps(r, allow_nan=False),) for r in filas[offset:offset+500]])
            seleccion = ','.join(f'PARSE_JSON(RAW):{n}::{t} AS "{n}"' for n, t in columnas.items())
            source = f'(SELECT {seleccion} FROM PSET4_CARGA_JSON)'
            on = ' AND '.join(f'T."{k}"=S."{k}"' for k in claves)
            names = ','.join(f'"{n}"' for n in columnas)
            values = ','.join(f'S."{n}"' for n in columnas)
            cur.execute('BEGIN')
            try:
                conflict = cur.execute(f'SELECT COUNT(*) FROM {ESQUEMA_OPERACION}.{tabla} T JOIN {source} S ON {on} WHERE T.HUELLA<>S.HUELLA').fetchone()[0]
                if conflict:
                    raise ValueError('La carga intenta cambiar registros publicados')
                cur.execute(f'MERGE INTO {ESQUEMA_OPERACION}.{tabla} T USING {source} S ON {on} WHEN NOT MATCHED THEN INSERT ({names}) VALUES ({values})')
                n, unique = cur.execute(f'SELECT COUNT(*),COUNT(DISTINCT T.HUELLA) FROM {ESQUEMA_OPERACION}.{tabla} T JOIN {source} S ON {on} AND T.HUELLA=S.HUELLA').fetchone()
                if n != len(filas) or unique != len(filas):
                    raise ValueError('Conciliación incompleta o duplicada')
                self.conn.commit()
            except BaseException:
                self.conn.rollback()
                raise
        return len(filas)

    def contenido(self, tabla, plan_id, lote_id=None):
        if tabla not in ['PLANES', 'LOTES_ENTRADA', 'LOTES_PROCESADOS']:
            raise ValueError('Tabla no permitida')
        where = 'PLAN_ID=%s' + (' AND LOTE_ID=%s' if lote_id else '')
        params = (plan_id, lote_id) if lote_id else (plan_id,)
        with self.conn.cursor() as cur:
            rows = cur.execute(f'SELECT CONTENIDO,HUELLA FROM {ESQUEMA_OPERACION}.{tabla} WHERE {where}', params).fetchall()
        if len(rows) > 1:
            raise ValueError('Clave Snowflake duplicada')
        if not rows:
            return None
        return json.loads(rows[0][0]) if isinstance(rows[0][0], str) else rows[0][0]

    def reloj(self, plan_id, nuevo=None):
        with self.conn.cursor() as cur:
            rows = cur.execute(f'SELECT DIA FROM {ESQUEMA_OPERACION}.RELOJ WHERE PLAN_ID=%s', (plan_id,)).fetchall()
            if len(rows) > 1:
                raise ValueError('Reloj duplicado')
            actual = int(rows[0][0]) if rows else 0
            if nuevo is not None:
                if nuevo < actual:
                    raise ValueError('El reloj no retrocede')
                if rows:
                    cur.execute(f'UPDATE {ESQUEMA_OPERACION}.RELOJ SET DIA=%s WHERE PLAN_ID=%s', (nuevo, plan_id))
                else:
                    cur.execute(f'INSERT INTO {ESQUEMA_OPERACION}.RELOJ VALUES (%s,%s)', (plan_id, nuevo))
                actual = nuevo
        return actual


def conectar_snowflake():
    import snowflake.connector
    config_path = Path(os.environ.get('SNOWFLAKE_CONNECTION_FILE', '/run/secrets/snowflake_connection.json'))
    key_path = Path(os.environ.get('SNOWFLAKE_PRIVATE_KEY_FILE', '/run/secrets/snowflake_key.p8'))
    config = json.loads(config_path.read_text())
    if config.get('schema_version') != 1:
        raise ValueError('Configuración privada incompatible')
    return snowflake.connector.connect(account=config['account'], user='PSET2_SVC', role='PSET2_PIPELINE',
        database='PSET2_OULAD', schema='ANALYTICS', warehouse='PSET2_WH', authenticator='SNOWFLAKE_JWT',
        private_key_file=str(key_path), private_key_file_pwd=config['private_key_passphrase'], login_timeout=30, network_timeout=120,
        session_parameters={'QUERY_TAG': 'pset04_operacion', 'STATEMENT_TIMEOUT_IN_SECONDS': 300})


def preparar_plan(repo, plan_id=PLAN_CONTROL):
    if plan_id == PLAN_DERIVA:
        from monitoreo.alertas import PROTOCOLO_MONITOREO
        import copy
        import random
        control = repo.contenido('PLANES', PLAN_CONTROL)
        if control is None:
            raise ValueError('Preparar primero el control original')
        previo = repo.contenido('PLANES', plan_id)
        if previo:
            if previo['protocolo'] != PROTOCOLO_MONITOREO['induccion']:
                raise ValueError('Protocolo de deriva alterado')
            return {'plan_id': plan_id, 'lotes': 8, 'etiquetas_consultadas': False}
        lotes = []
        for item in control['lotes']:
            lote = copy.deepcopy(repo.contenido('LOTES_ENTRADA', PLAN_CONTROL, item['lote_id']))
            lote['plan_id'] = plan_id
            lote['cohorte_id'] = lote['cohorte_id'].replace(PLAN_CONTROL, plan_id)
            lote['manifiesto']['cohorte_id'] = lote['cohorte_id']
            lote['solicitud']['cohorte_id'] = lote['cohorte_id']
            lote['alterado'] = lote['lote_id'] in PROTOCOLO_MONITOREO['induccion']['lotes']
            if lote['alterado']:
                por_edicion = {}
                for row in lote['solicitud']['matriculas']:
                    por_edicion.setdefault(row['edicion'], []).append(row)
                for edicion, rows in sorted(por_edicion.items()):
                    rows.sort(key=lambda r: r['matricula'])
                    donor = [copy.deepcopy(r['features']) for r in rows]
                    random.Random(PROTOCOLO_MONITOREO['induccion']['seed']+lote['orden']).shuffle(donor)
                    for row, features in zip(rows, donor):
                        # Las features completas viajan juntas para preservar su coherencia interna.
                        if features['studied_credits'] is not None: features['studied_credits'] += PROTOCOLO_MONITOREO['induccion']['desplazamiento_creditos']
                        row['features'] = features
            lotes.append(lote)
        repo.insertar('LOTES_ENTRADA', [{'PLAN_ID': plan_id, 'LOTE_ID': l['lote_id'], 'ORDEN': l['orden'], 'DIA': l['dia'],
            'CORTE': l['corte'], 'COHORTE_ID': l['cohorte_id'], 'CONTENIDO': l} for l in lotes])
        plan = {'plan_id': plan_id, 'protocolo': PROTOCOLO_MONITOREO['induccion'], 'control': PLAN_CONTROL,
                'matriculas_corte': control['matriculas_corte'], 'lotes': [{k:l[k] for k in ['lote_id','orden','dia','corte','cohorte_id','modulos']} for l in lotes]}
        repo.insertar('PLANES', [{'PLAN_ID': plan_id, 'CONTENIDO': plan}])
        return {'plan_id': plan_id, 'lotes': 8, 'etiquetas_consultadas': False}
    anterior = repo.contenido('PLANES', plan_id)
    if anterior:
        if anterior['protocolo'] != PROTOCOLO_LOTES:
            raise ValueError('Versionar el plan antes de cambiar su protocolo')
        for item in anterior['lotes']:
            lote = repo.contenido('LOTES_ENTRADA', plan_id, item['lote_id'])
            if lote is None:
                raise ValueError('Plan publicado sin todos sus lotes')
        return {'plan_id': plan_id, 'lotes': len(anterior['lotes']), 'matriculas_corte': anterior['matriculas_corte'], 'etiquetas_consultadas': False}
    else:
        meta = json.loads((ROOT/'tests/fixtures/referencia.json').read_text())
        nombres = [f['name'] for f in json.loads(meta['modelos']['14']['signature']['inputs'])]
        columnas = ['enrollment_key', 'cutoff_day', 'id_student', 'edition_key', 'code_module', 'code_presentation'] + nombres
        with repo.conn.cursor() as cur:
            cur.execute('SELECT '+','.join(columnas)+" FROM PSET2_OULAD.ANALYTICS.OBT_FEATURES WHERE CODE_PRESENTATION='2014J' AND CUTOFF_DAY IN (14,28) ORDER BY ENROLLMENT_KEY,CUTOFF_DAY")
            registros = [dict(zip(columnas, row)) for row in cur.fetchall()]
        lotes = construir_lotes(registros, plan_id)
        anterior = {'plan_id': plan_id, 'protocolo': PROTOCOLO_LOTES, 'fuente': 'PSET2_OULAD.ANALYTICS.OBT_FEATURES',
                    'fuente_contenido_sha256': identidad(normalizar(registros)),
                    'matriculas_corte': sum(len(l['solicitud']['matriculas']) for l in lotes),
                    'lotes': [{k: l[k] for k in ['lote_id', 'orden', 'dia', 'corte', 'cohorte_id', 'modulos']} for l in lotes]}
    repo.insertar('LOTES_ENTRADA', [{'PLAN_ID': plan_id, 'LOTE_ID': l['lote_id'], 'ORDEN': l['orden'], 'DIA': l['dia'],
        'CORTE': l['corte'], 'COHORTE_ID': l['cohorte_id'], 'CONTENIDO': l} for l in lotes])
    # El plan se publica al final: un fallo parcial se repara sin aceptar cambios de contenido.
    repo.insertar('PLANES', [{'PLAN_ID': plan_id, 'CONTENIDO': anterior}])
    return {'plan_id': plan_id, 'lotes': len(lotes), 'matriculas_corte': sum(len(l['solicitud']['matriculas']) for l in lotes), 'etiquetas_consultadas': False}


def filas_predicciones(almacen, lote, respuesta):
    with closing(almacen.conexion()) as db:
        rows = db.execute('SELECT * FROM predicciones WHERE cohorte_id=? AND corte=? ORDER BY matricula', (lote['cohorte_id'], lote['corte'])).fetchall()
    if len(rows) != len(lote['solicitud']['matriculas']):
        raise ValueError('El outbox no contiene el lote completo')
    ids = {r['id_prediccion'] for r in respuesta['predicciones']}
    if ids != {r['id_prediccion'] for r in rows}:
        raise ValueError('El outbox y la respuesta no coinciden')
    resultado = []
    for r in rows:
        m = json.loads(r['modelo']); salida = json.loads(r['salida'])
        resultado.append({'ID_PREDICCION': r['id_prediccion'], 'PLAN_ID': lote['plan_id'], 'LOTE_ID': lote['lote_id'],
            'COHORTE_ID': r['cohorte_id'], 'MATRICULA': r['matricula'], 'CORTE': r['corte'], 'DIA_SIMULADO': lote['dia'],
            'TIMESTAMP': r['momento'], 'ENTRADAS': json.loads(r['entradas']), 'SALIDA': salida,
            'MODELO': m['nombre'], 'VERSION_MODELO': str(m['version']), 'RUN_ID': m['run_id'],
            'SNAPSHOT_ID': m['snapshot_id'], 'SPLIT_ID': m['split_id'], 'GOLD': m['gold'],
            'POLITICA_ID': respuesta['politica_id'], 'RESPALDO': bool(salida['respaldo']), 'LATENCIA_MS': r['latencia_ms']})
    return resultado


def procesar_lote(repo, almacen, lote_id, api_url, plan_id=PLAN_CONTROL, execution_id='manual'):
    previo = repo.contenido('LOTES_PROCESADOS', plan_id, lote_id)
    if previo:
        return {**previo, 'repeticion': True}
    lote = repo.contenido('LOTES_ENTRADA', plan_id, lote_id)
    if lote is None:
        raise ValueError('Lote no registrado')
    for n in range(1, lote['orden']):
        if repo.contenido('LOTES_PROCESADOS', plan_id, f'L{n:02}') is None:
            raise ValueError('Debe completarse el lote precedente')
    repo.reloj(plan_id, lote['dia'])
    almacen.registrar_cohorte(lote['manifiesto'])
    body = json.dumps(lote['solicitud'], allow_nan=False).encode()
    request = urllib.request.Request(api_url.rstrip('/')+'/predecir', data=body, headers={'Content-Type': 'application/json',
        'X-Pset4-Plan': plan_id, 'X-Pset4-Lote': lote_id, 'X-Pset4-Ejecucion': execution_id})
    with urllib.request.urlopen(request, timeout=180) as response:
        respuesta = json.load(response)
    filas = filas_predicciones(almacen, lote, respuesta)
    repo.insertar('PREDICCIONES', filas)
    resumen = {'plan_id': plan_id, 'lote_id': lote_id, 'orden': lote['orden'], 'dia_simulado': lote['dia'],
        'corte_dias': lote['corte'], 'predicciones': len(filas), 'nuevas_propuestas': respuesta['nuevas_propuestas'],
        'version_modelo': respuesta['modelo']['version'], 'run_id': respuesta['modelo']['run_id'],
        'respaldo': respuesta['respaldo'], 'execution_id': execution_id, 'etiquetas_disponibles': False}
    repo.insertar('LOTES_PROCESADOS', [{'PLAN_ID': plan_id, 'LOTE_ID': lote_id, 'CONTENIDO': resumen}])
    return resumen


def liberar_etiquetas(repo, dia, plan_id=PLAN_CONTROL):
    plan = repo.contenido('PLANES', plan_id)
    if plan is None or any(repo.contenido('LOTES_PROCESADOS', plan_id, l['lote_id']) is None for l in plan['lotes']):
        raise ValueError('Completar predicciones antes de liberar etiquetas')
    repo.reloj(plan_id, dia)
    fuentes = {}
    for item in plan['lotes']:
        lote = repo.contenido('LOTES_ENTRADA', plan_id, item['lote_id'])
        fuentes.update(lote['fuentes'])
    maduras = {m: f for m, f in fuentes.items() if f['fin_periodo'] + PROTOCOLO_LOTES['demora_etiqueta_dias'] <= dia}
    if not maduras:
        return {'plan_id': plan_id, 'dia_simulado': dia, 'etiquetas': 0, 'fuente_target_consultada': False}
    por_clave = {f['enrollment_key']: m for m, f in maduras.items()}
    # El filtro se aplica en Snowflake: ni siquiera se extraen resultados inmaduros.
    with repo.conn.cursor() as cur:
        rows = cur.execute('''SELECT O.ENROLLMENT_KEY,O.TARGET_CLASS FROM PSET2_OULAD.GOLD.OUTCOME_ENROLLMENT O
            JOIN PSET2_OULAD.GOLD.FACT_ENROLLMENT E ON E.ENROLLMENT_KEY=O.ENROLLMENT_KEY
            JOIN PSET2_OULAD.GOLD.DIM_EDITION D ON D.EDITION_KEY=E.EDITION_KEY
            WHERE D.CODE_PRESENTATION='2014J' AND D.MODULE_PRESENTATION_LENGTH+%s<=%s''',
            (PROTOCOLO_LOTES['demora_etiqueta_dias'], dia)).fetchall()
    labels = {key: target for key, target in rows if key in por_clave}
    if set(labels) != set(por_clave) or not set(labels.values()) <= {'Approved', 'Fail', 'Withdrawn'}:
        raise ValueError('Etiquetas maduras incompletas')
    repo.insertar('ETIQUETAS', [{'PLAN_ID': plan_id, 'MATRICULA': por_clave[k], 'TARGET_CLASS': target,
        'DIA_DISPONIBLE': maduras[por_clave[k]]['fin_periodo']+PROTOCOLO_LOTES['demora_etiqueta_dias']} for k, target in labels.items()])
    return {'plan_id': plan_id, 'dia_simulado': dia, 'etiquetas': len(labels), 'fuente_target_consultada': True}


def exportar_predicciones(repo, destino, plan_id=PLAN_CONTROL):
    """Exportación auditable sin targets ni ejemplos sintéticos ajenos al plan."""
    import csv
    columnas = list(TABLAS_OPERACION['PREDICCIONES'])
    with repo.conn.cursor() as cur:
        planes = [plan_id] if plan_id is not None else [PLAN_CONTROL, PLAN_DERIVA]
        where = 'PLAN_ID IN ('+','.join(['%s']*len(planes))+')'
        rows = cur.execute('SELECT '+','.join(f'"{c}"' for c in columnas)+f' FROM {ESQUEMA_OPERACION}.PREDICCIONES WHERE '+where+' ORDER BY PLAN_ID,LOTE_ID,MATRICULA', tuple(planes)).fetchall()
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(destino.suffix+'.tmp')
    with temporal.open('w', newline='') as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow([c.lower() for c in columnas])
        for row in rows:
            writer.writerow([json.dumps(json.loads(value), separators=(',', ':'), ensure_ascii=False) if TABLAS_OPERACION['PREDICCIONES'][col]=='VARIANT' else value for col, value in zip(columnas, row)])
    temporal.replace(destino)
    return {'plan_id': plan_id, 'predicciones_exportadas': len(rows), 'sha256': sha256(destino)}


ARCHIVOS_RAW = {'studentInfo.csv':'STUDENTINFO','studentRegistration.csv':'STUDENTREGISTRATION',
                'courses.csv':'COURSES','vle.csv':'VLE','studentVle.csv':'STUDENTVLE'}
INGESTA_DATA = Path('/datasets')
INGESTA_RAW = ROOT/'.local/ingesta/raw'
CTX_RAW = ('PSET2_SVC','PSET2_PIPELINE','PSET2_OULAD','RAW','PSET2_WH')


def validar_execution_id(valor):
    if not isinstance(valor,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',valor):
        raise ValueError('Identificador de ejecución inválido')
    return valor


def guardar_informe(path,contenido):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(contenido,ensure_ascii=False,indent=2)+'\n')
    tmp.chmod(0o600);tmp.replace(path)


def conectar_raw():
    conn=conectar_snowflake()
    with conn.cursor() as cur:
        cur.execute('USE SCHEMA RAW')
        cur.execute("ALTER SESSION SET QUERY_TAG='pset04_ingesta_raw'")
    return conn


def raw_verified_files(selected):
    manifest = json.loads((INGESTA_DATA / 'manifest.json').read_text())
    names = list(ARCHIVOS_RAW) if selected == 'all' else [selected]
    result = []
    for name in names:
        meta = manifest['files'][name]
        path = INGESTA_DATA / name
        h = hashlib.sha256()
        with path.open('rb') as f:
            for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
                h.update(b)
        if h.hexdigest() != meta['sha256'] or path.stat().st_size != meta['bytes']:
            raise RuntimeError('input_checksum_mismatch')
        with path.open(newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            columns = next(reader)
            count = 0
            for row in reader:
                if len(row) != len(columns):
                    raise RuntimeError('source_column_count_mismatch')
                count += 1
            if count != meta['rows']:
                raise RuntimeError('source_row_count_mismatch')
        if not columns or len(set(columns)) != len(columns) or (not all((re.fullmatch('[a-z][a-z0-9_]*', c) for c in columns))):
            raise RuntimeError('invalid_source_columns')
        result.append((name, meta, columns))
    return result

def raw_ensure_managed(cur, table, definition, marker):
    cur.execute(f"CREATE TABLE IF NOT EXISTS {table} ({definition}) COMMENT='{marker}'")
    row = cur.execute("SELECT COMMENT FROM PSET2_OULAD.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='RAW' AND TABLE_NAME=%s", (table,)).fetchone()
    if not row or row[0] != marker:
        raise RuntimeError('unmanaged_existing_table')

def raw_target_counts(cur, table, checksum):
    row = cur.execute(f'SELECT COUNT(*), COUNT(DISTINCT SOURCE_ROW_NUMBER),\n        COUNT_IF(SOURCE_SHA256 IS NULL OR SOURCE_SHA256 <> %s)\n        FROM {table}', (checksum,)).fetchone()
    return {'rows': int(row[0]), 'unique_source_rows': int(row[1]), 'other_checksums': int(row[2] or 0)}

def raw_audit(cur, name, checksum, run_id, attempt, status, expected, rows):
    cur.execute('INSERT INTO INGESTION_LOG\n        (SOURCE_FILE,SOURCE_SHA256,RUN_ID,ATTEMPT_ID,STATUS,EXPECTED_ROWS,ACTUAL_ROWS,RECORDED_AT)\n        VALUES (%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP())', (name, checksum, run_id, attempt, status, expected, rows))

def raw_verify_source_values(conn):
    """Reconciliar clases y valores vacíos con la auditoría de esta copia."""
    with conn.cursor() as cur:
        classes = cur.execute("SELECT COUNT_IF(FINAL_RESULT='Fail'),COUNT_IF(FINAL_RESULT='Withdrawn'),COUNT_IF(FINAL_RESULT IN ('Pass','Distinction')),COUNT_IF(IMD_BAND=''),COUNT_IF(IMD_BAND IS NULL) FROM STUDENTINFO").fetchone()
        registration = cur.execute("SELECT COUNT_IF(DATE_REGISTRATION=''),COUNT_IF(DATE_UNREGISTRATION=''),COUNT_IF(DATE_UNREGISTRATION IS NULL) FROM STUDENTREGISTRATION").fetchone()
        resources = cur.execute("SELECT COUNT_IF(WEEK_FROM=''),COUNT_IF(WEEK_TO='') FROM VLE").fetchone()
    if tuple(classes) != (7052, 10156, 15385, 1111, 0) or tuple(registration) != (45, 22521, 0) or tuple(resources) != (5243, 5243):
        raise RuntimeError('source_value_reconciliation_failed')
    return {'Fail': int(classes[0]), 'Withdrawn': int(classes[1]), 'Approved': int(classes[2]), 'empty_imd_band': int(classes[3]), 'empty_registration_date': int(registration[0]), 'empty_unregistration_date': int(registration[1]), 'empty_week_from': int(resources[0]), 'empty_week_to': int(resources[1]), 'source_empty_values_preserved': True}

def raw_load_file(conn, name, meta, columns, run_id, attempt, force=False, progress=None):
    table = ARCHIVOS_RAW[name]
    checksum = meta['sha256']
    expected = meta['rows']
    cols = ', '.join((c.upper() + ' VARCHAR' for c in columns))
    technical = 'SOURCE_SHA256 VARCHAR, SOURCE_ROW_NUMBER NUMBER, LOAD_RUN_ID VARCHAR, LOADED_AT TIMESTAMP_LTZ'
    with conn.cursor() as cur:
        if progress is not None:
            progress['phase'] = 'target_contract'
        raw_ensure_managed(cur, table, cols + ', ' + technical, 'pset2.raw.v1:' + name)
        actual = [r[0] for r in cur.execute(f'DESC TABLE {table}').fetchall()]
        if actual != [c.upper() for c in columns] + ['SOURCE_SHA256', 'SOURCE_ROW_NUMBER', 'LOAD_RUN_ID', 'LOADED_AT']:
            raise RuntimeError('target_schema_mismatch')
        current = raw_target_counts(cur, table, checksum)
        if current == {'rows': expected, 'unique_source_rows': expected, 'other_checksums': 0} and (not force):
            raw_audit(cur, name, checksum, run_id, attempt, 'NOOP', expected, expected)
            return {'file': name, 'status': 'NOOP', **current}
        temp = 'TMP_' + table + '_' + uuid.uuid4().hex[:12].upper()
        if progress is not None:
            progress['phase'] = 'temporary_table'
        cur.execute(f'CREATE TEMPORARY TABLE {temp} LIKE {table}')
        with tempfile.TemporaryDirectory(prefix='oulad-raw-') as work:
            gzpath = Path(work) / (name + '.gz')
            with (INGESTA_DATA / name).open('rb') as source, gzpath.open('wb') as target:
                with gzip.GzipFile(filename='', fileobj=target, mode='wb', compresslevel=3, mtime=0) as compressed:
                    shutil.copyfileobj(source, compressed, 8 * 1024 * 1024)
            stage_path = f'@OULAD_FILES/{table}/{checksum}'
            if progress is not None:
                progress['phase'] = 'stage_upload'
            cur.execute(f"PUT 'file://{gzpath}' {stage_path} AUTO_COMPRESS=FALSE SOURCE_COMPRESSION=GZIP OVERWRITE=FALSE PARALLEL=2")
            put = cur.fetchall()
            if not put or any((str(row[6]).upper() not in ['UPLOADED', 'SKIPPED'] for row in put)):
                raise RuntimeError('stage_upload_incomplete')
            selection = ', '.join((f'${i}::VARCHAR' for i in range(1, len(columns) + 1)))
            if progress is not None:
                progress['phase'] = 'copy_to_temporary'
            cur.execute(f"COPY INTO {temp} FROM (\n                SELECT {selection}, '{checksum}', METADATA$FILE_ROW_NUMBER,\n                    '{run_id}', CURRENT_TIMESTAMP()\n                FROM {stage_path}/{name}.gz)\n                FILE_FORMAT=(FORMAT_NAME='PSET2_OULAD.RAW.OULAD_CSV_V1')\n                ON_ERROR='ABORT_STATEMENT' FORCE=TRUE")
        copied = raw_target_counts(cur, temp, checksum)
        if copied != {'rows': expected, 'unique_source_rows': expected, 'other_checksums': 0}:
            raise RuntimeError('copy_reconciliation_failed')
        try:
            if progress is not None:
                progress['phase'] = 'publish_transaction'
            cur.execute('BEGIN')
            cur.execute(f'DELETE FROM {table}')
            cur.execute(f'INSERT INTO {table} SELECT * FROM {temp}')
            raw_audit(cur, name, checksum, run_id, attempt, 'LOADED', expected, expected)
            cur.execute('COMMIT')
        except Exception:
            cur.execute('ROLLBACK')
            raise
        finally:
            cur.execute(f'DROP TABLE IF EXISTS {temp}')
        final = raw_target_counts(cur, table, checksum)
        if final != copied:
            raise RuntimeError('published_reconciliation_failed')
        return {'file': name, 'status': 'LOADED', **final}


def ingestar_raw(execution_id,archivo='all',forzar=False):
    import logging,uuid
    validar_execution_id(execution_id)
    if archivo not in ['all',*ARCHIVOS_RAW]:raise ValueError('Archivo no permitido')
    logging.disable(logging.CRITICAL)
    report={'checked_at_utc':ahora(),'run_id':execution_id,'attempt_id':uuid.uuid4().hex,
            'status':'failed','mode':'load','source_partition':archivo,'files':[]}
    try:
        with conectar_raw() as conn:
            with conn.cursor() as cur:
                ctx=cur.execute('SELECT CURRENT_USER(),CURRENT_ROLE(),CURRENT_DATABASE(),CURRENT_SCHEMA(),CURRENT_WAREHOUSE()').fetchone()
                if tuple(ctx)!=CTX_RAW:raise RuntimeError('unexpected_session_context')
            if not os.statvfs(INGESTA_DATA).f_flag & os.ST_RDONLY:raise RuntimeError('source_not_read_only')
            files=raw_verified_files(archivo)
            report['source_manifest_sha256']=sha256(INGESTA_DATA/'manifest.json')
            with conn.cursor() as cur:
                raw_ensure_managed(cur,'INGESTION_LOG',
                    'SOURCE_FILE VARCHAR, SOURCE_SHA256 VARCHAR, RUN_ID VARCHAR, ATTEMPT_ID VARCHAR, STATUS VARCHAR, EXPECTED_ROWS NUMBER, ACTUAL_ROWS NUMBER, RECORDED_AT TIMESTAMP_LTZ',
                    'pset2.raw.ingestion-log.v1')
                cur.execute("CREATE STAGE IF NOT EXISTS OULAD_FILES COMMENT='pset2.raw.stage.v1'")
                cur.execute('''CREATE FILE FORMAT IF NOT EXISTS OULAD_CSV_V1 TYPE=CSV COMPRESSION=AUTO SKIP_HEADER=1
                    FIELD_OPTIONALLY_ENCLOSED_BY='"' EMPTY_FIELD_AS_NULL=FALSE NULL_IF=()
                    ERROR_ON_COLUMN_COUNT_MISMATCH=FALSE ENCODING='UTF8' ''')
            for name,meta,columns in files:
                report['active_file']=name
                report['files'].append(raw_load_file(conn,name,meta,columns,execution_id,report['attempt_id'],forzar,report))
            if archivo=='all':report['source_value_checks']=raw_verify_source_values(conn)
            report.update(status='ok',datasets_read_only=True,phase='completed')
    except Exception as exc:
        report.update(error_class=type(exc).__name__)
        if isinstance(getattr(exc,'errno',None),int):report['errno']=exc.errno
    report['finished_at_utc']=ahora()
    guardar_informe(INGESTA_RAW/(execution_id+'_'+report['attempt_id']+'.json'),report)
    if report['status']!='ok':raise RuntimeError('Ingesta fallida; consultar informe privado agregado')
    return report


def validar_solicitud_job(data):
    if not isinstance(data,dict) or set(data)!={'execution_id'}:raise ValueError('Solicitud inválida')
    return validar_execution_id(data['execution_id'])


def comando_ingesta(componente,job_id):
    """Lista cerrada de ejecutables y argumentos, sin shell ni comandos suministrados."""
    import sys
    if not re.fullmatch(r'[a-f0-9]{32}',job_id):raise ValueError('Identificador del trabajo inválido')
    if componente=='dbt':return [sys.executable,'/workspace/dbt/bootstrap.py','build-gold']
    if componente!='spark':raise ValueError('Componente no permitido')
    return ['/opt/spark/bin/spark-submit','--master','local[2]','--driver-memory','1g','--jars',
        '/opt/spark/oulad-jars/spark-snowflake_2.12-3.2.3-spark_3.5.jar,/opt/spark/oulad-jars/snowflake-jdbc-4.4.1.jar,/opt/spark/oulad-jars/parquet-avro-1.13.1.jar',
        '--conf','spark.ui.enabled=false','--conf','spark.eventLog.enabled=false',
        '--conf','spark.sql.shuffle.partitions=16','--conf','spark.sql.adaptive.enabled=true',
        '--conf','spark.redaction.regex=(?i)secret|password|token|access.?key|pem_private_key|sfurl|account',
        '/workspace/spark/build_obt.py','--action','build-obt','--run-id',job_id]


def ejecutar_proceso_ingesta(args,log,timeout):
    import subprocess,signal
    with Path(log).open('w') as output:
        Path(log).chmod(0o600)
        proc=subprocess.Popen(args,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
        try:return proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            return 124


def trabajo_ingesta(componente,job,artifacts):
    import sys,time
    jobs=artifacts/'runner-jobs';deadline=time.monotonic()+1200
    code=ejecutar_proceso_ingesta(comando_ingesta(componente,job['job_id']),jobs/(job['job_id']+'.log'),1200)
    if code:return {'status':'failed','returncode':code}
    if componente=='spark':
        result=json.loads((Path('/workspace/output')/(job['job_id']+'.json')).read_text())
        result['returncode']=code
        return result
    data=json.loads((artifacts/'target/run_results.json').read_text())
    nodes=[{k:r[k] for k in ['unique_id','status','execution_time','failures']} for r in data['results']]
    if not nodes or any(r['status'] not in ['success','pass'] for r in nodes):raise ValueError('dbt incompleto')
    result={'status':'ok','returncode':code,'results':nodes,'models_succeeded':sum(r['status']=='success' for r in nodes),
            'tests_passed':sum(r['status']=='pass' for r in nodes),'elapsed_seconds':round(data['elapsed_time'],2),'quality':{}}
    for layer,action in [('bronze','quality-export'),('silver','quality-export-silver'),('gold','quality-export-gold')]:
        log=jobs/(job['job_id']+'-'+layer+'.log')
        code=ejecutar_proceso_ingesta([sys.executable,'/workspace/dbt/bootstrap.py',action],log,max(1,int(deadline-time.monotonic())))
        if code:return {'status':'failed','returncode':code,'phase':'quality_'+layer}
        metrics=json.loads(log.read_text().strip())
        if not isinstance(metrics,list) or not all(set(m)=={'dataset','metric','value','denominator'} for m in metrics):raise ValueError('Exportación inválida')
        result['quality'][layer]=metrics
    return result


def servir_jobs_ingesta(componente):
    from concurrent.futures import ThreadPoolExecutor
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    import threading,secrets
    if componente not in ['dbt','spark']:raise ValueError('Componente inválido')
    token=os.environ['PSET4_INGESTA_TOKEN']
    if len(token)<32:raise ValueError('Configurar secreto interno de ingesta')
    artifacts=Path('/workspace/artifacts');jobs=artifacts/'runner-jobs';jobs.mkdir(parents=True,exist_ok=True)
    lock=threading.RLock();pool=ThreadPoolExecutor(max_workers=1)
    for path in jobs.glob('*.json'):
        state=json.loads(path.read_text())
        if state['state'] in ['RUNNING','QUEUED']:
            state.update(state='FAILED',finished_at_utc=ahora(),category='worker_restarted');guardar_informe(path,state)
    def run(job,path):
        with lock:job.update(state='RUNNING',started_at_utc=ahora());guardar_informe(path,job)
        try:report=trabajo_ingesta(componente,job,artifacts)
        except Exception as exc:report={'status':'failed','error_class':type(exc).__name__}
        with lock:
            job.update(state='SUCCESS' if report['status']=='ok' else 'FAILED',finished_at_utc=ahora())
            report.update(component=componente,execution_id=job['execution_id'],job_id=job['job_id'],attempt=job['attempt'],
                          started_at_utc=job['started_at_utc'],finished_at_utc=job['finished_at_utc'],codigo_sha256=sha256(__file__))
            folder=ROOT/'.local/ingesta/pipeline'/job['execution_id']
            guardar_informe(folder/(componente+'_attempt_'+str(job['attempt'])+'.json'),report)
            guardar_informe(folder/(componente+'.json'),report);guardar_informe(path,job)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send(self,status,data):
            body=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def authorized(self):return secrets.compare_digest(self.headers.get('X-Ingesta-Token',''),token)
        def do_GET(self):
            if self.path=='/health':return self.send(200,{'status':'ok','component':componente})
            if not self.authorized():return self.send(401,{'error':'unauthorized'})
            match=re.fullmatch(r'/jobs/([A-Za-z0-9_-]{1,100})',self.path)
            if not match:return self.send(404,{'error':'unknown_route'})
            with lock:
                path=jobs/(match[1]+'.json')
                return self.send(200,json.loads(path.read_text())) if path.exists() else self.send(404,{'error':'unknown_job'})
        def do_POST(self):
            if not self.authorized():return self.send(401,{'error':'unauthorized'})
            if self.path!='/jobs':return self.send(404,{'error':'unknown_route'})
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=1024:raise ValueError('Tamaño inválido')
                identifier=validar_solicitud_job(json.loads(self.rfile.read(length)))
            except Exception:return self.send(400,{'error':'invalid_request'})
            with lock:
                path=jobs/(identifier+'.json');prev=json.loads(path.read_text()) if path.exists() else None
                if prev and prev['state'] in ['QUEUED','RUNNING','SUCCESS']:return self.send(200,prev)
                attempt=prev['attempt']+1 if prev else 1
                job={'execution_id':identifier,'component':componente,'attempt':attempt,'state':'QUEUED',
                     'job_id':identidad([identifier,componente,attempt])[:32],'created_at_utc':ahora()}
                guardar_informe(path,job);pool.submit(run,job.copy(),path);self.send(202,job)
    ThreadingHTTPServer(('0.0.0.0',8090),Handler).serve_forever()


def ejecutar_job_ingesta(componente,execution_id):
    import time
    validar_execution_id(execution_id)
    if componente not in ['dbt','spark']:raise ValueError('Componente no permitido')
    base='http://'+componente+':8090'
    def request(path,data=None):
        req=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),
            headers={'Content-Type':'application/json','X-Ingesta-Token':os.environ['PSET4_INGESTA_TOKEN']})
        with urllib.request.urlopen(req,timeout=20) as response:return json.load(response)
    state=request('/jobs',{'execution_id':execution_id});deadline=time.monotonic()+1300
    while time.monotonic()<deadline:
        state=request('/jobs/'+execution_id)
        if state['state'] in ['SUCCESS','FAILED']:
            if state['state']!='SUCCESS':raise RuntimeError('Trabajo fallido; revisar informe agregado')
            return state
        time.sleep(3)
    raise TimeoutError('Revisar el trabajo existente antes de crear otra ejecución')


def verificar_informes_ingesta(raw,dbt,spark,manifest,contract,manifest_sha):
    """Puerta de calidad: no aceptar solo códigos de salida o contadores parciales."""
    if not all(r['status']=='ok' for r in [raw,dbt,spark]):raise ValueError('Etapa fallida')
    if raw['mode']!='load':raise ValueError('Modo Raw inválido')
    selected=set(ARCHIVOS_RAW) if raw['source_partition']=='all' else {raw['source_partition']}
    if selected-set(ARCHIVOS_RAW) or {r['file'] for r in raw['files']}!=selected or len(raw['files'])!=len(selected):raise ValueError('Fuentes incompletas')
    for r in raw['files']:
        if r['status'] not in ['NOOP','LOADED'] or r['rows']!=r['unique_source_rows'] or r['rows']!=manifest['files'][r['file']]['rows'] or r['other_checksums']!=0:raise ValueError('Raw sin reconciliar')
    if raw['source_manifest_sha256']!=manifest_sha or spark['source_manifest_sha256']!=manifest_sha:raise ValueError('Manifiesto distinto')
    if not dbt['results'] or any(r['status'] not in ['success','pass'] for r in dbt['results']):raise ValueError('dbt incompleto')
    if dbt['models_succeeded']!=23 or dbt['tests_passed']!=168:raise ValueError('Contrato dbt incompleto')
    if dbt['execution_id']!=spark['execution_id'] or raw['run_id']!=dbt['execution_id']:raise ValueError('Ejecuciones distintas')
    if not raw['finished_at_utc']<=dbt['started_at_utc']<dbt['finished_at_utc']<=spark['started_at_utc']<spark['finished_at_utc']:raise ValueError('Orden de etapas inválido')
    for name in ['published','population_key_sets_equal','readback_all_columns_equal','gold_source_sha256_verified','target_and_withdrawal_excluded']:
        if spark[name] is not True:raise ValueError('Spark sin reconciliar: '+name)
    if spark['output_columns']!=contract['output_columns'] or set(spark['output_columns'])&set(contract['forbidden_columns']):raise ValueError('Contrato de features inválido')
    if spark['temporal_tests_passed']!=len(contract['cutoff_days']) or sorted(r['cutoff_day'] for r in spark['per_cutoff'])!=contract['cutoff_days']:raise ValueError('Cortes incompletos')
    if spark['rows']!=spark['unique_keys'] or spark['rows']!=sum(r['rows'] for r in spark['per_cutoff']):raise ValueError('Claves OBT incompletas')
    gold={(r['dataset'],r['metric']):r['value'] for r in dbt['quality']['gold']}
    for r in spark['per_cutoff']:
        if not r['future_perturbation_unchanged'] or r['rows']!=gold[('eligibility_day_'+str(r['cutoff_day']),'expected_enrollments')]:raise ValueError('Población o temporalidad inválida')
    return {'status':'ok','execution_id':dbt['execution_id'],'raw_files':raw['files'],'raw_selected_rows':sum(r['rows'] for r in raw['files']),
            'dbt_models_succeeded':dbt['models_succeeded'],'dbt_tests_passed':dbt['tests_passed'],'obt_rows':spark['rows'],
            'obt_columns':len(spark['output_columns']),'obt_unique_keys':spark['unique_keys'],'stage_order_verified':True,
            'temporal_tests_passed':spark['temporal_tests_passed'],'readback_all_columns_equal':True,
            'content_sha256_by_cutoff':spark['content_sha256_by_cutoff'],'per_cutoff':spark['per_cutoff'],
            'spark_run_id':spark['run_id'],'source_manifest_sha256':manifest_sha}


def verificar_ingesta(execution_id):
    validar_execution_id(execution_id)
    folder=ROOT/'.local/ingesta/pipeline'/execution_id
    raw=max((json.loads(p.read_text()) for p in INGESTA_RAW.glob(execution_id+'_*.json')),key=lambda r:r['finished_at_utc'])
    dbt=json.loads((folder/'dbt.json').read_text());spark=json.loads((folder/'spark.json').read_text())
    result=verificar_informes_ingesta(raw,dbt,spark,json.loads((INGESTA_DATA/'manifest.json').read_text()),
        json.loads((ROOT/'spark/feature-contract.json').read_text()),sha256(INGESTA_DATA/'manifest.json'))
    result.update(checked_at_utc=ahora(),codigo_sha256=sha256(__file__))
    guardar_informe(folder/'verification.json',result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ingestar', action='store_true')
    group.add_argument('--servir-jobs', choices=['dbt','spark'])
    group.add_argument('--ejecutar-job', choices=['dbt','spark'])
    group.add_argument('--verificar-ingesta', action='store_true')
    parser.add_argument('--source-file', choices=['all',*ARCHIVOS_RAW], default='all')
    parser.add_argument('--forzar-recarga', action='store_true')
    group.add_argument('--registrar-cohorte', type=Path)
    group.add_argument('--ejemplo', type=Path)
    group.add_argument('--preparar-plan', action='store_true')
    group.add_argument('--procesar-lote', choices=[f'L{n:02}' for n in range(1,9)])
    group.add_argument('--liberar-etiquetas', type=int, metavar='DIA_SIMULADO')
    group.add_argument('--exportar-predicciones', type=Path)
    group.add_argument('--exportar-escenarios', type=Path)
    group.add_argument('--monitorear-lote', choices=['todos',*[f'L{n:02}' for n in range(1,9)]])
    group.add_argument('--reentrenar', choices=['solicitar','preparar','decidir','rollback'])
    parser.add_argument('--fase', choices=['prediccion','maduro'], default='prediccion')
    parser.add_argument('--plan', default=PLAN_CONTROL, choices=[PLAN_CONTROL, PLAN_DERIVA])
    parser.add_argument('--api-url', default=os.environ.get('PSET4_API_URL', 'http://api:8000'))
    parser.add_argument('--execution-id', default='manual')
    parser.add_argument('--cohorte-id', default='ejemplo-api')
    parser.add_argument('--base-local', type=Path, default=ROOT / '.local/operacion.sqlite')
    args = parser.parse_args()
    if args.servir_jobs:
        servir_jobs_ingesta(args.servir_jobs);return
    if args.ingestar or args.ejecutar_job or args.verificar_ingesta:
        if args.ingestar:result=ingestar_raw(args.execution_id,args.source_file,args.forzar_recarga)
        elif args.ejecutar_job:result=ejecutar_job_ingesta(args.ejecutar_job,args.execution_id)
        else:result=verificar_ingesta(args.execution_id)
        print(json.dumps(result,ensure_ascii=False));return
    if args.reentrenar:
        data={'operacion':args.reentrenar,'execution_id':args.execution_id,
              'decision':os.environ.get('PSET4_DECISION'),'motivo':os.environ.get('PSET4_MOTIVO'),
              'responsable':os.environ.get('PSET4_RESPONSABLE')}
        url=os.environ.get('PSET4_MONITOR_URL','http://monitoreo:8090')+'/reentrenar'
        request=urllib.request.Request(url,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(request,timeout=1200) as response:print(json.dumps(json.load(response),ensure_ascii=False))
        return
    if args.monitorear_lote:
        url = os.environ.get('PSET4_MONITOR_URL', 'http://monitoreo:8090')+'/monitorear'
        request = urllib.request.Request(url, data=json.dumps({'plan_id': args.plan, 'lote_id': args.monitorear_lote, 'fase': args.fase}).encode(), headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(request, timeout=600) as response:
            print(json.dumps(json.load(response), ensure_ascii=False))
        return
    if args.plan == PLAN_DERIVA:
        if args.base_local == ROOT/'.local/operacion.sqlite':
            args.base_local = ROOT/'.local/deriva/operacion.sqlite'
        if args.api_url == 'http://api:8000':
            args.api_url = 'http://api_deriva:8000'
    if args.preparar_plan or args.procesar_lote or args.liberar_etiquetas is not None or args.exportar_predicciones or args.exportar_escenarios:
        # También protege las ejecuciones CLI fuera de Kestra. La API tiene su propia transacción SQLite.
        import fcntl
        lock = args.base_local.parent/'escritor-snowflake.lock'
        lock.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with lock.open('a') as gate:
            fcntl.flock(gate, fcntl.LOCK_EX)
            with conectar_snowflake() as conn:
                repo = RepositorioSnowflake(conn)
                if args.preparar_plan:
                    repo.asegurar()
                    result = preparar_plan(repo, args.plan)
                elif args.procesar_lote:
                    result = procesar_lote(repo, Almacen(args.base_local), args.procesar_lote, args.api_url, args.plan, args.execution_id)
                elif args.liberar_etiquetas is not None:
                    result = liberar_etiquetas(repo, args.liberar_etiquetas, args.plan)
                elif args.exportar_predicciones:
                    result = exportar_predicciones(repo, args.exportar_predicciones, args.plan)
                else:
                    result = exportar_predicciones(repo, args.exportar_escenarios, None)
                print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return
    almacen = Almacen(args.base_local)
    if args.ejemplo:
        generar_ejemplo(args.ejemplo, almacen, args.cohorte_id)
    else:
        almacen.registrar_cohorte(json.loads(args.registrar_cohorte.read_text()))
        print('Manifiesto registrado; sin llamadas a Snowflake ni predicciones nuevas.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # Los conectores pueden incluir host, cuenta y JWT en su traceback.
        print(json.dumps({'status': 'failed', 'error_class': type(exc).__name__}))
        raise SystemExit(1)
