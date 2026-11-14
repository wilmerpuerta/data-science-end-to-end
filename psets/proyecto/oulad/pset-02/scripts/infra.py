"""Comandos de infraestructura portables desde cualquier directorio."""
from pathlib import Path
import argparse,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','validate','pull','build','up','status','stop','down','dbt-version','spark-test'])
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--cloud',action='store_true',help='Añadir ejecutor Kestra con montajes privados de solo lectura.')
    mode.add_argument('--local-only',action='store_true',help='Usar explícitamente solo la infraestructura sin montajes cloud.')
    parser.add_argument('--no-cache',action='store_true',help='Reconstruir capas propias; solo válido con build.')
    args=parser.parse_args();action=args.action
    if args.no_cache and action!='build':parser.error('--no-cache solo se usa con build')
    cloud_enabled=args.cloud or (not args.local_only and (ROOT/'pset-02/.env.cloud').is_file() and (ROOT/'pset-02/docker-compose.cloud.yml').is_file())
    if action=='prepare':
        return subprocess.call([sys.executable,str(ROOT/'pset-02/scripts/preparar_infra.py')])
    if action=='build':
        # Usar contexto relativo con docker build evita que Compose/Bake
        # normalice de forma distinta rutas Unicode en macOS.
        images=[('pset2-dbt:core1.10.13-snowflake1.10.2','pset-02/dbt')]
        if cloud_enabled:
            images.append(('pset2-kestra:v1.0.0-snowflake4.7.4','pset-02/ingestion'))
            images.append(('pset2-spark:3.5.6-snowflake3.2.3','pset-02/spark'))
        for tag,context in images:
            code=subprocess.call(['docker','build']+(['--no-cache'] if args.no_cache else [])+['-t',tag,context],cwd=ROOT)
            if code:return code
        return 0
    env=ROOT/'pset-02/.env.infra'
    if not env.is_file():raise SystemExit('Falta .env.infra. Ejecutar infra.py prepare; si ya existían volúmenes, recuperar primero el archivo privado original.')
    cmd=['docker','compose','--project-directory',str(ROOT/'pset-02'),
         '--env-file',str(env)]
    if cloud_enabled:
        cloud=ROOT/'pset-02/.env.cloud'
        if not cloud.is_file():raise SystemExit('Falta .env.cloud. Ejecutar configurar_cloud.py en la terminal local.')
        cmd+=['--env-file',str(cloud)]
    cmd+=['-f',str(ROOT/'pset-02/docker-compose.yml')]
    if cloud_enabled:cmd+=['-f',str(ROOT/'pset-02/docker-compose.cloud.yml')]
    operations={'validate':['config','--quiet'],'pull':['pull','--ignore-buildable'],
                'up':['up','-d','--wait','--wait-timeout','240'],
                'stop':['stop'],'down':['down'],
                'dbt-version':['run','--rm','--no-deps','dbt','--version'],
                'spark-test':['exec','-T','spark','/opt/spark/bin/spark-submit','--master','local[2]',
                              '--driver-memory','1g','/workspace/spark/smoke_test.py']}
    if action=='status':
        result=subprocess.run(cmd+['ps','--format','json'],capture_output=True,text=True)
        if result.returncode:raise SystemExit('Docker Compose no respondió. Revisar el motor local.')
        content=result.stdout.strip()
        rows=json.loads(content) if content.startswith('[') else [json.loads(line) for line in content.splitlines() if line]
        print(json.dumps([{'service':r['Service'],'state':r['State'],'health':r.get('Health','')} for r in rows],indent=2))
        return 0
    return subprocess.call(cmd+operations[action],cwd=ROOT)
if __name__=='__main__':raise SystemExit(main())
