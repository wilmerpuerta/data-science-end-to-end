"""Datos verificados y registro transaccional privado de cohortes y predicciones."""
from contextlib import contextmanager, closing
from datetime import datetime, timezone
from pathlib import Path
import argparse
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


PLAN_CONTROL = 'oulad-2014j-control-v1'
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
    request = urllib.request.Request(api_url.rstrip('/')+'/predecir', data=body, headers={'Content-Type': 'application/json'})
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
        rows = cur.execute('SELECT '+','.join(f'"{c}"' for c in columnas)+f' FROM {ESQUEMA_OPERACION}.PREDICCIONES WHERE PLAN_ID=%s ORDER BY LOTE_ID,MATRICULA', (plan_id,)).fetchall()
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--registrar-cohorte', type=Path)
    group.add_argument('--ejemplo', type=Path)
    group.add_argument('--preparar-plan', action='store_true')
    group.add_argument('--procesar-lote', choices=[f'L{n:02}' for n in range(1,9)])
    group.add_argument('--liberar-etiquetas', type=int, metavar='DIA_SIMULADO')
    group.add_argument('--exportar-predicciones', type=Path)
    parser.add_argument('--plan', default=PLAN_CONTROL, choices=[PLAN_CONTROL])
    parser.add_argument('--api-url', default=os.environ.get('PSET4_API_URL', 'http://api:8000'))
    parser.add_argument('--execution-id', default='manual')
    parser.add_argument('--cohorte-id', default='ejemplo-api')
    parser.add_argument('--base-local', type=Path, default=ROOT / '.local/operacion.sqlite')
    args = parser.parse_args()
    if args.preparar_plan or args.procesar_lote or args.liberar_etiquetas is not None or args.exportar_predicciones:
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
                else:
                    result = exportar_predicciones(repo, args.exportar_predicciones, args.plan)
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
