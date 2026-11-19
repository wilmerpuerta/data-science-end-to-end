import base64,json,subprocess,tempfile,time,urllib.request,urllib.parse,hashlib,sys,os,shutil
from datetime import datetime,timezone
from pathlib import Path
import websocket
ROOT=Path(__file__).resolve().parents[1]
def chrome_binary():
 configured=os.environ.get('CHROME_BIN')
 candidate=configured or shutil.which('google-chrome') or shutil.which('chromium') or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
 if not Path(candidate).is_file():raise RuntimeError('Configurar CHROME_BIN con un Chrome/Chromium instalado')
 return candidate
if sys.argv[1:]==['--verificar']:
 urllib.request.urlopen('http://127.0.0.1:5001/health',timeout=5).read()
 print(json.dumps({'status':'browser_and_server_checked','browser':chrome_binary(),'root':str(ROOT),'screenshot_captured':False}));raise SystemExit(0)
profile=Path(tempfile.mkdtemp(prefix='pset3-mlflow-chrome-'))
chrome=subprocess.Popen([chrome_binary(),'--headless=new','--remote-debugging-port=0','--remote-allow-origins=*','--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-sync','--user-data-dir='+str(profile),'about:blank'],stdout=subprocess.DEVNULL,stderr=open(profile/'chrome.log','w'))
try:
 for _ in range(100):
  if (profile/'DevToolsActivePort').exists():break
  if chrome.poll() is not None:raise RuntimeError('Chrome exited: '+(profile/'chrome.log').read_text()[-1000:])
  time.sleep(.2)
 port=(profile/'DevToolsActivePort').read_text().splitlines()[0]
 pages=json.load(urllib.request.urlopen('http://127.0.0.1:'+port+'/json'))
 ws=websocket.create_connection(pages[0]['webSocketDebuggerUrl'],timeout=30,suppress_origin=True)
 seq=0
 def call(method,params=None):
  global seq
  seq+=1;ws.send(json.dumps({'id':seq,'method':method,'params':params or {}}))
  while True:
   result=json.loads(ws.recv())
   if result.get('id')==seq:
    if 'error' in result:raise RuntimeError(result['error'])
    return result.get('result',{})
 def evaluate(expression):return call('Runtime.evaluate',{'expression':expression,'returnByValue':True}).get('result',{}).get('value')
 call('Emulation.setDeviceMetricsOverride',{'width':1560,'height':1080,'deviceScaleFactor':1,'mobile':False})
 url='http://127.0.0.1:5001/#/compare-runs?runs='+urllib.parse.quote(json.dumps(['dc2fa9bb8bee4944bd00611a6ac5c34f','bb2b400975994efdb01ea418118dda67']))+'&experiments=%5B%226%22%5D'
 call('Page.navigate',{'url':url})
 time.sleep(8)
 actions=[]
 for title in ['Visualizations','Parameters']:
  expr="""(()=>{const e=document.evaluate("//*[normalize-space(text())='"+TITLE+"']",document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue;if(!e)return {found:false};const h=e.closest('[role=button],.ant-collapse-header')||e;h.dispatchEvent(new MouseEvent('click',{bubbles:true}));return {found:true,tag:h.tagName,html:h.outerHTML.slice(0,350)}})()""".replace('TITLE',json.dumps(title))
  result=evaluate(expr);actions.append({'title':title,'result':result});print('ACTION',result)
 time.sleep(1)
 call('Emulation.setDeviceMetricsOverride',{'width':900,'height':1120,'deviceScaleFactor':2,'mobile':False})
 time.sleep(1)
 print('URL',evaluate('location.href'))
 print('TEXT',evaluate('document.body.innerText')[:3500])
 print('HEADINGS',evaluate("Array.from(document.querySelectorAll('*')).filter(e=>e.children.length===0 && ['Visualizations','Parameters','Metrics'].includes(e.textContent)).map(e=>e.parentElement.outerHTML.slice(0,300))"))
 (profile/'pset3-cdp.json').write_text(json.dumps({'port':port,'ws':pages[0]['webSocketDebuggerUrl'],'url':url}))
 out=ROOT/'docs/evidencia';out.mkdir(exist_ok=True)
 shot=call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
 (out/'mlflow-comparacion.png').write_bytes(base64.b64decode(shot['data']))
 (profile/'pset3-ui-text.txt').write_text(evaluate('document.body.innerText'))
 (profile/'pset3-ui.html').write_text(evaluate('document.body.innerHTML'))
 meta={'captured_at_utc':datetime.now(timezone.utc).isoformat(),'source':'MLflow 2.22.0 real local comparison UI rendered by Chrome headless','url':url,'run_ids':['dc2fa9bb8bee4944bd00611a6ac5c34f','bb2b400975994efdb01ea418118dda67'],'browser':call('Browser.getVersion'),'viewport_css':[900,1120],'device_scale_factor':2,'actions':actions,'image_modified':False,'sha256':hashlib.sha256((out/'mlflow-comparacion.png').read_bytes()).hexdigest()}
 rect=evaluate("(()=>{const e=document.evaluate(\"//*[normalize-space(text())='Metrics']\",document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue;const r=(e.closest('[role=button]')||e).getBoundingClientRect();return {x:0,y:r.y+window.scrollY,width:900,height:270,scale:1}})()")
 detail=call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':True,'clip':rect})
 (out/'mlflow-comparacion-detalle.png').write_bytes(base64.b64decode(detail['data']))
 meta.update(detail_sha256=hashlib.sha256((out/'mlflow-comparacion-detalle.png').read_bytes()).hexdigest(),detail_clip=rect,detail_method='native browser screenshot of contiguous metrics region; no image editing')
 (out/'mlflow-comparacion.json').write_text(json.dumps(meta,indent=2))
 chrome.terminate()
 print('PID',chrome.pid,'PROFILE',profile)
except BaseException:
 chrome.terminate();raise
