"""Valida fuentes y documentación de cierre sin reescribir README ni dependencias."""
from generar_contenidos import ROOT
from validar_fuentes import validate
import re

def main():
    validate()
    for name in ['README.md','docs/respuesta-feedback.md','docs/trazabilidad-entregables.md']:
        source=ROOT/'pset-01'/name
        assert source.is_file()
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',source.read_text()):
            if re.match(r'https?://|#',target):continue
            assert (source.parent/target.split('#')[0]).exists(),(name,target)
    print('Documentación revisada y enlaces locales válidos. README y dependencias se conservan.')

if __name__=='__main__':main()
