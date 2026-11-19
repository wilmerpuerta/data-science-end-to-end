"""Genera únicamente secretos locales de infraestructura, sin datos Snowflake."""
from pathlib import Path
import os
import secrets
ROOT=Path(__file__).resolve().parents[2]
def main():
    path=ROOT/'pset-02/.env.infra'
    if path.exists():
        print('.env.infra ya existe; se conserva sin leer ni sobrescribir.')
        return
    values={'PSET2_POSTGRES_PASSWORD':secrets.token_hex(32),
            'PSET2_KESTRA_PASSWORD':'Aa1'+secrets.token_hex(24)}
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'w') as f:
        f.write('# Privado local. No versionar ni compartir.\n')
        for k,v in values.items():f.write(f'{k}={v}\n')
    print('.env.infra creado con permisos privados. No contiene credenciales Snowflake.')
if __name__=='__main__':main()
