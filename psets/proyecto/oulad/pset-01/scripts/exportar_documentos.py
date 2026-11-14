"""Exporta íntegramente las fuentes Markdown a notebook y PDF, sin resumir."""
from pathlib import Path
import re,html,hashlib,json
import nbformat
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,LongTable,TableStyle,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[2]
FONT=Path('/System/Library/Fonts/Supplemental')
def init_fonts():
 for name,file in [('Body','Arial.ttf'),('Body-Bold','Arial Bold.ttf'),('Body-Italic','Arial Italic.ttf'),('Body-BoldItalic','Arial Bold Italic.ttf')]: pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
 pdfmetrics.registerFontFamily('Body',normal='Body',bold='Body-Bold',italic='Body-Italic',boldItalic='Body-BoldItalic')
def plain(t):
 t=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1 (\2)',t)
 return t.replace('`','')
def markup(t):
 t=html.escape(plain(t)); t=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',t); t=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',t)
 return t
def render_md(src,dest,memo=False):
 text=src.read_text(); story=[]; base=10.2 if memo else 10.5; leading=13.6 if memo else 14.7; references=False
 normal=ParagraphStyle('normal',fontName='Body',fontSize=base,leading=leading,spaceAfter=6,splitLongWords=True)
 tiny=ParagraphStyle('cell',parent=normal,fontSize=8.5,leading=11.3,spaceAfter=2)
 reference_style=ParagraphStyle('reference',parent=normal,fontSize=9.5,leading=12.5,spaceAfter=5)
 styles={1:ParagraphStyle('h1',parent=normal,fontName='Body-Bold',fontSize=17 if memo else 20,leading=22,spaceBefore=12,spaceAfter=10,keepWithNext=True),2:ParagraphStyle('h2',parent=normal,fontName='Body-Bold',fontSize=12 if memo else 15,leading=18,spaceBefore=10,spaceAfter=7,keepWithNext=True),3:ParagraphStyle('h3',parent=normal,fontName='Body-Bold',fontSize=11.5,leading=15,spaceBefore=8,keepWithNext=True)}
 lines=text.splitlines(); i=0
 while i<len(lines):
  l=lines[i].strip()
  if not l or l=='---': i+=1; continue
  if l.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
    if not all(re.fullmatch(r':?-+:?',c) for c in cells): rows.append([Paragraph(markup(c),tiny) for c in cells])
    i+=1
   n=len(rows[0]); available=483
   if n==4: widths=[80,134,134,135]
   elif n==2: widths=[130,353]
   elif n==3: widths=[98,180,205]
   elif n==7: widths=[82,42,83,64,77,47,88]
   else: widths=[available/n]*n
   table=LongTable(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
   table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9eff5')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#bfc8d1')),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.extend([table,Spacer(1,8)]);continue
  m=re.match(r'^(#{1,6})\s+(.*)',l)
  if m:
   if m[2]=='Referencias': references=True
   if memo and m[2].startswith('3. Viabilidad de negocio'): story.append(PageBreak())
   story.append(Paragraph(markup(m[2]),styles[min(len(m[1]),3)]));i+=1;continue
  para=[l];i+=1
  while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||- )',lines[i].strip()): para.append(lines[i].strip());i+=1
  content=' '.join(para)
  if content.startswith('- '):content='• '+content[2:]
  story.append(Paragraph(markup(content),reference_style if references else normal))
 dest.parent.mkdir(parents=True,exist_ok=True)
 def footer(c,doc):
  c.setFont('Body',8);c.setFillColor(colors.HexColor('#536174'));c.drawString(56,27,'Wilmer Puerta · PSet 1 · 12-nov-2026');c.drawRightString(539,27,str(doc.page))
 doc=SimpleDocTemplate(str(dest),pagesize=(595.28,841.89),rightMargin=56,leftMargin=56,topMargin=38 if memo else 45,bottomMargin=44,title=src.stem,author='Wilmer Puerta',subject='Fuente SHA-256 '+hashlib.sha256(src.read_bytes()).hexdigest())
 doc.build(story,onFirstPage=footer,onLaterPages=footer)
def main():
 init_fonts();full=ROOT/'pset-01/proyecto-completo-pset1.md'; text=full.read_text()
 # Separar por encabezado manteniendo todos los caracteres y el orden.
 sections=re.split(r'(?m)(?=^#{1,3} )',text);nb=nbformat.v4.new_notebook();nb.cells=[nbformat.v4.new_markdown_cell(s) for s in sections if s]
 nb.metadata={'language_info':{'name':'python'},'authors':[{'name':'Wilmer Puerta'}],'source_sha256':hashlib.sha256(full.read_bytes()).hexdigest(),'evidence':'Auditoría descriptiva real; no entrenamiento ni pipeline'}
 nbformat.validate(nb);dest=ROOT/'pset-01/notebooks/PSet1_notebook_completo_Puerta_Wilmer.ipynb';dest.parent.mkdir(exist_ok=True);nbformat.write(nb,dest)
 render_md(ROOT/'pset-01/propuesta-pset1.md',ROOT/'pset-01/output/pdf/PSet1_memo_Puerta_Wilmer.pdf',True)
 render_md(full,ROOT/'pset-01/output/pdf/PSet1_notebook_completo_Puerta_Wilmer.pdf')
 print('Notebook válido y dos PDF exportados desde Markdown íntegro')
if __name__=='__main__': main()
