"""Descarga los artefactos exactos del lock y verifica bytes y SHA-256."""
import hashlib,json,sys,urllib.request
from pathlib import Path
lock=json.loads(Path(sys.argv[1]).read_text());out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
for item in lock['artifacts']:
    data=urllib.request.urlopen(item['url'],timeout=120).read()
    if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
        raise SystemExit('Artefacto distinto del lock: '+item['artifact'])
    (out/(item['artifact']+'-'+item['version']+'.jar')).write_bytes(data)
