"""Prueba HTTP local con credenciales de infraestructura sin imprimirlas."""
from pathlib import Path
import argparse,base64,json,time,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parents[2]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seed',action='store_true');parser.add_argument('--execute',action='store_true');parser.add_argument('--check-auth',action='store_true');args=parser.parse_args()
    settings=dict(line.split('=',1) for line in (ROOT/'pset-02/.env.infra').read_text().splitlines() if line and not line.startswith('#'))
    token=base64.b64encode(('admin@psets.local:'+settings['PSET2_KESTRA_PASSWORD']).encode()).decode()
    port=int(settings.get('PSET2_KESTRA_PORT','8080'));assert 1024<=port<=65535
    base=f'http://127.0.0.1:{port}'
    def request(path,method='GET',data=None,content_type='application/x-yaml'):
        r=urllib.request.Request(base+path,method=method,data=data,
            headers={'Authorization':'Basic '+token,'Content-Type':content_type})
        with urllib.request.urlopen(r,timeout=20) as response:return json.loads(response.read())
    for prefix in ['/api/v1/main','/api/v1']:
        try:
            if args.seed:
                # Consultar antes de crear para conservar la misma definición en reinicios.
                try: flow=request(prefix+'/flows/pset2.local/infra_smoke')
                except urllib.error.HTTPError as e:
                    if e.code!=404:raise
                    flow=request(prefix+'/flows','POST',(ROOT/'pset-02/kestra/infra_smoke.yml').read_bytes())
            else:flow=request(prefix+'/flows/pset2.local/infra_smoke')
            assert flow['id']=='infra_smoke' and flow['namespace']=='pset2.local'
            result={'status':'ok','flow':'pset2.local/infra_smoke','api_prefix':prefix,'seed':args.seed}
            if args.check_auth:
                try:
                    with urllib.request.urlopen(base+prefix+'/flows/pset2.local/infra_smoke',timeout=10):pass
                except urllib.error.HTTPError as error:
                    if error.code!=401:raise
                    result['unauthenticated_request_rejected']=True
                else:raise SystemExit('La API respondió sin autenticación. Revisar configuración antes de seguir.')
            if args.execute:
                run=request(prefix+'/executions/pset2.local/infra_smoke','POST',b'--PSET2Smoke--\r\n','multipart/form-data; boundary=PSET2Smoke')
                for _ in range(30):
                    execution=request(prefix+'/executions/'+run['id'])
                    state=execution['state']['current']
                    if state in ['SUCCESS','FAILED','WARNING','KILLED','CANCELLED']:break
                    time.sleep(1)
                if state!='SUCCESS':raise SystemExit('El flujo local no terminó en SUCCESS: '+state)
                result.update(execution_id=run['id'],execution_state=state)
            print(json.dumps(result))
            return
        except urllib.error.HTTPError as e:
            if e.code==404:continue
            raise SystemExit(f'Kestra HTTP {e.code}; no se muestran datos de autenticación.')
    raise SystemExit('No se encontró la ruta API/flujo esperado.')
if __name__=='__main__':
    try:main()
    except urllib.error.URLError:raise SystemExit('No se pudo acceder a la API local. Comprobar servicios y permisos de red.')
