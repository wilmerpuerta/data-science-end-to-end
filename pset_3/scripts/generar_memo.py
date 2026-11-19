"""Memo nativo vectorial de seis páginas; solo evidencia agregada y decisiones guardadas."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,math,hashlib,shutil,html
from figura_tuning import resumen_tuning, dibujar_canvas
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
V=Path(__file__).resolve().parents[1];W,H=A4;M=40;CW=W-2*M
OUT=V/'output/pdf/PSet3_memo_Puerta_Wilmer.pdf';OUT.parent.mkdir(parents=True,exist_ok=True)
for folder,a,b in [(Path('/System/Library/Fonts/Supplemental'),'Arial.ttf','Arial Bold.ttf'),(Path('/usr/share/fonts/truetype/dejavu'),'DejaVuSans.ttf','DejaVuSans-Bold.ttf')]:
 if (folder/a).exists():pdfmetrics.registerFont(TTFont('Memo',str(folder/a)));pdfmetrics.registerFont(TTFont('MemoBold',str(folder/b)));break
else:raise RuntimeError('Instalar Arial o DejaVu')
pdfmetrics.registerFontFamily('Memo',normal='Memo',bold='MemoBold',italic='Memo',boldItalic='MemoBold')
NAVY=colors.HexColor('#15364b');TEAL=colors.HexColor('#087e8b');INK=colors.HexColor('#233645');GRAY=colors.HexColor('#536776');PALE=colors.HexColor('#eff6f7');RED=colors.HexColor('#b34d55')
styles={'body':ParagraphStyle('body',fontName='Memo',fontSize=10.5,leading=14,textColor=INK),'small':ParagraphStyle('small',fontName='Memo',fontSize=9.3,leading=12.2,textColor=GRAY),'cell':ParagraphStyle('cell',fontName='Memo',fontSize=9.2,leading=12,textColor=INK),'head':ParagraphStyle('head',fontName='MemoBold',fontSize=9.2,leading=12,textColor=colors.white)}
def read(p):return json.loads((V/p).read_text())
def f(x,n=4):return f'{x:.{n}f}'
def pct(x,n=2):return f'{100*x:.{n}f} %'
def esc(x):return html.escape(str(x))
E=read('docs/eda/resumen.json');F=read('docs/features/resumen.json');MODELS=read('docs/modelos/resultados.json');D=read('docs/negocio/finalistas.json');FINAL=read('docs/seleccion/evaluacion.json');EARLY=read('docs/anticipacion/resultados.json');A=read('docs/ablacion/resultados.json');BUDGET=read('.local/llm/costos.json');RUNS=pd.read_csv(V/'docs/corridas.csv')
assert len(MODELS['candidates'])==6 and FINAL['status']=='registered';decision=D['content'];winner=decision['winner'];challenger=decision['challenger'];NAME={'lineal':'Logística','bagging':'RandomForest','boosting':'HGB','red_neuronal':'MLP','bayes':'GaussianNB','llm_generativo':'GPT prompting','dummy':'Dummy'}
c=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1);c.setTitle('PSet 3 - OULAD: anticipar apoyo académico');c.setAuthor('Wilmer Puerta');page_no=0;y=H-45;MD=[];MIN_Y={};FIGURES=[]
def ensure(height):
 if y-height<52:raise RuntimeError(f'Desborde página {page_no}: y={y:.1f}, requiere {height:.1f}')
def finish():
 MIN_Y[page_no]=y;c.setStrokeColor(TEAL);c.line(M,36,W-M,36);c.setFillColor(GRAY);c.setFont('Memo',8);c.drawString(M,23,'Wilmer Puerta | PSet 3 | OULAD | 18-nov-2026');c.drawRightString(W-M,23,f'{page_no} / 6')
def page(title):
 global page_no,y
 if page_no:finish();c.showPage();MD.append('\n<!-- PAGE -->\n')
 page_no+=1;y=H-45;c.setFillColor(NAVY);c.setFont('MemoBold',19);c.drawString(M,y,title);y-=29;MD.append('# '+title)
def para(s,small=False,gap=6):
 global y
 p=Paragraph(s,styles['small' if small else 'body']);w,h=p.wrap(CW,900);ensure(h+gap);p.drawOn(c,M,y-h);y-=h+gap;MD.append(s.replace('<b>','**').replace('</b>','**'))
def section(s):
 global y
 ensure(23);c.setFillColor(TEAL);c.setFont('MemoBold',12.2);c.drawString(M,y-12,s);y-=23;MD.append('## '+s)
def table(rows,widths=None):
 global y
 if widths is None:widths=[CW/len(rows[0])]*len(rows[0])
 data=[[Paragraph(esc(v),styles['head' if i==0 else 'cell']) for v in r] for i,r in enumerate(rows)];t=Table(data,colWidths=widths)
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('LINEBELOW',(0,-1),(-1,-1),.4,TEAL)]));_,h=t.wrap(CW,1000);ensure(h+8);t.drawOn(c,M,y-h);y-=h+8;MD.extend(['| '+' | '.join(str(x) for x in r)+' |' for r in rows])
def bars(labels,values,errors=None,height=150,maxval=None,suffix='%'):
 global y
 ensure(height+7);top=y-16;left=M+115;width=CW-175;step=(height-25)/len(labels);domain=maxval or max(values)*1.2
 c.setFont('Memo',9)
 for i,(label,val) in enumerate(zip(labels,values)):
  yy=top-i*step;c.setFillColor(INK);c.drawRightString(left-8,yy,label);c.setFillColor(TEAL if label!='Dummy' else GRAY);c.rect(left,yy-2,max(.5,width*val/domain),9,fill=1,stroke=0)
  if errors is not None:
   lo=left+width*max(0,val-errors[i])/domain;hi=left+width*(val+errors[i])/domain;c.setStrokeColor(NAVY);c.line(lo,yy+2,hi,yy+2);c.line(lo,yy-1,lo,yy+5);c.line(hi,yy-1,hi,yy+5)
  c.setFillColor(INK);c.drawString(M+CW-54,yy,(f'{val*100:.2f} %' if suffix=='%' else str(int(val))))
 c.setStrokeColor(GRAY);c.line(left,top-(len(labels)-1)*step-9,left,top+14);y-=height+7;FIGURES.append({'page':page_no,'kind':'native_vector_bars','labels':labels,'values':values})

# Página 1
page('Anticipar apoyo académico')
para('Experimentación, selección y evidencia para priorizar tutorías. <b>El criterio del negocio:</b> maximizar la cobertura de matrículas con Fail, con el mismo cupo del 10 % por edición. Detectar riesgo no demuestra que una tutoría evite el resultado.')
section('1. EDA: hallazgos que cambian el experimento')
para(f'Desarrollo al día 56: <b>{E["rows"]:,} matrículas / {E["unique_students"]:,} estudiantes</b>; OBT original: 35 columnas. Fail: {pct(E["fail_prevalence"])}. El EDA usa desarrollo y conserva las filas atípicas. Spearman se justifica por colas largas y relaciones monotónicas; categorías nominales no se ordenan artificialmente.')
table([['Hallazgo','Evidencia','Consecuencia'],['Desbalance y objetivo',f'Approved 9.219; Fail 4.918; Withdrawn 2.194. Razón mayor/menor 4,20.','AP de Fail y cobertura a cupo fijo; accuracy no decide.'],['Clics con cola larga','Mediana 53; p99 686,1; máximo 7.028. IQR: 1.158; |Z| >= 3: 264.','Conservar extremos y ensayar log1p dentro de la ablación.'],['Ausencia y NULL estructural','432 sin registros al corte: 75,69 % Fail vs 28,88 % con registros. Razón quincenal indefinida: 2.516.','Separar ausencia de cero; imputación e indicadores en cada train-fold. No inferir causalidad.']],[105,200,CW-305])
# Distribuciones vectoriales ampliadas, con denominador y escala explícitos.
ensure(148);top=y;c.setFillColor(NAVY);c.setFont('MemoBold',10.2);c.drawString(M,top-10,'Distribución del target (desarrollo)')
c.setFont('Memo',9);c.setFillColor(GRAY);c.drawString(M,top-25,'n = 16.331 matrículas al día 56')
names=['Approved','Fail','Withdrawn'];counts=[9219,4918,2194]
for i,(name,n) in enumerate(zip(names,counts)):
 yy=top-48-i*25;c.setFont('Memo',9.5);c.setFillColor(INK);c.drawString(M,yy,name)
 c.setFillColor(TEAL if name=='Fail' else colors.HexColor('#93bdc3'));c.rect(M+68,yy-2,92*n/max(counts),11,fill=1,stroke=0)
 c.setFillColor(INK);count=f'{n:,}'.replace(',','.');share=f'{100*n/sum(counts):.1f}'.replace('.',',');c.drawString(M+168,yy,f'{count} ({share} %)')
x0=M+267;width=CW-279;c.setFont('MemoBold',10.2);c.setFillColor(NAVY);c.drawString(x0,top-10,'Clics actuales: caja y referencias')
c.setFont('Memo',9);c.setFillColor(GRAY);c.drawString(x0,top-25,'Últimos 14 días; escala log1p')
q=pd.read_csv(V/'docs/eda/descriptivos_numericos.csv').set_index('variable').loc['clicks_current_14d'];out=pd.read_csv(V/'docs/eda/outliers.csv').set_index('variable').loc['clicks_current_14d'];lo=0;hi=float(out['limite_superior']);yy=top-56
scale=lambda v:x0+width*math.log1p(float(v))/math.log1p(float(q['max']))
c.setStrokeColor(GRAY);c.line(scale(lo),yy,scale(hi),yy)
for value in [lo,hi]:c.line(scale(value),yy-5,scale(value),yy+5)
c.setFillColor(PALE);c.rect(scale(q['25%']),yy-9,scale(q['75%'])-scale(q['25%']),18,fill=1,stroke=1);c.setStrokeColor(TEAL);c.line(scale(q['50%']),yy-9,scale(q['50%']),yy+9)
c.setFillColor(TEAL);c.circle(scale(q['99%']),yy,2.8,fill=1,stroke=0);c.setFillColor(RED);c.circle(scale(q['max']),yy,3.2,fill=1,stroke=0)
c.setFont('Memo',8.5);c.setFillColor(INK);c.drawCentredString(scale(q['99%']),yy+13,'p99');c.drawRightString(scale(q['max']),yy+13,'máx.')
axis=top-80;c.setStrokeColor(GRAY);c.line(x0,axis,x0+width,axis)
for i,value in enumerate([0,10,100,1000,int(q['max'])]):
 xx=scale(value);c.line(xx,axis-3,xx,axis+3);label=f'{value:,}'.replace(',','.')
 if i==0:c.drawString(xx,axis-14,label)
 elif i==4:c.drawRightString(xx,axis-14,label)
 else:c.drawCentredString(xx,axis-14,label)
c.setFont('Memo',9);c.drawString(x0,top-112,'Q1 10 | mediana 53 | Q3 131')
c.setFont('Memo',8.8);c.drawString(x0,top-128,'Límite IQR 312,5; p99 686,1; máx. 7.028.')
y-=148;FIGURES.append({'page':1,'kind':'native_target_and_iqr_reference','height_pt':148,'target_denominator':sum(counts),'target_percentages':True,'click_axis':'log1p','iqr_upper_limit_is_reference':True})
section('Relaciones que orientan las features')
cols=['clicks_current_14d','active_days_current_14d','recency_days','num_of_prev_attempts','Fail'];labels=['Clics','Días','Recencia','Intentos','Fail'];corr=pd.read_csv(V/'docs/eda/correlaciones.csv').set_index('variable');ensure(213);cell=35;xx=M+65;top=y-19;c.setFont('Memo',10)
def correlation_color(val):
 a=abs(val)
 return colors.Color(1-.10*a,1-.55*a,1-.55*a) if val<0 else colors.Color(1-.85*a,1-.50*a,1-.45*a)
for j,label in enumerate(['Clics','Días','Rec.','Prev.','Fail']):c.setFillColor(INK);c.drawCentredString(xx+j*cell+cell/2,y-8,label)
for i,label in enumerate(labels):
 yy=top-i*cell;c.setFillColor(INK);c.setFont('Memo',9.5);c.drawRightString(xx-6,yy-22,label)
 for j in range(5):
  val=float(corr.loc[cols[i],cols[j]]);c.setFillColor(correlation_color(val));c.rect(xx+j*cell,yy-cell,cell,cell,fill=1,stroke=0);c.setFillColor(colors.white if val>.75 else INK);c.setFont('Memo',10.5);c.drawCentredString(xx+j*cell+cell/2,yy-22,f'{val:.2f}')
text='<b>Spearman por pares observados.</b><br/>Clics y días activos están muy relacionados (0,90): parte de la señal es redundante.<br/><br/>Menos actividad y mayor recencia se asocian con Fail (-0,30; -0,33 y +0,28). Son señales candidatas, sin interpretación causal ni selección automática de variables.'
p=Paragraph(text,styles['body']);_,h=p.wrap(CW-267,180);assert h<=172;p.drawOn(c,M+267,y-10-h)
legend_x=M+273;legend_y=y-190;legend_w=180
for i in range(60):c.setFillColor(correlation_color(-1+2*i/59));c.rect(legend_x+i*legend_w/60,legend_y,legend_w/60+.1,6,fill=1,stroke=0)
c.setFillColor(GRAY);c.setFont('Memo',8.5)
for val,label in [(-1,'-1'),(0,'0'),(1,'+1')]:c.drawCentredString(legend_x+(val+1)*legend_w/2,legend_y-12,label)
y-=213;FIGURES.append({'page':1,'kind':'native_spearman_heatmap','cell_size_pt':cell,'matrix_size':5,'color_scale':[-1,1]})
para('<b>Lectura para el negocio:</b> la actividad aporta señales candidatas para priorizar el apoyo. Su utilidad incremental se contrasta con el modelo estático y a igual cupo; la inactividad, por sí sola, no demuestra por qué ocurre Fail.')
para('Fuentes: docs/eda/*.csv y 01_eda.ipynb. IQR y Z-score son diagnósticos, no reglas de eliminación.',True)

# Página 2
page('Features y validación')
section('2. Dos derivadas disponibles al corte')
table([['Feature','Motivo y disponibilidad','Tratamiento'],['log1p_clicks_current_14d','Cola larga observada; solo clics de los últimos 14 días hasta el corte.','log1p determinista, sin aprender del futuro.'],['clicks_per_active_day_14d','Intensidad entre quienes tienen días activos en la ventana actual.','Clics / días si días > 0; NULL si no. Imputación e indicador aprendidos en train-fold.']],[143,220,CW-363])
para('Ambas viven en <b>src/pipeline.py</b>. La allowlist descarta IDs, target, folds y campos futuros. Medianas, escalado y one-hot se ajustan solo con entrenamiento; las categorías nuevas se ignoran de forma controlada. Se verifican ventanas y actividad posterior al corte.')
rows=[['Ablación lineal fija','AP CV','Cobertura CV','Delta cobertura']]
for r in A['results']:rows.append([{'static':'Estáticas','original':'Longitudinal original','log_only':'Solo log1p','intensity_only':'Solo intensidad','both':'Ambas derivadas'}[r['mode']],f(r['ap_fail_mean']),pct(r['coverage_mean']),f"{100*r['delta_coverage_vs_original']:+.3f} pp"])
table(rows,[175,94,113,CW-382])
para('La ganancia de ambas es solo +0,104 puntos porcentuales de cobertura y no supera la dispersión entre folds: <b>no se demuestra mejora estable de las derivadas</b>. Se informa el resultado negativo; el ensayo principal conserva la representación predeclarada, sin escoger features usando prueba.')
section('3. Preparación, partición y métricas')
table([['Partición al día 56','Matrículas','Estudiantes'],['Entrenamiento / CV','16.331','15.482'],['Prueba 2014J','8.758','8.442'],['Purgadas por estudiante compartido','1.205','1.145']],[CW-190,95,95])
para('<b>Cinco folds persistidos por estudiante</b>, estratificados y con semilla 42: no comparten alumnos. Todos los candidatos usan el mismo snapshot, preparación, validación completa y métricas. El diagnóstico de train usa las mismas 1.000 filas estratificadas por fold para todos; no se presenta como train completo.')
para('<b>Técnica:</b> AP de Fail; Brier y log-loss complementan calibración. <b>Negocio:</b> media CV de TP / Fail con K=floor(0,10 N) por edición y fold. Se desempata por dispersión, AP, Brier, costo y run_id según protocolo; no por resultados de prueba.')
para('<b>2014J ya fue observado en v1.</b> La reconstrucción es un benchmark retrospectivo reutilizado. Se congela la decisión antes de una única evaluación final conjunta de esta versión; no se afirma una prueba inédita ni se ajusta con su resultado.')
para('El agrupamiento evita que el historial de una misma persona aparezca a ambos lados de la validación. A igual cupo se evalúa a quién priorizar con recursos limitados; AP resume la ordenación del riesgo sin fijar un umbral. Las particiones persistidas permiten comparar modelos sin introducir diferencias por nuevos sorteos.')
para('Snapshot: 0a75615bd8ff... | split: 231cd638f375... | protocolo predictivo: 07111fdf724a...<br/>Hashes completos, enmiendas operativas y archivos: docs/protocolo-congelado.json y docs/enmienda-*.json.',True)

# Página 3
page('Diseño y comparación de candidatos')
section('4. Experimento y 5. resultados por defecto')
para(f'Dos baselines preceden a seis familias: Dummy más frecuente y proceso reactivo al cierre. El control estático es una comparación separada. Presupuesto principal: <b>2 + 6 + 90 + 1 = 99 ejecuciones</b>; con folds y análisis auxiliares, el experimento registra {len(RUNS)} runs ({int((RUNS.status=="FINISHED").sum())} FINISHED y {int((RUNS.status=="FAILED").sum())} FAILED, conservados para auditoría).')
rows=[['Familia','AP train*','AP CV ± DE','Brecha','Cobertura CV ± DE','Fit CV s','LR']]
allrows=[MODELS['baselines'][0]]+MODELS['candidates']
for r in allrows:
 fam=r['family'];lr={'boosting':'0,1','red_neuronal':'0,001'}.get(fam,'N/A');rows.append([NAME[fam],f(r['train_ap_fail_mean'],3),f"{r['cv_ap_fail_mean']:.3f} ± {r['cv_ap_fail_std']:.3f}",f(r['ap_gap'],3),f"{100*r['cv_coverage_mean']:.2f} ± {100*r['cv_coverage_std']:.2f} %",f(r['cv_fit_seconds_total'],2),lr])
table(rows,[84,52,89,47,117,65,CW-454])
para('* Train: muestra fija de hasta 1.000 filas por train-fold. CV: todos los casos, media ± DE (no IC). Defaults de scikit-learn salvo semilla; GPT usa prompting predeclarado. LR = tasa de aprendizaje cuando aplica.',True)
para('RandomForest y MLP muestran brechas AP grandes (0,439 y 0,273); MLP agotó 200 iteraciones. GaussianNB tiene brecha pequeña, pero log-loss CV 2,741: una brecha reducida no garantiza buenas probabilidades.')
ordered=sorted(allrows,key=lambda r:r['cv_coverage_mean'],reverse=True);bars([NAME[r['family']] for r in ordered],[r['cv_coverage_mean'] for r in ordered],[r['cv_coverage_std'] for r in ordered],height=159,maxval=.28)
para('Cobertura de Fail al mismo cupo. La política reactiva tiene cobertura preventiva cero; su atención posterior no equivale a anticipación.',True)
section('LLM fundacional generativo mediante prompting')
para('GPT-6 Luna se probó con <b>18 ejemplos (6 por clase) y proporciones del train-fold</b>, sin etiquetas de las consultas. Recibe la misma matriz preparada, con nombres y valores dispersos a seis cifras significativas; devuelve probabilidades verificadas por consulta. No entrena sus pesos con todas las filas. Su contexto limitado y probabilidades autodeclaradas son parte del ensayo, no una garantía de calibración.')
para('AP CV 0,382 y cobertura 14,87 %: supera Dummy, pero no está entre los tres primeros por negocio y no pasa al tuning. Inferencia CV registrada: 349,8 s, frente a 0,18-0,53 s en las familias tabulares; fit del GPT construye contexto y no refleja ese costo. Hubo recuperación de caché y ocho peticiones concurrentes: estos tiempos no equivalen a un servicio productivo en frío.')
para('La conclusión corresponde al prompt y modelo ensayados. Otro diseño requeriría una nueva evaluación comparable, con igual cupo y presupuesto explícito.')
para(f'Consumo global conservador: <b>USD {float(BUDGET["spent"]):.4f}</b> / USD 10, incluidos pilotos e intentos fallidos; 720 llamadas con uso registrado. El gasto de esta muestra no estima el costo anual de la Universidad.',True)

# Página 4
page('Tuning y trazabilidad')
section('6. Tres familias x treinta configuraciones')
para('Top 3 por cobertura CV: logística, HGB y GaussianNB. RandomizedSearchCV: 30 configuraciones únicas por familia, cinco folds y refit; runs hijos por configuración y defaults elegibles.')
table([['Familia','Espacio predeclarado','Escala'],['Logística','C 0,001-100; pesos None/balanced; iteraciones 300/600/1.000; tol 1e-5-1e-3.','C y tol log.'],['HGB','LR 0,02-0,2; 60/100/160 iteraciones; hojas 7/15/31/63; profundidad None/3/5/8; min hoja 10-80; L2 1e-4-10; early stopping booleano.','LR y L2 log.'],['GaussianNB','var_smoothing 1e-12-1e-3.','Logarítmica.']],[80,335,CW-415])
rows=[['Familia','Default','Ajustado','Delta pp','DE ref. pp','Mejora estable']]
for r in decision['tuning_improvements']:
 default=next(x for x in MODELS['candidates'] if x['family']==r['family']);rows.append([NAME[r['family']],pct(default['cv_coverage_mean']),pct(default['cv_coverage_mean']+r['delta_coverage']),f"{100*r['delta_coverage']:+.3f}",f(100*r['cv_spread_reference'],3),'No'])
table(rows,[82,79,79,74,88,CW-402])
tuning_rows=resumen_tuning(V);ensure(116);figure_meta=dibujar_canvas(c,tuning_rows,M,y,CW);figure_meta['page']=page_no;FIGURES.append(figure_meta);y-=116
para('Segmentos: DE de cinco folds, no IC. Ningún delta supera la mayor DE: <b>sin mejora demostrada</b>. La mayor media guía una elección provisional. Cada control estático finalista se ajusta aparte: 30 sorteos iguales + default.')
section('Tracking: evidencia exportada y captura real')
para('Docker persiste SQLite y artefactos en oulad-apoyo-academico-v2. Se verificaron <b>370 pipelines</b> con firma, ejemplo e interfaz predict_proba. Se registran parámetros/semilla, origen/fecha/hash, métricas train/CV/DE/tiempos y tags de fase, familia y commit real. Los 382 runs incluyen padres y fallos; no son 382 modelos distintos.')
image=V/'docs/evidencia/mlflow-comparacion-detalle.png';ensure(163);c.drawImage(str(image),M,y-150,width=CW,height=150,preserveAspectRatio=True,anchor='c',mask='auto');y-=160
para('Captura nativa de la interfaz local, sin edición: izquierda HGB dc2fa9bb8bee...; derecha logística bb2b40097599.... Las filas muestran AP y cobertura CV, con su desviación.',True)
para('Código versionado antes del ajuste. Intentos técnicos y enmiendas documentados; se preservan commits y probabilidades. Fuentes: docs/tuning/, docs/corridas.csv y 04_tuning.ipynb.',True)

# Página 5
page('Decisión y evaluación final')
section('7. Champion por valor esperado en CV')
para(f'<b>HGB: {pct(winner["cv_coverage_mean"])} ± {100*winner["cv_coverage_std"]:.2f} pp</b>; logística: {pct(challenger["cv_coverage_mean"])} ± {100*challenger["cv_coverage_std"]:.2f} pp. La diferencia de {100*decision["winner_challenger_difference"]:.3f} pp es menor que la dispersión de referencia ({100*decision["fold_variation_reference"]:.3f} pp). HGB maximiza la media predeclarada; <b>no hay superioridad estable ni económica demostrada</b>.')
rows=[['Modelo / política','TP','FP','FN','Cobertura','AP']]
for key,label in [('dummy','Dummy'),('static_boosting','HGB estático'),('winner','HGB longitudinal'),('challenger','Logística longitudinal')]:
 r=FINAL['models'][key];b=r['business']['0.1'];rows.append([label,b['tp'],b['fp'],b['fn'],pct(b['coverage']),f(r['technical']['ap_fail'])])
rows.append(['Reactiva preventiva',0,'N/A','N/A','0,00 %','N/A']);table(rows,[155,48,48,51,103,CW-405])
para('<b>Prueba:</b> 8.758 matrículas, 8.442 estudiantes, 1.947 Fail y K=872. HGB captura 465 Fail frente a 309 de su control estático: <b>+156 / +50,49 %</b>, sin atribuir efecto causal a tutorías. La reactiva puede atender 872 Fail conocidos después del cierre, con cupo acotado, y cero cobertura preventiva.')
para('Logística obtiene 477 TP y AP 0,4388 en prueba, frente a 465 TP y AP 0,4265 de HGB. <b>No se reelige con prueba</b>: queda como challenger competitivo. La decisión se fijó por CV y su escasa separación exige una validación prospectiva antes de prometer ventaja.')
bars(['HGB estático','HGB longitudinal','Logística long.'],[309,465,477],height=93,maxval=520,suffix='TP')
para('Fail captados con el mismo K=872; el resultado observado en prueba no sustituye el criterio de selección.',True)
section('Costo, explicación y registro reproducible')
para('Refit: HGB 1,80 s vs logística 0,32 s. Primer pase de 1.000 filas: 0,244 s vs 0,042 s; medianas de cinco repeticiones: 0,046 s vs 0,019 s (dos hilos). Los escenarios de costo FN/FP = 1, 2, 5 y 10 son relativos: no se inventa una tarifa institucional. El umbral es el score del último cupo por edición, con desempate por clave, no 0,5 universal.')
para('<b>Lectura operativa:</b> los 872 cupos de HGB incluyen 465 matrículas con Fail y 407 con otros resultados; 1.482 Fail quedan fuera del cupo. Este balance muestra la cobertura posible con los recursos fijados, sin estimar fracasos evitados. La valoración económica posterior deberá combinar costos de atención, beneficio incremental de la tutoría y personas únicas atendidas; no basta con multiplicar los casos detectados por una ganancia supuesta.')
local=read('docs/seleccion/explicacion_local_desarrollo.json');g=next(x for x in local['groups'] if x['group']=='actividad_completa');para(f'Explicación: permutación en 200 casos de desarrollo (2 repeticiones) destaca clics recientes/acumulados y carga académica. En un caso de alto riesgo de desarrollo, sustituir el grupo de actividad por un perfil observado central cambia P(Fail) de {g["actual_p_fail"]:.3f} a {g["p_fail_with_observed_reference_group"]:.3f}. Es contraste descriptivo local, no SHAP aditivo ni intervención causal.')
para('<b>Registry:</b> oulad-apoyo-academico-v2-modelo, champion v1 / challenger v2.<br/>Fuente champion: dc2fa9bb8bee4944bd00611a6ac5c34f.<br/>Evaluación final: fcd23ae22d6c46ffb41c1e4f23e1c02d.<br/>Proceso limpio carga models:/...@champion y reproduce exactamente AP y negocio, sin nuevas llamadas API.',True)

# Página 6
page('Anticipación y siguiente decisión')
section('Utilidad para anticipar tutorías')
para('Se evalúan ambas familias finalistas en cohortes propias de semanas 2/4/6 y día 56, con parámetros fijados, cinco folds por estudiante y purga de todos los alumnos presentes en 2014J. El cuadro resume HGB; el anexo conserva ambas familias y los controles E/E+I/L. El denominador de políticas es el Fail de la cohorte inicial (4.914).')
pol={r['policy']:r for r in EARLY['policies'] if r['family']=='boosting'}
rows=[['Política','Cohorte elegible','TP / K=1.691','TP con margen al día 56','Al día 70']]
for key,label,n in [('longitudinal_semana2','Semana 2',17246),('longitudinal_semana4','Semana 4',16838),('longitudinal_semana6','Semana 6',16529),('longitudinal_escalonada','Escalonada 40/30/30',17246)]:
 p=pol[key];rows.append([label,f'{n:,}',p['tp'],p['tp_with_margin_day56'],p['tp_with_margin_day70']])
table(rows,[116,99,98,111,CW-424])
para('Margen ilustrativo: 7 días de coordinación + 14 de apoyo. Con plazo día 56, semana 4 deja margen y captura 1.011 Fail; semana 6 llega tarde bajo ese supuesto. Semana 2 captura 915 frente a 755 del estático pareado (+160), permitiendo apoyo más temprano. <b>No son fracasos evitados</b>: son casos potencialmente atendibles en una simulación.')
para('Un solo presupuesto nace del día 14, por edición/fold; no se repiten matrículas. La escalonada usa 645/501/545 cupos, total 1.691, y selecciona 1.633 personas únicas. Contar matrículas no equivale a contar estudiantes. Los plazos y la unidad de asignación deben acordarse con la Universidad.')
section('Sin registros: asociación y aporte incremental')
para('En semana 2, Fail es 52,67 % sin registros al corte y 26,78 % con ellos: RR 1,97 (IC 95 % 1,85-2,08), phi 0,143. La diferencia estandarizada por edición es 26,27 pp (98,05 % de población cubierta). AP de HGB: E 0,3965; E+indicador 0,4247; longitudinal 0,4570. Hay asociación y señal incremental en este desarrollo; ni confusión residual ni causalidad quedan resueltas. No se usa "nunca tendrá actividad", que no es observable al corte.')
section('8. Limitaciones y conclusión sobre prompting')
para('<b>Prompting sí es factible y se ensayó.</b> Su costo operativo puede ser relevante a escala: la adopción de un LLM externo queda como una <b>decisión de negocio posterior</b>, para evaluar consumo, latencia, integración, mantenimiento y valor incremental mediante un análisis de <b>costo-beneficio con la Universidad</b>. El ensayo costó cerca de USD 1,12 y no prueba un gasto elevado en esta muestra; tampoco justifica su adopción, dado el menor desempeño del GPT probado.')
para('Límites: 2014J es un benchmark ya observado; CV y decisiones reutilizan desarrollo. La maduración de etiquetas no tiene fecha de publicación conocida; el margen curso-terminado/corte sería -12, +2, +16 y +30 días en cortes 14/28/42/56, insuficiente para certificar un despliegue prospectivo temprano. Las probabilidades del proveedor no son deterministas ni se conoce su preentrenamiento sobre OULAD; la reproducción usa respuestas archivadas.')
para('La evidencia termina en predicción y simulación. El siguiente paso es acordar con la Universidad el plazo mínimo de acción, el cupo por persona y los costos de atención. Una cohorte futura y un piloto con un diseño de evaluación adecuado permitirán estimar el efecto de las tutorías, su equidad y su costo-beneficio. Un eventual LLM externo deberá justificar valor incremental frente a los modelos tabulares, considerando precisión, latencia, integración y mantenimiento, además del consumo de API. Código, seis notebooks con salidas, CSV, contratos y verificación acompañan la entrega.')
finish();assert page_no==6;c.save();shutil.copyfile(OUT,V/'docs'/OUT.name)
(V/'memo-pset3.md').write_text('\n\n'.join(MD)+'\n')
meta={'pages':6,'pdf_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((V/'memo-pset3.md').read_bytes()).hexdigest(),'native_vector_figures':FIGURES,'native_UI_screenshot':'docs/evidencia/mlflow-comparacion-detalle.png','minimum_cursor_y':MIN_Y,'body_font_pt':10.5,'table_font_pt':9.2,'font':'embedded Arial or DejaVu','source':'completed v2 reports only; no new training, test evaluation or API calls','prompting_summary_included':True}
(V/'docs/memo-construccion.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pages':6,'minimum_y':MIN_Y,'output':str(OUT)}))
