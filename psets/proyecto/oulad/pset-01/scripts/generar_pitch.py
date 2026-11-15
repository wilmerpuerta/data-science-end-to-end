"""PPTX OOXML nativo y fuente exacta visible. Fallback sin artifact-tool local.
No usa python-pptx ni diapositivas aplanadas. Diagramas y textos editables.
"""
from generar_contenidos import ROOT,write
import json,zipfile,html,re
def box(text,x,y,w,h,size=26,color='FFFFFF',bold=False,fill=None):
 return dict(text=text,x=x,y=y,w=w,h=h,size=size,color=color,bold=bold,fill=fill)
def main():
 slides=json.loads((ROOT/'pset-01/scripts/pitch-contenido.json').read_text())
 assert len(slides)==6
 out=['# Pitch revisado: seis diapositivas','', 'Wilmer Puerta · Revisión del 15-nov-2026. Fuente visible exacta del PPTX. Notas y fuentes se conservan aparte. Se mantiene el diseño editorial y los objetos nativos editables.']
 for i,s in enumerate(slides,1):
  out+=['',f"## Diapositiva {i}",'', '### Contenido visible exacto','',s['title'],'',s['message'],'']+[o['text']+'\n' for o in s['objects']]+['### Visual propuesto','',s['visual'],'','### Notas del presentador','',s['notes'],'','### Fuentes','',s['sources']]
 write('pset-01/pset01-presentacion.md','\n'.join(out))
 make_pptx(slides)

NS='xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
def rels(items): return '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/{kind}" Target="{target}"/>' for i,(kind,target) in enumerate(items,1))+'</Relationships>'
def shape(i,o):
 esc=html.escape; unit=lambda x:str(round(x*9525))
 paras=''.join('<a:p><a:pPr/><a:r><a:rPr lang="es-EC" sz="'+str(round(o['size']*75))+'" b="'+str(int(o['bold']))+'"><a:solidFill><a:srgbClr val="'+o['color']+'"/></a:solidFill><a:latin typeface="Arial"/></a:rPr><a:t>'+esc(t)+'</a:t></a:r><a:endParaRPr lang="es-EC"/></a:p>' for t in o['text'].split('\n'))
 return f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="Text {i}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{unit(o["x"])}" y="{unit(o["y"])}"/><a:ext cx="{unit(o["w"])}" cy="{unit(o["h"])}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" rIns="0" tIns="0" bIns="0"/><a:lstStyle/>{paras}</p:txBody></p:sp>'
GROUP='<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
def make_pptx(slides):
 # Base técnica normalizada por PowerPoint, sin diapositivas, notas ni propiedades
 # personales. Conserva temas y relaciones válidos para regenerar sin reparación.
 files=json.loads((ROOT/'pset-01/scripts/pitch-base.json').read_text())
 for i,s in enumerate(slides,1):
  objs=[box(s['title'],64,55,1150,116,44 if i!=6 else 40,'FFFFFF',True),box(s['message'],64,185,1150,64,29,'87CEEB')]+s['objects']
  files[f'ppt/slides/slide{i}.xml']=f'<p:sld {NS}><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="101016"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>{GROUP}'+''.join(shape(j,o) for j,o in enumerate(objs,2))+'</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
  note=shape(2,box(s['notes']+'\nFuentes: '+s['sources'],0,0,600,700,18,'000000')).replace('<p:nvPr/>','<p:nvPr><p:ph type="body" idx="1"/></p:nvPr>',1)
  files[f'ppt/notesSlides/notesSlide{i}.xml']=f'<p:notes {NS}><p:cSld><p:spTree>{GROUP}{note}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>'
  files[f'ppt/notesSlides/_rels/notesSlide{i}.xml.rels']=rels([('slide',f'../slides/slide{i}.xml'),('notesMaster','../notesMasters/notesMaster1.xml')])
 path=ROOT/'pset-01/output/pitch/PSet1_pitch_Puerta_Wilmer.pptx'
 path.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for name,text in files.items():
   if not text.startswith('<?xml'):text='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+text
   z.writestr(name,text)
 print('Pitch: seis diapositivas nativas y Markdown exacto con base técnica normalizada')

if __name__=='__main__':main()
