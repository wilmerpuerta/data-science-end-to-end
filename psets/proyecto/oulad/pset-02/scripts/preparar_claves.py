"""Generar claves cifradas fuera del repositorio; ejecutar interactivamente.

No conecta con Snowflake. La frase se introduce directamente en OpenSSL.
"""
from pathlib import Path
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path,
                        default=Path.home()/'.config/psets/snowflake')
    args = parser.parse_args()
    folder = args.output_dir.expanduser().resolve()
    if folder == ROOT or ROOT in folder.parents:
        raise SystemExit('La carpeta de claves debe estar fuera del repositorio.')
    if not shutil.which('openssl'):
        raise SystemExit('Falta OpenSSL; no se generaron archivos.')
    names = ['rsa_key.p8', 'rsa_key.pub', 'registrar_usuario.local.sql']
    if any((folder/name).exists() for name in names):
        raise SystemExit('Ya existe un archivo de autenticación en el destino. No se sobrescribe ni rota automáticamente.')
    if not sys.stdin.isatty():
        raise SystemExit('Ejecutar en una terminal interactiva para introducir la frase de cifrado.')
    os.umask(0o077)
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    print('OpenSSL pedirá una frase de cifrado, su confirmación y después la misma frase para exportar la clave pública.')
    print('No compartas la frase ni la guardes en comandos o archivos versionados.')
    with tempfile.TemporaryDirectory(prefix='.keygen-', dir=folder) as tmp:
        work = Path(tmp)
        private, public, sqlfile = [work/name for name in names]
        subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA',
                        '-pkeyopt', 'rsa_keygen_bits:2048', '-aes-256-cbc',
                        '-out', str(private)], check=True)
        subprocess.run(['openssl', 'rsa', '-in', str(private), '-pubout',
                        '-out', str(public)], check=True)
        body = ''.join(line.strip() for line in public.read_text().splitlines()
                       if not line.startswith('-----'))
        if not re.fullmatch(r'[A-Za-z0-9+/=]+', body):
            raise SystemExit('Formato inesperado de clave pública. No se publicó el SQL local.')
        template = ROOT/'pset-02/snowflake/03_usuario_servicio.sql.example'
        sqlfile.write_text(template.read_text().replace('__PUBLIC_KEY_BODY__', body))
        # Hard links: publicar sin sobrescribir archivos existentes. Al salir,
        # TemporaryDirectory elimina solo los enlaces temporales.
        for name in names:
            os.link(work/name, folder/name)
    print('Archivos creados fuera del repositorio:')
    for name in names:
        print(folder/name)
    print('Siguiente paso: ejecutar registrar_usuario.local.sql en Snowsight, sentencia a sentencia.')
    print('No se ejecutó SQL ni se probó conexión con Snowflake.')

if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError:
        raise SystemExit('OpenSSL no terminó correctamente. No se publicó un juego completo de archivos; revisar antes de reintentar.')
