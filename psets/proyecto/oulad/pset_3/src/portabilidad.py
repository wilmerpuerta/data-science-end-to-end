"""Verificación de las adaptaciones de rutas de la entrega pset_3."""
from pathlib import Path
import json
import subprocess
from .common import ROOT, identity, sha256


def raiz_git(folder):
    result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=folder,
                            capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError('Clonar el repositorio con su historial Git antes de verificar el protocolo')
    return Path(result.stdout.strip()).resolve()


def hash_fuente_original(name):
    """Normaliza solo los dos cambios de rutas declarados, verificando ambos lados."""
    actual = sha256(ROOT/name)
    path = ROOT/'docs/enmienda-portabilidad.json'
    if not path.is_file():
        raise RuntimeError('Falta la enmienda de portabilidad de la entrega')
    patch = json.loads(path.read_text())
    content = patch['content']
    fixed = json.loads((ROOT/'docs/protocolo-congelado.json').read_text())
    io = json.loads((ROOT/'docs/enmienda-lectura-api.json').read_text())
    allowed = {'src/seguimiento.py', 'src/openai_api.py'}
    if (identity(content) != patch['id'] or content['base_protocol_id'] != fixed['id']
            or content['base_io_patch_id'] != io['id'] or set(content['sources']) != allowed
            or content['validator_sha256'] != sha256(Path(__file__))):
        raise RuntimeError('Enmienda de portabilidad incompatible o alterada')
    if name not in allowed:
        return actual
    record = content['sources'][name]
    archived = ROOT/'docs/portabilidad/fuentes-originales'/name
    if (actual != record['after'] or sha256(archived) != record['before']
            or record['before'] != io['content']['sources'][name]['after']):
        raise RuntimeError('Fuente de portabilidad alterada: '+name)
    return record['before']
