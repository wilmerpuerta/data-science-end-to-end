"""Deriva cifras descriptivas y límites de negocio; no ajusta modelos ni políticas."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]

def fmt(value, places=1):
    return str(Decimal(str(value)).quantize(Decimal(10)**-places,rounding=ROUND_HALF_UP)).replace('.',',')

def build():
    audit=json.loads((ROOT/'pset-01/docs/auditoria-resultados.json').read_text())
    manifest=json.loads((ROOT/'datasets/manifest.json').read_text())
    courses=ROOT/'datasets/courses.csv'
    assert hashlib.sha256(courses.read_bytes()).hexdigest()==manifest['files']['courses.csv']['sha256']
    with courses.open() as f:
        lengths={(r['code_module'],r['code_presentation']):int(r['module_presentation_length']) for r in csv.DictReader(f)}
    with (ROOT/'pset-01/docs/poblaciones-por-edicion.csv').open() as f:
        rows=list(csv.DictReader(f))
    cuts=[]
    for day in [14,28,42,56]:
        parts=[r for r in rows if r['population']==f'day_{day}']
        count=lambda key:sum(int(Decimal(r[key])) for r in parts)
        n,f,k=count('N'),count('Fail'),count('K')
        assert (n,f,k)==tuple(audit['populations']['cuts'][str(day)][key] for key in ['N','Fail','K_sum_by_edition'])
        upper=sum(min(int(Decimal(r['K'])),int(r['Fail'])) for r in parts)
        minimum=min((v-day)/7 for v in lengths.values());maximum=max((v-day)/7 for v in lengths.values())
        cuts.append({'cutoff_day':day,'eligible_enrollments':n,'future_failures':f,'capacity_slots':k,
                     'oracle_upper_tp':upper,'oracle_upper_coverage_pct':100*upper/f,
                     'lead_weeks_available_min':minimum,'lead_weeks_available_max':maximum,
                     'lead_weeks_display':fmt(minimum)+'-'+fmt(maximum)})
    return {'revision':'2026-11-15','status':'ok','unit':'matrícula estudiante-módulo-edición',
            'original_enrollments':audit['populations']['original']['N'],'original_failures':audit['populations']['original']['Fail'],
            'original_failure_pct':100*audit['populations']['original']['Fail']/audit['populations']['original']['N'],
            'duration_days_min':min(lengths.values()),'duration_days_max':max(lengths.values()),'per_cutoff':cuts,
            'primary_cutoff_day':56,'primary_capacity_fraction':0.10,'relative_improvement_target_pct':10,
            'policies':['reactiva','estática','longitudinal'],
            'scope':'Descriptivos del histórico completo, márgenes temporales y cota ideal; no rendimiento obtenido. La evaluación real debe recalcular N, Fail y K en la prueba reservada.',
            'anticipation_reference':'Cierre aproximado mediante duración de edición; no fecha observada de tutoría ni comunicación de notas.'}

def main():
    report=build();(ROOT/'pset-01/docs/metricas-negocio.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Métricas descriptivas de negocio y márgenes por corte reconciliados.')

if __name__=='__main__':main()
