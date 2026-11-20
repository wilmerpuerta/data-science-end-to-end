# Recursos y estructura propuesta

Actualización local de 20-nov-2026. API Docker disponible en localhost:8004 y tablero en localhost:8504; modelos tempranos y fixtures preparados. El MLflow propio está en localhost:5004; el histórico se conserva separado en 5001. Compose único e ingesta hasta OBT verificados. Se verificaron cargas de predicciones a Snowflake con el rol existente. Esta integración no hizo llamadas LLM ni entrenamientos nuevos.

## Recursos

| Recurso | Base disponible | Necesidad antes de ejecutar |
|---|---|---|
| Equipo local | Mac con 32 GiB de RAM y cuatro CPU lógicas. Docker dispone de aproximadamente 8 GiB; el espacio disponible debe medirse antes de nuevas copias o builds. | Evaluar 12-16 GiB para Docker y procurar unos 30 GiB libres como margen inicial, no como requisito rígido. Medir consumo; no eliminar respaldos o volúmenes sin revisión. |
| Datos e infraestructura | Fuentes OULAD, pipeline de PSet 02 y MLflow/Registry de PSet 03. | Compose único y continuidad verificados; Registry clonado con 20.790 archivos (2,84 GB decimales) y OBT idéntica al PSet 02. Preservar snapshots y respaldos. |
| Snowflake | Configuración usada en PSet 02. | Acceso verificado; PREDICCIONES y tablas operativas nuevas en ANALYTICS, sin ampliar permisos. Las consultas usan el warehouse existente; MONITOREO y ALERTAS verificados; los costos monetarios finales siguen pendientes. |
| API y tablero | API y tablero implementados y probados. | FastAPI/Pydantic y Streamlit operativos; dependencias fijadas e imágenes verificadas. |
| GitHub Actions y GHCR | Repositorio existente del curso. | CI/CD y publicación por commit verificados; main integra el proyecto y master conserva su historial. Los workflows activos se instalan en la raíz real del repositorio. |
| Modelo y fixtures | Champions específicos de días 14/28 y champion histórico de día 56, todos en versión 1. | Versiones compatibles y fixtures exportadas verificadas. El candidato reentrenado de semana 4 continúa rechazado; las pruebas unitarias no dependen de servicios. |
| Demo | Infraestructura local. | Grabación de pantalla, guion hasta siete minutos y enlace accesible al profesor. |

Partiendo del HGB, no se prevén GPU ni llamadas nuevas a un LLM. El límite de API autorizado para PSet 03 no constituye un presupuesto nuevo del PSet 04.

## Estructura

La ruta de entrega es `psets/proyecto_final/`, conservando las entregas anteriores como historial; la fuente del PSet 02 es `pset_2/`. La carpeta final ya está creada y contiene el servicio API, dbt/Spark, fixtures y memos históricos. Los servicios y cuatro flujos ya están incorporados; notebooks y comunicación finales permanecen pendientes.

```text
proyecto_final/
├── docker-compose.yml
├── README.md
├── .env.example
├── requirements.txt
├── kestra/
│   ├── ingesta.yml
│   ├── produccion_lotes.yml
│   ├── monitoreo.yml
│   └── reentrenamiento.yml
├── dbt/
├── spark/
├── src/
├── notebooks/
├── api/
├── monitoreo/
├── tests/fixtures/
└── docs/historial/
```

La entrega usará archivos reales y rutas configurables para que el proyecto final pueda ejecutarse sin depender de accesos enlazados a carpetas históricas. Se incluirán `src/pipeline.py`, el código de reentrenamiento y los notebooks requeridos por la rúbrica. Los CSV, diagramas y entregables finales vivirán en `docs/`.

GitHub busca workflows en `.github/workflows/` de la raíz del repositorio, no dentro de un proyecto anidado. Al integrar en el fork del curso se mantendrán los workflows existentes y se fijará el directorio de trabajo del proyecto final. Referencia: [GitHub workflows](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows). La publicación está en `main`, bajo `psets/proyecto/oulad/proyecto_final/`; los workflows activos están en la raíz del fork del curso.

La meta principal acordada es +10 % relativo en cobertura de Fail frente al estático con los mismos cupos. El adelanto de hasta el 30 % de cupos reactivos futuros queda como escenario presupuestario. La disponibilidad actual de tutores, costos por tipo de atención y unidad del cupo deben concretarse antes de convertirla en capacidad operativa; la fracción no es una garantía de bajo FP.
