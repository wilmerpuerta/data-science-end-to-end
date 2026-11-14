"""Comprueba sincronía textual, formatos, datos, enlaces e invariantes."""
from pathlib import Path
from collections import Counter
import re,json,hashlib,zipfile,xml.etree.ElementTree as ET
import nbformat,pymupdf
from exportar_documentos import plain
ROOT=Path(__file__).resolve().parents[2]
def actualizar_inventario():
 inventory={}
 for p in sorted(ROOT.rglob('*')):
  if p.is_file() and not any(x in p.parts for x in ['.venv','tmp','backups','__pycache__','.git','.local','.secrets','secrets','node_modules','.retry-probes','target','dbt_packages','logs']) and p.name not in ['.DS_Store','entregables-manifest.json'] and not (p.name.startswith('.env') and p.name!='.env.example') and p.suffix not in ['.pem','.p8','.key','.pub'] and not p.name.endswith('.local.sql') and not ('datasets' in p.parts and p.suffix=='.csv'):
   inventory[str(p.relative_to(ROOT))]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 (ROOT/'pset-01/docs/entregables-manifest.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
def compact(t): return ''.join(c for c in t.casefold() if c.isalnum())
def visible_md(line):
 line=re.sub(r'^#{1,6}\s+','',line.strip());line=re.sub(r'^- ','',line)
 return plain(line).replace('*','')
def main():
 result={'checks':{},'limitations':['PSet 1 no incluye entrenamiento ni piloto; el avance del pipeline PSet 2 se registra por separado.','Colab pendiente de acceso identificable y sincronización.','PSet 1 conserva su auditoría original de repeticiones; la auditoría global posterior y sus decisiones están en PSet 2.']}
 def check(name,value):
  result['checks'][name]=value
  if value is not True: raise AssertionError((name,value))
 nb=nbformat.read(ROOT/'pset-01/notebooks/PSet1_notebook_completo_Puerta_Wilmer.ipynb',as_version=4);nbformat.validate(nb)
 full=ROOT/'pset-01/proyecto-completo-pset1.md';check('notebook_exact_source',''.join(c.source for c in nb.cells)==full.read_text())
 for name,src in [('memo','propuesta-pset1.md'),('notebook_completo','proyecto-completo-pset1.md')]:
  pdf=pymupdf.open(ROOT/f'pset-01/output/pdf/PSet1_{name}_Puerta_Wilmer.pdf');result[name+'_pages']=len(pdf)
  if name=='memo':check('memo_1_to_2_pages',1<=len(pdf)<=2)
  extracted=''.join(''.join(span['text'] for b in p.get_text('dict')['blocks'] if 'lines' in b for line in b['lines'] for span in line['spans'] if span['bbox'][1]<800) for p in pdf)
  text=compact(extracted);missing=[]
  for line in (ROOT/'pset-01'/src).read_text().splitlines():
   if not line.strip() or re.fullmatch(r'[|:\- ]+',line):continue
   cells=line.strip().strip('|').split('|') if line.startswith('|') else [line]
   for c in cells:
    t=compact(visible_md(c))
    if t and t not in text:missing.append(c[:160])
  result[name+'_missing_fragments']=missing;check(name+'_complete_text',not missing)
  check(name+'_page_geometry',all(0<=span['bbox'][0]<span['bbox'][2]<=p.rect.width+1 and 0<=span['bbox'][1]<span['bbox'][3]<=p.rect.height+1 for p in pdf for b in p.get_text('dict')['blocks'] if 'lines' in b for line in b['lines'] for span in line['spans']))
 slides=json.loads((ROOT/'pset-01/scripts/pitch-contenido.json').read_text()); ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
 with zipfile.ZipFile(ROOT/'pset-01/output/pitch/PSet1_pitch_Puerta_Wilmer.pptx') as z:
  names=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)];check('six_native_slides',len(names)==6)
  for i,s in enumerate(slides,1):
   root=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'));actual='\n'.join(e.text or '' for e in root.findall('.//a:t',ns));expected='\n'.join([s['title'],s['message']]+[o['text'] for o in s['objects']])
   check(f'slide_{i}_exact_visible_text',actual==expected);check(f'slide_{i}_native_editability',len(root.findall('.//a:t',ns))>3 and b'<p:pic>' not in z.read(f'ppt/slides/slide{i}.xml'))
   note=ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'));check(f'slide_{i}_notes',s['notes'] in '\n'.join(e.text or '' for e in note.findall('.//a:t',ns)))
   md=(ROOT/'pset-01/pset01-presentacion.md').read_text();check(f'slide_{i}_markdown',all(t in md for t in [s['title'],s['message']]+[o['text'] for o in s['objects']]))
 ppt=ROOT/'pset-01/output/pitch/PSet1_pitch_Puerta_Wilmer.ppt';check('genuine_ppt',ppt.read_bytes()[:8]==bytes.fromhex('d0cf11e0a1b11ae1'))
 for kind,filename in [('pptx','pitch-revision.pdf'),('ppt','ppt-revision.pdf')]:
  review=ROOT/'tmp'/filename
  if review.exists():
   pdf=pymupdf.open(review);check(kind+'_powerpoint_render_six_slides',len(pdf)==6)
   for i,s in enumerate(slides):check(f'{kind}_powerpoint_render_{i+1}_complete',compact('\n'.join([s['title'],s['message']]+[o['text'] for o in s['objects']]))==compact(pdf[i].get_text()))
 # Publicar el informe parcial antes de validar su propio enlace en README.
 (ROOT/'pset-01/docs/verificacion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 links=[]
 for f in [ROOT/'README.md',ROOT/'pset-01/README.md',ROOT/'pset-02/README.md']:
  for label,target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',f.read_text()):
   if re.match(r'https?://|#',target):continue
   if not (f.parent/target.split('#')[0]).exists():links.append(str(f.relative_to(ROOT))+': '+target)
 check('readme_links_valid',not links)
 manifest=json.loads((ROOT/'datasets/manifest.json').read_text())
 for name,meta in manifest['files'].items():
  path=ROOT/'datasets'/name; h=hashlib.sha256()
  with path.open('rb') as f:
   for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
  check('unchanged_'+name,h.hexdigest()==meta['sha256'] and path.stat().st_size==meta['bytes'])
 a=json.loads((ROOT/'pset-01/docs/auditoria-resultados.json').read_text())['populations']
 for k,v in [('original',a['original']),('initial',a['initial'])]+list(a['cuts'].items()):check('class_sum_'+k,v['N']==v['Fail']+v['Withdrawn']+v['Approved'])
 for name in ['canvas-wilmer-puerta.md','propuesta-pset1.md','proyecto-completo-pset1.md','pset01-presentacion.md']:
  t=(ROOT/'pset-01'/name).read_text();check('no_personal_paths_'+name,'/Users/' not in t and 'Downloads' not in t)
  check('four_risk_groups_'+name,all('R'+str(i) in t for i in range(1,5)))
 # La etapa 2 ya puede tener implementación real; exigir evidencia local
 # en lugar de mantener la condición histórica de ausencia de Compose.
 compose=ROOT/'pset-02/docker-compose.yml'
 if compose.exists():
  evidence=json.loads((ROOT/'pset-02/docs/infraestructura-verificacion.json').read_text())
  check('pset2_compose_execution_documented',evidence.get('compose_config_valid') is True and all(evidence['services'][s]['health']=='healthy' for s in ['kestra','postgres','spark']))
 else:check('pset2_compose_not_yet_implemented',True)
 for n in ['pset-03','pset-04']:check(n+'_prepared',(ROOT/n/'.gitkeep').exists())
 (ROOT/'pset-01/docs/verificacion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 actualizar_inventario()
 print(f"OK: {len(result['checks'])} verificaciones. Memo {result['memo_pages']} páginas; completo {result['notebook_completo_pages']} páginas; pitch 6 diapositivas.")
if __name__=='__main__':main()
