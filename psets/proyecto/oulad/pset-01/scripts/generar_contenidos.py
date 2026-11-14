"""Reconstruye fuentes desde el encargo conservado y auditoría local.
Antes de regenerar, revise cambios editoriales: los archivos distintos se respaldan.
"""
from pathlib import Path
import json,re,shutil,datetime
ROOT=Path(__file__).resolve().parents[2]
PROMPT=(ROOT/'prompt-codex-psets.md').read_text()
def section(start,end): return PROMPT.split(start,1)[1].split(end,1)[0].strip()
def write(path,text):
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True); text=text.strip()+'\n'
    if p.exists() and p.read_text()!=text:
        b=ROOT/'backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')/path; b.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,b)
    p.write_text(text)
def main():
    a=json.loads((ROOT/'pset-01/docs/auditoria-resultados.json').read_text()); pop=a['populations']; orig=pop['original']; init=pop['initial']
    def summary(c): return f"{c['Fail']:,} Fail ({100*c['Fail']/c['N']:.2f} %), {c['Withdrawn']:,} Withdrawn ({100*c['Withdrawn']/c['N']:.2f} %) y {c['Approved']:,} aprobaciones ({100*c['Approved']/c['N']:.2f} %), sobre {c['N']:,} matrículas".replace(',','.')
    evidence=f"Auditoría local del 12 de noviembre de 2026: {summary(orig)}. En la población inicialmente registrada hasta el día 0, {summary(init)}. Son matrículas, no personas únicas ni una tasa institucional actual."
    refs=section('# Referencias','## M.').split('\n\n---')[0].replace('https://research.stem.open.ac.uk/ouanalyse/open-dataset-more/','https://research.stem.open.ac.uk/ouanalyse/dataset/')
    extra=section('## 9. Referencias adicionales para la revisión','Las referencias [1]–[4]').strip()
    extra=extra.replace('Documenta el flujo de alertas; no utilizar su descripción como evidencia causal de tutorías.','Describe el flujo de alertas como antecedente operativo, sin evidencia causal para este proyecto.').replace('no extrapolar su efecto a tutoría académica específica ni a OULAD.','su efecto no es directamente extrapolable a tutoría académica específica ni a OULAD.').replace('no afirmar eficacia universal de las alertas.','no establece eficacia universal de las alertas.')
    # Las fuentes originales se preservan; se documentan las limitaciones de verificación externa.
    memo=section('### 1. El problema de negocio y la métrica de éxito','## 6. Pitch revisado')
    memo='## 1. El problema de negocio y la métrica de éxito\n\n'+memo
    memo=memo.replace('### 2.','## 2.').replace('### 3.','## 3.').replace('### 4.','## 4.')
    memo=memo.replace('OULAD es público y su descarga está confirmada por el autor; la auditoría local permanece pendiente hasta documentar su ejecución [1], [2].','OULAD es público y los cinco archivos se auditaron localmente [1], [2].')
    memo=memo.replace('La publicación describe 32.593 matrículas y 10.655.280 registros diarios de interacción. Incorporar aquí una tasa local de reprobación solo después de verificar población y conteos.',evidence)
    memo=memo.replace('K igual al 10 % de matrículas elegibles','K = floor(0.10 × N) de matrículas elegibles')
    memo='# Apoyo académico a tiempo\n\nWilmer Puerta · PSet 1 · 12 de noviembre de 2026\n\n'+memo+'\n\n'+'''Referencias: [1] J. Kuzilek, M. Hlosta y Z. Zdrahal, “Open University learning analytics dataset,” Scientific Data, 4, 170171, 2017. https://doi.org/10.1038/sdata.2017.171. [2] The Open University, “Open dataset”, https://research.stem.open.ac.uk/ouanalyse/dataset/. Evidencia local: datasets/manifest.json y docs/auditoria-datos.md (12-nov-2026).'''
    write('pset-01/propuesta-pset1.md',memo)
    invariants=section('## 3. Decisiones vigentes e invariantes','## 4. Cuantificación')
    full=section('# **1. Ideas de Proyectos**','## M. Enunciado')
    full='# 1. Ideas de Proyectos\n\n'+full.split('\n\n---')[0] if False else '# 1. Ideas de Proyectos\n\n'+full
    full=full[:full.index('\n# Referencias')]
    # Reconciliar afirmaciones históricas con la auditoría sin alterar otras ideas.
    replacements={
      'Queda pendiente auditar cobertura, volumen, faltantes, uniones y estudiantes repetidos.':'La auditoría descriptiva local documenta volumen, faltantes, uniones y estudiantes únicos; queda pendiente validar cobertura semántica y particiones temporales.',
      'resta auditar los archivos.':'la auditoría descriptiva local está documentada; resta validación temporal y de cobertura.',
      'la auditoría de calidad de los datos sigue pendiente.':'la auditoría descriptiva se documenta en el apartado de evidencia local; continúa pendiente validar la cobertura semántica.',
      'pero no se ha auditado aquí la copia local.':'y la copia local cuenta con auditoría descriptiva y checksums.',
      'Estas cifras son documentales, no conteos verificados del archivo del equipo ni del subconjunto finalmente elegible.':'Estas cifras describen la publicación. Los conteos locales y las poblaciones elegibles se presentan separadamente en la evidencia local.',
      'no se afirma que ya se hayan completado esos pasos.':'se completó la auditoría descriptiva, pero el procesamiento de características y la inferencia siguen pendientes.',
      'En un piloto posterior: diferencia en reprobación entre estrategias de atención comparables, acompañada de participación, costos y posibles efectos adversos.':'En un piloto posterior: diferencia absoluta en proporción de aprobación entre grupos asignados, con intervalo de confianza; reportar también Fail, Withdrawn, participación, costos y posibles efectos adversos.',
      'Para evaluar causalmente el programa, una institución tendría que comparar políticas de atención con capacidad equivalente, idealmente mediante un diseño experimental viable o, si no lo fuera, un diseño cuasiexperimental justificado.':'Para evaluar causalmente la oferta de apoyo, se propone el protocolo aleatorio posterior desarrollado en la revisión metodológica. Comparar políticas de selección sería una pregunta adicional con presupuesto equivalente.',
      'Descarga confirmada por el equipo.':'Archivo local presente y auditado descriptivamente.',
      'Descarga confirmada.':'Archivo local presente y auditado descriptivamente.',
      'Técnico — Fuga de información (alta)':'Técnico — Fuga de información (crítica)',
      'cada estudiante contará una sola vez en la cobertura acumulada':'cada matrícula contará una sola vez en TP acumulados; se informarán además personas únicas',
      'La primera etapa generará un inventario de archivos, períodos, categorías, matrículas, estudiantes únicos y clases del target.':'La auditoría descriptiva generó el inventario de archivos, períodos, categorías, matrículas, personas únicas y clases del target. La cobertura semántica continúa pendiente.',
      'Antes de implementar se confirmarán la ruta de los archivos descargados, los módulos y ediciones elegibles, las variables realmente disponibles al inicio y los recursos de ejecución.':'La fuente local se confirmó en datasets/. Antes de implementar se validarán los módulos y pares de ediciones elegibles para la evaluación temporal, las variables realmente disponibles al inicio y los recursos de ejecución.',
    }
    for old,new in replacements.items(): full=full.replace(old,new)
    full=full.replace('El proceso institucional será simulado y la meta predictiva deberá comprobarse.','El proceso institucional será simulado y la meta predictiva deberá comprobarse.')
    audit='## Evidencia local y límites de la auditoría\n\n'+evidence+'\n\n'+(ROOT/'pset-01/docs/auditoria-datos.md').read_text()
    mapping='''## Correspondencia de riesgos

Los ocho riesgos ampliados se agrupan sin cambiar sus supuestos: grupo R1 del memo y pitch = ampliados R1 y R4 (mejora y transferencia); grupo R2 = ampliados R2, R3 y R8 (fuga, cobertura y procesamiento); grupo R3 = ampliados R5 y R6 (capacidad e impacto); grupo R4 = ampliado R7 (equidad y confianza). Gravedades de los grupos: alta, crítica, alta y alta.
'''
    continuity='''## Continuidad con PSet 2

Diseño pendiente: Fuente → Kestra → Raw → dbt/Bronze → dbt/Silver → dbt/Gold → Spark/OBT, persistido en Snowflake. La OBT tendrá grano matrícula–corte. El pipeline, los modelos y el MVP no se han implementado. El documento de contrato fija elegibilidad antes de actividad y separa target de predictores. No se ejecutaron servicios ni recursos cloud.
'''
    guide='''## Guía del pitch

Seis diapositivas: oportunidad de apoyo, magnitud auditada, decisión quincenal, viabilidad y MVP, beneficio ilustrativo y riesgos, solicitud y criterios de avance. El texto visible exacto y las notas se conservan en pset01-presentacion.md. La comparación 40 a 44 es ilustrativa; el piloto posterior mide aprobación por asignación.

## Registro de cambios y sincronización

12-nov-2026: reconciliación del respaldo completo, auditoría descriptiva local, especificación de recencia, capacidad y protocolo posterior. Colab fue un antecedente de trabajo; no se proporcionó URL ni sesión autenticada identificable para respaldar, comparar y sincronizar sus celdas. Sincronización remota pendiente. Esta fuente local es la base controlada.
'''
    full='# Proyecto completo del PSet 1\n\nWilmer Puerta · 12 de noviembre de 2026\n\nEstado: propuesta revisada y auditoría descriptiva. No se entrenaron modelos ni ejecutaron intervenciones.\n\n'+full.strip()+'\n\n# Revisión metodológica vigente\n\n'+invariants+'\n\n'+mapping+'\n\n'+audit+'\n\n'+continuity+'\n\n'+guide+'\n\n# Referencias\n\n'+refs+'\n\n'+extra
    write('pset-01/proyecto-completo-pset1.md',full)
    risk=memo.split('## 4. Riesgos principales',1)[1].split('Referencias:',1)[0]
    canvas='''# Canvas de viabilidad y riesgos

Wilmer Puerta · PSet 1 · 12-nov-2026

## Problema y decisión

Universidad hipotética, sin socio comprometido. Focalizar revisión preventiva con capacidad limitada; el resultado inmediato es una lista para el tutor. El coordinador valida cupos, el tutor revisa siempre contexto y decide apoyo. El sistema calcula y ordena, sin sanciones ni contactos reales en el MVP.

## Predicción y éxito

Unidad: matrícula estudiante–módulo–edición. Probabilidades de Fail, Withdrawn y aprobación (Pass + Distinction) al cierre. Cortes: 14, 28, 42 y 56. Población registrada hasta día 0, excluyendo únicamente retiros ya ocurridos al corte. Orden por P(Fail). Regresión logística multinomial y Random Forest, cada uno estático frente al mismo algoritmo enriquecido con actividad longitudinal. Sin notas de evaluaciones.

PR-AUC para Fail (implementación por fijar antes de entrenar), calibración e incertidumbre. Meta provisional: +10 % relativo de TP@K en día 56 frente al baseline estático con igual población y K. K = floor(0.10 × N) por edición y corte, sensibilidad 5 % y 20 %. Umbral: última puntuación admitida, desempate estable por clave sin target. Si TP estático es cero, informar diferencia absoluta. Omitir una futura reprobación se considera el error más costoso por oportunidad perdida; falsas alertas consumen cupos. Costos y capacidad reales por validar.

Comparador adicional: días desde la última actividad hasta corte, descendente. Nunca activos con cobertura comprobada: contar desde día 0; cobertura desconocida: marcar información insuficiente y aplicar política común documentada antes de evaluar. Actividad previa al inicio se conserva y se audita. Las repeticiones consumen cupos y los TP acumulados cuentan una vez por matrícula; informar personas únicas y anticipación al cierre.

## Datos y acceso

| Dato | Fuente | Estado real |
|---|---|---|
| Antecedentes y etiquetas | studentInfo.csv | Existe, acceso local confirmado, auditado descriptivamente |
| Registro y retiro | studentRegistration.csv | Existe, acceso local confirmado, auditado descriptivamente |
| Edición y duración | courses.csv | Existe, acceso local confirmado, auditado descriptivamente |
| Recursos | vle.csv | Existe, acceso local confirmado, auditado descriptivamente |
| Actividad fechada | studentVle.csv | Existe, acceso local confirmado, auditado descriptivamente |
| Capacidad y costos institucionales | Institución participante | No disponibles ni acceso confirmado |
| Oferta, participación y efectos del programa propuesto | Futuro piloto | No existen todavía para esta intervención |

'''+evidence+'''

La auditoría descriptiva no prueba cobertura completa ni disponibilidad inicial de todos los antecedentes. Validación con ediciones posteriores compatibles, estudiantes separados y etiquetas históricas maduras antes del corte simulado. Transformaciones aprendidas solo con entrenamiento. No usar target ni fecha futura de retiro como predictor.

## Resultado de negocio y seguimiento

Focalización: TP@K, precisión, recobrado, omisiones, primeras detecciones, anticipación y revisiones repetidas con el mismo presupuesto. Impacto posterior: asignación aleatoria por persona a oferta definida de acompañamiento o atención habitual, estratificada según diseño. Intención de tratar, diferencia absoluta de aprobación e intervalo de confianza. Registrar también Fail, Withdrawn, oferta, contacto, participación, otras ayudas, tiempos y costos. Resolver matrículas múltiples y contaminación; calcular muestra posteriormente según tasa inicial, efecto mínimo, potencia y agrupamiento. No estima efectos individuales ni demuestra superioridad causal de selección longitudinal.

## Riesgos, supuestos, verificación y gravedad

'''+risk+'\n\nReferencias: Kuzilek et al. (2017), doi:10.1038/sdata.2017.171; documentación oficial de OULAD; auditoría local en docs/auditoria-datos.md y datasets/manifest.json.'
    write('pset-01/canvas-wilmer-puerta.md',canvas)
    # Texto docente íntegro, separado de decisiones locales.
    write('pset-02/enunciado.md','# Enunciado del profesor\n\n'+section('## M. Enunciado del PSet 2 para `pset-02/enunciado.md`','## N.').rstrip('-\n ')+'\n\nNota del proyecto: la estructura pset_2/ transcrita se implementará en pset-02/. Los ejemplos 120 y 4.3 % son del profesor, no resultados OULAD.')
    write('pset-02/rubrica.md',section('## N. Rúbrica del PSet 2 para `pset-02/rubrica.md`','## O.').rstrip('-\n '))
    write('pset-01/rubrica.md',section('## O. Rúbrica del PSet 1 para `pset-01/rubrica.md`','NONEXISTENT')+'\n\nNota de organización local: este repositorio contiene cuatro etapas definidas por el usuario. Se conserva literalmente la referencia del profesor a cinco PSets y su ponderación; no se inventan requisitos para PSet 3 o 4.')
    for d in ['pset-03','pset-04','pset-02/kestra','pset-02/dbt','pset-02/spark']:
        (ROOT/d).mkdir(parents=True,exist_ok=True); (ROOT/d/'.gitkeep').touch()
    print('Fuentes editoriales generadas')
if __name__=='__main__': main()
