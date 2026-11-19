"""Prueba interactiva JWT sin guardar identificador de cuenta ni secretos."""
from pathlib import Path
from datetime import datetime, timezone
from importlib.metadata import version
import argparse
import getpass
import json
import logging
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = ('PSET2_SVC', 'PSET2_PIPELINE', 'PSET2_OULAD', 'RAW', 'PSET2_WH')

def connection_options(account, key, passphrase, tag='pset02_connection_check'):
    """Opciones comunes de los clientes de comprobación, sin imprimir secretos."""
    return dict(account=account, user=EXPECTED[0], role=EXPECTED[1],
                database=EXPECTED[2], schema=EXPECTED[3], warehouse=EXPECTED[4],
                authenticator='SNOWFLAKE_JWT', private_key_file=str(key),
                private_key_file_pwd=passphrase, login_timeout=30, network_timeout=30,
                session_parameters={'QUERY_TAG':tag,'STATEMENT_TIMEOUT_IN_SECONDS':60})

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-installation', action='store_true',
                        help='Comprobar importación y versión sin conectar ni leer claves.')
    args = parser.parse_args()
    # El conector puede registrar mensajes con información de conexión.
    # En esta prueba solo se publica un resultado sanitizado.
    logging.disable(logging.CRITICAL)
    try:
        import snowflake.connector
    except ImportError:
        print('Falta instalar scripts/requirements-conexion.txt en el entorno de PSet 2.')
        return 1
    connector_version = version('snowflake-connector-python')
    if args.check_installation:
        print(f'Conector importado: {connector_version}. No se abrió conexión ni se leyeron claves.')
        return 0
    if not sys.stdin.isatty():
        print('Ejecutar en una terminal interactiva. No pasar secretos por argumentos o pipes.')
        return 1
    print('Prueba con PSET2_SVC y PSET2_PIPELINE. Los valores introducidos no se guardan.')
    account = input('Identificador de cuenta (organizacion-cuenta, sin https:// ni .snowflakecomputing.com): ').strip()
    if (not re.fullmatch(r'[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*', account)
            or 'snowflakecomputing.' in account.lower()
            or 'snowflake.com' in account.lower()):
        print('Usar solo el identificador para clientes, sin URL, comillas ni espacios.')
        print('Obtenerlo localmente en Snowsight con CURRENT_ORGANIZATION_NAME() y CURRENT_ACCOUNT_NAME().')
        return 1
    default_key = Path.home()/'.config/psets/snowflake/rsa_key.p8'
    key_input = input(f'Ruta de clave privada [Enter para {default_key}]: ').strip()
    key = Path(key_input).expanduser().resolve() if key_input else default_key.resolve()
    if key == ROOT or ROOT in key.parents or not key.is_file():
        print('La clave debe existir fuera del repositorio. No se intentó conectar.')
        return 1
    passphrase = getpass.getpass('Frase de cifrado de la clave privada (no se muestra): ')
    if not passphrase:
        print('La clave generada para este proyecto requiere frase de cifrado.')
        return 1
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'connector_version': connector_version, 'status': 'failed',
              'scope': 'Autenticación y contexto de sesión; sin cargas ni prueba de dbt/Spark.'}
    try:
        with snowflake.connector.connect(**connection_options(account,key,passphrase)) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE()')
                row = cur.fetchone()
            if tuple(row or ()) != EXPECTED:
                report['category'] = 'unexpected_session_context'
            else:
                report['status'] = 'ok'
                report['expected_session_context_verified'] = True
    except snowflake.connector.errors.Error as exc:
        # No publicar str(exc), traceback, account, clave ni detalles del JWT.
        report['category'] = 'connector_error'
        report['errno'] = exc.errno if isinstance(exc.errno, int) else None
        report['sqlstate'] = exc.sqlstate if isinstance(exc.sqlstate, str) and len(exc.sqlstate) == 5 and exc.sqlstate.isalnum() else None
        if report['errno'] == 290404:
            report['http_status'] = 404
            report['next_check'] = 'account_identifier_and_endpoint'
    except Exception:
        report['category'] = 'local_key_or_connection_error'
    finally:
        passphrase = None
    target = ROOT/'pset-02/docs/conexion-snowflake.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    if report['status'] == 'ok':
        print('Conexión correcta: usuario de servicio, rol, base, esquema y warehouse esperados.')
    else:
        print('La prueba no terminó correctamente. Resultado sanitizado:')
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if report.get('errno') == 290404:
            print('HTTP 404: comprobar primero el identificador de cuenta para clientes.')
            print('No regenerar claves ni cambiar grants basándose únicamente en este código.')
    print('Informe sin credenciales: pset-02/docs/conexion-snowflake.json')
    return 0 if report['status'] == 'ok' else 1

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print('\nPrueba cancelada; no se imprimieron valores de autenticación.')
        raise SystemExit(1)
