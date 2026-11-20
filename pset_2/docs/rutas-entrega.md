# Rutas de la entrega PSet 2

La carpeta `pset-02/` conserva la versión histórica. La entrega es `pset_2/`; los archivos son reales y la raíz contiene la estructura solicitada. El memo fue revisado el 20-nov para incorporar el calendario activo y las rutas vigentes. El PDF original aprobado se conserva en [historial](historial/PSet2_memo_Puerta_Wilmer_13nov2026.pdf); sus hashes y la revisión están en [registro de revisión](memo-revision-calendario.json). La tabla conserva la correspondencia histórica; los comandos vigentes están en el README.

| Ubicación histórica | Ubicación de entrega |
|---|---|
| `pset-02/scripts/` | `pset_2/kestra/scripts/` |
| `pset-02/ingestion/` | `pset_2/kestra/ingestion/` |
| `pset-02/orchestration/` | `pset_2/kestra/orchestration/` |
| `pset-02/snowflake/` | `pset_2/dbt/snowflake/` |
| `pset-02/docker-compose.cloud.yml` | `pset_2/kestra/docker-compose.cloud.yml` |
| `pset-02/output/pdf/PSet2_memo_Puerta_Wilmer.pdf` | `pset_2/docs/PSet2_memo_Puerta_Wilmer.pdf` |
| `pset-02/output/` (otros informes agregados) | `pset_2/docs/evidencia/` |
| `pset-02/memo-pset2.md`, `enunciado.md`, `rubrica.md` | `pset_2/docs/` |
| Auditoría de PSet 1 usada por el pipeline | `pset_2/docs/referencias/pset1-auditoria-resultados.json` |
| Metadatos de fuentes | `pset_2/docs/referencias/datasets/` |

Los paths internos `/workspace/...` de los contenedores se conservan: Compose monta en ellos las nuevas ubicaciones del host. Las transformaciones SQL, la lógica de features Spark, la ingesta y el contrato de datos conservan sus fuentes. Se ajustan rutas, empaquetado, documentación y auxiliares de validación y reproducción; los informes de nuevas comprobaciones no se confunden con una ejecución cloud histórica.

La copia de entrega usa `pset2-entrega` y puertos `18090/18091`, de modo que no reemplaza el stack histórico `pset2`. Los secretos permanecen en archivos privados o externos; `.env.example` contiene ejemplos ficticios. El respaldo original se conserva en la carpeta privada `backups/` y no se publica.
