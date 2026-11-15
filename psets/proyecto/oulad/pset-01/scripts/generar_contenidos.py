"""Valida las fuentes editoriales vigentes sin reconstruirlas desde el encargo histórico.

Las fuentes Markdown revisadas y pitch-contenido.json se versionan como entradas.
El bootstrap original queda en el respaldo local de la revisión del 15-nov-2026.
"""
from pathlib import Path
import datetime
import shutil

ROOT=Path(__file__).resolve().parents[2]

def write(path,text):
    p=ROOT/path
    p.parent.mkdir(parents=True,exist_ok=True)
    text=text.strip()+'\n'
    if p.exists() and p.read_text()!=text:
        backup=ROOT/'backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')/path
        backup.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,backup)
    p.write_text(text)

def main():
    from validar_fuentes import validate
    checks=validate()
    print(f'Fuentes editoriales vigentes: {len(checks)} invariantes aprobadas. No se reemplaza contenido con el prompt histórico.')

if __name__=='__main__':main()
