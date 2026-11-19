"""Los trabajos spark-submit se prueban en su contenedor, no al importar pytest.

Las pruebas del PSet 03 que requieren recursos privados se habilitan con
PSET3_PYTEST=1; el núcleo público del PSet 04 se importa desde proyecto_final.
test_features.py requiere --run-id y escribe un informe del trabajo Spark;
smoke_test.py requiere los CSV montados en /datasets. Ninguno es un módulo de
tests pytest. Las pruebas unitarias de Raw siguen incluidas en la colección.
"""
import os
import sys
from pathlib import Path

_final = Path(__file__).resolve().parent / "proyecto_final"
if _final.is_dir():
    sys.path.insert(0, str(_final))

collect_ignore = [
    'laboratorios',
    'tmp',
    'backups',
    'pset_3/tmp',
    'pset-02/spark/test_features.py',
    'pset-02/spark/smoke_test.py',
]

if os.environ.get("PSET3_PYTEST") != "1":
    collect_ignore.append("pset_3/tests")
