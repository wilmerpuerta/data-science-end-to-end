# Guía de usuario del portal de la API

El portal [http://localhost:8004/docs](http://localhost:8004/docs) abre Swagger UI, la consola interactiva para consultar el servicio y enviar lotes de predicción de riesgo de Fail.

El usuario debe abrirlo en el mismo equipo donde se ejecuta Docker. El tablero de gráficos y alertas está en [http://localhost:8504](http://localhost:8504).

## 1. Preparación

La infraestructura y el archivo `.env` deben estar configurados según el [README del proyecto](../README.md). Los comandos de esta guía se ejecutan desde `proyecto_final/`.

Si la API no está levantada, ejecutar:

```sh
docker compose up -d --wait api
```

Para utilizar los modelos registrados debe estar disponible el servidor MLflow configurado. El portal permite comprobar el estado y saber si un resultado utilizó el respaldo.

## 2. Comprobar el servicio

1. Abrir [http://localhost:8004/docs](http://localhost:8004/docs).
2. Desplegar **GET /salud**.
3. Pulsar **Try it out** y luego **Execute**.
4. Comprobar que la respuesta indique `estado: "ok"` y `modelo_cargado: true`.

Ejemplo de respuesta saludable:

```json
{
  "estado": "ok",
  "modelo_cargado": true,
  "respaldo_disponible": true,
  "cortes_disponibles": [14, 28]
}
```

## 3. Consultar el modelo

1. Desplegar **GET /modelo** y pulsar **Try it out**.
2. Introducir `14` en `corte_dias` para semana 2, o `28` para semana 4.
3. Pulsar **Execute**.

La respuesta muestra nombre, versión, alias y `run_id`, además de la procedencia del modelo y el indicador de respaldo. Si se omite el corte, se consultan ambos modelos.

## 4. Preparar un ejemplo válido

La cohorte debe registrarse antes de solicitar predicciones. El registro es una operación administrativa local, no una opción pública del portal.

Para una demostración, ejecutar en la terminal:

```sh
docker compose exec -T api python -m src.datos \
  --ejemplo /app/.local/demo-portal \
  --cohorte-id demo-portal
```

El comando registra 40 matrículas sintéticas y genera estos archivos en el equipo:

```text
proyecto_final/.local/demo-portal/cohorte.json
proyecto_final/.local/demo-portal/semana2.json
proyecto_final/.local/demo-portal/semana4.json
```

Los ejemplos no contienen targets y permanecen separados de los planes de simulación del proyecto. Sus resultados no sirven para estimar desempeño o impacto educativo.

## 5. Solicitar predicciones de semana 2

En macOS, copiar el contenido del archivo al portapapeles:

```sh
pbcopy < .local/demo-portal/semana2.json
```

También se puede abrir el archivo en el editor y copiar todo su contenido.

En el portal:

1. Desplegar **POST /predecir**.
2. Pulsar **Try it out**.
3. Reemplazar todo el contenido de **Request body** por el JSON copiado.
4. Pulsar **Execute**.
5. Comprobar que el código de respuesta sea **200**.

El ejemplo generado sustituye los valores ilustrativos que Swagger muestra inicialmente. Se debe enviar el lote completo, conservando los identificadores registrados y todas las features requeridas.

## 6. Interpretar la respuesta

La respuesta contiene información del lote y una lista `predicciones`, con un resultado por matrícula.

| Campo | Interpretación |
|---|---|
| `nuevas_propuestas` | Cantidad de propuestas que reservan un cupo nuevo en esta ronda. |
| `modelo` | Identificación y procedencia del modelo que produjo el lote. |
| `respaldo` | Si es `true`, ese resultado utilizó la línea base de respaldo. |
| `predicciones[].id_prediccion` | Identificador para rastrear cada resultado. |
| `predicciones[].riesgo_fail` | Probabilidad estimada de Fail. |
| `predicciones[].posicion_en_edicion` | Posición en el ranking de la edición. |
| `predicciones[].decision` | `proponer_tutoria`, `tutoria_ya_propuesta` o `seguimiento`. |
| `predicciones[].accion` | Acción sugerida, sujeta a revisión humana. |
| `predicciones[].consume_cupo_nuevo` | Indica si la propuesta reserva un cupo adicional. |
| `predicciones[].version_modelo` y `predicciones[].run_id` | Versión y corrida del modelo responsable del resultado. |

Las propuestas requieren revisión humana. No equivalen a tutorías realizadas ni a reprobaciones evitadas.

## 7. Ejecutar semana 4

Primero debe completarse la ronda de semana 2. Después, copiar el segundo archivo:

```sh
pbcopy < .local/demo-portal/semana4.json
```

Repetir el envío en **POST /predecir**, reemplazando todo el cuerpo por el JSON de semana 4.

Con este ejemplo sintético y la configuración experimental actual se propone 1 tutoría en semana 2 y 3 adicionales en semana 4: 4 cupos compartidos entre ambas rondas. Estos valores ilustran la política del prototipo; no representan un presupuesto institucional aprobado.

Reenviar exactamente el mismo lote devuelve sus resultados originales, sin consumir cupos adicionales ni volver a puntuarlo. La respuesta conserva la versión que produjo ese lote.

## 8. Consultar métricas

En **GET /metricas**, pulsar **Try it out → Execute** para consultar volumen de solicitudes, predicciones registradas, errores 4xx/5xx y latencias p50/p95.

Estas métricas generales incluyen las pruebas manuales del servicio. Los CSV de los escenarios se filtran por plan. Las llamadas manuales se guardan en el registro local; Kestra realiza la carga de los lotes planificados a Snowflake. El ejemplo `demo-portal` no se incorpora a esos CSV.

## 9. Interpretar errores

| Código | Qué revisar |
|---|---|
| **404** | La cohorte todavía no está registrada desde una fuente confiable. |
| **422** | Campos ausentes, tipos, categorías, rangos o matrículas incompletas, duplicadas o incompatibles. Revisar `detail` en la respuesta. |
| **409** | El corte ya fue procesado con otro contenido, falta la ronda anterior o cambió la política de una cohorte iniciada. |

No cambiar identificadores de cohortes reales para intentar reasignar cupos. Un lote ya procesado requiere revisión administrativa si se necesita corregirlo.

Las solicitudes deben contener la cohorte completa del corte y no deben incluir resultados finales ni targets. Para datos reales, el responsable del pipeline debe preparar y registrar el manifiesto antes del uso del portal.


## Revisión de un modelo reentrenado

Swagger sirve para predicciones y consulta del modelo activo. La aprobación del candidato se realiza en [Kestra](http://localhost:8094), dentro de la ejecución del flujo `pset4.oulad/reentrenamiento`, tarea `aprobacion` en PAUSED. El tablero muestra el historial global de reentrenamientos y el [registro de cambios](cambios.md#resultado-del-reentrenamiento-y-pausa-humana-19-nov-2026) contiene la comparación para revisar.

Antes de reanudar la pausa, revisar cupos iguales, TP, FP, cobertura, exclusión del lote reservado y cumplimiento de la regla. Completar `decision` (rechazar/aprobar), `responsable` y `motivo`. Reanudar registra una decisión real; no debe utilizarse como comprobación de conectividad. El worker verifica esos datos contra Kestra y evita promover un candidato que no cumple la regla. Después de decidir, consultar `GET /modelo`; la API resuelve el alias para cada lote nuevo sin reconstruir la imagen.

El ciclo `reentrenamiento-28-deriva-v1` fue **rechazado por Wilmer Puerta**: añade cuatro TP y la regla exige al menos siete. La pausa ya se reanudó con ese motivo, el flujo terminó en SUCCESS y el champion permanece en versión 1. Para consultar esta decisión, abrir la ejecución `6lcaE9ak8kGv4myx06ZMMw` y sus outputs; no volver a reanudar una ejecución terminada. La meta frente al estático y la regla de reemplazo del champion son comparaciones distintas.


## Operación del respaldo y revisión de necesidades

Cuando `respaldo=true`, `modelo.puntuacion_individual=false` y `criterio_priorizacion=orden_administrativo_matricula`, el servicio prepara una cola administrativa para revisión humana. El mensaje operativo aclara que no hay estimación individual. El valor numérico constante de `riesgo_fail` se conserva por compatibilidad con el Dummy histórico; **no significa que el estudiante tenga riesgo cero**. No usarlo para negar apoyo, sancionar o interpretar causas. El predictor estático usado para la meta +10 % es otro comparador y no es este respaldo.

El operador habilita `PSET4_FORCE_FALLBACK=1` en el `.env` privado y aplica:

```sh
docker compose up -d --no-build --pull never --force-recreate --wait api api_deriva
```

Consultar `/salud` y `/modelo` y enviar únicamente lotes nuevos de cohortes confiables. El cambio se lee al iniciar el proceso: editar `.env` sin recrear los servicios no basta. El respaldo conserva el 10 % por edición, el reparto de rondas y las propuestas previas. No permite saltar validaciones ni reasignar cupos.

Para reactivar el modelo, el responsable revisa la causa, corrige el problema y valida el servicio. Establecer `PSET4_FORCE_FALLBACK=0` y repetir el comando. Las peticiones de lotes ya registrados devuelven su respuesta original, incluso si cambió el interruptor; esto preserva el historial y evita consumir cupos de nuevo. Reenviar un lote no lo convierte en una predicción nueva.

El tutor revisa necesidades, accesibilidad, cobertura de los registros y contactos previos antes de confirmar una propuesta. La ausencia de actividad puede reflejar problemas de datos o formas distintas de estudiar. Quien no recibe propuesta conserva los canales habituales de apoyo y puede solicitar revisión. La coordinación académica resuelve desacuerdos y registra el motivo de cualquier decisión final; la API registra propuestas, no acredita tutorías realizadas ni dispone de un módulo de apelaciones implementado.
