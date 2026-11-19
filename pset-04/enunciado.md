# PSet 04: enunciado extraído

Fuente: [rúbrica original](CD-PSet-4.pdf). Extracción textual; el PDF conserva la maquetación oficial.

SHA-256 del original: `f354204512cfd1c73268936608b5de3fcd64be85367ac10f24b995af1babe7c7`.

## Página 1

PSet #4: Despliegue, Monitoreo y Comunicación del
                     Modelo

                                  Ciencia de Datos

El objetivo es cerrar el roadmap de un proyecto de Ciencia de Datos:

Formulación → Pipeline de datos → OBT → Experimentación → Modelo registrado → API
de servicio de inferencia → Pruebas y CI/CD → Predicciones registradas → Monitoreo →
Alertas → Reentrenamiento → Resultado de negocio → Presentación ejecutiva

Este PSet es el Proyecto Final.



1. Patrón de despliegue: ¿batch u online?

Decide cómo llegan las predicciones a quien actúa sobre ellas. Justifica tu elección con:

    ●​ La latencia que exige la decisión que definiste en el PSet #1: ¿en cuánto tiempo debe
       estar disponible la predicción?
    ●​ La frecuencia con la que llegan nuevos datos.
    ●​  El volumen de predicciones por día.
    ●​  El costo de actuar con una predicción desactualizada.

                                             ¿Qué patrón
       Criterio                 Caso
                                                        favorece?
Latencia de la       La reunión de inventario es los
                                                    Batch
decisión              lunes

Construyes la API de la sección 2 sin importar tu elección. Si elegiste batch, el flujo de Kestra
de la sección 5 genera las predicciones de cada período y las guarda en Snowflake. Si elegiste
la opción online, ese mismo flujo simula el tráfico de producción hacia la API.

Explica también qué tendría que cambiar en el caso de uso para que el otro patrón fuera el
adecuado.

2. Servicio de predicción

Expón el modelo como una API con FastAPI, empaquetado en un contenedor de Docker y
agregado a tu docker-compose.yml junto a Kestra, Spark y MLflow.

La API debe tener como mínimo estos endpoints:

## Página 2

Endpoint                  Qué devuelve
GET /salud    Estado del servicio y si el modelo cargó correctamente
GET /modelo  Nombre, versión, alias y run_id del modelo en uso
POST /        Predicción, decisión, versión del modelo e id de la
predecir       predicción

Requisitos:

    ●​  El modelo se carga desde models:/<proyecto>-modelo@champion. Cambiar de
       versión no debe requerir reconstruir la imagen.
    ●​ La entrada se valida mediante un esquema de Pydantic que coincide con la firma
       registrada en MLflow: tipos, rangos y categorías permitidas. Una entrada inválida
       devuelve un 422 con un mensaje que indica qué campo falló.
    ●​  Si tu problema es de clasificación, el servicio aplica el umbral de decisión que elegiste
      en el PSet #3 y devuelve la probabilidad y la decisión.
    ●​ La respuesta incluye la acción del PSet #1, no solo el número. Por ejemplo:
     {"probabilidad": 0.81, "decision": "contactar", "version_modelo":
       3}.
    ●​ Cada predicción queda registrada con su id, timestamp, entradas, salida, versión del
      modelo y latencia en milisegundos, en una tabla PREDICCIONES de Snowflake (directo
      o mediante una carga periódica con Kestra).

¡Una predicción que no puedes rastrear hasta la versión que la produjo no puede auditarse!

3. Pruebas automáticas e integración continua

Escribe pruebas con pytest en el directorio tests/.

    1.​ Contrato: una entrada válida devuelve 200 con el esquema esperado. Un campo
        faltante, un tipo incorrecto y una categoría desconocida devuelven un 422.
    2.​ Modelo: el modelo cargado reproduce la métrica registrada en MLflow en una muestra
          fija guardada en el repositorio, dentro de una tolerancia que justifiques.
    3.​ Comportamiento de negocio: al menos 2 pruebas de comportamiento que tu modelo
      debe cumplir según tu dominio. Por ejemplo: aumentar los días de atraso de una factura
      no debe reducir su probabilidad de impago.
    4.​ Respaldo (fallback): si el modelo no carga, el servicio responde con la línea base del
      PSet #3 (dummy o de negocio) e indica en la respuesta que se usó el respaldo.

Configura GitHub Actions (ci.yml) para que las pruebas se ejecuten en cada push y en cada
pull request: instalar dependencias, construir la imagen y ejecutar pytest.

En CI no tienes acceso a tu servidor de MLflow. Usa una copia del modelo exportada con
mlflow.sklearn.save_model en tests/fixtures/.

## Página 3

4. Versionado y registro del modelo

Usa el Model Registry del PSet #3 como fuente de verdad del modelo en producción:

    ●​ Regla de promoción: escribe la regla según la cual un challenger reemplaza al
      champion. Debe usar la métrica de negocio y la variación entre pliegues. Por ejemplo: el
       challenger se promueve si supera al champion en la métrica de negocio por más de una
       desviación estándar de la CV, evaluados ambos en la misma ventana de datos.
    ●​  Rollback: demuestra que puedes volver a la versión anterior moviendo el alias, sin
        reconstruir la imagen, y que /modelo refleja el cambio.
    ●​  Trazabilidad: cada fila de PREDICCIONES indica qué versión del modelo la generó.

5. Simulación de producción

Tu modelo no recibe tráfico de producción, así que lo simulas:

    1.​ Toma los datos posteriores a la fecha de corte del entrenamiento. Si no tienes datos
        posteriores, usa el conjunto de prueba ordenado cronológicamente.
    2.​ Divídelos en al menos 8 lotes que correspondan a períodos sucesivos (días, semanas o
      meses, según el horizonte del PSet #1).
    3.​ Construye un flujo de Kestra produccion_lotes.yml que, por cada lote: lea el lote
      de Snowflake, genere las predicciones (llamando a la API o puntuando en lote), las
      guarde y, cuando el target del lote ya esté disponible, lo una con sus predicciones para
        calcular el desempeño.

Respeta el horizonte: el target de un lote llega después del horizonte de predicción, no al
mismo tiempo que la predicción.

Además, construye al menos un lote con deriva inducida intencionalmente. Por ejemplo:
desplaza la distribución de una feature importante, cambia la proporción de una categoría o
altera la relación entre una feature y el target. Documenta exactamente qué alteraste. Con ese
lote demuestras que tus alertas y tu reentrenamiento funcionan.

Si tus datos no están ordenados cronológicamente, explica cómo construiste los lotes y qué
limita tus conclusiones.

6. Monitoreo

6.1 Métricas de sistema, de modelo y de datos
   Tipo                              Métricas mínimas
Sistema    Latencia p50 y p95, tasa de errores (4xx y 5xx), volumen de solicitudes
             Distribución de las predicciones, tasa de cada decisión, métrica técnica y
Modelo
            métrica de negocio por lote (cuando llega el target)

## Página 4

Porcentaje de faltantes por feature, valores fuera de rango, categorías no vistas
Datos
          en entrenamiento

6.2 Deriva de datos y deriva conceptual

Compara cada lote contra la distribución de entrenamiento para detectar deriva de datos:

    ●​  Calcula el PSI por feature y justifica los umbrales.
    ●​  Aplica la prueba de Kolmogorov-Smirnov a las variables numéricas y la prueba de chi-
      cuadrado a las categóricas. Decide la alerta con el PSI y usa la prueba estadística como
       respaldo.

Para detectar deriva conceptual, compara la métrica técnica de cada lote con el promedio y la
desviación de la CV del PSet #3.

Completa esta tabla con la acción que corresponde a cada caso en tu proyecto:

Entradas Desempeño      Diagnóstico       Acción
                       Deriva de datos sin
Cambian Se mantiene
                       impacto
                       Deriva de datos con
Cambian Cae
                       impacto
Estables Cae          Deriva conceptual

6.3 Alertas

Define cada alerta con esta plantilla:

                                        Quién la
     Métrica     Umbral Ventana Severidad                 Acción
                                                recibe
PSI de                                      Equipo   Revisar fuente y evaluar
               > 0.25  1 lote      Alta
monto_factura                           de datos reentrenamiento

Construye un flujo de Kestra en monitoreo.yml que se ejecute después de cada lote, calcule
las métricas, las guarde en una tabla MONITOREO de Snowflake y dispare alertas (en el log de
Kestra, por correo o por Slack).

El lote con deriva inducida debe disparar la alerta, y los lotes sin alterar no deben dispararla. Si
aparecen falsas alarmas, documéntalas y explica cómo ajustarías el umbral.

6.4 Tablero

Construye un tablero (Grafana, Streamlit o Metabase) que muestre, lote por lote, las métricas
de sistema, de modelo y de deriva, con las alertas y los reentrenamientos marcados.

## Página 5

7. Reentrenamiento y despliegue continuo

7.1 Disparador

Define qué dispara el reentrenamiento y justifícalo con tu monitoreo:

    ●​ Por desempeño: la métrica técnica o de negocio de un lote queda por debajo de un
      umbral durante N lotes consecutivos. Por ejemplo: el MAE supera el promedio de la CV
     más dos desviaciones durante 2 lotes.
    ●​ Por calendario: cada cierto número de lotes, aunque no haya alertas.

La deriva de datos sin caída de desempeño no dispara el reentrenamiento.

El reentrenamiento solo usa lotes cuyo target ya llegó.

7.2 Tubería de reentrenamiento

Construye un flujo de Kestra reentrenamiento.yml que:

    1.​ Se dispare por la alerta de la sección 6.3 o por calendario.
    2.​ Arme el conjunto de entrenamiento con una ventana de datos que justifique: todo el
        histórico, una ventana móvil o el histórico con mayor peso en los lotes recientes.
    3.​ Reentrene con la misma preparación de src/pipeline.py y con los hiperparámetros
       del champion, sin repetir el tuning.
    4.​ Registre la corrida en MLflow con el tag fase=reentrenamiento y el motivo del
       disparo.
    5.​ Registre el nuevo modelo como versión en el Model Registry con el alias
      'challenger'.
    6.​ Evalúe champion y challenger sobre el mismo lote etiquetado más reciente, que
      ninguno de los dos vio en entrenamiento.
    7.​ Aplique la regla de promoción de la sección 4 y deténgase en una tarea en pausa
       hasta que una persona la apruebe o la rechace.
    8.​ Si se aprueba, mueva el alias 'champion' al modelo nuevo. Si se rechaza, deje el
      champion intacto y registre el motivo.

La API toma el nuevo champion sin reconstruir la imagen.

7.3 Despliegue continuo del código

Agrega un flujo de GitHub Actions en cd.yml que, en cada merge a main con las pruebas en
verde, construya la imagen de la API y la publique en GitHub Container Registry, usando el
hash del commit como tag. Tu docker-compose.yml usa esa imagen.

El código se despliega automáticamente, pero el modelo no. Explica en el documento por qué.

## Página 6

7.4 Evidencia

Ejecuta el ciclo completo sobre el lote con deriva inducida: alerta → reentrenamiento →
challenger → comparación → decisión.

Si el challenger no supera al champion, documenta la comparación y el motivo del rechazo.

8. Ética operativa y criterios de retirada

    1.​ Desempeño por subgrupo: calcula la métrica técnica y la tasa de cada decisión para
        al menos un subgrupo relevante de tu dominio (región, segmento, tipo de cliente, canal,
         etc.). Explica si la diferencia entre los subgrupos es aceptable tanto para el negocio
     como para las personas afectadas.
    2.​ Costo del error: identifica a la persona o al área que asume cada tipo de error del
      modelo: un falso positivo y un falso negativo, o una sobreestimación y una
       subestimación.
    3.​ Criterios de retirada: escribe al menos 3 condiciones observables bajo las cuales el
      modelo se ajusta o se retira de producción, cada una con su métrica, umbral y
       respuesta. Por ejemplo: si la métrica de negocio queda por debajo de la línea base de
       negocio durante 2 lotes seguidos, aun después de reentrenar, el servicio pasa al modo
      de respaldo.
    4.​ Interruptor de respaldo: implementa un interruptor (variable de entorno o endpoint
       protegido) que permita a la API utilizar la regla de negocio en lugar del modelo.
      Demuestra que funciona.
    5.​ Supervisión humana: revisa el juicio humano que definiste en el PSet #1 y decide si
       sigue siendo adecuado según el comportamiento del modelo. Si cambió, justifica el
       cambio.

9. Resultado de negocio

Con las predicciones de la simulación, calcula lote por lote la métrica de negocio y compárala
contra:

    ●​ La línea base de negocio (la regla o el proceso actual).
    ●​ No hacer nada, si aplica a tu caso.

Marca en qué lote ocurrió cada reentrenamiento y qué efecto tuvo.

Responde la pregunta del PSet #1: ¿valió la pena actuar según la predicción? Si el modelo no
supera a la línea base, dilo y explica por qué.

## Página 7

10. Proyecto end to end

Reúne los PSet #1 a #4 en un solo proyecto:

    1.​ Un repositorio: todo el código del proyecto reside en la carpeta proyecto_final/,
      con la estructura descrita en la sección Repositorio. Incluye la ingesta, dbt y Spark del
      PSet #2, los notebooks y la carpeta src/ del PSet #3, y lo construido en este PSet.
    2.​ Un docker-compose.yml: levanta Kestra, Spark, MLflow, la API y el tablero con un solo
      comando.
    3.​ Un README: reproduce el proyecto desde cero, en este orden: fuente → Raw →
      Bronze → Silver → Gold → OBT → EDA y modelo → registro → API → simulación →
       monitoreo → reentrenamiento.
    4.​ Correcciones: corrige las observaciones que recibiste en los PSet #1, #2 y #3. Registra
      en docs/cambios.md cada observación, qué cambiaste y en qué archivo.
    5.​ Decisiones actualizadas: si cambiaste una decisión de un PSet anterior (target,
       horizonte, métrica, umbral, fuente de datos, grano de la OBT), actualízala en todo el
       proyecto y regístrala en docs/cambios.md.
    6.​ Trazabilidad: una predicción de la tabla PREDICCIONES debe poder rastrearse hasta la
       versión del modelo, su run_id, el snapshot de la OBT con el que se entrenó y las tablas
      Gold de las que se derivó.
    7.​ Coherencia: las cifras del pitch del PSet #1 se reemplazan por las de la sección 9.

11. Comunicación

Comunicas el proyecto completo a dos audiencias distintas.

Audiencia técnica: el documento técnico descrito a continuación.

Audiencia ejecutiva: una presentación de 10 a 12 diapositivas. La audiencia es el
patrocinador al que le hiciste el pitch del PSet #1: no sabe qué son ni un PSI ni un champion.

La presentación cubre el proyecto desde la formulación hasta la operación y debe responder:

    ●​ Qué problema resolvimos y para quién.
    ●​ Qué cambió en la decisión.
    ●​ Cuánto valor generó, con una cifra.
    ●​ Qué riesgos quedan y cómo se vigilan.
    ●​ Qué recomiendas: escalar, ajustar o retirar el modelo, y qué se necesita para hacerlo.

Ninguna diapositiva muestra una métrica técnica sin su consecuencia de negocio. La
arquitectura va en un solo diagrama simple, y el detalle técnico va en anexos.

## Página 8

Video de demostración: tu infraestructura corre en tu máquina local y yo no tengo acceso a
ella. Graba un video de máximo 7 minutos que muestre:

    ●​  Levantar la infraestructura con docker-compose.
    ●​ Una ejecución de la ingesta hasta la OBT: Kestra, dbt y Spark.
    ●​ Una predicción válida y una entrada inválida rechazada.
    ●​  El rollback de versión.
    ●​  El lote con deriva dispara una alerta.
    ●​  El ciclo de reentrenamiento con la pausa de aprobación y el cambio de modelo.
    ●​  El interruptor de respaldo.

El enlace del video de la DEMO debe estar en el documento técnico.



Documento técnico

Entrega un documento técnico del proyecto completo de hasta 12 páginas, sin contar los
anexos.

El documento debe explicar tus decisiones, NO definir las herramientas ni los conceptos vistos
en clase.

Debe contener:

1. Problema y formulación​
La versión final de la formulación del PSet #1: problema, unidad, target, horizonte, métrica
técnica, métrica de negocio, línea base, umbral de decisión y juicio humano.

2. Arquitectura end-to-end​
Un diagrama del proyecto completo, desde la fuente hasta la API, el monitoreo y el
reentrenamiento, junto con la explicación del flujo.

3. Datos​
 Ingesta, retries y backfill; problemas de calidad en sus métricas y decisiones; capas Bronze,
Silver y Gold; star schema con el grano de la tabla de hechos; OBT con su grano y la validación
de joins; batch vs. streaming.

4. Modelado​
 Hallazgos de la EDA que cambiaron el experimento, features y plan de prueba para demostrar
que no presentan fuga, esquema de validación, resultados de líneas base y candidatos, tuning
y modelo ganador con su run_id y versión.

5. Despliegue​
 Patrón de despliegue, servicio de predicción con un ejemplo de solicitud y respuesta, qué

## Página 9

cubren las pruebas, qué queda fuera de CI y captura de GitHub Actions en verde con la imagen
publicada.

6. Versionado, reentrenamiento y despliegue continuo​
 Regla de promoción, disparador y ventana de reentrenamiento, evidencia del rollback y del
ciclo completo sobre el lote con deriva, y por qué el modelo no se promueve automáticamente.

7. Simulación, monitoreo y alertas​
 Construcción de los lotes, qué alteraste en el lote con deriva, tabla de alertas, gráficos lote por
lote y diagnóstico del tipo de deriva detectada.

8. Ética y retirada​
 Análisis por subgrupo, costo de cada error, criterios de retirada e interruptor de respaldo.

9. Resultado de negocio​
La métrica de negocio lote por lote frente a la línea base, con los reentrenamientos marcados,
en tabla y en gráfico.

10. Limitaciones y siguientes pasos​
Lo que no se pudo resolver y qué harían primero si el proyecto continuara.

Anexos​
 Los memos de los PSets #1, #2 y #3, y docs/cambios.md.



Repositorio

El repositorio debe permitir reproducir el proyecto completo, desde el código fuente hasta el
reentrenamiento.

La estructura del repositorio:


  None‎
  proyecto_final/
  ├── docker-compose.yml
  ├── .env.example
  ├── requirements.txt
  ├── README.md
  ├── .github/
  │   └── workflows/
  │       ├── ci.yml
  │       └── cd.yml

## Página 10

├── kestra/
│   ├── ingesta.yml
│   ├── produccion_lotes.yml
│   ├── monitoreo.yml
│   └── reentrenamiento.yml
├── dbt/
├── spark/
├── src/
│   ├── datos.py
│   ├── pipeline.py
│   └── reentrenar.py
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_features.ipynb
│   ├── 03_baseline_candidatos.ipynb
│   ├── 04_tuning.ipynb
│   ├── 05_seleccion.ipynb
│   ├── 06_simulacion_produccion.ipynb
│   └── 07_analisis_monitoreo.ipynb
├── api/
│   ├── Dockerfile
│   ├── main.py
│   └── esquemas.py
├── monitoreo/
│   ├── deriva.py
│   └── alertas.py
├── tests/
│   ├── fixtures/
│   ├── test_contrato.py
│   ├── test_modelo.py
│   └── test_comportamiento.py
└── docs/
    ├── arquitectura.png
    ├── modelo_dimensional.png
    ├── cambios.md
    ├── corridas.csv

## Página 11

├── predicciones.csv
      ├── monitoreo.csv
      ├── alertas.csv
      ├── reentrenamientos.csv
      ├── PSet4_memo_<apellido_1>_<apellido_2>.pdf
      ├── PSet4_presentacion_<apellido_1>_<apellido_2>.pdf
      └── historial/
         ├── PSet1_memo_<apellido_1>_<apellido_2>.pdf
         ├── PSet1_pitch_<apellido_1>_<apellido_2>.pdf
         ├── PSet2_memo_<apellido_1>_<apellido_2>.pdf
         └── PSet3_memo_<apellido_1>_<apellido_2>.pdf


Exporta a docs/ en formato CSV:

    ●​ Las tablas PREDICCIONES y MONITOREO.
    ●​  El registro de alertas.
    ●​ Todas las corridas del experimento en corridas.csv, incluidas las de reentrenamiento
       (con mlflow.search_runs).
    ●​ Las corridas de reentrenamiento por separado en reentrenamientos.csv (filtrando
       por fase='reentrenamiento').

El README.md debe explicar cómo levantar la infraestructura, cómo configurar las variables de
entorno y la conexión a Snowflake, cómo ejecutar las pruebas y el orden de ejecución completo
de la sección 10.

Antes de entregar, ejecuta cada notebook primero con Restart y luego con Run All. Se calificará
con la salida guardada.

¡No subas contraseñas, tokens ni credenciales al repositorio!



Entregables

   Entregable                               Requisito
                  Proyecto completo de los PSets #1 a #4, con README reproducible
Repositorio
                desde cero
Infraestructura   Un docker-compose.yml con Kestra, Spark, MLflow, API y tablero
              En Docker, carga el modelo por alias, valida entradas y registra
API
                   predicciones

## Página 12

Pruebas en verde en cada push y pull request, imagen publicada en
CI/CD
                cada merge a main
Simulación       Mínimo 8 lotes, uno con deriva inducida
Monitoreo         Tablas en Snowflake, alertas funcionando y tablero
                    Flujo en Kestra disparado por métrica, con challenger y aprobación
Reentrenamiento
                manual
Correcciones     docs/cambios.md con las observaciones de los PSets #1 a #3
               docs/corridas.csv, docs/predicciones.csv, docs/
Evidencia        monitoreo.csv, docs/alertas.csv, docs/
               reentrenamientos.csv
Video            Demostración de máximo 7 minutos
Documento
                  Proyecto completo, máximo 12 páginas
técnico
Presentación
                10 a 12 diapositivas
ejecutiva

Nombre del documento: PSet4_memo_<apellido_1>_<apellido_2>.pdf

Nombre de la presentación: PSet4_presentacion_<apellido_1>_<apellido_2>.pdf



Rúbrica

                                 Criterio                            Peso
Patrón de despliegue y servicio de predicción                   15%
Pruebas automáticas y CI/CD                              10%
Reentrenamiento, promoción y rollback                        10%
Simulación de producción y métricas de monitoreo                10%
Deriva de datos, deriva conceptual y alertas                    10%
Ética operativa, criterios de retirada y respaldo                   10%
Resultado de negocio y presentación ejecutiva                   15%
Integración end-to-end, correcciones, reproducibilidad y documento
                                                  20%
técnico

Total                                                 100%
