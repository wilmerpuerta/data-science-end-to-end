# Entrega con estructura de rúbrica

La carpeta pública es `pset_3/`. Los archivos requeridos están directamente en su raíz y en `notebooks/`, `src/` y `docs/`, con archivos reales. No contiene una carpeta `v2/` ni `output/pdf/`. El PDF de seis páginas está exclusivamente en `docs/PSet3_memo_Puerta_Wilmer.pdf` y es idéntico al aprobado.

Se incluyen auxiliares necesarios: `mlflow/` para el Dockerfile, `config/` y `prompts/` para los contratos del experimento, y `scripts/` y `tests/` para generación y verificación. Los datos privados y los volúmenes de MLflow se suministran separadamente conforme al README; no se incluyen en el ZIP público.

Los seis notebooks se ejecutaron en kernels nuevos, con las salidas guardadas. Los dos primeros recalculan EDA y preparación; los siguientes verifican resultados históricos y la carga por alias. Se conservaron 382 corridas: el empaquetado no creó nuevas corridas ni llamadas API. Las 48 pruebas unitarias pasaron. Preparación, cargador de datos, CSV de corridas y PDF conservan sus bytes originales.

Las adaptaciones de raíz Git y credenciales están registradas en `enmienda-portabilidad.json`, con fuentes anteriores y hashes. No se sustituyen los SHAs históricos de entrenamiento por el commit del empaquetado.

Ver `estructura-entrega.json`, `portabilidad/notebooks-reproducidos.json` y `pruebas-estructura.txt` para los controles. Las limitaciones académicas y de reproducción declaradas en el PSet 03 se conservan.
