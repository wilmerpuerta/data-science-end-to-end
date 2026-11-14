"""Exporta el memo Markdown a seis páginas con diagramas vectoriales.

Desde raíz: python pset-02/scripts/generar_memo.py
No conecta a servicios ni utiliza archivos privados.
"""
from pathlib import Path
import hashlib
import html
import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Flowable, Paragraph, Table, TableStyle

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / 'memo-pset2.md'
OUTPUT = BASE / 'output/pdf/PSet2_memo_Puerta_Wilmer.pdf'
NAVY = colors.HexColor('#16324a')
TEAL = colors.HexColor('#087e8b')
INK = colors.HexColor('#253746')
MUTED = colors.HexColor('#556978')
PALE = colors.HexColor('#edf5f6')
WIDTH, HEIGHT = A4
MARGIN = 46
CONTENT_WIDTH = WIDTH - 2 * MARGIN


def fonts():
    """Arial en macOS; DejaVu o Liberation en Linux; override opcional."""
    candidates = [
        (Path(os.environ.get('PSET2_MEMO_FONT_DIR', '.')), 'Arial.ttf', 'Arial Bold.ttf'),
        (Path('/System/Library/Fonts/Supplemental'), 'Arial.ttf', 'Arial Bold.ttf'),
        (Path('/usr/share/fonts/truetype/dejavu'), 'DejaVuSans.ttf', 'DejaVuSans-Bold.ttf'),
        (Path('/usr/share/fonts/truetype/liberation2'), 'LiberationSans-Regular.ttf', 'LiberationSans-Bold.ttf'),
    ]
    for folder, normal, bold in candidates:
        if (folder / normal).is_file() and (folder / bold).is_file():
            pdfmetrics.registerFont(TTFont('Memo', str(folder / normal)))
            pdfmetrics.registerFont(TTFont('MemoBold', str(folder / bold)))
            pdfmetrics.registerFontFamily('Memo', normal='Memo', bold='MemoBold', italic='Memo', boldItalic='MemoBold')
            return
    raise SystemExit('Instale Arial, DejaVu Sans o Liberation Sans, o defina PSET2_MEMO_FONT_DIR.')


def plain(text):
    return text.replace('**','').replace('`','')


def inline(text):
    return html.escape(plain(text)).replace(' %','&nbsp;%')


def blocks(source):
    lines = source.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith('```'):
            kind = line[3:]
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                body.append(lines[i])
                i += 1
            yield kind, '\n'.join(body)
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                if not re.fullmatch(r'[| :\-]+', lines[i]):
                    rows.append([cell.strip() for cell in lines[i].strip('|').split('|')])
                i += 1
            yield 'table', rows
            continue
        elif line.startswith('### '):
            yield 'h3', line[4:]
        elif line.startswith('## '):
            yield 'h2', line[3:]
        elif line.startswith('# '):
            yield 'h1', line[2:]
        else:
            body = [line]
            while i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].startswith(('#', '|', '```')):
                i += 1
                body.append(lines[i])
            yield 'p', ' '.join(body)
        i += 1


def graph(text):
    nodes = dict(re.findall(r'(\w+)\["([^"]+)"\]', text))
    # La sintaxis de nodos está restringida y todas las aristas se leen del MD.
    edges = []
    for line in text.splitlines():
        line = re.sub(r'\["[^\"]+"\]', '', line).strip()
        match = re.fullmatch(r'(\w+)\s+(-->|---)\s+(\w+)', line)
        if match:
            edges.append(match.groups())
    assert nodes and all(a in nodes and b in nodes for a, _, b in edges)
    return nodes, edges


class Diagram(Flowable):
    def __init__(self, text):
        super().__init__()
        self.kind = 'arquitectura' if '%% arquitectura' in text else 'estrella'
        self.nodes, self.edges = graph(text)
        self.width = CONTENT_WIDTH
        self.height = 240 if self.kind == 'arquitectura' else 213

    def draw(self):
        c = self.canv
        if self.kind == 'arquitectura':
            layout = {
                'CSV': (10, 232, 155, 36), 'PG': (338, 232, 155, 36),
                'K': (177, 176, 150, 39), 'DR': (60, 108, 165, 39),
                'SR': (338, 108, 155, 39), 'SP': (190, 56, 130, 35),
                'R': (0, 0, 80, 38), 'B': (100, 0, 80, 38),
                'S': (200, 0, 80, 38), 'G': (300, 0, 80, 38), 'O': (400, 0, 103, 38),
            }
            routes = {
                ('CSV', 'K'): [(87,232),(87,195),(177,195)],
                ('PG', 'K'): [(415,232),(415,195),(327,195)],
                ('K', 'DR'): [(220,176),(220,163),(142,163),(142,147)],
                ('K', 'SR'): [(285,176),(285,163),(415,163),(415,147)],
                ('K', 'R'): [(177,185),(0,185),(0,45),(40,45),(40,38)],
                ('DR', 'B'): [(142,108),(142,38)],
                ('G', 'SR'): [(340,38),(340,99),(375,99),(375,108)],
                ('SR', 'O'): [(461,108),(461,38)],
            }
        else:
            layout = {
                'DS': (0,163,155,42), 'DE': (174,163,155,42), 'DN': (348,163,155,42),
                'FE': (0,82,213,43), 'FA': (290,82,213,43),
                'DR': (174,0,155,42), 'DD': (348,0,155,42),
            }
            routes = {
                ('DS','FE'): [(45,163),(45,125)],
                ('DE','FE'): [(225,163),(225,146),(106,146),(106,125)],
                ('DN','FE'): [(370,163),(370,135),(190,135),(190,125)],
                ('DS','FA'): [(115,163),(115,155),(315,155),(315,125)],
                ('DE','FA'): [(280,163),(280,146),(395,146),(395,125)],
                ('DN','FA'): [(455,163),(455,125)],
                ('DR','FA'): [(251,42),(251,63),(360,63),(360,82)],
                ('DD','FA'): [(440,42),(440,82)],
            }
        if self.kind == 'arquitectura':
            layout = {key:(x,y*.85,w,h*.85) for key,(x,y,w,h) in layout.items()}
            routes = {key:[(x,y*.85) for x,y in points] for key,points in routes.items()}
        assert set(layout) == set(self.nodes)
        c.setStrokeColor(TEAL)
        c.setLineWidth(.85)
        for a, arrow, b in self.edges:
            if (a,b) in routes:
                pts = routes[a,b]
            else:
                x,y,w,h = layout[a]
                xx,yy,ww,hh = layout[b]
                pts = [(x+w,y+h/2),(xx,yy+hh/2)]
            path = c.beginPath()
            path.moveTo(*pts[0])
            for point in pts[1:]:
                path.lineTo(*point)
            c.drawPath(path)
            if arrow == '-->':
                x,y = pts[-1]; px,py = pts[-2]
                if x == px:
                    d = 1 if y > py else -1
                    c.line(x,y,x-2.5,y-d*4)
                    c.line(x,y,x+2.5,y-d*4)
                else:
                    d = 1 if x > px else -1
                    c.line(x,y,x-d*4,y-2.5)
                    c.line(x,y,x-d*4,y+2.5)
        for key,(x,y,w,h) in layout.items():
            cloud = self.kind == 'arquitectura' and key in {'R','B','S','G','O'}
            fact = key in {'FE','FA'}
            c.setFillColor(NAVY if cloud or fact else PALE)
            c.setStrokeColor(NAVY if cloud or fact else colors.HexColor('#b9d7db'))
            c.roundRect(x,y,w,h,5,stroke=1,fill=1)
            c.setFillColor(colors.white if cloud or fact else INK)
            labels = self.nodes[key].split('<br/>')
            size = 9.2 if self.kind == 'arquitectura' else 9.0
            c.setFont('MemoBold',size)
            for j,label in enumerate(labels):
                if pdfmetrics.stringWidth(label,'MemoBold',size) > w-10:
                    raise ValueError('Etiqueta fuera de caja: '+label)
                c.drawCentredString(x+w/2,y+h/2+(len(labels)-1)*5.7-j*11.4-3,label)


def styles():
    base = dict(fontName='Memo', fontSize=10.2, leading=13.25, textColor=INK,
                alignment=TA_LEFT, splitLongWords=True)
    return {
        'p': ParagraphStyle('body', **base),
        'caption': ParagraphStyle('caption', **(base | dict(fontSize=9,leading=11.5,textColor=MUTED))),
        'ref': ParagraphStyle('reference', **(base | dict(fontSize=8.8,leading=11.4))),
        'h1': ParagraphStyle('title',fontName='MemoBold',fontSize=23,leading=26,textColor=NAVY),
        'h2': ParagraphStyle('heading',fontName='MemoBold',fontSize=18,leading=22,textColor=NAVY),
        'h3': ParagraphStyle('subheading',fontName='MemoBold',fontSize=11.5,leading=15,textColor=TEAL),
        'cell': ParagraphStyle('cell',fontName='Memo',fontSize=9.1,leading=11.8,textColor=INK),
        'head': ParagraphStyle('head',fontName='MemoBold',fontSize=9.1,leading=11.8,textColor=colors.white),
        'code': ParagraphStyle('code',fontName='Memo',fontSize=9.2,leading=12.5,textColor=NAVY),
    }


def flowable(kind, body, st):
    if kind == 'mermaid':
        return Diagram(body), 8
    if kind == 'table':
        n = len(body[0])
        if n == 4:
            widths = [.20,.22,.24,.34]
        elif n == 3:
            widths = [.29,.40,.31]
        else:
            widths = [.67,.33]
        cells = [[Paragraph(inline(cell),st['head' if i==0 else 'cell']) for cell in row] for i,row in enumerate(body)]
        obj = Table(cells,colWidths=[CONTENT_WIDTH*w for w in widths],hAlign='LEFT')
        obj.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[PALE,colors.white]),
            ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#b9d7db')),
        ]))
        return obj, 11
    if kind == 'bash':
        obj = Table([[Paragraph('<br/>'.join(inline(s) for s in body.splitlines()),st['code'])]],colWidths=[CONTENT_WIDTH])
        obj.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('BOX',(0,0),(-1,-1),.5,colors.HexColor('#b9d7db')),('LEFTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
        return obj, 10
    style = kind
    if kind == 'p' and body.startswith(('Figura ', 'Wilmer ')):
        style = 'caption'
    elif kind == 'p' and body.startswith(('R1.', 'E1.')):
        style = 'ref'
    gap = {'h1':9,'h2':15,'h3':7,'p':9}[kind]
    return Paragraph(inline(body),st[style]), gap


def main():
    fonts()
    text = SOURCE.read_text()
    pages = text.split('<!-- pagebreak -->')
    assert len(pages)==6
    st = styles()
    # Calcular primero: si una sección desborda, no reemplazar el PDF anterior.
    prepared = []
    heights = []
    for number, page in enumerate(pages,1):
        objs = []
        for kind, body in blocks(page):
            obj,gap = flowable(kind,body,st)
            _,h = obj.wrap(CONTENT_WIDTH,HEIGHT)
            objs.append((obj,h,gap))
        used = sum(h+gap for _,h,gap in objs)
        limit = HEIGHT-103
        if used > limit:
            raise ValueError(f'Página {number}: requiere {used:.1f} pt, disponible {limit:.1f} pt')
        prepared.append(objs)
        heights.append(round(used,1))
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    temporary = OUTPUT.with_suffix('.tmp.pdf')
    c = canvas.Canvas(str(temporary),pagesize=A4,invariant=1)
    c.setTitle('PSet 2 - Pipeline reproducible para apoyo académico con OULAD')
    c.setAuthor('Wilmer Puerta')
    c.setSubject('Fuente SHA-256: '+hashlib.sha256(SOURCE.read_bytes()).hexdigest())
    for number,objs in enumerate(prepared,1):
        c.setFillColor(TEAL)
        c.rect(MARGIN,HEIGHT-28,38,3,fill=1,stroke=0)
        c.setFillColor(MUTED)
        c.setFont('Memo',8)
        c.drawRightString(WIDTH-MARGIN,HEIGHT-29,'CIENCIA DE DATOS | PIPELINE END-TO-END')
        y = HEIGHT-47
        for obj,h,gap in objs:
            y -= h
            obj.drawOn(c,MARGIN,y)
            y -= gap
        c.setStrokeColor(colors.HexColor('#cbd8df'))
        c.setLineWidth(.5)
        c.line(MARGIN,41,WIDTH-MARGIN,41)
        c.setFont('Memo',8)
        c.setFillColor(MUTED)
        c.drawString(MARGIN,27,'Wilmer Puerta | PSet 2 | 13 nov 2026')
        c.drawRightString(WIDTH-MARGIN,27,f'{number} / 6')
        c.showPage()
    c.save()
    temporary.replace(OUTPUT)
    print('PDF generado: 6 páginas; uso vertical (pt): '+str(heights))


if __name__=='__main__':
    main()
