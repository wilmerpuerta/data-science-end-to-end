"""Los trabajos spark-submit se prueban en su contenedor, no al importar pytest.

test_features.py requiere --run-id y escribe un informe del trabajo Spark;
smoke_test.py requiere los CSV montados en /datasets. Ninguno es un módulo de
tests pytest. Las pruebas unitarias de Raw siguen incluidas en la colección.
"""
collect_ignore = [
    'pset-02/spark/test_features.py',
    'pset-02/spark/smoke_test.py',
]
