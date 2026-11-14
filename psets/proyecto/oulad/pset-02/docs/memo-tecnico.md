# Memo técnico del PSet 2

La fuente editorial es [memo-pset2.md](../memo-pset2.md). El [PDF de seis páginas](../output/pdf/PSet2_memo_Puerta_Wilmer.pdf) se genera desde esa única fuente; los diagramas Mermaid se dibujan como vectores con los mismos nodos y aristas. No se edita el PDF por separado. Se conserva la convención de nombre del autor utilizada en PSet 1.

## Generar y verificar

Desde la raíz del repositorio, con Python 3.11 o posterior y Arial, DejaVu Sans o Liberation Sans instaladas:

```bash
python3 -m venv tmp/venv-memo
tmp/venv-memo/bin/python -m pip install -r pset-02/scripts/requirements-memo.txt
tmp/venv-memo/bin/python pset-02/scripts/generar_memo.py
tmp/venv-memo/bin/python pset-02/scripts/verificar_memo.py --render
```

Si ya existe un entorno con esas dependencias, usar su intérprete; la comprobación local utilizó .venv/bin/python. En macOS se busca Arial del sistema; en Linux se busca DejaVu Sans o Liberation Sans en sus rutas estándar. PSET2_MEMO_FONT_DIR permite indicar una carpeta externa con Arial.ttf y Arial Bold.ttf. Los tipos de letra no se copian al repositorio. El diseño usa A4 y fuentes incrustadas; no requiere Snowflake, Docker, claves ni acceso de red para exportar o verificar con el entorno instalado.

El generador calcula el espacio de cada página y rechaza desbordamientos antes de reemplazar el PDF. El [informe de verificación](memo-verificacion.json) contrasta cada párrafo, celda y etiqueta de diagrama en su página, verifica seis páginas, límites de texto y cifras frente a los JSON de ejecución. También compara los Markdown de resultados con sus generadores y comprueba los enlaces. Las páginas PNG de revisión quedan en tmp/pdfs/pset2-memo, excluido de Git. La extracción textual no sustituye revisar visualmente las seis páginas.

## Alcance de la evidencia

El memo describe la implementación y los resultados de los días 12 y 13 de noviembre de 2026. Conserva explícitos los límites: ensayos controlados de fallo, calendarios desactivados, backfill por fichero, cobertura y exactitud desconocidas, reproducción local con recursos Snowflake reutilizados y costo monetario sin medir. No hay entrenamiento ni publicación GitHub. El documento y sus scripts de exportación son posteriores a la instantánea de 214 archivos de la reproducción limpia y no se presentan como incluidos en esa prueba.

## Correspondencia con el enunciado y la rúbrica

| Criterio | Página del memo | Evidencia complementaria |
|---|---|---|
| Kestra, ingesta y orquestación; 15 % | 1-2 | [Raw](ingesta-raw-verificacion.json), [pruebas integrales](pipeline-pruebas.json) |
| Calidad y limpieza; 20 % | 3 | [Bronze](calidad-bronze.json), [Silver](calidad-silver.json) |
| dbt y capas; 15 % | 3-4 | [Build real de las tres capas](dbt-build-gold.json) |
| Star schema; 15 % | 4 | [Modelado](gold.md), [métricas Gold](calidad-gold.json) |
| Spark y OBT; 15 % | 5 | [Verificación OBT](obt-verificacion.json), [contrato](../spark/feature-contract.json) |
| Infraestructura y reproducción; 10 % | 1 y 6 | [README](../README.md), [reproducción limpia](reproduccion-limpia.json) |
| Documento y decisiones; 10 % | 1-6 | Dos diagramas, decisiones de calidad, batch frente a streaming y limitaciones |

La correspondencia facilita revisar la entrega; no asigna una calificación ni convierte límites declarados en funcionalidades probadas.
