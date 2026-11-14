"""PPTX OOXML nativo y fuente exacta visible. Fallback sin artifact-tool local.
No usa python-pptx ni diapositivas aplanadas. Diagramas y textos editables.
"""
from generar_contenidos import ROOT,write
import json,zipfile,html
def box(text,x,y,w,h,size=26,color='FFFFFF',bold=False,fill=None):
 return dict(text=text,x=x,y=y,w=w,h=h,size=size,color=color,bold=bold,fill=fill)
def main():
 slides=[]
 def add(title,message,objects,visual,notes,sources): slides.append(dict(title=title,message=message,objects=objects,visual=visual,notes=notes,sources=sources))
 add('Apoyo académico a tiempo','Identificar mejor a quién apoyar, con la misma capacidad preventiva.',[
 box('Wilmer Puerta',64,290,1000,42,28,'87CEEB'),box('Señales  →  Prioridad  →  Revisión del tutor',64,405,1130,80,37),box('Prueba de concepto con OULAD · Universidad hipotética',64,610,1100,40,22,'87CEEB')],
 'Flujo horizontal editable de señales a revisión del tutor.',
 'No existe socio institucional comprometido. El sistema propone una prioridad y el tutor siempre revisa contexto y decide. No hay contactos reales ni sanciones automáticas.',
 'Propuesta del proyecto y documentación oficial de OULAD, doi:10.1038/sdata.2017.171.')
 add('El riesgo cambia durante el módulo','Una lista fija puede omitir trayectorias que empeoran.',[
 box('21,64 %',64,265,550,100,76,'FF354B',True),box('7.052 Fail de 32.593 matrículas originales',64,367,1150,50,32),box('Retiros: 10.156 (31,16 %) · Aprobación: 15.385 (47,20 %)',64,437,1150,48,26),box('Revisión temprana: día 14  →  28  →  42  →  56',64,525,1150,55,32,'87CEEB'),box('Fuente: auditoría local OULAD, 12-nov-2026. No es una tasa institucional actual.',64,625,1150,42,20,'87CEEB')],
 'Cifra central y línea de cuatro cortes, todo editable.',
 'Denominador original: 32.593 matrículas, 28.785 personas únicas. Población inicialmente registrada hasta día 0: 32.314. Al día 56: 26.294 elegibles, 6.972 Fail y 4.056 Withdrawn; se excluyen retiros ya ocurridos y registros tardíos o sin fecha. La cifra central cuantifica el histórico completo, no una universidad actual. La trayectoria de riesgo es una hipótesis a evaluar, no una curva ya estimada.',
 'datasets/manifest.json; docs/auditoria-datos.md; docs/poblaciones-por-edicion.csv.')
 add('Una prioridad de revisión que se actualiza','El tutor decide el apoyo a partir de una lista quincenal.',[
 box('Observar actividad  →  Estimar P(Fail)',64,260,1150,66,38,'87CEEB'),box('Ordenar K cupos  →  Tutor revisa y decide',64,346,1150,66,38),box('Presupuesto preventivo simulado: 10 % por edición y corte',64,455,1150,52,30),box('K = floor(0.10 × N) · Sensibilidad: 5 % y 20 %',64,522,1150,50,28),box('Comparador operativo: recencia frente a priorización con modelos',64,610,1150,50,25,'87CEEB')],
 'Dos pasos de flujo con textos nativos editables.',
 'Cortes 14, 28, 42 y 56. Ordenar por P(Fail), umbral último caso admitido, desempate estable por clave sin etiqueta. Recencia descendente desde última interacción <= corte. Nunca activos con cobertura comprobada: contar desde inicio; desconocidos: marcar insuficiencia y fijar política común antes de evaluar. La regla usa tiempo y es adicional. Comparación principal: estático/longitudinal, mismo algoritmo, N y K. Los clics no demuestran intención. Repeticiones consumen cupos y TP acumulados cuentan una vez por matrícula.',
 'Decisiones metodológicas del proyecto; auditoría local de elegibilidad.')
 add('Viabilidad, evaluación y producto concreto','Datos disponibles y una comparación retrospectiva delimitada.',[
 box('OULAD auditado: 5 archivos · 10.655.280 registros de actividad',64,262,1150,68,30,'87CEEB'),box('Regresión logística multinomial y Random Forest',64,344,1150,44,29),box('Estático frente a longitudinal · Ediciones posteriores compatibles',64,405,1150,55,27),box('Estudiantes separados · Igual capacidad · PR-AUC y TP@K',64,467,1150,55,28),box('MVP previsto: preparación, puntuaciones por corte, listas, evolución y reporte',64,554,1150,78,29)],
 'Secuencia de datos, validación y producto descrita con objetos editables.',
 'El target distingue Fail, Withdrawn y Pass/Distinction. Etiquetas maduras antes de predicción simulada; transformaciones aprendidas solo con entrenamiento. Familias estática/longitudinal comparadas por algoritmo; sin notas de evaluaciones. PR-AUC para Fail, calibración e incertidumbre. La auditoría no demuestra todavía viabilidad de particiones temporales. No se entrenaron modelos ni se construyó el MVP. PSet 2 preparará Kestra, dbt, Spark y Snowflake.',
 'Kuzilek et al., 2017, doi:10.1038/sdata.2017.171; auditoría local y contrato preliminar de datos.')
 add('Beneficio medible y condiciones de éxito','Meta provisional: +10 % relativo de detecciones al día 56, a igual K.',[
 box('40  →  44',64,250,540,90,65,'FF354B',True),box('Futuras reprobaciones identificadas con 100 revisiones',64,345,1150,45,28),box('Ejemplo ilustrativo, no resultado obtenido ni reprobaciones evitadas',64,400,1150,45,24,'87CEEB'),box('R1 Mejora incierta: comparar con incertidumbre\nR2 Calidad y fuga: auditar fechas y cobertura\nR3 Capacidad y efecto: simular carga y evaluar piloto\nR4 Equidad y confianza: revisar errores y mantener juicio humano',64,468,1150,157,24),box('Piloto posterior: aprobación entre grupos asignados a oferta de apoyo o atención habitual',64,640,1150,45,20,'87CEEB')],
 'Ejemplo numérico y cuatro riesgos compactos, editables.',
 'Gravedades R1 alta, R2 crítica, R3 alta, R4 alta. R1 supone aporte transferible; R2 información disponible y comparable; R3 capacidad viable y apoyo útil; R4 errores aceptables entre grupos. El ejemplo equivale a +4 puntos de precisión (40 % a 44 %) y +10 % relativo en TP. No es rendimiento medido de recencia. Si TP estático=0 informar diferencia absoluta. Los ocho riesgos ampliados se agrupan R1={1,4}, R2={2,3,8}, R3={5,6}, R4={7}. El piloto estimaría oferta de un programa, no efectos individuales ni superioridad causal de selección longitudinal.',
 'Meta y ejemplo hipotéticos del proyecto; protocolo de impacto posterior. No hay retorno financiero estimado.')
 add('Respaldar una prueba de concepto y una decisión informada','Avanzar al piloto solo con evidencia favorable y condiciones acordadas.',[
 box('Se necesita un responsable académico y un referente de tutorías',64,263,1150,65,31,'87CEEB'),box('Validar el presupuesto preventivo y la capacidad de revisión',64,340,1150,55,29),box('Auditar y cuantificar  →  Comparar y demostrar  →  Decidir sobre piloto',64,425,1150,85,32),box('Criterios: mejora e incertidumbre, calidad, carga y equidad',64,535,1150,52,28),box('Piloto posterior: oferta aleatoria de apoyo vs atención habitual\nMedir aprobación, retiro, participación y costos',64,606,1150,80,23,'87CEEB')],
 'Hitos y criterio de avance en una composición editorial editable.',
 'La auditoría descriptiva ya está realizada, con cobertura y temporalidad aún por validar. No hay plazo inventado ni compromiso de reducción de Fail. Piloto: aleatorización por persona con estratificación pertinente, asignación coherente de múltiples matrículas; controlar contaminación o ajustar por agrupamiento. Intención de tratar, diferencia absoluta de aprobación e intervalo de confianza. Informar también Fail, Withdrawn, oferta, contacto, participación, otras ayudas, tiempos y costos. Calcular muestra según tasa inicial, efecto mínimo, potencia y pérdidas. Aprobación = Pass + Distinction. Mantener apoyo habitual. El piloto requiere institución y autorizaciones futuras.',
 'Diseño del proyecto. OU Analyse: https://research.stem.open.ac.uk/ouanalyse/ respalda plausibilidad operativa, no causalidad. Klenke et al., arXiv:2102.08803, efecto positivo impreciso en otro contexto.')
 out=['# Pitch revisado: seis diapositivas','', 'Wilmer Puerta · 12-nov-2026. Fuente visible exacta del PPTX. Los bloques de notas y fuentes no son texto visible. Paleta: negro/rojo, azul cielo y blanco.']
 for i,s in enumerate(slides,1):
  out+=['',f"## Diapositiva {i}",'', '### Contenido visible exacto','',s['title'],'',s['message'],'']+[o['text']+'\n' for o in s['objects']]+['### Visual propuesto','',s['visual'],'','### Notas del presentador','',s['notes'],'','### Fuentes','',s['sources']]
 write('pset-01/pset01-presentacion.md','\n'.join(out)); write('pset-01/scripts/pitch-contenido.json',json.dumps(slides,ensure_ascii=False,indent=2))
 make_pptx(slides)

NS='xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
def rels(items): return '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/{kind}" Target="{target}"/>' for i,(kind,target) in enumerate(items,1))+'</Relationships>'
def shape(i,o):
 esc=html.escape; unit=lambda x:str(round(x*9525))
 paras=''.join('<a:p><a:pPr/><a:r><a:rPr lang="es-EC" sz="'+str(round(o['size']*75))+'" b="'+str(int(o['bold']))+'"><a:solidFill><a:srgbClr val="'+o['color']+'"/></a:solidFill><a:latin typeface="Arial"/></a:rPr><a:t>'+esc(t)+'</a:t></a:r><a:endParaRPr lang="es-EC"/></a:p>' for t in o['text'].split('\n'))
 return f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="Text {i}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{unit(o["x"])}" y="{unit(o["y"])}"/><a:ext cx="{unit(o["w"])}" cy="{unit(o["h"])}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" rIns="0" tIns="0" bIns="0"/><a:lstStyle/>{paras}</p:txBody></p:sp>'
GROUP='<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
def make_pptx(slides):
 path=ROOT/'pset-01/output/pitch/PSet1_pitch_Puerta_Wilmer.pptx'; path.parent.mkdir(parents=True,exist_ok=True)
 files={}; overrides=[]
 def put(n,t): files[n]='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+t if not t.startswith('<?xml') else t
 def part(n,ct): overrides.append(f'<Override PartName="/{n}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.{ct}+xml"/>')
 put('_rels/.rels',rels([('officeDocument','ppt/presentation.xml')]))
 put('ppt/presentation.xml',f'<p:presentation {NS}><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId7"/></p:sldMasterIdLst><p:sldIdLst>'+''.join(f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1,7))+'</p:sldIdLst><p:sldSz cx="12192000" cy="6858000" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>'); part('ppt/presentation.xml','presentation.main')
 put('ppt/_rels/presentation.xml.rels',rels([('slide',f'slides/slide{i}.xml') for i in range(1,7)]+[('slideMaster','slideMasters/slideMaster1.xml')]))
 put('ppt/slideMasters/slideMaster1.xml',f'<p:sldMaster {NS}><p:cSld><p:spTree>{GROUP}</p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles/></p:sldMaster>');part('ppt/slideMasters/slideMaster1.xml','slideMaster')
 put('ppt/slideMasters/_rels/slideMaster1.xml.rels',rels([('slideLayout','../slideLayouts/slideLayout1.xml'),('theme','../theme/theme1.xml')]))
 put('ppt/slideLayouts/slideLayout1.xml',f'<p:sldLayout {NS} type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{GROUP}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>');part('ppt/slideLayouts/slideLayout1.xml','slideLayout')
 put('ppt/slideLayouts/_rels/slideLayout1.xml.rels',rels([('slideMaster','../slideMasters/slideMaster1.xml')]))
 colors={'dk1':'101016','lt1':'FFFFFF','dk2':'182E55','lt2':'F1F5F9','accent1':'E1263E','accent2':'87CEEB','accent3':'265DAB','accent4':'B8C7D9','accent5':'FF8E9A','accent6':'7188A8','hlink':'87CEEB','folHlink':'E1263E'}
 put('ppt/theme/theme1.xml','<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="OULAD"><a:themeElements><a:clrScheme name="OULAD">'+''.join(f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>' for k,v in colors.items())+'</a:clrScheme><a:fontScheme name="Arial"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="OULAD"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>')
 overrides.append('<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>')
 for i,s in enumerate(slides,1):
  objs=[box(s['title'],64,55,1150,116,44 if i!=6 else 40,'FFFFFF',True),box(s['message'],64,185,1150,64,29,'87CEEB')]+s['objects']
  put(f'ppt/slides/slide{i}.xml',f'<p:sld {NS}><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="101016"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>{GROUP}'+''.join(shape(j,o) for j,o in enumerate(objs,2))+'</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>');part(f'ppt/slides/slide{i}.xml','slide')
  put(f'ppt/slides/_rels/slide{i}.xml.rels',rels([('slideLayout','../slideLayouts/slideLayout1.xml'),('notesSlide',f'../notesSlides/notesSlide{i}.xml')]))
  note=shape(2,box(s['notes']+'\nFuentes: '+s['sources'],0,0,600,700,18))
  put(f'ppt/notesSlides/notesSlide{i}.xml',f'<p:notes {NS}><p:cSld><p:spTree>{GROUP}{note}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>');part(f'ppt/notesSlides/notesSlide{i}.xml','notesSlide')
  put(f'ppt/notesSlides/_rels/notesSlide{i}.xml.rels',rels([('slide',f'../slides/slide{i}.xml')]))
 put('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'+''.join(overrides)+'</Types>')
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for n,t in files.items(): z.writestr(n,t)
 print('Pitch: seis diapositivas nativas y Markdown exacto')
if __name__=='__main__': main()
