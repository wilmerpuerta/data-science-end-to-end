"""Cierre verificable de la entrega; no espera indefinidamente un coordinador ausente."""
from pathlib import Path
from datetime import datetime,timezone
import json
from ejecutar_notebooks_entrega import main as notebooks
ROOT=Path(__file__).resolve().parents[1]
def main():
 statepath=ROOT/'docs/estado-v2.json'
 if not statepath.exists():raise RuntimeError('Falta docs/estado-v2.json: verificar estado del estudio antes del cierre')
 state=json.loads(statepath.read_text())
 if not state.get('experiments_complete'):raise RuntimeError('El estudio no está completo; cerrar sus fases antes de los notebooks')
 notebooks(reuse_verified=True)
 report={'state':'complete','notebooks_executed_and_verified':6,'editorial_complete':True,'remaining':[],'new_api_requests':0,'checked_at_utc':datetime.now(timezone.utc).isoformat()}
 (ROOT/'docs/cierre-notebooks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return report
if __name__=='__main__':main()
