"""Asistente interactivo: configuración privada fuera de Git, sin cargas."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,getpass,json,logging,os,re,sys
from probar_conexion import ROOT,EXPECTED,connection_options

def write_exclusive(path,content):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:f.write(content)

def dotenv_path(path):
    # Solo rutas: la frase y la cuenta se almacenan en el JSON externo.
    # Compose interpreta escapes dentro de comillas dobles; $ se prohíbe
    # para no activar interpolación inesperada del nombre de archivo.
    text=str(path)
    if any(c in text for c in ['$', '\n', '\r', '\x00']):
        raise ValueError('Ruta incompatible con el archivo de montaje local.')
    return json.dumps(text,ensure_ascii=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-dir',type=Path,default=Path.home()/'.config/psets/snowflake')
    args=parser.parse_args()
    directory=args.config_dir.expanduser().resolve()
    if directory==ROOT or ROOT in directory.parents:
        raise SystemExit('La configuración privada debe estar fuera del repositorio.')
    config=directory/'pset2-connection.json'
    mounts=ROOT/'pset-02/.env.cloud'
    if config.exists() or mounts.exists():
        raise SystemExit('Ya existe configuración cloud. No se lee ni sobrescribe; revisar antes de cambiarla.')
    if not sys.stdin.isatty():raise SystemExit('Ejecutar en una terminal interactiva.')
    logging.disable(logging.CRITICAL)
    try:import snowflake.connector
    except ImportError:raise SystemExit('Usar pset-02/.venv/bin/python, que ya tiene el conector instalado.')
    print('Se comprobará la conexión y se guardarán cuenta y frase de cifrado en un JSON local fuera de Git, con permisos 0600.')
    print('La clave privada no se copia. .env.cloud contendrá únicamente rutas para futuros montajes de solo lectura.')
    account=input('Identificador de cuenta que funcionó en la prueba anterior: ').strip()
    if not re.fullmatch(r'[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*',account) or 'snowflakecomputing.' in account.lower() or 'snowflake.com' in account.lower():
        raise SystemExit('Usar solo el identificador para clientes, sin URL ni comillas.')
    default=Path.home()/'.config/psets/snowflake/rsa_key.p8'
    entered=input(f'Ruta de clave privada [Enter para {default}]: ').strip()
    key=(Path(entered).expanduser() if entered else default).resolve()
    if key==ROOT or ROOT in key.parents or not key.is_file():raise SystemExit('La clave debe existir fuera del repositorio.')
    try:
        mount_content='# Privado local: solo rutas. No versionar.\n'+\
            'SNOWFLAKE_CONNECTION_HOST_PATH='+dotenv_path(config)+'\n'+\
            'SNOWFLAKE_PRIVATE_KEY_HOST_PATH='+dotenv_path(key)+'\n'
    except ValueError:raise SystemExit('Elegir rutas sin $, saltos de línea ni retornos de carro.')
    passphrase=getpass.getpass('Frase de cifrado de la clave privada (oculta): ')
    if not passphrase:raise SystemExit('Se requiere la frase de cifrado.')
    try:
        with snowflake.connector.connect(**connection_options(account,key,passphrase,'pset02_private_config_check')) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE()')
                if tuple(cur.fetchone() or ())!=EXPECTED:raise SystemExit('Contexto inesperado. No se guardó configuración.')
    except snowflake.connector.errors.Error as exc:
        errno=exc.errno if isinstance(exc.errno,int) else None
        raise SystemExit(f'Conexión fallida; errno={errno}. No se guardó configuración ni se imprimen detalles privados.')
    except Exception:
        raise SystemExit('No se pudo validar la clave o la conexión. No se guardó configuración.')
    os.umask(0o077)
    directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    payload={'schema_version':1,'account':account,'private_key_passphrase':passphrase}
    write_exclusive(config,json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    # Si el segundo archivo falla, conservar el primero y explicarlo sin
    # borrar ni sobrescribir configuración del usuario.
    try:write_exclusive(mounts,mount_content)
    except OSError:raise SystemExit('El JSON privado quedó creado, pero no se pudo crear .env.cloud. Revisar antes de repetir; no se sobrescribe.')
    passphrase=None
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'status':'ok',
            'expected_session_context_verified':True,'private_configuration_created':True,
            'scope':'Configuración privada y prueba del host. Sin carga de CSV ni conexión desde contenedores.'}
    (ROOT/'pset-02/docs/configuracion-cloud.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Configuración privada preparada y conexión comprobada.')
    print('Cuenta y frase fuera del repositorio; .env.cloud solo contiene rutas. No compartir ninguno de esos archivos.')
    print('No se cargaron CSV ni se modificaron tablas de Snowflake.')

if __name__=='__main__':
    try:main()
    except (KeyboardInterrupt,EOFError):raise SystemExit('Configuración cancelada; no se imprimieron valores privados.')
