# Memo técnico del PSet 2

La fuente editorial es [memo-pset2.md](memo-pset2.md). El [PDF de seis páginas](PSet2_memo_Puerta_Wilmer.pdf) se genera desde esa única fuente; los diagramas Mermaid se dibujan como vectores con los mismos nodos y aristas. No se edita el PDF por separado. Se conserva la convención de nombre del autor utilizada en PSet 1.

## Generar y verificar

Desde la raíz del repositorio, con Python 3.11 o posterior y Arial, DejaVu Sans o Liberation Sans instaladas:

```bash
python3 -m venv tmp/venv-memo
tmp/venv-memo/bin/python -m pip install -r pset_2/kestra/scripts/requirements-memo.txt
tmp/venv-memo/bin/python pset_2/kestra/scripts/generar_memo.py
tmp/venv-memo/bin/python pset_2/kestra/scripts/verificar_memo.py --render
```

Si ya existe un entorno con esas dependencias, usar su intérprete; la comprobación local utilizó .venv/bin/python. En macOS se busca Arial del sistema; en Linux se busca DejaVu Sans o Liberation Sans en sus rutas estándar. PSET2_MEMO_FONT_DIR permite indicar una carpeta externa con Arial.ttf y Arial Bold.ttf. Los tipos de letra no se copian al repositorio. El diseño usa A4 y fuentes incrustadas; no requiere Snowflake, Docker, claves ni acceso de red para exportar o verificar con el entorno instalado.

El generador calcula el espacio de cada página y rechaza desbordamientos antes de reemplazar el PDF. El [informe de verificación](memo-verificacion.json) contrasta cada párrafo, celda y etiqueta de diagrama en su página, verifica seis páginas, límites de texto y cifras frente a los JSON de ejecución. También compara los Markdown de resultados con sus generadores y comprueba los enlaces. Las páginas PNG de revisión quedan en tmp/pdfs/pset2-memo, excluido de Git. La extracción textual no sustituye revisar visualmente las seis páginas.

## Alcance de la evidencia

El memo conserva los resultados de los días 12 y 13 de noviembre de 2026 y añade la revisión de calendario del 20-nov. El padre está activo y la ejecución Schedule recuperada del 15-nov terminó SUCCESS; Raw mantiene desactivado su trigger independiente. La prueba es un backfill del calendario, distinto de la recarga por fichero y de observar la fecha original en tiempo real. [Evidencia](calendario-programado.md). Se mantienen los límites de calidad, escritor único, reproducción con recursos Snowflake existentes y costo monetario desconocido. No hay entrenamiento. La documentación nueva es posterior a los 214 archivos de la reproducción histórica; no se afirma incluida en esa instantánea.

## Correspondencia con el enunciado y la rúbrica

| Criterio | Página del memo | Evidencia complementaria |
|---|---|---|
| Kestra, ingesta y orquestación; 15 % | 1-2 | [Raw](ingesta-raw-verificacion.json), [pruebas integrales](pipeline-pruebas.json), [cron y Schedule](calendario-verificacion.json) |
| Calidad y limpieza; 20 % | 3 | [Bronze](calidad-bronze.json), [Silver](calidad-silver.json) |
| dbt y capas; 15 % | 3-4 | [Build real de las tres capas](dbt-build-gold.json) |
| Star schema; 15 % | 4 | [Modelado](gold.md), [métricas Gold](calidad-gold.json) |
| Spark y OBT; 15 % | 5 | [Verificación OBT](obt-verificacion.json), [contrato](../spark/feature-contract.json) |
| Infraestructura y reproducción; 10 % | 1 y 6 | [README](../README.md), [reproducción limpia](reproduccion-limpia.json) |
| Documento y decisiones; 10 % | 1-6 | Dos diagramas, decisiones de calidad, batch frente a streaming y limitaciones |

La correspondencia facilita revisar la entrega; no asigna una calificación ni convierte límites declarados en funcionalidades probadas.
