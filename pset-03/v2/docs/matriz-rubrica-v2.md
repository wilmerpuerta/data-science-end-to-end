# Matriz de evidencia de la reconstrucción v2

Actualización: 2026-11-18T07:08:12.704065-05:00. Proceso: notebooks_complete_editorial_pending; fase: reproduccion.

Seguimiento de evidencia disponible y pendiente. No asigna nota ni sustituye la auditoría final. Los notebooks preparados se distinguen de los ejecutados y verificados.

| Criterio | Peso | Estado | Evidencia | Comprobación pendiente |
|---|---:|---|---|---|
| EDA y features | 15 % | evidencia disponible | `notebooks/01_eda.ipynb`; `notebooks/02_features.ipynb`; `docs/eda/resumen.json`; `docs/features/resumen.json`; `docs/ablacion/resultados.json` |  |
| Preparación y validación | 15 % | evidencia disponible | `src/pipeline.py`; `src/datos.py`; `docs/protocolo-congelado.json` | Mantener declaración de benchmark 2014J previamente observado |
| Baselines y seis candidatos | 15 % | evidencia disponible | `notebooks/03_baseline_candidatos.ipynb`; `docs/modelos/resultados.json`; `docs/prompting.md` | Auditoría de cronología y artefactos |
| Tuning | 15 % | evidencia disponible | `notebooks/04_tuning.ipynb`; `config/espacios-tuning.json`; `docs/tuning/resultados.json` | Tres familias por negocio, >=30 configuraciones únicas por familia, nested y delta frente a dispersión |
| Tracking y Registry | 20 % | parcial | `docs/corridas.csv`; `docs/protocolo-congelado.json`; `docs/seleccion/evaluacion.json` | Auditar metadata, firmas y ejemplos, padres/hijas, captura real y aliases vivos; esta matriz no los certifica |
| Selección y negocio | 15 % | evidencia disponible | `notebooks/05_seleccion.ipynb`; `docs/negocio/finalistas.json`; `docs/seleccion/evaluacion.json`; `docs/seleccion/reproduccion-champion.json` | Decisión previa, evaluación conjunta, umbral a cupo fijo, costos, explicación y reproducción |
| Reproducibilidad y memo | 5 % | parcial | `README.md`; `requirements.lock.txt`; `docs/01-verificacion.json`; `docs/05-verificacion.json`; `docs/PSet3_memo_Puerta_Wilmer.pdf` | Ejecutar 03-06 en kernels nuevos, revisar PDF de hasta 6 páginas y auditar ZIP |
| Criterio del negocio y control estático | adicional | evidencia disponible | `docs/protocolo-congelado.json`; `docs/negocio/finalistas.json` | Dummy, reactiva y control estático son comparaciones distintas; elección por cobertura CV |
| Semanas 2/4/6 y margen para actuar | adicional | evidencia disponible | `notebooks/anexos/06_anticipacion.ipynb`; `docs/anticipacion/resultados.json` | Cohortes propias, cupo compartido sin repetir matrículas, estudiantes únicos y plazos explícitos |
| Ausencia de registros e incremento predictivo | adicional | evidencia disponible | `docs/anticipacion/resultados.json` | Asociación con incertidumbre y comparación E/E+I/L; sin afirmación causal |

## Notebooks

| Archivo | Preparado | Ejecutado | Hash y kernel nuevo verificados |
|---|---|---|---|
| 01_eda.ipynb | True | True | True |
| 02_features.ipynb | True | True | True |
| 03_baseline_candidatos.ipynb | True | True | True |
| 04_tuning.ipynb | True | True | True |
| 05_seleccion.ipynb | True | True | True |
| anexos/06_anticipacion.ipynb | True | True | True |

La existencia de código o de una plantilla no prueba la finalización del experimento. Una respuesta inválida del LLM detiene la fase. La denominación fundacional no afirma rendimiento SOTA en OULAD. 2014J es un benchmark reutilizado y las simulaciones de tutoría no estiman un efecto causal.

Regenerar: `.venv/bin/python scripts/verificar_avance_rubrica.py` desde v2.
