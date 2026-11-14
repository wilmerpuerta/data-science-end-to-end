# Encargo para Codex en VS Code: repositorio `psets` y entrega revisada del PSet 1

**Autor:** Wilmer Puerta  
**Fecha de preparación:** 12 de noviembre de 2026

## A. Solicitud ejecutable

Lee este documento completo y las instrucciones aplicables de la carpeta abierta. Organiza un único proyecto académico en un repositorio local llamado `psets`, con cuatro etapas: `pset-01`, `pset-02`, `pset-03` y `pset-04`. Reconstruye los entregables revisados del PSet 1; prepara la documentación y estructura de continuidad del PSet 2; conserva sus rúbricas. El dataset compartido estará en `datasets/` en la raíz.

Ejecuta las tareas autorizadas hasta generar y verificar los archivos. Conserva respaldo de versiones existentes y no sobrescribas cambios de contenido ajenos sin reconciliarlos. No necesitas el historial de otro chat: este documento contiene el contexto, las decisiones actualizadas, las tres ideas y las rúbricas.

**Prioridad de instrucciones:** este bloque A–K define las rutas, nombres, alcance y organización actuales. El bloque L contiene el material de proyecto y sus actualizaciones; úsalo como contenido, adaptando referencias de rutas o formatos a A–K. El bloque M conserva el enunciado del PSet 2 y N su rúbrica; son requisitos de la siguiente entrega, no evidencia de implementación. O contiene la rúbrica del PSet 1. Conserva la distinción entre texto del profesor y decisiones del proyecto.

### Cómo identificar la raíz

- Trabaja en el `psets/` abierto en VS Code. No interpretes `/psets` como una carpeta que deba crearse directamente en la raíz del sistema operativo.
- Si la carpeta abierta ya se llama `psets`, no crees un segundo `psets/` dentro.
- Si está abierta su carpeta contenedora y no existe `psets/`, créalo allí. Si la ubicación sigue ambigua, pregunta solo por esa ruta y continúa preparando contenidos independientes.
- Nunca codifiques `/Users/wilmer.puerta/...` ni `Downloads` como dependencia del proyecto final. La fuente oficial local será `datasets/`.
- No inicialices un repositorio Git dentro de otro sin necesidad. Inspecciona primero. La publicación en GitHub la realizará el usuario; no crear repositorios remotos, hacer push ni enviar mensajes como parte de este encargo.

## B. Estructura objetivo

```text
psets/
├── README.md
├── .gitignore
├── datasets/
│   ├── README.md
│   ├── manifest.json                  # si los archivos se han auditado
│   ├── studentInfo.csv                # los aporta el usuario; no versionados
│   ├── studentRegistration.csv
│   ├── courses.csv
│   ├── vle.csv
│   └── studentVle.csv
├── pset-01/
│   ├── README.md
│   ├── rubrica.md
│   ├── canvas-wilmer-puerta.md
│   ├── propuesta-pset1.md             # misma versión sustantiva que el memo PDF
│   ├── pset01-presentacion.md         # mismas seis diapositivas que el PowerPoint
│   ├── proyecto-completo-pset1.md     # tres ideas, comparación y desarrollo ampliado
│   ├── notebooks/
│   │   └── PSet1_notebook_completo_Puerta_Wilmer.ipynb
│   ├── output/
│   │   ├── pdf/
│   │   │   ├── PSet1_memo_Puerta_Wilmer.pdf
│   │   │   └── PSet1_notebook_completo_Puerta_Wilmer.pdf
│   │   └── pitch/
│   │       ├── PSet1_pitch_Puerta_Wilmer.pptx
│   │       └── PSet1_pitch_Puerta_Wilmer.ppt
│   ├── scripts/                       # generadores y auditoría, si se crean
│   └── docs/
│       ├── auditoria-datos.md
│       ├── respuesta-feedback.md
│       └── trazabilidad-entregables.md
├── pset-02/
│   ├── README.md
│   ├── enunciado.md
│   ├── rubrica.md
│   ├── .env.example
│   ├── kestra/
│   ├── dbt/
│   ├── spark/
│   └── docs/
│       ├── plan-implementacion.md
│       └── contrato-datos.md
├── pset-03/
│   └── .gitkeep
└── pset-04/
    └── .gitkeep
```

Esta es una distribución de trabajo. Adáptala mínimamente a archivos existentes sin perder su claridad. `pset-02/docker-compose.yml` es un entregable obligatorio de la futura implementación: no crear un Compose vacío o aparentemente funcional solo para cumplir la estructura. Créalo cuando se implemente y verifique el servicio. Las carpetas aún vacías pueden contener `.gitkeep` para conservarlas en Git.

Los cuatro PSets pertenecen al mismo proyecto y comparten datos y definiciones; sus entregables y estados permanecen separados. La rúbrica recibida menciona cinco PSets del curso: preserva su texto literal y explica que este repositorio organiza las cuatro etapas definidas por el usuario, sin cambiar la ponderación del profesor ni inventar requisitos para PSet 3 o 4.

## C. Alcance que debes completar ahora

### PSet 1: producir el paquete revisado

1. `canvas-wilmer-puerta.md`, con datos y estado de acceso, predicción, métricas, umbral, acción, juicio, riesgos, evidencia o plan de verificación y gravedad.
2. `propuesta-pset1.md` y `PSet1_memo_Puerta_Wilmer.pdf`, con las mismas cuatro secciones y referencias, en 1–2 páginas legibles al exportar.
3. `pset01-presentacion.md` y presentación editable de exactamente seis diapositivas. El Markdown debe contener título, mensaje y contenido visible exactos de cada diapositiva, más visual propuesto, notas y fuentes claramente separados. No usarlo solo como una lista genérica de recomendaciones.
4. `proyecto-completo-pset1.md`, notebook `.ipynb` y PDF completo con las mismas tres opciones, matriz, selección, desarrollo metodológico y ajustes por feedback. Conservar todos los detalles sustantivos, sin la celda de rúbrica en el PDF y sin las instrucciones de producción de este encargo.
5. Los README, rúbricas y documentación de trazabilidad descritos aquí.

**Nombre del memo:** usar como nombre canónico `PSet1_memo_Puerta_Wilmer.pdf`, consistente con la serie PSet1. Una solicitud anterior escribió `PSe1_memo...`; si ya existe ese archivo, conservarlo como respaldo o alias documentado, sin mantener dos versiones divergentes. No confundirlo con el memo histórico de cinco páginas: el requisito vigente para el memo breve es 1–2 páginas.

**Correspondencia entre formatos:** Markdown, notebook y PDFs no deben tener metas, cifras, riesgos o alcance contradictorios. Las notas del pitch pueden ampliar, pero no cambiar, el mensaje visible. Generar los formatos desde una fuente de contenido controlada cuando sea posible. No resumir el proyecto completo para producir su notebook o PDF. Las diferencias de paginación y diseño son admisibles; las diferencias metodológicas no.

**PowerPoint:** producir `.pptx` nativo editable y `.ppt` real si hay conversor disponible; no renombrar una extensión para simular otro formato. Si falta conversión, entregar `.pptx` y registrar `.ppt` pendiente. No aplanar toda la presentación en imágenes. No se requiere regenerar el PDF del pitch en este encargo.

### PSet 2: preparar continuidad, no fingir ejecución

Crear `enunciado.md`, `rubrica.md`, README, plan de implementación, contrato de datos y `.env.example` con valores de ejemplo. No entrenar modelos, ejecutar el pipeline del PSet 2, crear recursos Snowflake, consumir créditos cloud ni instalar infraestructura pesada como parte de esta reconstrucción del PSet 1.

El README de PSet 2 distinguirá lo planificado de lo comprobado. Incluirá el procedimiento previsto de arranque y ejecución, marcado como pendiente hasta que existan Compose, flujos y scripts reales. No presentar comandos como verificados si solo son un diseño. La reproducibilidad futura debe quedar especificada con criterios concretos.

## D. Datos comunes en `datasets/`

Los archivos originales son `studentInfo.csv`, `studentRegistration.csv`, `courses.csv`, `vle.csv` y `studentVle.csv`. `assessments.csv` y `studentAssessment.csv`, si están presentes, no se usan para entrenar la comparación principal; cualquier uso adicional se documentará separadamente.

- Buscar primero estos nombres exactos en la raíz `datasets/` y, si falta alguno, identificar subcarpetas ya existentes y comunicar su ubicación antes de duplicar archivos.
- El usuario aportará los CSV. Si faltan, pedir los nombres faltantes o su ruta mientras se continúa con documentos independientes. No buscar como dependencia una copia en Descargas ni descargar otra versión silenciosamente.
- La ubicación de entrada debe ser configurable, con valor por defecto derivado de la raíz del repositorio. Resolver rutas desde la ubicación del script/configuración y documentar la ejecución; no depender del directorio de trabajo accidental.
- En PSet 2, el volumen local se montará explícitamente como solo lectura si ese es el mecanismo de acceso elegido. `.env.example` y Compose deberán resolver de forma coherente `../datasets` desde `pset-02/` cuando se implementen.
- Documentar origen, licencia, versión o fecha del archivo, SHA-256, bytes y conteos verificados en el manifiesto. No inventar verificaciones ni actualizaciones de una fuente histórica estática.
- Mantener los archivos originales sin modificaciones; las salidas derivadas pertenecen a la etapa que las produce.

La reconstrucción del PSet 1 sí puede ejecutar una auditoría descriptiva de estos archivos: conteos por clase, población, elegibilidad, claves, relaciones y cobertura. No usar resultados de otros proyectos ni archivos de predicciones o modelos previos para aparentar experimentos de este proyecto.

En `datasets/README.md`, explicar los cinco archivos, el origen oficial, cómo colocarlos, su exclusión de Git, cómo verificar checksums y qué metadatos documenta el manifiesto. Si el repositorio no contiene los CSV, la reproducibilidad se completa mediante obtención autorizada de la versión identificada y comprobación de su checksum; no basta indicar 'usa los datos que tengas'.

## E. README de la raíz

Debe explicar:

1. Nombre del proyecto, autor y propósito para un lector externo.
2. Cuatro entregas como etapas del mismo proyecto: PSet 1, propuesta; PSet 2, pipeline de datos; PSet 3 y 4, alcance pendiente de sus enunciados.
3. Árbol breve con enlaces relativos a los README de PSet 1 y 2 y a `datasets/README.md`.
4. Dónde colocar OULAD y cómo cada etapa consume los datos comunes.
5. Estado real de los entregables, sin marcar terminados los pendientes de conversión, datos o sincronización.
6. Qué leer primero: propuesta, Canvas, proyecto completo y guía/pitch.
7. Procedimiento de verificación y continuidad entre etapas, diferenciando documentación de servicios ejecutados.
8. Política de versionado local y preparación para GitHub: código, Markdown, manifiestos y documentación trazables; datos crudos, secretos, entornos, caches y temporales excluidos.

No sustituir este README por una explicación del curso sin contexto del proyecto. No declarar repositorio publicado ni enlace remoto inexistente.

## F. README de `pset-01/`

Debe incluir problema, objetivo, contexto hipotético, enlaces a todos sus entregables reales y a `rubrica.md`, y estado de verificación. Explicar:

- Tres ideas y por qué se seleccionó la primera.
- Pregunta estática vs longitudinal y comparador operativo adicional.
- Meta relativa del 10 %, presupuesto preventivo del 10 %, cuatro cortes y diferencia entre focalización e impacto.
- Cómo reproducir la auditoría descriptiva desde `../datasets`, con comandos reales si el script existe.
- Cómo regenerar Markdown, notebook y exportaciones, indicando dependencias efectivas y limitaciones de conversión.
- Acceso a Colab como antecedente y estado explícito de sincronización.
- Tabla de respuestas al feedback, con evidencia de dónde se atiende cada punto y cualquier cuantificación aún pendiente.

La fuente local revisada pasa a ser la base controlada del trabajo en VS Code. Colab se sincroniza si existe acceso autenticado, respaldando y verificando las celdas; si no existe, documentar que está pendiente, sin bloquear los archivos locales ni declarar actualizado el remoto.

## G. README de `pset-02/` y reproducibilidad futura

El README debe recoger fielmente el enunciado y separar **preparado**, **pendiente de implementación** y **verificado en ejecución**. Incorporar:

- Flujo requerido: Fuente → Kestra → Raw → dbt/Bronze → dbt/Silver → dbt/Gold → Spark/OBT, con persistencia final en Snowflake.
- Docker Compose local con al menos Kestra y Spark, más dbt Core en Docker o dbt Cloud. Justificar la opción al implementarla.
- Datos de entrada en `../datasets`, parámetros y montajes. Ninguna ruta personal fija.
- Requisitos reales de Docker y recursos, versiones compatibles y fijadas al instalar. No elegir etiquetas `latest` como garantía de reproducibilidad ni generar locks que no hayan sido resueltos.
- `.env.example` con nombres de variables y valores ficticios: ruta de datos y configuración Snowflake que corresponda al método de autenticación elegido. Secretos en entorno local, nunca valores reales en archivos versionados.
- Procedimiento previsto para levantar servicios, comprobar salud, cargar Raw, ejecutar dbt, construir OBT con Spark y verificar tablas. Convertirlo en comandos ejecutados y comprobados cuando se implemente, no antes.
- Trigger y frecuencia justificados para un histórico estático; reintentos, backfill por particiones, logs y control de cargas. No confundir frecuencia de ejecución con aparición real de nuevos datos OULAD.
- Idempotencia: reejecutar la misma carga o partición no introduce duplicados; identificadores de ejecución y manifest/checksum permiten reconciliar.
- Métricas de calidad, tests de claves y relaciones, reglas de fechas, validación de joins y tablas de evidencia problema–acción–justificación.
- Reproducción desde un clon limpio: obtención de datos identificados, configuración de credenciales, creación documentada de recursos, ejecución ordenada y verificación de artefactos. Incluir también dependencias cloud; Docker por sí solo no reproduce Snowflake.
- Costos y ejecución controlada: no afirmar que un pipeline es gratuito o probado sin datos de consumo; explicar suspensión/limpieza de recursos al implementar.
- Batch suficiente para revisión quincenal; describir qué nuevo requisito justificaría streaming sin implementarlo.
- Documento técnico máximo seis páginas sin anexos y `PSet2_memo_Puerta_Wilmer.pdf` como nombre previsto; aún no producir un memo que describa una implementación inexistente.

### Contrato y diseño de datos de continuidad

En `docs/contrato-datos.md`, fijar preliminarmente:

- Matrícula: `(id_student, code_module, code_presentation)`.
- OBT: matrícula + `cutoff_day`; hasta cuatro filas por matrícula según elegibilidad.
- Población elegible construida antes de unir actividad; preservar matrículas sin clics.
- Predictores calculados con información disponible al corte; no filtrar del futuro con target, fecha de retiro ni resultados finales.
- Target separado y disponible para evaluación retrospectiva; no incluirlo accidentalmente entre predictores.
- Transformaciones deterministas por corte frente a transformaciones aprendidas: imputación, escalado o selección aprendida se ajustan solo con entrenamiento, no globalmente durante ELT.
- Star schema Gold propuesto: dimensiones y hechos con grano explícito, evitando sumar varias veces antecedentes o multiplicar eventos en joins.
- Recencia e interacciones agregadas por intervalos comparables; definición de día cero, fechas negativas y recursos disponibles por edición antes de validar rangos.
- Reconciliación entre grano original, hechos y OBT; tests para claves, relaciones y cardinalidades.
- Definir qué mide completitud, validez y consistencia. La exactitud respecto de la realidad externa no queda demostrada solo porque un valor sea válido o se copie fielmente del archivo.

No inventar requisitos de PSet 3 ni PSet 4. Mantener sus carpetas preparadas sin asignarles temarios o entregables aún no recibidos.

## H. Git y archivos compartidos

Crear `.gitignore` coherente con un futuro repositorio:

- Ignorar `.env` y variantes con secretos, conservando `.env.example`.
- Ignorar contenidos crudos y derivados voluminosos de `datasets/`, preservando `datasets/README.md` y el manifiesto de metadatos autorizado si se generó.
- Ignorar `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`, caches, logs, temporales y respaldos locales.
- No ignorar indiscriminadamente Markdown, notebooks finales, diagramas ni el código necesario para reproducir.
- Los entregables finales PDF/PPT pueden versionarse si es la política del repositorio; no incluir grandes copias redundantes ni evidencias ficticias.

Validar los enlaces de los tres README dentro de la estructura nueva. No enlazar rutas personales de la conversación. No incluir contenido de credenciales ni volcados de entorno en logs de auditoría.

## I. Sincronía entre entregables y respaldo de trabajo previo

Usar los cuatro grupos de riesgos en memo, Canvas y pitch; conservar el desglose ampliado de ocho riesgos en el documento completo con su correspondencia. Mantener las tres ideas y la matriz íntegra en el respaldo completo.

Cifras reales: auditadas desde `datasets/`. Cifras documentales: las de las publicaciones, etiquetadas. Ejemplos: explícitamente hipotéticos. No mezclar estos niveles ni atribuir causalidad a detección o variación de clics.

Las métricas PR-AUC, casos a igual K y tasa de aprobación del piloto responden a preguntas distintas. La comparación con recencia no reemplaza la hipótesis estática/longitudinal. El protocolo posterior evalúa oferta de apoyo, no efectos individuales ni superioridad causal de la selección longitudinal.

Si se encuentra trabajo nuevo en la carpeta, reconciliar antes de usar el respaldo de este documento. No eliminar cambios realizados por el usuario ni sustituir resultados actuales por el histórico incluido.

## J. Verificación final del encargo

- [ ] Un solo `psets/` y carpetas `pset-01` a `pset-04`; `datasets` común.
- [ ] README root, PSet 1 y PSet 2 claros y con enlaces válidos.
- [ ] Rúbrica PSet 1 conservada; enunciado y rúbrica PSet 2 preservados, separando texto del profesor de decisiones del proyecto.
- [ ] Canvas, propuesta breve, guía/pitch y proyecto completo revisados en Markdown.
- [ ] Memo PDF de 1–2 páginas, notebook completo válido y PDF completo con todo el contenido sustantivo.
- [ ] PowerPoint de seis diapositivas con edición nativa; `.ppt` genuino o limitación explícita.
- [ ] Los mismos contenidos sustantivos entre Markdown y sus exportaciones.
- [ ] Fuentes de datos portables; auditoría y estado del manifiesto documentados; cuantificación pendiente si no hay archivos.
- [ ] Coherencia de target, cortes, población, K, meta, riesgos y alcance.
- [ ] Pipeline PSet 2 documentado como pendiente; ninguna ejecución o reproducibilidad declarada sin evidencia.
- [ ] Colab sincronizado con comprobación o pendiente comunicado.
- [ ] Sin rutas de Descargas, secretos ni publicación remota automática.

Al terminar, entregar la lista de archivos creados o actualizados, las verificaciones realizadas y los pendientes reales. No basta una propuesta de estructura: crear los archivos autorizados y efectuar las exportaciones posibles.

## K. Cómo usar este encargo

El usuario colocará este archivo en la raíz `psets/` y pedirá a Codex:

> Lee `prompt-codex-psets.md` completo. Ejecuta el encargo A–K usando el contenido y las rúbricas incluidos en L–O. Crea la estructura y los README, reconstruye los entregables revisados del PSet 1 en Markdown y sus formatos correspondientes, y deja documentado el inicio reproducible del PSet 2. Los CSV de OULAD están o serán colocados en `datasets/`. Conserva respaldos y comunica los pendientes reales sin inventar resultados.

---

## L. Contenido de proyecto y ajustes acordados

El siguiente material incluye las decisiones revisadas, el memo de partida, las seis diapositivas, las referencias y el desarrollo íntegro de las tres ideas. Sus rutas antiguas deben adaptarse a A–K. La tabla de archivos y la política de sincronización de A–K prevalecen sobre cualquier mención histórica.

## 2. Feedback que debemos resolver

1. **Problema y formulación:** la meta mide detección adicional, pero falta definir cómo se evaluaría si las tutorías mejoran los resultados académicos.
2. **Viabilidad de negocio:** falta un proceso de seguimiento concreto para comparar y delimitar los resultados validables por simulación sin institución participante.
3. **Pitch:** debe mostrar viabilidad técnica, evaluación y alcance del MVP, además de cuantificar problema y beneficio esperado.

El usuario mantiene el proyecto de predicción temprana. No solicita construir un modelo de efecto individual de tutorías ni ejecutar un nuevo proyecto de intervención. La solución acordada es explicitar el diseño de evaluación posterior, manteniendo la ejecución actual centrada en predicción y focalización retrospectiva.

## 3. Decisiones vigentes e invariantes

- **Caso seleccionado:** riesgo de reprobación al cierre de un módulo, con OULAD. Universidad hipotética, sin socio institucional comprometido.
- **Unidad:** matrícula estudiante–módulo–edición. OBT futura: esa matrícula en un corte de observación; hasta cuatro filas por matrícula elegible.
- **Población inicial:** registrada hasta el inicio oficial. En cada corte, excluir solo retiros ya ocurridos; contabilizar exclusiones. No utilizar la fecha futura de retiro como predictor.
- **Salida:** probabilidades de `Fail`, `Withdrawn` y aprobación (`Pass` + `Distinction`). Ordenar la revisión por `P(Fail)`. Retiro y abandono institucional son conceptos distintos.
- **Cortes:** días 14, 28, 42 y 56. Ocho semanas es observación temprana, no duración total del módulo. El horizonte termina al cierre de cada edición.
- **Modelos:** regresión logística multinomial y Random Forest. Comparar cada algoritmo con variables estáticas frente al mismo algoritmo enriquecido con actividad longitudinal. No agregar notas de evaluaciones al análisis principal.
- **Métrica técnica:** PR-AUC para Fail; complementar con precisión, recobrado, calibración e incertidumbre. Fijar la implementación de PR-AUC antes de comparar.
- **Meta:** al menos 10 % relativo más de futuras reprobaciones detectadas en el día 56, frente al baseline estático, con la misma población y capacidad. Es meta provisional; no garantía, resultado alcanzado ni 10 puntos porcentuales.
- **Presupuesto:** `K = floor(0.10 × N_elegibles)` por edición y corte, sensibilidad 5 % y 20 %. Es un cupo preventivo simulado; no es capacidad institucional medida. La tutoría habitual queda fuera de la simulación: no se afirma que nueva atención adicional sea gratuita ni que exista personal reservado.
- **Umbral:** puntuación del último caso que cabe en K. Desempate estable sin consultar la etiqueta. Informar ediciones con K insuficiente; no elegir retrospectivamente el presupuesto que favorezca el modelo.
- **Error prioritario:** se considera provisionalmente más grave omitir casos futuros de reprobación, por la oportunidad de apoyo perdida. Las falsas alertas consumen cupos; costos relativos y prioridad requieren validación institucional.
- **Validez:** ediciones posteriores compatibles; etiquetas históricas maduras antes del instante simulado; estudiantes separados entre ajuste y prueba; todas las filas y cortes de una matrícula en la misma partición. Definir transformaciones y ajustes dentro del entrenamiento.
- **Juicio:** el sistema calcula y ordena; el tutor revisa siempre contexto y decide contacto, orientación o derivación. No sanciones automáticas ni contacto real en el MVP.
- **Tres niveles:** calidad predictiva; focalización simulada; impacto educativo posterior. No confundirlos.

### Comparador operativo reproducible

Añadir una política simple de seguimiento: ordenar las matrículas elegibles por días desde la última interacción registrada hasta el corte, de mayor a menor, y asignar los mismos K cupos.

Antes de evaluar, fijar: tratamiento de quienes nunca registraron actividad, disponibilidad de actividad previa al inicio, distinción entre inactividad y cobertura desconocida, y desempate estable. Una opción de diseño es contar desde el inicio para quienes carecen de actividad y tienen cobertura comprobada; los estados desconocidos deben señalizarse y tratarse con una regla explícita común. Auditar esta opción antes de adoptarla.

Esta política ya usa actividad temporal: es un comparador operativo adicional, no un baseline estático ni un proceso institucional observado. No afirmar superioridad sobre OU Analyse. Mantener la comparación estática/longitudinal como prueba principal de la hipótesis.

Métricas: TP@K, precisión@K, recobrado@K, casos omitidos, primeras detecciones y anticipación hasta cierre. Para la comparación del día 56, mismo N y K. Para cuatro listas sucesivas, mismas reglas de capacidad; revisiones repetidas consumen cupos y cada matrícula se cuenta una sola vez en TP acumulados. Informar también estudiantes únicos.

### Protocolo de impacto posterior, sin ejecutarlo en este PSet

- **Pregunta:** ¿ofrecer un programa definido de acompañamiento preventivo mejora la aprobación respecto de la atención habitual?
- **Población:** estudiantes elegibles identificados como en riesgo mediante una regla fijada antes de asignar la intervención; fecha de corte y ámbito de validez documentados.
- **Asignación:** aleatoria por estudiante a oferta de acompañamiento proactivo o atención habitual, con estratificación pertinente por módulo/riesgo. Resolver matrículas múltiples asignando a cada persona de manera coherente. Si se requiere aleatorizar por tutor o grupo para evitar contaminación, ajustar diseño, muestra e inferencia por agrupamiento.
- **Intervención:** contacto, evaluación de necesidades, tutoría y seguimiento con frecuencia y contenidos acordados. Conservar el apoyo habitual en ambos grupos.
- **Resultado principal:** proporción que aprueba al cierre (`Pass` + `Distinction`), con diferencia absoluta en puntos porcentuales e intervalo de confianza entre grupos asignados. Informar también Fail y Withdrawn para no confundir una baja de Fail con mayor retiro.
- **Análisis:** intención de tratar; no comparar solo quienes aceptaron tutoría contra quienes no la aceptaron. Registrar oferta, contacto, participación, otras ayudas y seguimiento. La aleatorización aborda confusión en expectativa; documentar contaminación e intervenciones concurrentes.
- **Muestra:** calcularla posteriormente según tasa inicial, efecto mínimo relevante, potencia, agrupamiento si corresponde y pérdidas esperadas. No inventar tamaño ni potencia.
- **Valor y recursos:** participación, tiempo y costo por estudiante y por aprobación adicional cuando los datos lo permitan; posibles efectos adversos o diferencias entre grupos.
- **Alcance de la inferencia:** este ensayo estimaría el efecto de ofrecer ese programa en esa población. No estima efectos individuales ni prueba automáticamente que la selección longitudinal sea mejor que otra política. Esa segunda pregunta requeriría una evaluación de políticas con presupuesto comparable.
- **Estado:** protocolo diseñado; ejecución fuera del MVP, condicionada a institución, capacidad, autorizaciones y datos nuevos.

## 4. Cuantificación y evidencia: reglas para producir los entregables

Antes de cerrar el pitch, buscar los CSV de OULAD en la carpeta autorizada del proyecto. Si están disponibles, realizar solo la auditoría descriptiva necesaria, sin iniciar el entrenamiento ni el pipeline del PSet 2:

1. Verificar archivo, checksum, versión, claves, matrícula única y categorías de `final_result`.
2. Calcular conteos y porcentajes de Fail, Withdrawn y aprobación en el conjunto original y en la población definida, por módulo y edición.
3. Reportar N elegible y K en cada corte; validar joins y registros sin actividad. Documentar numerador, denominador, exclusiones y fecha de cálculo.
4. Cuantificar el problema con una tasa verificada, sin extrapolarla a una universidad hipotética ni a la población actual de The Open University.
5. No borrar ceros de actividad ni asumir equivalencia entre falta de eventos y falta de cobertura.

Si los CSV no están disponibles, solicitar únicamente su ubicación mientras se continúa el trabajo independiente. Usar las cifras documentales para justificar acceso y escala; no inventar la tasa de reprobación. Registrar explícitamente que el componente de magnitud del problema sigue pendiente. No marcar como completamente cerrado el feedback de cuantificación sin evidencia.

**Cifras documentales ya utilizadas:** siete módulos, 22 ediciones de 2013–2014, 32.593 registros estudiante–módulo–edición y 10.655.280 registros diarios de interacción. No son estudiantes únicos y no sustituyen el conteo de reprobaciones.

**Beneficio esperado ilustrativo:** con 100 revisiones, pasar de 40 a 44 futuras reprobaciones identificadas equivale a 4 casos adicionales y 10 % relativo. Precisión de esas listas: 40 % y 44 %; incremento de 4 puntos porcentuales. Todos esos valores son ilustrativos, no obtenidos. No asignar un desempeño inventado a la regla operativa. No convertir detecciones adicionales en aprobaciones ganadas ni dinero ahorrado.

**Antecedente:** OU Analyse actualiza semanalmente riesgo de fallar la siguiente evaluación y lo presenta a tutores/equipos de apoyo. Esa descripción respalda plausibilidad operativa, no prueba efecto causal de tutorías ni equivalencia con nuestro target de cierre. Existen estudios de acompañamiento y alertas con resultados distintos; no afirmar que no existen investigaciones o que las universidades solo intervienen después de reprobar.

## 5. Memo: texto editorial de partida

Redactar el memo en las cuatro secciones siguientes, usando el contenido propuesto y ajustando extensión sin perder las decisiones necesarias. Objetivo 1–2 páginas legibles; no reducir la fuente a tamaños incómodos para forzar el límite. Mantener referencias IEEE breves. El cuerpo debe sostenerse solo y estar dirigido al patrocinador.

### 1. El problema de negocio y la métrica de éxito

Una universidad hipotética con tutorías limitadas necesita decidir a quién revisar antes del cierre de cada módulo. Una lista inicial puede omitir estudiantes cuya situación cambia. El proyecto evaluará si la evolución de la actividad digital mejora la focalización preventiva con los mismos cupos; no promete reducir reprobaciones sin evaluar posteriormente el apoyo.

Para cada matrícula estudiante–módulo–edición se estimarán probabilidades de reprobación, retiro y aprobación al cierre, usando información hasta los días 14, 28, 42 y 56. Se compararán regresión logística multinomial y Random Forest con antecedentes estáticos frente a los mismos algoritmos enriquecidos con actividad longitudinal. PR-AUC para reprobación será la métrica técnica principal. La meta provisional es identificar en el día 56 al menos un 10 % relativo más de futuras reprobaciones que el baseline estático, a igual población y capacidad. Se seleccionarán las K puntuaciones más altas, con K igual al 10 % de matrículas elegibles por edición; el umbral será la última puntuación que cabe en esos cupos. Se considera prioritario reducir omisiones de estudiantes que posteriormente reprueban, sin ignorar que las falsas alertas consumen recursos. Capacidad y costos relativos son supuestos por validar.

### 2. Viabilidad técnica

OULAD es público y su descarga está confirmada por el autor; la auditoría local permanece pendiente hasta documentar su ejecución [1], [2]. `studentInfo.csv` aporta antecedentes y resultado; `studentVle.csv`, actividad fechada; `vle.csv`, recursos; `courses.csv`, edición y duración; y `studentRegistration.csv`, registro y retiro. Los cinco tienen acceso confirmado. La publicación describe 32.593 matrículas y 10.655.280 registros diarios de interacción. Incorporar aquí una tasa local de reprobación solo después de verificar población y conteos.

Se construirán características de nivel, recencia y cambio quincenal, distinguiendo inactividad de falta de cobertura y sin usar información futura. La prueba utilizará ediciones posteriores compatibles y estudiantes no usados para ajustar el modelo; las etiquetas históricas deberán estar disponibles antes de cada predicción simulada. Se comparará también una regla operativa de recencia a igual capacidad. El MVP ofrecerá preparación reproducible, inferencia por corte, listas, evolución del riesgo y reporte comparativo. La infraestructura de datos se desarrollará progresivamente en la siguiente etapa con Kestra, dbt, Spark y Snowflake. No hay acceso confirmado a registros institucionales de capacidad, costos o intervenciones.

### 3. Viabilidad de negocio

La propuesta cambia la asignación de revisión preventiva: una lista quincenal sustituye la selección fija o reactiva del escenario hipotético. El coordinador define cupos; el tutor revisa contexto y decide apoyo. El sistema ordena prioridades y no ejecuta sanciones. La simulación comparará regla de recencia, baseline estático y modelos longitudinales con igual población y presupuesto, midiendo detecciones, omisiones, anticipación y revisiones repetidas. El 10 % de capacidad corresponde a un presupuesto preventivo simulado; preservar otros servicios no demuestra disponibilidad de personal adicional.

El impacto académico se evaluaría en un piloto posterior: asignar aleatoriamente estudiantes elegibles a oferta de acompañamiento definido o atención habitual y comparar la proporción que aprueba al cierre, por grupo asignado, con intervalo de confianza. Se observarán también retiro, reprobación, participación, tiempos y costos. La muestra dependerá de la tasa inicial y del efecto mínimo relevante. El PSet actual diseña este protocolo; OULAD permite evaluar focalización retrospectiva, no el efecto causal de nuestra intervención ni ahorros.

### 4. Riesgos principales

**R1. Mejora insuficiente o poco transferible; alta.** Se rompe el supuesto de aporte longitudinal consistente. Comparar a igual K por edición, con incertidumbre; conservar el baseline o limitar el alcance si no se sostiene.

**R2. Información futura o actividad mal representada; crítica.** Se rompe la disponibilidad y comparabilidad al corte. Auditar fechas, etiquetas, cobertura, claves y transformaciones; reconstruir cualquier evaluación afectada. Medir factibilidad de procesamiento y acotar módulos con criterios previos si hace falta.

**R3. Capacidad inviable o apoyo sin efecto; alta.** Se rompe la viabilidad de revisión e intervención útil. Simular cupos del 5 %, 10 % y 20 %, repeticiones y carga; medir participación y resultados solo en el piloto posterior. No afirmar eficiencia monetaria sin costos.

**R4. Errores desiguales o pérdida de confianza; alta.** Se rompe una priorización aceptable entre grupos. Revisar errores por subgrupos con volumen suficiente y el lenguaje de alertas; ajustar reglas y preservar juicio humano y vías habituales de apoyo.

## 6. Pitch revisado: seis diapositivas exactas

Paleta: negro y rojo principales; azul y azul cielo secundarios; texto principalmente blanco. Composición ejecutiva, una idea central por diapositiva, diagramas editables y cifras legibles. No convertir cada diapositiva en un párrafo. Referencias y detalles complementarios en notas. Respetar las habilidades de presentación disponibles; conservar la edición nativa de textos y diagramas.

### Diapositiva 1 — Apoyo académico a tiempo

- **Autor:** Wilmer Puerta.
- **Mensaje:** identificar mejor a quién apoyar, con la misma capacidad preventiva.
- **Visual:** señales → prioridad → revisión del tutor.
- **Nota:** universidad hipotética, prueba de concepto con OULAD; no socio comprometido.

### Diapositiva 2 — El riesgo cambia durante el módulo

- **Problema:** una lista fija puede omitir trayectorias que empeoran.
- **Cifra central:** tasa y número de reprobaciones realmente calculados para el ámbito analizado, con denominador y fuente; distinguir retiros.
- **Visual:** trayectoria y ventana de revisión en semanas 2, 4, 6 y 8.
- **Fallback:** si no hay CSV, usar un escenario claramente hipotético y declarar pendiente la cuantificación real, sin dar el gap por cerrado. No presentar escala total del dataset como tasa del problema.

### Diapositiva 3 — Una prioridad de revisión que se actualiza

- **Flujo:** observar actividad → estimar riesgo de reprobar → ordenar cupos → tutor revisa y decide.
- **Decisión:** presupuesto preventivo simulado del 10 %; sensibilidad 5 % y 20 %.
- **Comparación operativa:** regla de recencia frente a priorización con modelos.
- **Nota:** la comparación estática/longitudinal se mantiene para aislar el aporte de características. No afirmar intención a partir de clics.

### Diapositiva 4 — Viabilidad, evaluación y producto concreto

- **Datos:** OULAD descargado; antecedentes, actividad fechada y resultados. Usar conteos auditados si existen; de lo contrario, cifras documentales etiquetadas.
- **Evaluación:** ediciones posteriores, estudiantes separados, igual capacidad; PR-AUC y casos detectados por cupo.
- **MVP:** preparación reproducible, puntuaciones por corte, listas y evolución del riesgo, reporte de comparación.
- **Visual:** datos → validación → lista demostrativa. Indicar que la construcción se ejecutará en etapas, no que ya funciona.

### Diapositiva 5 — Beneficio medible y condiciones de éxito

- **Meta ilustrada:** 40 → 44 futuras reprobaciones identificadas con 100 revisiones = +10 % relativo.
- **Etiqueta permanente:** meta ilustrativa, no resultado obtenido ni reprobaciones evitadas.
- **Riesgos compactos:** mejora incierta; calidad/fuga; capacidad/efecto del apoyo; equidad/confianza, con respuesta breve para cada uno.
- **Puente al impacto:** piloto posterior medirá aprobación entre grupos asignados; el estudio actual mide focalización. No inventar retorno financiero.

### Diapositiva 6 — Respaldar una prueba de concepto y una decisión informada

- **Solicitar:** responsable académico, referente de tutorías y validación del presupuesto preventivo.
- **Hitos:** auditar y cuantificar → comparar y demostrar → decidir si procede piloto.
- **Criterios:** mejora e incertidumbre, calidad, carga y equidad; no aprobar solo por un promedio favorable.
- **Piloto posterior:** oferta aleatoria de apoyo vs atención habitual; aprobación, retiro, participación y costos.
- **Cierre:** avanzar al piloto solo con evidencia favorable y condiciones institucionales acordadas. Sin plazo inventado ni compromiso de reducción de reprobación.

## 7. Notebook local y PDF completo

Crear un notebook nbformat 4 con celdas Markdown por apartado y encabezados navegables. Incluir:

1. Título, autor, fecha, alcance y estado de evidencia.
2. Tres ideas con sus seis apartados y referencias.
3. Comparación completa, matriz de seis criterios y desempate.
4. Desarrollo ampliado del caso 1: negocio, predicción, datos, evaluación, acción, riesgos y MVP.
5. Revisión por feedback: comparador operativo, presupuesto preventivo, protocolo posterior de impacto y límites de simulación.
6. Preparación para PSet 2, sin ejecutar su infraestructura dentro de esta tarea.
7. Guía del pitch, referencias y registro breve de cambios.

Usar el respaldo de la sección 10 y sustituir formulaciones obsoletas con las decisiones vigentes anteriores. Mantener los ocho riesgos desarrollados, explicando su agrupación en los cuatro del memo/pitch. No reducir el notebook completo a una copia del memo. No incluir salidas o entrenamientos ficticios. Las celdas de código descriptivo, si se agregan para auditar CSV disponibles, deben tener rutas configurables y ejecuciones reales; no son obligatorias para la documentación.

La exportación a PDF debe conservar todo el contenido sustantivo: tres opciones, matriz, decisión, desarrollo y actualizaciones. Excluir la rúbrica inicial y las instrucciones de producción. Las tablas deben ser legibles y no cortarse horizontalmente. Se puede adaptar el estilo para impresión sin resumir. Verificar conteos y encabezados, referencias y extracción de texto, además de revisar visualmente todas las páginas.

## 8. Límite con PSet 2 y controles de entrega

El PSet 2 requiere Fuente → Kestra → Raw → dbt/Bronze → dbt/Silver → dbt/Gold → Spark/OBT en Snowflake, Docker Compose con al menos Kestra y Spark, ingesta automática, reintentos, backfill, calidad, esquema estrella y OBT. Es batch; no requiere streaming ni entrenar el modelo. En este encargo solo actualizar su encaje como siguiente etapa; no desplegar servicios ni consumir recursos cloud.

La futura OBT tendrá grano matrícula–corte. Construir la población elegible antes de unir actividad, evitando perder matrículas sin clics. Separar resultados futuros de predictores. Versionar definiciones para que el baseline estático y los modelos enriquecidos compartan cohortes. No atribuir a VS Code por sí solo el papel de infraestructura de datos.

### Verificación final

- Memo de 1–2 páginas y cuatro secciones, con referencias y lectura autónoma.
- Pitch editable de exactamente seis diapositivas, con datos, evaluación, MVP, beneficio y solicitud.
- Notebook local válido; todas las ideas, comparación y propuesta completa presentes.
- PDF completo sin la celda de rúbrica y sin omitir contenidos sustantivos.
- Ningún 10 % presentado como resultado logrado, mejora de exactitud general o reducción educativa.
- Riesgos, target, fuente, cortes y presupuestos coherentes entre archivos.
- Tasa de reprobación y demás resultados identificados como auditados, documentales o ilustrativos, según corresponda.
- No generalizaciones sobre universidades ni afirmación de que no hay estudios de acompañamiento.
- Archivos PDF y PPT revisados visualmente; fuentes y caracteres legibles; referencias verificables.
- Actualización de Colab comprobada o pendiente comunicada expresamente.
- Respaldos y limitaciones de herramientas documentados, sin confundir formatos ni declarar resultados no ejecutados.

## 9. Referencias adicionales para la revisión

[5] The Open University, “OU Analyse.” [En línea]. Disponible en: https://research.stem.open.ac.uk/ouanalyse/. [Consultado: 11-nov-2026]. Documenta el flujo de alertas; no utilizar su descripción como evidencia causal de tutorías.

[6] E. P. Bettinger y R. B. Baker, “The Effects of Student Coaching in College: An Evaluation of a Randomized Experiment in Student Advising,” *Educational Evaluation and Policy Analysis*, vol. 36, no. 1, pp. 3–19, 2014. Resumen del estudio publicado por AERA: https://www.aera.net/Newsroom/Recent-AERA-Research/The-Effects-of-Student-Coaching. [Consultado: 11-nov-2026]. Acompañamiento individualizado y persistencia; no extrapolar su efecto a tutoría académica específica ni a OULAD.

[7] J. Klenke et al., “Effects of Early Warning Emails on Student Performance,” arXiv:2102.08803, versión revisada 2023, doi: 10.48550/arXiv.2102.08803. https://arxiv.org/abs/2102.08803. [Consultado: 11-nov-2026]. Los autores describen un efecto positivo estimado con poca precisión; no afirmar eficacia universal de las alertas.

Las referencias [1]–[4] se conservan al final del respaldo siguiente. Al producir el memo/pitch, renumerar según orden de aparición y verificar metadatos antes de publicarlos; no conservar números sin su entrada bibliográfica. No introducir fuentes no leídas como evidencia de resultados.

## 10. Respaldo sustantivo completo para reconstruir el notebook

El contenido siguiente conserva las tres ideas y el desarrollo original. Aplicar las actualizaciones explícitas de las secciones 2–8 antes de emitir la nueva versión: el comparador por recencia ya aparecía como referencia operativa propuesta y ahora debe quedar plenamente especificado; el protocolo de impacto se concreta; y la implementación pasa a contemplar el pipeline de la etapa siguiente. La matriz y sus puntuaciones siguen siendo juicios de diseño históricos, no resultados experimentales ni una nueva calificación docente.


# **1. Ideas de Proyectos**

## 1.1. Predicción temprana del riesgo de reprobación y seguimiento de la actividad digital para priorizar el acompañamiento académico: estudio con OULAD.

## 1.2. Detección de segmentos compatibles con fibrilación auricular para priorizar la revisión en programas de monitoreo cardiovascular.

## 1.3. Predicción del crecimiento anual de ingresos por cliente para priorizar oportunidades comerciales en telecomunicaciones.

## **1.1. Predicción temprana del riesgo de reprobación y seguimiento de la actividad digital para priorizar el acompañamiento académico: estudio con OULAD.**

### **1.1.1. Idea:**

Desarrollar un prototipo de alerta temprana con OULAD [1] para evaluar si las características longitudinales de interacción digital mejoran la identificación de estudiantes que posteriormente reprueban un módulo, frente al uso exclusivo de características estáticas. El contexto será una universidad hipotética con capacidad limitada de acompañamiento académico.

El prototipo actualizará el riesgo en las semanas 2, 4, 6 y 8 y mostrará su evolución para apoyar la priorización de tutorías. Estas semanas corresponden a la ventana de observación temprana seleccionada.

### **1.1.2. Problema:**

**Negocio.** Un acompañamiento principalmente posterior a la reprobación limita la intervención preventiva y puede aumentar las necesidades de recuperación académica. Una clasificación inicial basada en antecedentes fijos omite cambios posteriores del estudiante. La universidad necesita actualizar la identificación del riesgo para focalizar recursos limitados y detectar casos que inicialmente quedarían fuera del apoyo.

**Ciencia de datos.** Se compararán regresión logística multinomial y Random Forest con variables estáticas, frente a los mismos algoritmos enriquecidos con actividad digital longitudinal. Se evaluará si el nivel, la regularidad y los cambios de interacción aportan mejora predictiva bajo condiciones comparables. La actividad digital se tratará como una señal contextual, no como prueba directa de compromiso.

### **1.1.3. Predicción:**

Para cada estudiante–módulo–edición activo en el corte, se estimará la probabilidad del resultado final: reprobación (`Fail`), retiro (`Withdrawn`) o aprobación (`Pass`/`Distinction`). La prioridad será el riesgo de reprobación. Se utilizarán únicamente datos disponibles hasta cada corte; el retiro del módulo se distinguirá del abandono institucional.

Se evaluarán PR-AUC, precisión y recobrado para reprobación, entrenando con ediciones anteriores y probando con posteriores. La meta provisional es detectar un 10% más de casos, en términos relativos, frente al modelo estático en la semana 8, con igual capacidad de atención. Los cortes anteriores mostrarán anticipación; la mejora deberá comprobarse.

### **1.1.4. Datos:**

OULAD es un dataset público anonimizado, con acceso y descarga confirmados por el equipo. Se utilizarán `studentInfo.csv` para antecedentes y resultado final; `studentVle.csv` para interacciones diarias; y `vle.csv`, `courses.csv` y `studentRegistration.csv` para contextualizar recursos, duración y elegibilidad. Se construirán indicadores quincenales de actividad, inactividad y tendencia a partir de los campos documentados en [2].

Queda pendiente auditar cobertura, volumen, faltantes, uniones y estudiantes repetidos. Se excluirá información futura y se preservará la atribución requerida por CC BY 4.0. La capacidad tutorial será simulada, pues no existen costos ni resultados de intervenciones confirmados. La descripción de los datos y su licencia se documentan en [1], [2].

### **1.1.5. Acción:**

Cada dos semanas, un tutor revisaría una lista ordenada por riesgo para decidir contactos, orientación o apoyo académico. La capacidad simulada inicial será el 10% de estudiantes elegibles por corte, con escenarios del 5% y 20%. El umbral dependerá de esa capacidad; el criterio humano determinará la intervención.

Se compararán casos identificados, omitidos y anticipación con el mismo presupuesto de contactos; las revisiones repetidas consumirán capacidad y cada estudiante contará una sola vez en la cobertura acumulada. El resultado demostrable será una mejor focalización potencial. Reducir reprobación o costos requerirá un piloto posterior que evalúe el efecto de las tutorías.

### **1.1.6. Riesgos:**

- **Técnico — Mejora insuficiente (alta).** Las variables longitudinales podrían no superar al baseline. Se contrastarán resultados bajo condiciones equivalentes y con incertidumbre; si no aportan valor, se conservará el enfoque estático y se reportará el resultado.

- **Técnico — Fuga de información (alta).** Datos futuros o estudiantes repetidos podrían inflar el desempeño. Se auditarán fechas y particiones; si se detectan problemas, se reconstruirá la evaluación antes de concluir.

- **Técnico — Interpretación incorrecta de la actividad (alta).** Menos clics podrían reflejar cambios del calendario o registros incompletos. Se revisarán cobertura y contexto del módulo; las señales ambiguas se ajustarán o excluirán.

- **Negocio — Capacidad tutorial poco realista (alta).** Las listas podrían exceder los recursos disponibles. Se analizarán presupuestos y contactos repetidos; una adopción futura requerirá validar la capacidad con tutores y ajustar la frecuencia de atención.

- **Negocio — Intervenciones sin impacto (alta).** Detectar riesgo podría no mejorar el resultado académico. Un piloto posterior comparará intervenciones y resultados; hasta entonces, las conclusiones se limitarán a predicción y focalización potencial.

- **Adopción — Alertas injustificadas o sobrecarga (alta).** Los errores podrían afectar la confianza o perjudicar a ciertos grupos. Se revisarán errores por subgrupos y carga de alertas; se ajustará la priorización manteniendo revisión humana y acceso habitual al apoyo.

## **1.2. Detección de segmentos compatibles con fibrilación auricular para priorizar la revisión en programas de monitoreo cardiovascular.**

### **1.2.1. Idea:**

Proponer un sistema de apoyo que identifique segmentos de señal cardíaca compatibles con fibrilación auricular y los priorice para revisión profesional. Su aplicación prevista sería un programa de monitoreo de pacientes con enfermedad cardiovascular crónica, coordinado por una aseguradora o un prestador de salud.

El proyecto se enfocará en la detección de una alteración presente en el registro. La prevención de complicaciones será un beneficio potencial que requerirá evaluación posterior. El entorno de desarrollo, las herramientas y la incorporación de una simulación IoT se definirán durante el desarrollo de la propuesta.

### **1.2.2. Problema:**

**Negocio.** En un programa hipotético de monitoreo cardiovascular, revisar grandes volúmenes de registros puede superar la capacidad disponible y demorar la identificación de segmentos relevantes. La organización necesita focalizar la revisión profesional para reconocer posibles episodios de fibrilación auricular y decidir oportunamente qué casos requieren valoración adicional.

**Ciencia de datos.** Se plantea clasificar segmentos de señal cardíaca según su compatibilidad con fibrilación auricular, utilizando anotaciones reales como referencia. Se evaluará si esa clasificación mejora la selección de registros para revisión frente a una estrategia de referencia por definir. La detección automatizada apoyará el juicio profesional sin establecer por sí sola un diagnóstico.

### **1.2.3. Predicción:**

La unidad de análisis será un segmento de señal cardíaca asociado a un paciente. La salida será una puntuación de compatibilidad con fibrilación auricular presente en ese segmento. La fuente candidata dispone de anotaciones de ritmo que permitirían construir el resultado objetivo [3], [4], sujeto a verificar su contenido y calidad.

Durante el desarrollo se definirán ventanas, características, algoritmos, métricas, baseline y evaluación con pacientes distintos entre entrenamiento y prueba. El criterio de negocio será identificar más segmentos relevantes con capacidad de revisión comparable. La meta cuantitativa se establecerá tras inspeccionar los datos; no se compromete anticipación de urgencias ni ahorro económico demostrado.

### **1.2.4. Datos:**

Se ha identificado Icentia11k como fuente pública candidata. Su documentación describe señales ECG de un monitor portátil y anotaciones de ritmos, incluida fibrilación auricular [3], [4]. **El equipo aún no dispone de los datos descargados ni ha inspeccionado señales o anotaciones.** La adquisición y auditoría quedan para la etapa de desarrollo.

Se verificará cobertura, calidad, condiciones de uso y representatividad para pacientes con enfermedad cardiovascular crónica. No se dispone de costos ni resultados de intervenciones. Se explorará después la simulación de transmisión o datos de dispositivos IoT; cualquier componente sintético se identificará y no sustituirá la evaluación con señales y etiquetas reales.

### **1.2.5. Acción:**

El sistema propondría una lista priorizada de segmentos para que un profesional revise la señal y determine si corresponde una valoración adicional. El umbral y la capacidad de revisión se definirán posteriormente. La organización conservaría sus procedimientos habituales de atención y el profesional mantendría la decisión clínica.

La utilidad se evaluaría por la identificación de segmentos relevantes, los casos omitidos y la carga de revisión frente al baseline acordado. Las alertas repetidas deberán contabilizarse. La reducción de tiempos, costos o complicaciones requeriría mediciones adicionales y una evaluación de las intervenciones, fuera de lo demostrable únicamente con clasificación retrospectiva.

### **1.2.6. Riesgos:**

- **Técnico — Datos insuficientes o inadecuados (alta).** La fuente podría no aportar señales y etiquetas utilizables. Se inspeccionará una muestra y su cobertura durante el desarrollo; si falla, se acotará el conjunto o se buscará otra fuente antes de entrenar.

- **Técnico — Evaluación optimista (alta).** Segmentos del mismo paciente en entrenamiento y prueba podrían inflar el desempeño. Se verificará la separación por paciente al diseñar la evaluación; cualquier solapamiento indebido exigirá rehacerla.

- **Técnico — Simulación IoT poco representativa (alta).** Datos sintéticos, ruido o pérdidas simuladas podrían no reproducir dispositivos reales. Se contrastarán con señales observadas durante el desarrollo; la simulación quedará limitada a pruebas técnicas si no puede validarse su realismo.

- **Negocio — Exceso de alertas o casos omitidos (alta).** El sistema podría sobrecargar la revisión o pasar por alto segmentos relevantes. Se evaluarán errores y carga frente al baseline; se ajustará la priorización o se descartará su utilidad si no mejora el proceso.

- **Negocio — Detección sin beneficio posterior (alta).** Priorizar registros podría no reducir complicaciones ni costos. Un piloto posterior deberá evaluar acciones y resultados; mientras tanto, las conclusiones se limitarán a desempeño y focalización potencial.

- **Adopción — Población poco representativa (alta).** Los pacientes del dataset podrían diferir del programa previsto. Se revisarán características y documentación disponibles; si no se acredita representatividad, se limitará la conclusión a la población observada y se requerirá validación externa.

## **1.3. Predicción del crecimiento anual de ingresos por cliente para priorizar oportunidades comerciales en telecomunicaciones.**

### **1.3.1. Idea:**

Desarrollar un modelo que estime la probabilidad de crecimiento, estabilidad o disminución de los ingresos efectivos de cada cliente durante el siguiente año calendario. Se utilizará el historial mensual de ingresos por producto o servicio de una empresa de telecomunicaciones para apoyar la asignación de recursos comerciales.

La evolución de ingresos y la composición de servicios permitirán caracterizar oportunidades de expansión. La clasificación por tamaño económico complementará la predicción, con segmentos por definir. El crecimiento incluirá ajustes tarifarios, aumentos en servicios existentes y servicios que comienzan a generar ingresos, conforme al criterio comercial descrito por el equipo.

### **1.3.2. Problema:**

**Negocio.** La empresa necesita distribuir ejecutivos, campañas y atención especializada entre clientes con distinto potencial de crecimiento. El ingreso actual identifica el tamaño de una cuenta, pero no determina su evolución futura. Incorporar esa perspectiva permitiría focalizar los recursos disponibles; el proceso actual de asignación deberá documentarse antes de evaluar su mejora.

**Ciencia de datos.** Se plantea una clasificación de tres resultados futuros utilizando tendencias, variabilidad y composición mensual de ingresos, junto con cantidad de servicios con ingresos y antigüedad observable. Se evaluará si el modelo mejora la identificación de clientes que crecen frente a una regla sencilla basada en tendencia histórica, por definir durante el desarrollo.

### **1.3.3. Predicción:**

Para cada cliente activo al cierre de un año, se estimarán las probabilidades de crecimiento, estabilidad y disminución de sus ingresos acumulados del año siguiente respecto al año de referencia. La banda de estabilidad y el tratamiento de historiales parciales o bases nulas se definirán con análisis de datos y criterio comercial.

La evaluación será temporal, con ventanas comparables: por ejemplo, aprender con información de 2020 y resultados de 2021, evaluar con información de 2021 y resultados de 2022, y después pronosticar 2023. Se medirán F1-macro y precisión y recobrado de crecimiento. Los años son ilustrativos; tres años de historia limitan las transiciones anuales evaluables.

### **1.3.4. Datos:**

El equipo confirma disponer de registros internos de ingresos efectivos por cliente, producto o servicio y mes durante tres años. Se verificará el identificador de cliente, fechas, continuidad, definición de cartera activa y consistencia de categorías. El ingreso total se obtendrá agregando los servicios de cada cliente en cada período.

Queda pendiente auditar volumen, calidad, faltantes, ajustes contables y permisos de uso académico y confidencialidad. Se distinguirán ingreso cero, registro ausente y salida del cliente. No se requieren reclamos ni NPS. La fuente es empresarial interna, informada por el equipo; su identificación documental y restricciones se completarán sin divulgar información confidencial.

### **1.3.5. Acción:**

Al iniciar el año, el responsable comercial utilizaría las probabilidades junto con el tamaño económico y la composición de servicios para priorizar cuentas. Podría asignar ejecutivos senior, ampliar atención o diseñar campañas y ofertas proactivas. La intensidad de la gestión dependerá de la capacidad disponible y del juicio comercial.

La utilidad inicial será identificar más clientes que posteriormente crecen con un presupuesto comercial comparable al baseline; la meta cuantitativa se definirá tras inspeccionar los datos. Se distinguirá crecimiento observado de ingreso incremental causado por la intervención, cuya demostración requeriría un piloto posterior con un grupo de comparación adecuado.

### **1.3.6. Riesgos:**

- **Técnico — Pocas transiciones anuales (alta).** Tres años podrían no cubrir suficientes ciclos para generalizar. Se verificará la cobertura temporal y la estabilidad de resultados; si resulta insuficiente, se ampliará el historial o se limitarán las conclusiones al período evaluado.

- **Técnico — Crecimiento aparente por historial parcial (alta).** Comparar pocos meses de ingresos con un año completo podría inflar el crecimiento. Se analizarán antigüedad y meses observados; los clientes recientes se tratarán por separado o mediante una comparación ajustada y documentada.

- **Técnico — Calidad y fuga de información (alta).** Faltantes, cambios de categorías o variables posteriores al corte podrían distorsionar resultados. Se auditarán registros y fechas; se corregirán las agregaciones y se reconstruirá la evaluación cuando corresponda, manteniendo las salidas reales como parte del resultado.

- **Negocio — Crecimiento sin respuesta a la gestión (alta).** Un cliente podría aumentar ingresos por tarifas u otros factores aun sin intervención. Un piloto posterior evaluará el efecto comercial incremental; hasta entonces, la conclusión se limitará a identificar potencial y focalizar cuentas.

- **Negocio — Priorización poco rentable (alta).** Las cuentas con mayor probabilidad de crecer podrían aportar incrementos pequeños o exigir demasiados recursos. Se analizarán importes, carga y costos cuando estén disponibles; se ajustará la asignación sin equiparar probabilidad de crecimiento con rentabilidad.

- **Negocio — Cambios tarifarios o de mercado (alta).** Nuevas condiciones podrían alterar los patrones históricos. Se revisarán resultados por período y cambios de política comercial; ante degradación, se actualizará el modelo y se recalibrará la estrategia de priorización.

- **Datos y adopción — Restricciones de uso (alta).** La disponibilidad interna podría no implicar autorización académica. Se confirmarán permisos y medidas de anonimización; si no se autoriza el uso, se limitará el alcance a datos permitidos o se reconsiderará la viabilidad.

# **2. Comparación y selección de la idea más viable**

## **2.1. Metodología de comparación**

Se comparan las tres ideas con los seis criterios establecidos, utilizando **Alto (3), Medio (2) y Bajo (1)**. Alto indica una condición favorable y suficientemente sustentada para diseñar el proyecto; Medio refleja una condición plausible con verificaciones relevantes pendientes; Bajo corresponde a una limitación que impide sostener su viabilidad actual. Las calificaciones son juicios de diseño basados en la información disponible, no resultados de experimentación.

Los criterios tienen el mismo peso y se suman sobre un máximo de 18 puntos. En caso de empate se prioriza la menor incertidumbre para construir y evaluar el proyecto, revisando acceso a datos, target, evaluación y alcance. El valor y la acción se califican por su utilidad y concreción potenciales; ninguna idea ha demostrado todavía impacto causal en una organización.

## **2.2. Matriz comparativa y justificación**

| Criterio | Idea 1: acompañamiento académico | Idea 2: fibrilación auricular | Idea 3: crecimiento de ingresos |
|---|---|---|---|
| **Valor de negocio** | **Medio (2).** Mejoraría la focalización de tutorías, pero la institución es hipotética y no se han confirmado capacidad, costos ni necesidades operativas. | **Medio (2).** Podría mejorar la revisión de registros; falta validar la necesidad y el beneficio operativo con un prestador o aseguradora. | **Alto (3).** Se vincula directamente con ingresos y asignación de recursos de una empresa real, bajo un criterio comercial descrito por el equipo. El beneficio incremental sigue pendiente de prueba. |
| **Acceso a datos** | **Alto (3).** OULAD está descargado y su acceso público está confirmado; resta auditar los archivos. | **Medio (2).** Icentia11k está identificado y documentado, pero el equipo todavía no lo ha descargado ni inspeccionado. | **Medio (2).** El equipo dispone de tres años de registros, pero falta confirmar autorización de uso académico y condiciones de confidencialidad. |
| **Target** | **Alto (3).** El resultado final está documentado y permite distinguir reprobación, retiro y aprobación [1], [2]. | **Alto (3).** La fuente documenta anotaciones de fibrilación auricular [3], [4]. La construcción de etiquetas por ventana deberá verificarse al inspeccionar los datos. | **Alto (3).** El cambio anual de ingresos es reconstruible con las mediciones históricas disponibles, sujeto a continuidad, banda de estabilidad y tratamiento de historiales parciales. |
| **Acción** | **Medio (2).** Se propone priorizar revisión y contacto tutorial; la capacidad y el proceso institucional son simulados. | **Medio (2).** Se propone priorizar segmentos para revisión profesional; faltan capacidad, umbral y validación del flujo clínico. | **Alto (3).** Existen decisiones concretas de asignación de ejecutivos, campañas y ofertas. Su implementación y presupuesto deberán acordarse con la empresa. |
| **Evaluación** | **Alto (3).** Está definida la comparación estática/longitudinal, los cortes temporales y las métricas con presupuesto comparable. Es evaluable retrospectivamente. | **Medio (2).** Las anotaciones permiten evaluar detección, pero ventanas, baseline y métricas todavía están por definir. | **Medio (2).** Puede contrastarse la predicción con resultados anuales observados; tres años ofrecen pocas transiciones temporales para evaluar estabilidad. |
| **Alcance** | **Alto (3).** Dos clasificadores, cuatro cortes y características agregadas permiten acotar un MVP con preparación de datos, modelo, despliegue demostrativo y monitoreo. | **Medio (2).** El procesamiento de ECG, la selección de segmentos y la posible simulación IoT añaden complejidad todavía no dimensionada. | **Alto (3).** Una clasificación anual con datos tabulares y una salida de priorización comercial permite acotar un MVP; no requiere integrar CRM ni ejecutar campañas reales. |
| **Total / 18** | **16** | **13** | **16** |

La puntuación de target refleja que el resultado existe o puede reconstruirse; no implica que las etiquetas hayan sido auditadas. El alcance Alto de las ideas 1 y 3 presupone un MVP demostrativo, cuyo producto y entorno se definirán en la propuesta. La validación de ahorro, reducción de reprobación o incremento comercial atribuible a intervenciones requeriría pilotos posteriores.

## **2.3. Decisión y justificación de la selección**

**Se selecciona la idea 1: predicción temprana del riesgo de reprobación para priorizar el acompañamiento académico.** La decisión ha sido acordada por el equipo. Aunque las ideas 1 y 3 empatan con 16 de 18 puntos, se aplica el criterio de desempate de menor incertidumbre para construir y evaluar el proyecto: OULAD ya está descargado, el resultado está documentado y la comparación estática/longitudinal está delimitada.

La idea 1 ofrece la combinación más favorable de datos accesibles, un target observable, una acción concreta de revisión tutorial y un alcance acotado. Su valor potencial consiste en focalizar mejor el acompañamiento académico. La evaluación retrospectiva permitirá comparar predicciones y priorización con capacidad equivalente; la auditoría de calidad de los datos sigue pendiente.

La selección no presupone que el modelo alcanzará la mejora relativa del 10% ni que las tutorías reducirán efectivamente la reprobación. El proceso institucional será simulado y la meta predictiva deberá comprobarse. Estas limitaciones están identificadas y permiten mantener un alcance evaluable sin depender de un piloto institucional para completar el proyecto académico.

**La idea 3 conserva una aplicación empresarial directa y queda como alternativa para un desarrollo posterior.** Su principal limitación es la profundidad temporal: tres años de ingresos mensuales no equivalen a tres ejemplos anuales completos por cliente, porque cada ejemplo requiere información previa y un año posterior observado. Con ventanas anuales comparables, el esquema planteado permite una transición inicial para entrenamiento y otra para evaluación, lo que limita comprobar estabilidad entre años.

Un mayor número de clientes puede aportar observaciones, pero no reemplaza la diversidad de ciclos temporales. También quedan pendientes la autorización de uso académico y la auditoría de continuidad de los registros. Ampliar la historia fortalecería la evaluación de la idea 3; con los datos actuales podría realizarse una evaluación inicial, reconociendo estas restricciones. Su valor comercial no elimina esa incertidumbre frente a la idea 1.

**La idea 2 permanece como una oportunidad válida, con menor preparación actual:** falta adquirir e inspeccionar las señales y definir el diseño de evaluación. Su menor puntuación refleja esas dependencias y la complejidad por dimensionar, no una menor importancia del problema de salud.

La propuesta detallada de la sección 3 desarrolla la idea 1 seleccionada.

# **3. Propuesta del proyecto seleccionado**

**Título:** Predicción temprana del riesgo de reprobación mediante características longitudinales de actividad digital para priorizar el acompañamiento académico.

Esta sección desarrolla el diseño ampliado de la idea 1 seleccionada. Es el respaldo de detalle de la propuesta breve de 1 a 2 páginas y del pitch de seis diapositivas. Las decisiones metodológicas aquí propuestas se verificarán al auditar los datos; no se presentan resultados de modelos ni de intervenciones ya ejecutadas.

## **3.1. Problema de negocio y formulación de ciencia de datos**

### **3.1.1. Situación actual, afectados y oportunidad**

Se plantea una universidad hipotética con enseñanza apoyada en una plataforma digital y capacidad limitada de acompañamiento. En este escenario, la revisión de antecedentes al inicio del módulo y la atención posterior a dificultades manifiestas podrían dejar sin contacto preventivo a estudiantes cuyo riesgo cambia durante el período. El proceso institucional descrito es un supuesto de aplicación, no una práctica atribuida a The Open University ni a todas las universidades.

El problema afecta a estudiantes que podrían recibir apoyo tardíamente, a tutores que deben distribuir tiempo limitado y a responsables académicos que necesitan justificar la asignación de recursos. Reprobar puede generar necesidades de recuperación y retrasos en el avance académico; no se asumirá que cada reprobación produce abandono, un costo fijo o una sanción institucional.

La decisión que se busca mejorar es **a quién revisar y contactar durante el módulo**. Los antecedentes estáticos permiten una primera estimación, pero no registran cambios posteriores de actividad. Incorporar observaciones quincenales permitiría revisar la prioridad de atención. Una caída de interacción será una señal candidata que debe contextualizarse, no una prueba de desinterés o dificultad por sí sola.

**Cadena de valor:** dificultades potencialmente no detectadas → estimación de riesgo de reprobación → priorización de revisión según capacidad → contacto y evaluación del tutor → mejor focalización potencial del acompañamiento. La mejora de resultados educativos dependerá de la intervención y requerirá evidencia adicional.

### **3.1.2. Objetivos y pregunta de investigación**

**Objetivo de negocio:** mejorar la focalización del acompañamiento preventivo, identificando más casos de futura reprobación con una capacidad de revisión comparable. El proyecto evaluará una política de priorización retrospectiva; no prometerá reducción de reprobación ni ahorro institucional con datos que no registran el efecto de las tutorías.

**Objetivo analítico:** determinar si añadir características longitudinales de actividad digital mejora la predicción frente al uso exclusivo de variables estáticas, y cómo cambia ese aporte entre las semanas 2, 4, 6 y 8. La comparación utilizará los mismos algoritmos, población y criterios de evaluación en cada corte.

**Pregunta:** ¿la información sobre nivel, regularidad y evolución de la actividad digital permite detectar más estudiantes que posteriormente reprueban, a igualdad de cupos de revisión? La hipótesis admite que el aporte sea pequeño, inconsistente o nulo. Un resultado negativo bien evaluado también responderá la pregunta de investigación.

### **3.1.3. Unidad, población, target y horizonte**

| Elemento | Definición propuesta |
|---|---|
| **Unidad de predicción** | Una matrícula estudiante–módulo–edición. El mismo estudiante puede tener varias matrículas; su identificador sirve para vinculación y control de evaluación, no como predictor. |
| **Población inicial** | Matrículas registradas hasta el inicio oficial del módulo. Esta delimitación permite comparar con una estimación estática inicial; las inscripciones posteriores se cuantificarán y quedarán fuera del análisis principal. |
| **Elegibilidad por corte** | Matrículas de la población inicial que no se hayan retirado al finalizar el día del corte. Quienes se retiren después permanecerán con su resultado futuro correspondiente. |
| **Target** | Resultado final del mismo módulo: `Fail` → reprobación; `Withdrawn` → retiro; `Pass` o `Distinction` → aprobación. Las categorías proceden del resultado documentado en OULAD [1], [2]. |
| **Salida** | Probabilidades de las tres categorías. La probabilidad de reprobación será la señal principal para ordenar la revisión. Retiro no equivale a aprobación ni demuestra abandono definitivo de la universidad. |
| **Cortes** | Final de los días 14, 28, 42 y 56 desde el inicio. La información disponible hasta ese día se utilizará para una revisión posterior al corte. |
| **Horizonte** | Desde cada corte hasta el cierre del mismo módulo. Las ocho semanas son una ventana temprana, no la duración completa del curso; el horizonte se calculará por edición. |

La fecha futura de retiro y el resultado final se reservarán para construir etiquetas y evaluar resultados. Para determinar elegibilidad solo se comprobará si un retiro ya había ocurrido al corte; no se incorporará su fecha futura al vector de características. Los resultados inexistentes o inválidos se investigarán y no se convertirán automáticamente en reprobación.

### **3.1.4. Comparación de modelos y referencias**

Se utilizarán regresión logística multinomial y Random Forest como clasificadores de referencia. Para cada algoritmo se compararán dos configuraciones: antecedentes estáticos conocidos al inicio, y los mismos antecedentes enriquecidos con actividad digital hasta el corte. Los modelos enriquecidos podrán ajustarse por corte; la versión estática conservará su estimación individual al no recibir información nueva.

El baseline principal será la configuración estática del mismo algoritmo. La selección de parámetros tendrá un esfuerzo comparable y se realizará antes de evaluar el conjunto final. Como referencia operativa adicional se propondrá ordenar por días desde la última actividad registrada, con desempate determinista; será una regla simulada, no un proceso institucional confirmado. La ventana y el manejo de ausencia de actividad se fijarán antes de la prueba final.

Las variables de desempeño académico acumulado, como notas de evaluaciones, quedarán fuera de la comparación principal para aislar el aporte de la interacción digital. Una extensión posterior podría incorporarlas, manteniendo explícito que respondería otra comparación. No se interpretará la superioridad frente al baseline estático como superioridad frente a todo sistema de seguimiento académico posible.

### **3.1.5. Evaluación técnica y éxito operativo**

La métrica técnica principal será el área bajo la curva precisión–recobrado para la categoría de reprobación frente al resto (**PR-AUC**). Se reportarán también precisión y recobrado en las listas priorizadas, matriz de confusión entre las tres categorías y calibración de probabilidades. Se fijará la implementación de PR-AUC y se utilizará consistentemente. La exactitud global no será la única medida, porque puede ocultar errores en categorías menos frecuentes.

La evaluación principal de focalización se realizará en el día 56 con capacidad simulada del 10% de matrículas elegibles por edición. Para cada edición, `K = piso(0,10 × N elegibles)`; se seleccionarán las K puntuaciones más altas, con desempate estable independiente del target. Las ediciones sin capacidad suficiente para una comparación interpretable se reportarán por separado. Se explorarán 5% y 20% como sensibilidad, sin elegir retrospectivamente el escenario más favorable.

**Meta provisional:** aumentar al menos un 10% relativo el número de casos de futura reprobación incluidos en la lista, respecto al baseline estático y a igualdad de K. Si `TP_L` y `TP_E` representan esos casos en la versión longitudinal y estática, la mejora será `(TP_L − TP_E) / TP_E × 100`. Si `TP_E = 0`, el porcentaje será indefinido y se informará la diferencia absoluta. Pasar de 40 a 44 casos constituye un 10% relativo; no equivale a evitar cuatro reprobaciones.

Los cortes anteriores mostrarán el balance entre anticipación y calidad predictiva. Las diferencias entre cortes pueden reflejar cambios en la población elegible, por lo que se informarán su tamaño y composición. En cada corte, ambas configuraciones se evaluarán sobre exactamente las mismas matrículas. Se presentarán resultados agregados y por edición, junto con incertidumbre mediante remuestreo agrupado por estudiante cuando sea viable.

La familia de modelo que sustentará la comparación principal se fijará con validación; ambos algoritmos se reportarán sin escoger al ganador usando la prueba final. El cumplimiento de la meta, la consistencia entre ediciones y el costo adicional de procesamiento se considerarán conjuntamente. Una mejora puntual e incierta no se presentará como garantía de generalización.

### **3.1.6. Umbral, acción y juicio humano**

El umbral operativo será la puntuación del último caso que cabe dentro de K, no una probabilidad fija arbitraria. En una aplicación real, un tutor revisaría las alertas después de cada corte, contrastaría señales y contactos previos, y decidiría si corresponde orientación, tutoría o derivación. El modelo no determinará causas ni decisiones disciplinarias.

El resultado inmediato será una lista priorizada acompañada de actividad reciente, variación respecto al corte anterior e identificación de información insuficiente. Estas señales describirán asociaciones y no explicaciones causales. Los estudiantes que no aparezcan en la lista conservarían las vías habituales de apoyo.

## **3.2. Viabilidad técnica y de datos**

### **3.2.1. Fuente, acceso y cobertura**

OULAD es la fuente principal. El equipo confirma descarga y acceso, pero no se ha auditado aquí la copia local. Su publicación describe siete módulos y 22 ediciones de 2013–2014, 32.593 registros estudiante–módulo–edición y 10.655.280 registros de interacción diaria [1]. Estas cifras son documentales, no conteos verificados del archivo del equipo ni del subconjunto finalmente elegible.

| Fuente | Acceso y contenido previsto | Cobertura y restricciones por verificar |
|---|---|---|
| `studentInfo.csv` | Descarga confirmada por el equipo. Antecedentes y `final_result`, que aporta la etiqueta. | Una fila por matrícula; categorías, duplicados, faltantes y disponibilidad real al inicio. No tratar una variable como inicial solo por estar en esta tabla. |
| `studentVle.csv` | Descarga confirmada. Fecha relativa, recurso y cantidad de clics [2]. | Agregación diaria por estudiante y recurso; volumen por edición, cobertura, ausencia de actividad y registros fuera de rango. |
| `vle.csv` | Descarga confirmada. Características del recurso para contextualizar la actividad. | Consistencia de claves y tipos entre ediciones; no asumir idéntica oferta digital en todos los módulos. |
| `courses.csv` | Descarga confirmada. Módulo, edición y duración. | Una fila por edición; fechas y duración para determinar horizonte y disponibilidad de etiquetas históricas. |
| `studentRegistration.csv` | Descarga confirmada. Registro y retiro. | Una fila por matrícula; utilizar fechas de forma compatible con el corte y revisar inconsistencias. |
| `assessments.csv` y `studentAssessment.csv` | Identificadas en OULAD; no requeridas para el modelo principal. | Uso eventual para contexto; su contenido no se añadirá sin documentar temporalidad y nueva comparación. |
| Capacidad, costos e intervenciones tutoriales | No disponibles ni confirmados. | Se requieren registros institucionales para evaluar impacto real. Los cupos del estudio son supuestos de simulación. |

La publicación y la documentación oficial describen el esquema y su licencia CC BY 4.0 [1], [2]. Se mantendrá la atribución y se trabajará con identificadores anonimizados. La existencia de una fuente pública no elimina la necesidad de revisar calidad y representatividad. No se incorporarán movilidad física, datos privados universitarios ni información externa para identificar estudiantes.

### **3.2.2. Preparación y características**

La primera etapa generará un inventario de archivos, períodos, categorías, matrículas, estudiantes únicos y clases del target. Las uniones utilizarán claves completas para evitar multiplicación accidental de filas. Se documentarán exclusiones y el número de registros que pasa cada filtro. Cuando no existan eventos de actividad, se distinguirá cero observado de cobertura desconocida antes de imputar.

Los antecedentes candidatos incluirán educación previa, intentos anteriores, créditos y contexto del módulo. Su uso dependerá de verificar que representan información disponible al inicio; cualquier campo ambiguo se excluirá del modelo principal o se declarará como supuesto comprobable. Los identificadores de estudiante y recurso no se usarán para memorizar personas. Los atributos demográficos se revisarán para auditoría de errores y se justificará por separado cualquier incorporación predictiva.

Se construirán características digitales acumuladas y por intervalos de igual duración: clics, días activos, días desde la última interacción, variedad de tipos de recurso y cambios entre quincenas. El primer corte no tendrá una tendencia entre dos quincenas completas; esa ausencia se representará explícitamente. Se distinguirán nivel y cambio: estabilidad de actividad no supone suficiencia, y una caída no identifica automáticamente riesgo.

La definición de intervalos, el tratamiento del día cero y la actividad anterior al inicio se fijarán en un diccionario antes de entrenar. Todo resumen se calculará sin registros posteriores al corte. Imputación, escalamiento, codificación y cualquier normalización aprendida se ajustarán únicamente con entrenamiento. La inferencia utilizará exactamente las mismas transformaciones.

### **3.2.3. Validación temporal y control de información futura**

Se reservarán ediciones posteriores compatibles para prueba y se entrenará con ediciones previas del mismo módulo y período de inicio cuando existan. Una etiqueta de entrenamiento solo será válida si el módulo histórico ya había concluido antes de la predicción simulada. El año de inicio por sí solo no garantiza ese orden: se verificará también la duración y el momento de disponibilidad del resultado.

Dentro del histórico admisible se separará validación para ajustes, agrupando por estudiante y, cuando la cobertura lo permita, respetando el orden de ediciones. La evaluación principal se realizará con estudiantes no utilizados para ajustar el modelo; los repetidos entre entrenamiento y prueba se excluirán de la prueba principal y se contabilizarán. Todos los cortes de una misma matrícula permanecerán en la misma partición.

La auditoría determinará qué pares de ediciones permiten este diseño sin fuga. No se forzará la inclusión de todos los módulos. Si la cobertura es insuficiente, se acotará el estudio y se explicará su población de validez. La escasez de ediciones limita la certeza de generalización incluso si existen muchas filas de actividad.

### **3.2.4. Implementación y factibilidad**

Se trabajará en Python desde Visual Studio Code, dentro de un entorno local con dependencias aisladas y versionadas. Los datos de actividad se procesarán por agregaciones para evitar cargar repetidamente todo el histórico. Se medirán memoria, tiempo de preparación e inferencia antes de decidir si es necesario reducir el subconjunto.

La solución separará preparación, entrenamiento, evaluación e inferencia. El modelo y sus transformaciones se conservarán juntos con la versión de datos, características y parámetros. La factibilidad se apoya en datos descargados y modelos delimitados, pero permanece condicionada a la auditoría y a una primera ejecución de procesamiento; no se afirma que ya se hayan completado esos pasos.

## **3.3. Viabilidad de negocio**

### **3.3.1. Cambio del proceso y responsables**

En el escenario de referencia, la institución dispone de una revisión inicial y responde a dificultades manifiestas o solicitudes. La propuesta incorpora una revisión quincenal de prioridades. El coordinador definiría capacidad y reglas de atención; los tutores revisarían contexto y decidirían el contacto; el responsable analítico controlaría calidad de datos y desempeño. Estos roles son propuestos y no representan participantes institucionales comprometidos.

El uso previsto comienza cuando se publica la lista correspondiente a un corte. El tutor revisa actividad y evolución, verifica si ya existe un contacto y decide una acción de apoyo. En una implementación real se registrarían fecha, duración, acción, respuesta y seguimiento. La información analítica no sustituye la conversación con el estudiante ni acredita una causa concreta de su dificultad.

### **3.3.2. Capacidad y simulación de la decisión**

El escenario base admite revisar al 10% de matrículas elegibles por edición y corte. El supuesto simplificador es un costo equivalente por revisión; se analizarán también capacidades del 5% y 20%. No se convertirá el número de cupos en horas o dinero sin información institucional que lo sustente.

La comparación principal del día 56 evaluará la focalización de una lista de tamaño fijo. Como análisis complementario se reproducirán las cuatro listas usando la misma regla de capacidad para ambos enfoques. Cada revisión repetida consumirá un cupo y cada matrícula contará una sola vez entre los casos correctamente identificados acumulados. También se informarán estudiantes únicos, pues una persona puede aparecer en más de un módulo.

Esta simulación permitirá examinar repetición de alertas y casos detectados por primera vez. No será equivalente a un programa real de tutorías: no modifica las trayectorias observadas ni supone que todas las personas seleccionadas aceptan apoyo. Se documentarán los presupuestos utilizados para evitar atribuir a la predicción una ganancia derivada de aumentar contactos.

### **3.3.3. Métricas de valor y límites de la evidencia**

| Pregunta | Métrica y evidencia |
|---|---|
| ¿Qué tan bien predice? | PR-AUC, precisión, recobrado y calibración, utilizando resultados históricos observados. |
| ¿Focaliza mejor la capacidad simulada? | Casos de futura reprobación incluidos a igual K, diferencias relativas y absolutas, omisiones y contactos repetidos. |
| ¿Con cuánta anticipación identifica? | Tiempo entre primera selección y cierre del módulo. No representa el inicio real de las dificultades. |
| ¿Actuar mejora resultados educativos? | En un piloto posterior: diferencia en reprobación entre estrategias de atención comparables, acompañada de participación, costos y posibles efectos adversos. |

Para evaluar causalmente el programa, una institución tendría que comparar políticas de atención con capacidad equivalente, idealmente mediante un diseño experimental viable o, si no lo fuera, un diseño cuasiexperimental justificado. Se mediría la estrategia asignada y no solo quienes aceptaron tutoría, evitando confundir autoselección con eficacia. El protocolo requeriría acuerdo institucional y no forma parte de la ejecución actual.

El criterio de avance del prototipo combinará mejora de focalización, incertidumbre aceptable para continuar investigando y carga manejable en los escenarios. La reducción efectiva de reprobación, el ahorro y la transferencia a otra universidad no podrán concluirse únicamente de OULAD. Si la mejora no se sostiene, se recomendará conservar el baseline o revisar el diseño en lugar de afirmar éxito.

## **3.4. Riesgos y respuestas previstas**

- **R1. Aporte longitudinal insuficiente — Técnico; severidad alta.** **Supuesto:** las nuevas características mejoran la focalización de forma consistente. **Verificación:** comparación emparejada por algoritmo y corte, diferencias absolutas y relativas e incertidumbre por edición. **Respuesta:** reportar el resultado negativo, conservar el baseline cuando corresponda y no justificar complejidad adicional sin evidencia.

- **R2. Información futura en características o entrenamiento — Técnico; severidad crítica.** **Supuesto:** toda entrada y etiqueta histórica usada para ajustar el modelo era conocida en la fecha simulada. **Verificación:** auditoría de cortes, fechas de retiro, finalización de ediciones, particiones y transformaciones. **Respuesta:** corregir el conjunto, reconstruir modelos y retirar conclusiones obtenidas con fuga.

- **R3. Falta de actividad confundida con falta de datos — Técnico; severidad alta.** **Supuesto:** los resúmenes representan actividad registrada comparable. **Verificación:** cobertura por edición y recurso, duplicados, faltantes y cambios de calendario. **Respuesta:** distinguir estados desconocidos, excluir fuentes o ediciones inconsistentes y mostrar información insuficiente en lugar de asignar riesgo sin sustento.

- **R4. Transferencia limitada — Técnico y de negocio; severidad alta.** **Supuesto:** las relaciones se mantienen en ediciones posteriores y poblaciones pertinentes. **Verificación:** evaluación por módulo, período y subgrupos con volumen suficiente. **Respuesta:** restringir el alcance declarado, recalibrar o solicitar validación externa antes de una adopción institucional.

- **R5. Capacidad y carga irreales — Negocio; severidad alta.** **Supuesto:** la revisión propuesta es viable para los tutores. **Verificación:** sensibilidad de capacidad, contactos repetidos y, en una futura adopción, tiempos reales de revisión. **Respuesta:** ajustar frecuencia, listas y reglas de seguimiento; no presentar eficiencia monetaria sin datos de costos.

- **R6. Detección sin efecto del apoyo — Negocio; severidad alta.** **Supuesto:** identificar antes permite una intervención útil y aceptada. **Verificación:** piloto posterior con comparación de políticas, participación y resultados. **Respuesta:** limitar la conclusión a predicción y focalización, y revisar el servicio de acompañamiento antes de ampliar su uso.

- **R7. Errores desiguales o pérdida de confianza — Adopción; severidad alta.** **Supuesto:** las alertas son comprensibles y sus errores no perjudican desproporcionadamente a ciertos grupos. **Verificación:** análisis de falsos positivos y negativos por subgrupos y revisión del lenguaje de la interfaz; consulta a tutores en una etapa posterior. **Respuesta:** ajustar variables o reglas, mantener juicio humano y evitar etiquetas sancionatorias.

- **R8. Procesamiento o cobertura incompatibles con el MVP — Técnico y de alcance; severidad media-alta.** **Supuesto:** los archivos pueden procesarse y existen suficientes ediciones compatibles. **Verificación:** inventario y primera ejecución con medición de recursos. **Respuesta:** limitar módulos con criterios de calidad definidos antes de mirar resultados; preservar la comparación estática/longitudinal y documentar la menor generalización.

## **3.5. Alcance y MVP**

### **3.5.1. Producto propuesto**

Se propone un MVP de análisis y priorización académica que reciba datos históricos con esquema validado, genere estimaciones para los cuatro cortes y permita consultar listas y evolución del riesgo. Incluirá un informe comparativo y un mecanismo de inferencia reproducible. La forma concreta de interacción —interfaz local, reporte navegable o servicio demostrativo— se elegirá durante la implementación, sin comprometer Colab como entorno de ejecución final.

El despliegue será demostrativo en un entorno controlado y separado del entrenamiento. El usuario podrá seleccionar edición, corte y capacidad; observará las probabilidades, señales disponibles y advertencias de calidad. El resultado final observado se mostrará únicamente en la vista de evaluación retrospectiva, claramente separado de la información que habría existido al emitir la alerta.

### **3.5.2. Etapas y evidencias de terminación**

| Etapa | Trabajo y evidencia verificable |
|---|---|
| **DATOS** | Inventario, diccionario, claves y reglas de elegibilidad; reporte de cobertura, calidad y exclusiones; subconjunto reproducible. |
| **EXPLORACIÓN / FEATURES** | Análisis de clases y actividad por edición; construcción de antecedentes y ventanas; comprobaciones de que cambiar datos futuros no altera características de un corte anterior. |
| **MODELO** | Comparación estática/longitudinal con regresión logística y Random Forest, validación documentada, prueba reservada y reporte de métricas e incertidumbre. |
| **DESPLIEGUE** | Modelo y transformaciones versionados, inferencia desde entradas validadas y demostración ejecutable mediante instrucciones de instalación y uso. |
| **MONITOREO** | Registro de versión, faltantes, volúmenes, distribución de puntuaciones y tamaño de listas; desempeño cuando se incorporen etiquetas observadas. |

El monitoreo se probará mediante reproducción histórica, no mediante conexión a una universidad. Se definirán rangos de referencia con entrenamiento y validación, sin atribuir a variaciones de datos una caída de precisión hasta disponer de resultados. Una entrada inválida impedirá emitir una predicción normal; cambios relevantes generarán una señal para revisión, no un reentrenamiento automático.

### **3.5.3. Criterios de aceptación y exclusiones**

El MVP se considerará técnicamente completo si reproduce las transformaciones y predicciones, verifica el respeto de los cortes, utiliza las mismas poblaciones y presupuestos para comparar, conserva la prueba final independiente y entrega resultados trazables con sus limitaciones. El cumplimiento de la meta del 10% se informará por separado: finalizar correctamente el proyecto no equivale a confirmar la hipótesis.

Quedan fuera del alcance la integración con plataformas institucionales, la captura en tiempo real, el contacto con estudiantes, la ejecución de tutorías, decisiones disciplinarias, movilidad física, predicción de abandono institucional, demostración causal de impacto y cuantificación de ahorro sin datos. No se incorporarán modelos complejos de secuencias como requisito del MVP.

Antes de implementar se confirmarán la ruta de los archivos descargados, los módulos y ediciones elegibles, las variables realmente disponibles al inicio y los recursos de ejecución. Estas verificaciones no cambian la selección de la idea, pero pueden ajustar su subconjunto de análisis. La propuesta breve conservará las decisiones esenciales, la evidencia de viabilidad y los riesgos en 1 a 2 páginas, conforme a los requisitos actualizados. Este documento ampliado conserva el detalle para continuar el proyecto.

# Referencias

[1] J. Kuzilek, M. Hlosta y Z. Zdrahal, “Open University learning analytics dataset,” *Scientific Data*, vol. 4, art. núm. 170171, nov. 2017, doi: [10.1038/sdata.2017.171](https://doi.org/10.1038/sdata.2017.171).

[2] The Open University, “Open University Learning Analytics dataset,” *OU Analyse*. [En línea]. Disponible en: https://research.stem.open.ac.uk/ouanalyse/open-dataset-more/. [Consultado: 28-oct-2026].

[3] S. Tan et al., “Icentia11k Single Lead Continuous Raw Electrocardiogram Dataset,” versión 1.0, *PhysioNet*, abr. 2022, doi: [10.13026/kk0v-r952](https://doi.org/10.13026/kk0v-r952).

[4] S. Tan et al., “Icentia11K: An Unsupervised Representation Learning Dataset for Arrhythmia Subtype Discovery,” en *Computing in Cardiology (CinC)*, 2021. [En línea]. Disponible en: https://www.cinc.org/2021/Program/accepted/229_Preprint.pdf. [Consultado: 28-oct-2026].


---



---

## M. Enunciado del PSet 2 para `pset-02/enunciado.md`

Transcripción del documento entregado por el usuario. Conservar los requisitos; la organización `pset_2/` del ejemplo se adapta a la carpeta `pset-02/` solicitada sin agregar un nivel duplicado. Los valores 120 y 4.3 % que aparecen como ejemplos del profesor no son resultados de OULAD.

PSet #2: Pipeline de Datos End-to-End
Ciencia de Datos
En el PSet #1 definiste un proyecto de ciencia de datos, justificaste su viabilidad y determinaste
qué datos necesitas. En este PSet debes construir la infraestructura y la tubería de datos que
alimentarán ese proyecto.
El objetivo es implementar un pipeline ELT reproducible desde la fuente hasta Snowflake
utilizando Kestra, dbt y Spark.
Al finalizar debes tener:
Fuente → Kestra → Raw → dbt → Bronze → dbt → Silver → dbt → Gold → Spark → OBT
Este PSet termina con datos limpios, modelados y preparados para las siguientes etapas del
proyecto.
1. Arquitectura
Diseña e implementa una arquitectura en la que Snowflake sea el destino de los datos.
Kestra debe encargarse de la ingesta y la orquestación. dbt debe realizar las transformaciones
y construir las capas Bronze, Silver y Gold. Spark debe utilizarse para construir una One Big
Table (OBT) a partir de los datos procesados.
La infraestructura local debe definirse en el archivo docker-compose.yml e incluir, como
mínimo: Kestra y Spark. Puedes utilizar dbt Core en Docker o en dbt Cloud.
Incluye un diagrama de la arquitectura implementada.
2. Ingesta con Kestra
Construye un flujo en Kestra que extraiga los datos de la fuente de tu proyecto y los cargue en
Snowflake.
La ingesta debe poder realizarse sin intervención manual.
Debes implementar y poder explicar:
● Trigger y frecuencia de ejecución
● Manejo de errores y retries

● Backfill de datos históricos.
Los datos originales deben almacenarse en un esquema Raw.
3. Calidad y limpieza de datos
Analiza la calidad de los datos antes de transformarlos.
Como mínimo, debes revisar la completitud, la precisión, la consistencia y la validez.
No basta con limpiar los datos. Debes justificar las decisiones tomadas.
Para los problemas principales, documenta:
| Problema | Evidencia | Acción | Justificación |
|---|---|---|---|
| IDs duplicados | 120 registros | Conservar registro más reciente | Representa la última actualización |
Las transformaciones de limpieza deben realizarse con dbt para generar la capa de Staging.
4. Modelado dimensional con dbt
A partir de Silver construye una capa Gold siguiendo un star schema.
Debes definir claramente el grano de la tabla de hechos y construir las dimensiones necesarias
para tu proyecto.
Incluye un diagrama del modelo dimensional.
Tu proyecto de dbt debe utilizar source() y ref() para gestionar las dependencias entre
modelos e incluir pruebas de calidad relevantes, como not_null, unique y relationships.
¡Los tests deben validar las reglas de tus datos y del problema de negocio!
5. OBT con Spark
Utiliza Spark para construir una One Big Table a partir de las tablas Gold.
La OBT debe integrar la información necesaria para alimentar el futuro modelo de ciencia de
datos.
Debes definir su grano y validar que los joins no hayan introducido duplicados ni hayan
modificado incorrectamente el número de observaciones.

El resultado debe almacenarse nuevamente en Snowflake.
En el documento debes explicar cuándo utilizarías el star schema y cuándo la OBT en tu
proyecto.
6. Batch vs. streaming
Tu pipeline se implementará mediante procesamiento por lotes.
Justifica esta decisión considerando la frecuencia con la que se generan los datos y la latencia
que realmente requiere el problema de negocio.
Explica también qué tendría que cambiar en el caso de uso para justificar una arquitectura de
streaming.
NO debes implementar streaming.
Documento técnico
Entrega un documento técnico de hasta 6 páginas, sin contar los anexos.
El documento debe explicar tu implementación y las decisiones tomadas, NO definir
teóricamente qué son Kestra, dbt, Spark o Snowflake.
Debe contener:
1. Arquitectura
Diagrama de la infraestructura y explicación del flujo de datos.
2. Ingesta
Fuente, frecuencia, granularidad, proceso de carga, retries y estrategia de backfill para crear
Raw.
3. Data Quality
Problemas encontrados, evidencia y decisiones de limpieza.
Utiliza métricas concretas. Por ejemplo:
El 4.3% de los registros no tenía customer_id.

4. Transformaciones y modelado
Explica la construcción de Bronze, Silver y Gold. Define el grano de la tabla de hechos y
presenta el esquema de estrella.
5. Spark y OBT
Explica cómo construiste la OBT, cuál es su grano y cómo validaste los joins.
6. Batch vs. streaming
Justifica por qué el batch es suficiente actualmente y bajo qué condiciones utilizarías streaming.
7. Limitaciones
Documenta problemas de datos o de arquitectura que aún no se hayan resuelto.
Repositorio
El repositorio debe permitir reproducir el pipeline.
La estructura del repo:
pset_2/
├── docker-compose.yml
├── .env.example
├── README.md
├── kestra/
├── dbt/
├── spark/
└── docs/
El README.md debe explicar cómo levantar la infraestructura y ejecutar Kestra, dbt y Spark.
¡No subas contraseñas, tokens ni credenciales al repositorio!

Entregables
| Entregable | Requisito |
|---|---|
| Repositorio | Código del pipeline y README |
| Documento técnico | Máximo 6 páginas |
| Arquitectura | Diagrama de infraestructura |
| Snowflake | Raw, Bronze, Silver, Gold y OBT |
| Kestra | Ingesta, retry y backfill funcionando |
| dbt | Limpieza, star schema y tests |
| Spark | Construcción de la OBT |
Nombre del documento: PSet2_memo_<apellido_1>_<apellido_2>.pdf

---

## N. Rúbrica del PSet 2 para `pset-02/rubrica.md`

# PSet 2: Rúbrica de evaluación

Transcripción de la tabla del documento compartido por el profesor. La implementación y las evidencias se desarrollarán en la etapa PSet 2.

| Criterio | Peso |
|---|---|
| Kestra, ingesta y orquestación para Raw | 15 % |
| Calidad y limpieza de datos | 20 % |
| dbt y arquitectura Bronze/Silver/Gold | 15 % |
| Star schema | 15 % |
| Spark y OBT | 15 % |
| Infraestructura y reproducibilidad | 10 % |
| Documento técnico y decisiones de arquitectura | 10 % |
| **Total** | **100 %** |

Fuente: documento «PSet #2: Pipeline de Datos End-to-End», página 5, facilitado por el usuario. El enunciado completo se conserva en `enunciado.md`.


---

## O. Rúbrica del PSet 1 para `pset-01/rubrica.md`

Conservar el texto siguiente como referencia del profesor, distinguiéndolo de la organización del repositorio en cuatro etapas.

# PSet 1: Rúbrica de evaluación

> PSet 1 es uno de los 5 PSets del curso, que en conjunto valen 25% de la nota final (ver `Sistema de Evaluación` del cronograma). Por defecto, los 5 PSets pesan igual entre sí (5% cada uno de la nota total), salvo que yo decida una ponderación distinta.

Los tres entregables de PSet 1 (Canvas de Viabilidad y Riesgos, Documento de propuesta, Presentación de negocio) se evalúan como una sola entrega, con los cinco criterios de esta rúbrica. Cada criterio se califica en una escala de 0 a 4; la nota final del PSet es el promedio de los cinco.

## 1. Formulación del problema y métrica de éxito

| Nivel | Descripción |
|---|---|
| 4, Excelente | La predicción es una salida concreta y medible (no el objetivo de negocio completo); la métrica de éxito es verificable con datos reales identificados, con punto de comparación (grupo de control o línea base); el umbral de decisión está justificado con una razón de negocio explícita, nombrando qué tipo de error cuesta más caro. |
| 3, Logrado | Predicción y métrica cumplen lo anterior, pero el umbral de decisión no tiene una justificación de negocio explícita, o falta el punto de comparación. |
| 2, En desarrollo | La predicción todavía confunde el objetivo de negocio con la salida concreta a predecir (ej. "predecir si el proyecto va a tener éxito"), o la métrica de éxito no es verificable con datos reales identificados. |
| 1, Insuficiente | No hay una predicción concreta ni una métrica de éxito, o ambas son genéricas ("mejorar la retención", "usar IA para optimizar"). |

## 2. Viabilidad técnica (predicción y datos)

| Nivel | Descripción |
|---|---|
| 4, Excelente | Cada dato necesario tiene su estado real marcado (ya existe con acceso confirmado / existe sin acceso confirmado / no existe todavía), con la fuente identificada cuando aplica. |
| 3, Logrado | Los datos necesarios están identificados, pero al menos uno no tiene su estado de acceso verificado o documentado. |
| 2, En desarrollo | Se listan los datos en términos generales ("datos de uso", "información de ventas") sin especificar de dónde saldrían ni si existen. |
| 1, Insuficiente | No se abordan los datos necesarios, o se asume sin evidencia que "los datos existen". |

## 3. Viabilidad de negocio (acción, juicio, resultado)

| Nivel | Descripción |
|---|---|
| 4, Excelente | La acción que cambia está claramente definida y depende directamente de la predicción; el juicio humano (quién decide, en qué casos el sistema actúa solo) está explícito; el resultado se mide con una métrica de negocio, no solo una métrica técnica del modelo. |
| 3, Logrado | Los tres elementos están presentes, pero alguno queda parcialmente desarrollado (ej. el juicio humano se menciona pero no se explica en qué casos interviene). |
| 2, En desarrollo | La predicción no está atada a una acción concreta ("sería interesante saber esto"), sin que quede claro qué decisión cambiaría. |
| 1, Insuficiente | No se aborda la viabilidad de negocio, o se limita a afirmar que el proyecto "generaría valor" sin especificar cómo. |

## 4. Riesgos

| Nivel | Descripción |
|---|---|
| 4, Excelente | Al menos dos riesgos, cada uno nombrando el supuesto concreto que rompe (no una descripción genérica), con evidencia real o un plan concreto de verificación, y una estimación de gravedad si ocurre. |
| 3, Logrado | Al menos dos riesgos con el supuesto identificado, pero sin evidencia ni plan de verificación para al menos uno. |
| 2, En desarrollo | Los riesgos son genéricos ("podría fallar el modelo", "podría no gustarle a los usuarios"), sin nombrar el supuesto que rompen. |
| 1, Insuficiente | Menos de dos riesgos, o ninguno verificable. |

## 5. Calidad del paquete como material profesional

| Nivel | Descripción |
|---|---|
| 4, Excelente | El documento de propuesta se entiende sin haber estado en la sesión de clase, en el orden pedido (problema/métrica, viabilidad técnica, viabilidad de negocio, riesgos), entre 1 y 2 páginas. La presentación sigue el formato de pitch a un patrocinador (problema y oportunidad, solución, evidencia de viabilidad, riesgos, qué se necesita para avanzar), no el formato de diapositiva de clase, en 5 a 8 diapositivas. Los tres entregables son consistentes entre sí (mismos datos, misma predicción, mismos riesgos). |
| 3, Logrado | Los tres entregables están completos y son consistentes entre sí, pero alguno se sale del formato pedido (ej. la presentación repite el formato de texto plano de las diapositivas de clase, o el documento excede las 2 páginas sin necesidad). |
| 2, En desarrollo | Falta uno de los tres entregables, o hay inconsistencias notorias entre ellos (datos distintos, riesgos distintos). |
| 1, Insuficiente | Falta más de un entregable, o el contenido es copia directa del laboratorio de clase sin revisión ni mejora. |

## Nota sobre el criterio central

El criterio que atraviesa los cinco puntos, tomado directamente del enunciado de PSet 1: la viabilidad técnica y de negocio debe estar sustentada con evidencia concreta del proyecto propio, no con afirmaciones genéricas, y los riesgos identificados deben ser específicos y verificables, siguiendo el mismo criterio de evidencia usado en la Semana 1, Sesión 2 y en el laboratorio de Semana 2, Sesión 2. Un entregable que suena profesional en el formato pero es vago en el contenido no califica como Excelente en ningún criterio, aunque esté bien escrito.

---
*Última actualización: 2026-08-31*