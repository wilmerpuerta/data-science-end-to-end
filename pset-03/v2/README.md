# PSet 3 · Reconstrucción v2

El respaldo privado completo de v1 fue verificado y restaurado de prueba. Los entregables originales siguen en `pset-03/`; esta reconstrucción se desarrolla por separado en `pset-03/v2/`. Los resultados previos no se presentan como corridas nuevas.

Estado actual: API verificada con prueba sintética y lote real de 32 consultas; EDA y preparación ejecutados en kernel nuevo. El protocolo operativo v2.1 está congelado; las fases definitivas se ejecutan mediante scripts/ejecutar_estudio.py. El estado actualizado está en docs/estado-v2.json. Consultar `docs/estado-v2.json`, `docs/paso-a-paso-v2.md` y `docs/prompting.md`. No hay un nuevo ganador ni un memo v2 terminado.

## Diseño y criterio del negocio

Mismo snapshot, partición y cinco folds persistidos por estudiante. El criterio principal es la cobertura de Fail con cupo del 10 % por edición en validación, con media y desviación entre folds; AP, Brier, log-loss, costos y tiempos complementan la decisión. La comparación incluye cinco familias tabulares y un GPT generativo mediante prompting. Dummy y proceso reactivo son las dos baselines; el control con variables estáticas se ajusta separadamente para medir el aporte longitudinal.

Los ejemplos del GPT proceden solo del train-fold y su cantidad se declara; no se presenta prompting como entrenamiento de pesos con todas las filas. Los seis modelos se evalúan sobre todas las mismas filas de validación. La métrica de entrenamiento usa una muestra idéntica de 1.000 filas por train-fold para todos, identificada como tal. Si el LLM queda entre los tres mejores por negocio, participa en el tuning de al menos 30 configuraciones.

2014J ya fue observado en v1: se declara benchmark retrospectivo reutilizado. Las elecciones de v2 se fijarán antes de una única nueva evaluación final conjunta. No se afirmará independencia inédita de la prueba. Las semanas 2, 4 y 6 tendrán cohortes propias, restricciones temporales y un presupuesto compartido sin repetir matrículas; sus resultados operativos no se confunden con un efecto causal de las tutorías.

## Entorno

Desde la raíz del repositorio, usar el mismo servidor Docker con volúmenes persistentes, sin reinicializarlo:

```sh
docker compose -f pset-03/docker-compose.yml up -d mlflow
```

El tracking usa `http://127.0.0.1:5001` y el experimento separado `oulad-apoyo-academico-v2`. La versión 2 tiene su propio entorno Python 3.11 y las dependencias exactas en `requirements.lock.txt`. El snapshot y las particiones verificadas son privados; `src/datos.py` no consulta Snowflake en vivo. Para reconstruir las fuentes, seguir las instrucciones Snowflake/OBT de `pset-02/README.md` y la exportación de `pset-03/scripts/exportar_snapshot.py` con credenciales locales; una extracción nueva produce otra identidad y exige otro protocolo.

## API OpenAI

La clave está en `.secrets/pset3-openai.env` de la raíz, excluida de Git, y nunca debe aparecer en el chat, notebooks o entregables públicos. El presupuesto total autorizado es USD 10, incluyendo pruebas de conectividad, candidatos, tuning y evaluación final; el cliente reserva costo antes de cada solicitud y conserva reservas ante fallos ambiguos. ChatGPT y API tienen facturación independiente. El modelo configurado es `gpt-6-luna`, con Responses, JSON Schema, razonamiento none y sin herramientas. La reproducción exacta de un LLM usa respuestas archivadas, no una promesa de determinismo del proveedor.

Comprobar acceso y saldo mediante una prueba sintética pequeña, sin matrículas del estudio:

```sh
pset-03/v2/.venv/bin/python pset-03/v2/scripts/preflight_openai.py
```

Si devuelve `insufficient_quota`/`credit_balance_exhausted`, activar créditos o facturación de API antes del estudio. No reemplazarlo con salidas ficticias ni aumentar el tope autorizado.

## Orden de ejecución

1. `01_eda.ipynb` y `02_features.ipynb` ya ejecutados con salidas nuevas y verificaciones por hash.
2. Completar preflight; revisar/congelar el código y el protocolo antes de cualquier clasificador del estudio mediante `scripts/congelar_protocolo.py`.
3. `scripts/ejecutar_comparacion.py`: primero dos baselines y después seis candidatos, mismos folds; etapa todavía no ejecutada.
4. `scripts/ejecutar_tuning.py`: tres familias mejores por negocio, al menos 30 configuraciones únicas cada una, con corridas hijas; etapa todavía no ejecutada.
5. Completar controles estáticos equivalentes, ablación predictiva, anticipación y congelación de finalistas, antes de la evaluación final.
6. Completar prueba conjunta, Registry y reproducción exacta en kernel nuevo; generar los notebooks 03–05 con salidas reales, memo legible de hasta seis páginas, CSV y auditoría literal.

Los scripts del estudio rechazan fuentes sin commit y protocolo no congelado. Los espacios de las seis búsquedas ya están en `config/espacios-tuning.json`. El cierre no se declara completo mientras falte un candidato, un tuning obligatorio o un entregable. La carpeta v2 no sustituye todavía la entrega original aprobada.

## Ejecución autónoma autorizada

El coordinador `scripts/ejecutar_estudio.py` ejecuta comparación, tuning, ablación, controles y decisión de negocio, anticipación, selección/Registry y reproducción. Actualiza `docs/estado-v2.json` cada diez segundos y guarda logs por fase en `.local/definitivo-*.log`. Se detiene al primer error y no reintenta llamadas ni aumenta el tope de USD 10. Antes de reanudar una fase con `--desde`, inspeccionar su log y verificar sus checkpoints; nunca lanzar un segundo coordinador. Mantener la computadora encendida durante las ejecuciones.

El primer intento está conservado en `.local/attempts/intento_1` y en el experimento `oulad-apoyo-academico-v2-intento1`. Se interrumpió por un límite de salida insuficiente del LLM, antes de obtener métricas de validación para esa familia. El intento definitivo usa un experimento nuevo con el nombre original y vuelve a ejecutar todas las familias. Los USD 10 incluyen el gasto del intento interrumpido.

La revisión v2.1 admite hasta 160 tokens de salida por consulta más 256 de margen, pide cuatro decimales por probabilidad, utiliza hasta ocho peticiones concurrentes de lotes de 32 y archiva las respuestas incompletas con su cobro. La reserva incluye la tarifa máxima de escritura de caché; la conciliación incorpora sus primas sin aplicar descuentos por lectura de caché. Estos cambios técnicos quedaron versionados y congelados antes del nuevo estudio.

## Recuperación de envolturas de respuesta

La API puede entregar un objeto íntegro precedido por texto ajeno al JSON. `scripts/recuperar_respuestas_llm.py` extrae un único objeto completo con prefijo acotado, exige todas las consultas/clases, rechaza claves duplicadas y verifica rangos y sumas. Conserva la respuesta original y no cambia, rellena ni vuelve a generar probabilidades. El coordinador puede continuar desde esa caché verificada, con un máximo de diez recuperaciones por fase; no reenvía el lote fallido al LLM. Respuestas truncadas, incompletas, irreconciliables o reservas de cobro incierto detienen el proceso. Cada recuperación queda registrada en `docs/recuperacion-respuestas-llm.json` y en el estado de ejecución. El consumo global incluye las peticiones fallidas; los tiempos y cargos nuevos de una reanudación pueden beneficiarse de la caché y se deben distinguir del costo acumulado.

## Enmienda operativa para rechazos transitorios

`docs/enmienda-transporte.json` registra una excepción explícita a la regla inicial de no reintentar: un solo reintento por hash para HTTP 400 `invalid_prompt`/`invalid_request_error` confirmado sin inferencia ni cobro, con un máximo de veinte recuperaciones por fase. Se observó y documentó que exactamente la misma petición rechazaba una vez y luego devolvía probabilidades válidas. No se cambian prompts, datos, scores, folds ni decisiones. No se reintentan respuestas con probabilidades válidas, errores de cuota/autenticación o cobros inciertos. Cada llamada conserva la reserva presupuestaria; ante otro rechazo del mismo hash, el proceso se detiene. Esta enmienda se declara antes de los nuevos reintentos y queda identificada en el estado, sin reescribir el protocolo predictivo histórico.
