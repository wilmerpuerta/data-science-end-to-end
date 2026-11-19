# Proyecto final: apoyo académico preventivo

Estado: **primer paso implementado y probado**. Se cerró el objetivo de negocio y se implementó el núcleo de asignación por cohorte. La API HTTP, la integración Docker/Kestra, la simulación final, el monitoreo y el reentrenamiento todavía no están implementados. Esta carpeta aún no es una entrega final ejecutable de extremo a extremo.

## Objetivo acordado

Lograr al menos **10 % de mejora relativa en cobertura de Fail frente al modelo estático, con los mismos cupos**, durante el período en curso. El modelo estático es un control predictivo; Dummy y política reactiva siguen siendo comparadores distintos. No se declara reducción causal de reprobaciones ni equivalencia entre alerta, tutoría propuesta y tutoría realizada.

La cobertura es `TP / Fail de la cohorte base`. La mejora relativa es `(cobertura_longitudinal / cobertura_estatica) - 1`. Con 500 Fail, 200 cupos y 100 TP del estático, la meta exige al menos 110 TP, es decir 22 % de cobertura frente a 20 %; no exige sumar diez puntos porcentuales. Si la cobertura estática es cero, la mejora relativa no se define y se informa el incremento de TP sin certificar la meta.

El adelanto de hasta el 30 % de la atención reactiva futura es un **escenario presupuestario**, no la meta predictiva ni una aprobación de fondos. La bolsa reactiva vigente se conserva separada. La capacidad institucional, las horas docentes y los costos siguen pendientes de validación.

## Estructura y etapa actual

Se utiliza el árbol de la rúbrica, con raíz `proyecto_final/`: `kestra/`, `dbt/`, `spark/`, `src/`, `notebooks/`, `api/`, `monitoreo/`, `tests/fixtures/`, `docs/historial/` y `.github/workflows/`. No se crean carpetas `v2`, `config` o `scripts` en esta entrega. Los archivos requeridos se incorporarán con su implementación, sin presentar archivos vacíos como evidencia funcional.

Archivos implementados en este paso:

- `src/pipeline.py`: preparación original del PSet 03 conservada byte a byte.
- `api/esquemas.py`: tipos y validaciones del núcleo de cupos; el esquema Pydantic de inferencia se añadirá con la API.
- `api/main.py`: priorización y evaluación de la meta. Todavía no expone endpoints FastAPI.
- `tests/test_comportamiento.py`: invariantes de dominio con datos sintéticos.
- `docs/cambios.md`: acuerdos, fuentes, supuestos, implementación y pendientes.
- `requirements.txt`: versiones explícitas de la preparación y del entorno del proyecto.

## Ejecutar el paso implementado

Desde esta carpeta, con Python 3.11 y uv:

```sh
uv run --python 3.11 --no-project --with pytest==8.3.5 python -m pytest -q tests/test_comportamiento.py
```

Para preparar el entorno completo del proyecto cuando se integre la API:

```sh
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

No se necesitan datos reales, claves, Snowflake ni MLflow para estas pruebas. Los ejemplos son sintéticos; los manifiestos y las asignaciones de producción deberán proceder de almacenamiento confiable y las operaciones de cada cohorte requerirán persistencia transaccional.

## Política provisional de cupos

La unidad simulada es matrícula-asignatura y se informa aparte el número de personas únicas. Se mantiene como referencia experimental la capacidad del 10 % por edición, calculada sobre la cohorte elegible completa del día 14. No representa un presupuesto institucional aprobado.

El prototipo permite repartir ese mismo cupo entre días 14 y 28. El valor de prueba es 25 % en semana 2 y el resto en semana 4; no es una política seleccionada ni acordada con la Universidad. Se evaluarán los repartos 0/100, 25/75, 50/50, 75/25 y 100/0 usando solo desarrollo. El orden es riesgo descendente y matrícula ascendente en empates. Una propuesta anterior conserva su reserva de cupo; no se cancela ni se cuenta otra vez por actualizar el score. Un lote parcial no obtiene un presupuesto nuevo.

Los manifiestos de población no se tomarán del cliente HTTP. Los endpoints deberán comprobarlos contra la cohorte registrada y guardar la versión de modelo y política, la ronda, los IDs y el resultado. La idempotencia concurrente y la persistencia aún están pendientes; la función pura actual es determinista y valida la integridad del lote.

## Continuidad y próximos pasos

Se reutilizarán los modelos completos tempranos ya guardados en MLflow por los experimentos del PSet 03, verificando corte, firma, fuentes y métricas. El champion histórico del día 56 no se sustituye ni se utiliza para puntuar semanas 2 o 4. No hace falta repetir el tuning para preparar esas versiones tempranas.

El siguiente paso es integrar las fuentes reutilizadas en este árbol, preparar el servicio por corte y la fixture de CI, y construir la API con `/salud`, `/modelo` y `/predecir`, su esquema Pydantic y sus pruebas. La simulación, los umbrales, el calendario de etiquetas y la aprobación humana de promociones se documentarán antes de ejecutar la evaluación final. Los ocho lotes deberán respetar la disponibilidad temporal; no se presentarán fragmentos de una cohorte como ocho períodos independientes.

Los CSV de predicciones, monitoreo, alertas y reentrenamiento se crearán al ejecutar los procesos reales. Los documentos y el video finales se prepararán con sus evidencias. No se crean salidas vacías para aparentar cumplimiento.

Las carpetas todavía vacías se conservan en Git con `.gitkeep`; son marcadores de estructura y no evidencia de servicios implementados. Se retirarán cuando se incorporen sus archivos funcionales.

La referencia local de programación es `../laboratorios/`, excluida de Git. Sus patrones y su adaptación al proyecto se registran en `docs/cambios.md`; el proyecto no importa código ni datos desde esa carpeta.
