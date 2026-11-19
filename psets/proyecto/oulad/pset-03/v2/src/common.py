"""Identidad y verificación de artefactos locales congelados."""
from pathlib import Path
import hashlib, json
ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / '.local'

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def identity(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def read_bundle(pointer='snapshot-current.json'):
    ref=json.loads((LOCAL/pointer).read_text())
    folder=(LOCAL/ref['directory']).resolve()
    if LOCAL.resolve() not in folder.parents:raise ValueError('Directorio fuera de .local')
    manifest=json.loads((folder/'manifest.json').read_text())
    if identity(manifest['identity'])!=manifest['id'] or ref['id']!=manifest['id']:
        raise ValueError('Identidad de manifiesto inválida')
    for name,meta in manifest['identity']['files'].items():
        if Path(name).name!=name or sha256(folder/name)!=meta['sha256']:
            raise ValueError('Artefacto alterado: '+name)
    return folder,manifest

def publish_pointer(name,folder,identifier):
    path=LOCAL/name
    # Crear una vez, sin reemplazar el snapshot o split de una ejecución previa.
    with path.open('x') as f:
        json.dump({'directory':str(folder.relative_to(LOCAL)),'id':identifier},f,indent=2)
        f.write('\n')
