"""Invariantes de los tres gaps docentes en fuentes editoriales y datos locales."""
from pathlib import Path
import json
from calcular_metricas_negocio import build

ROOT=Path(__file__).resolve().parents[2]

def validate():
    checks={}
    def check(name,value):
        checks[name]=bool(value)
        if not value:raise AssertionError(name)
    metrics=json.loads((ROOT/'pset-01/docs/metricas-negocio.json').read_text())
    check('business_metrics_match_local_evidence',metrics==build())
    selected=metrics['per_cutoff'][-1]
    check('primary_population_and_capacity',selected['eligible_enrollments']==26294 and selected['future_failures']==6972 and selected['capacity_slots']==2619)
    check('available_lead_not_model_performance',selected['lead_weeks_display']=='25,4-30,4' and round(selected['oracle_upper_coverage_pct'],1)==37.6)
    for name in ['propuesta-pset1.md','propuesta-pset1_version_extendida.md','canvas-wilmer-puerta.md','proyecto-completo-pset1.md']:
        text=(ROOT/'pset-01'/name).read_text().casefold()
        check(name+'_three_policies',all(word in text for word in ['reactiva','estática','longitudinal']))
        check(name+'_coverage_and_lead',all(word in text for word in ['cobertura preventiva','anticipación potencial','25,4-30,4','primera selección']))
        check(name+'_shared_capacity',all(word in text for word in ['2.619','6.972','26.294','repeti']) and any(word in text for word in ['presupuesto total','presupuestos totales']))
        check(name+'_business_target_and_baseline_zero',all(word in text for word in ['10 %','tp estático','diferencia absoluta']))
        check(name+'_technical_feasibility',all(word in text for word in ['108.277','35 columnas','168 pruebas dbt','random forest','pr-auc']))
        check(name+'_mvp_scope',all(word in text for word in ['mvp','selector','versionad','d2l','wifi','lopdp','fase posterior']))
        check(name+'_separate_intervention_hypothesis',all(word in text for word in ['hipótesis','costos','participación','personas únicas']))
    for name in ['propuesta-pset1.md','propuesta-pset1_version_extendida.md','proyecto-completo-pset1.md']:
        text=(ROOT/'pset-01'/name).read_text().casefold()
        check(name+'_tutoring_protocol',all(word in text for word in ['aleatoria por estudiante','atención habitual','aprobación','pass','distinction','intención de tratar','intervalo de confianza','matrículas múltiples','fuera del mvp']))
    slides=json.loads((ROOT/'pset-01/scripts/pitch-contenido.json').read_text())
    check('pitch_six_slides',len(slides)==6)
    visible=['\n'.join([s['title'],s['message']]+[o['text'] for o in s['objects']]).casefold() for s in slides]
    check('pitch_problem_quantified_visibly',all(word in visible[0] for word in ['21,64','7.052','32.593']))
    check('pitch_benefit_and_lead_visibly',all(word in visible[1] for word in ['10 %','2.619','25,4-30,4','potencial','evaluar']))
    check('pitch_three_policies_visibly',all(word in visible[2] for word in ['reactiva','estática','longitudinal','mismo k']))
    check('pitch_feasibility_and_evaluation_visibly',all(word in visible[3] for word in ['5 csv','108.277','random forest','prueba temporal','estudiantes separados','pr-auc']))
    check('pitch_mvp_and_exclusions_visibly',all(word in visible[4] for word in ['selector','listas','tres políticas','versionad','oulad','d2l','wifi']))
    check('pitch_sponsor_request_and_risks_visibly',all(word in visible[5] for word in ['apoyo solicitado','validar los cupos','r1','r2','r3','r4','hipótesis posterior']))
    return checks

if __name__=='__main__':
    checks=validate();print(f'OK: {len(checks)} invariantes de fuentes revisadas.')
