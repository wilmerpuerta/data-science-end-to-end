# Recursos y estructura propuesta

Revisión local de 18-nov-2026. API Docker disponible en localhost:8004; modelos tempranos y fixtures preparados. El servidor MLflow histórico se conserva. No se han ejecutado cargas Snowflake ni nuevas llamadas LLM en esta etapa.

## Recursos

| Recurso | Base disponible | Necesidad antes de ejecutar |
|---|---|---|
| Equipo local | Mac con 32 GiB de RAM y cuatro CPU lógicas. Docker dispone de aproximadamente 8 GiB; disco libre observado: unos 13 GiB. | Evaluar 12-16 GiB para Docker y procurar unos 30 GiB libres como margen inicial, no como requisito rígido. Medir consumo; no eliminar respaldos o volúmenes sin revisión. |
| Datos e infraestructura | Fuentes OULAD, pipeline de PSet 02 y MLflow/Registry de PSet 03. | Integración en Compose único y verificación de continuidad; preservar snapshots y respaldos. |
| Snowflake | Configuración usada en PSet 02. | Confirmar acceso y créditos; definir esquema y permisos para PREDICCIONES, MONITOREO y evidencia. No se ha autorizado ni ejecutado consumo nuevo en esta preparación. |
| API y tablero | API implementada y probada; tablero pendiente. | FastAPI/Pydantic y Streamlit como propuesta de tablero; dependencias fijadas y contenedores. |
| GitHub Actions y GHCR | Repositorio existente del curso. | Configurar CI/CD, permisos de publicación y rama main sin perder master. Los workflows activos se instalan en la raíz real del repositorio. |
| Modelo y fixtures | Champion HGB día 56 y antecedentes de cortes tempranos. | Versiones operativas compatibles con los cortes que asignen cupos; exportación y muestra fija para CI; no depender del servidor local para pruebas unitarias. |
| Demo | Infraestructura local. | Grabación de pantalla, guion hasta siete minutos y enlace accesible al profesor. |

Partiendo del HGB, no se prevén GPU ni llamadas nuevas a un LLM. El límite de API autorizado para PSet 03 no constituye un presupuesto nuevo del PSet 04.

## Estructura

La ruta local propuesta es `psets/proyecto_final/`, conservando `pset-01/` a `pset-04/` como etapas e historial. La carpeta final ya está creada y contiene el servicio API, dbt/Spark, fixtures y memos históricos. Los servicios y sus archivos se incorporarán al implementarlos; el árbol siguiente es la estructura objetivo de la rúbrica.

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

GitHub busca workflows en `.github/workflows/` de la raíz del repositorio, no dentro de un proyecto anidado. Al integrar en el fork del curso se mantendrán los workflows existentes y se fijará el directorio de trabajo del proyecto final. Referencia: [GitHub workflows](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows). La ubicación definitiva de publicación se documentará antes de cambiar ramas o automatizaciones del repositorio.

La meta principal acordada es +10 % relativo en cobertura de Fail frente al estático con los mismos cupos. El adelanto de hasta el 30 % de cupos reactivos futuros queda como escenario presupuestario. La disponibilidad actual de tutores, costos por tipo de atención y unidad del cupo deben concretarse antes de convertirla en capacidad operativa; la fracción no es una garantía de bajo FP.
