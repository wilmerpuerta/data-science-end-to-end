# PSet 3: enunciado extraído

Fuente: [PDF original](CD_PSet_3.pdf). Extracción textual; el PDF conserva la maquetación oficial.

## Página 1

PSet #3: Experimentación y Selección del 
Modelo 
Ciencia de Datos 
En el PSet #2 construiste el pipeline que carga la OBT de tu proyecto en Snowflake. En este 
PSet, experimentarás para encontrar el mejor modelo de ML para tu caso de negocio, 
respaldado por evidencia. 
El objetivo es experimentar como lo haría un equipo de ciencia de datos: explorar los datos, 
construir features sin fuga de datos, comparar una línea base con varios modelos candidatos, 
ajustar los hiperparámetros de los mejores y elegir un ganador. Cada ejecución y cada modelo 
deben quedar registrados y versionados en MLflow. 
Al finalizar debes tener: 
OBT → EDA → Features → Pipeline → Línea base → Candidatos → Tuning → Selección → 
Model Registry 
Este PSet termina con un modelo registrado en MLflow y listo para desplegarse en el PSet #4 
(Proyecto Final). 
Importante: este PSet evalúa la calidad de la evidencia, no la métrica más alta!  
Un modelo modesto bien evaluado tiene más valor que uno ‘state-of-the-art’ sin 
fundamento. 
1. Exploración de datos (EDA) 
Explora la OBT en un notebook antes de modelar. 
Como mínimo debes revisar: 
●​ Tamaño, tipos de datos y valores faltantes por columna. 
●​ Estadística descriptiva de las variables 
●​ La distribución del target y sus características. 
●​ Detección de valores atípicos con IQR (diagrama de caja) y Z-score (≥ 3 desviaciones 
estándar). 
●​ La relación entre el target y las características: Pearson o Spearman (justificar) 
●​ El desbalance de clases, si tu problema es de clasificación. 
Documenta al menos 3 hallazgos que afecten el modelado: 


## Página 2

 
Hallazgo 
Evidencia 
Consecuencia en el modelo 
Target con cola 
larga 
El 2% de las tarifas supera 
$200 
Usar MAE en lugar de RMSE y probar 
log(target) 
Un insight es valioso si explica qué cambia en el experimento. 
2. Features 
Diseña al menos 2 features derivadas. Al menos una de ellas debe derivarse de un hallazgo de 
la EDA. 
Para cada feature explica: 
●​ Qué evidencia muestra que aporta. 
●​ ¿Por qué ya existe en el momento de la inferencia? 
●​ ¿Qué codificación usarás si se trata de una variable categórica? 
¡Una feature que no existe en el momento de la predicción es un caso de data leakage! 
3. Preparación y esquema de validación 
La imputación, la codificación y el escalado se realizan dentro de un Pipeline y un 
ColumnTransformer de scikit-learn que se ajustan solo con los datos de entrenamiento. La 
preparación vive en src/pipeline.py, y los notebooks la importan en lugar de copiarla. 
Divide los datos una sola vez: 
Conjunto 
Uso 
Entrenamiento 
Validación cruzada, comparación de modelos y tuning 
Prueba 
(hold-out) 
Se usa una sola vez, al final, con el ganador y el segundo 
mejor 
Elige el esquema de validación cruzada que corresponde a tus datos y justifícalo: 
●​ Temporal (TimeSeriesSplit): separación basada en un punto en el tiempo. 
●​ Por grupo (GroupKFold): separación por grupos. 
●​ Aleatorio (train_test_split): todos tienen la misma probabilidad de ser 
seleccionados. 
●​ Estratificado (StratifiedKFold): mantiene la distribución de clases. 


## Página 3

 
Usa las métricas que ya definiste: 
●​ Métrica técnica: la misma para todos los modelos. 
●​ Métrica de negocio: refleja el costo del error más costoso de tu proyecto. 
Si en el experimento te das cuenta de que otra métrica es mejor, la cambias y justificas el 
cambio. 
4. MLflow: servidor de tracking 
Agrega MLflow a tu docker-compose.yml como servidor de tracking, con un backend store y 
un artifact store. 
Crea un experimento con el nombre de tu proyecto. Cada ejecución debe registrar lo siguiente: 
Qué 
Ejemplo 
Parámetros 
Hiperparámetros y semilla 
Datos 
Tabla de origen, fecha de corte del snapshot y hash del dataset 
Métricas 
Entrenamiento, promedio y desviación de la CV, segundos de 
entrenamiento 
Tags 
Fase (baseline, candidato, tuning, final), familia del modelo y 
commit de Git 
Artefactos 
El pipeline entrenado (mlflow.sklearn.log_model) con su firma y un 
ejemplo de entrada 
Una corrida que no puedes reproducir no cuenta como evidencia. 
5. Línea base 
Antes de entrenar cualquier modelo, entrena dos líneas base: 
1.​ Ingenua: DummyRegressor o DummyClassifier (media, mediana o clase más 
frecuente). 
2.​ De negocio: la regla o el proceso actual definido en el PSet #1 (si existe). 
Todo modelo candidato tiene que superar a las dos. Si alguno no lo logra, documéntalo como 
hallazgo. 
 


## Página 4

6. Modelos candidatos 
Entrena al menos 5 familias de modelos con sus hiperparámetros por defecto. Todos deben 
usar la misma preparación, la misma validación y la misma métrica. 
Familia 
Ejemplo  
Lineal regularizado 
Ridge, Lasso, LogisticRegression, etc 
Bagging 
RandomForest, etc 
Boosting 
HistGradientBoosting, XGBoost,  LightGBM, 
etc 
Red neuronal 
MLPRegressor, MLPClassifier, etc 
State of the Art 
Modelos fundacionales generativos: 
TimesFM, Trimestral, GPT, Claude, etc. 
Para cada modelo, reporta la métrica en entrenamiento y en CV, la brecha entre ambas y el 
tiempo de entrenamiento. Usa esos números para diagnosticar el sobreajuste. 
Además, prueba un LLM mediante prompting. Si tu problema no se puede plantear de esa 
forma, explica por qué. 
7. Ajuste de hiperparámetros (fine-tuning) 
Ajusta los 3 mejores candidatos de la fase anterior: 
●​ Usa búsqueda de hiperparámetros (RandomizedSearchCV), Optuna o búsqueda 
exhaustiva. Justifica tu elección. 
●​ Evalúa al menos 30 configuraciones por modelo, utilizando el mismo esquema de CV. 
●​ Define y justifica el espacio de búsqueda: rangos y escala. Por ejemplo, la tasa de 
aprendizaje se expresa en escala logarítmica. 
●​ Registra cada configuración como corrida hija (nested run) dentro de una corrida padre 
por modelo. 
Reporta cuánto mejoró cada modelo respecto a su versión sin ajustar. Si la mejora es menor 
que la desviación entre pliegues, no se considera mejora. 
 
 
 


## Página 5

Presupuesto mínimo de experimentación: 
Fase 
Ejecuciones 
mínimas 
Línea base 
2 
Candidatos 
5 
Tuning 
90 (3 modelos 
× 30) 
Final 
1 
8. Selección del modelo ganador y registro 
Elige el ganador con evidencia en los experimentos: 
1.​ Compara el ganador con el segundo mejor usando el promedio y la desviación de la CV. 
¿La diferencia supera la variación entre pliegues? 
2.​ Evalúa ambos una sola vez en el conjunto de prueba. 
3.​ Calcula la métrica de negocio. Si clasificas, elige el umbral de decisión según el costo 
de cada tipo de error. 
4.​ Compara el costo y la explicabilidad: tiempo de entrenamiento e inferencia. ¿Puedes 
explicar por qué el modelo hace una predicción? 
Registra el ganador en el Model Registry de MLflow: 
●​ Nombre: <proyecto>-modelo 
●​ Alias: champion para el ganador y challenger para el segundo mejor. 
En un notebook limpio, carga el modelo desde models:/<proyecto>-modelo@champion y 
reproduce exactamente la métrica registrada. 
Exporta las ejecuciones del experimento a docs/corridas.csv usando 
mlflow.search_runs. El servidor está en su máquina local y yo no tengo acceso a él. 
 
Documento técnico 
Entrega un documento técnico de hasta 6 páginas, sin contar los anexos. 
El documento debe explicar tus decisiones, NO definir qué son MLflow, la validación cruzada ni 
ningún concepto ya revisado en clase.  


## Página 6

Debe contener: 
1. EDA 
Los hallazgos, con su evidencia y su consecuencia en el modelo. Tablas y gráficos estadísticos, 
boxplots, distribuciones, gráfico de calor de correlación, etc.  
2. Features 
Las features derivadas, con su justificación y la prueba de que no presentan fuga. 
3. Preparación y validación 
La división de los datos, el esquema de CV y las dos métricas. 
4. Diseño experimental 
¿Cuántas ejecuciones hiciste, qué registraste en cada una y una captura de pantalla de la 
comparación en la interfaz de MLflow? 
5. Resultados 
Una tabla y gráficos con todos los modelos: métrica en entrenamiento, en CV (promedio ± 
desviación), brecha, learning rate y tiempo. 
6. Tuning 
El espacio de búsqueda, el número de configuraciones y la mejora respecto al modelo por 
defecto. Una tabla y unos gráficos con los resultados del tuning de los modelos. 
7. Decisión 
El modelo ganador con su run_id y su versión en el registro, la métrica de prueba, la métrica 
de negocio y la razón por la que gana frente al segundo mejor. Tablas y gráficos de los 
resultados. 
8. Limitaciones 
Lo que limitó su experimento con justificación y evidencia. 
 
Repositorio 
El repositorio debe permitir reproducir cada experimento. 
La estructura del repositorio: 


## Página 7

None‎
pset_3/ 
├── docker-compose.yml 
├── .env.example 
├── requirements.txt 
├── README.md 
├── notebooks/ 
│   ├── 01_eda.ipynb 
│   ├── 02_features.ipynb 
│   ├── 03_baseline_candidatos.ipynb 
│   ├── 04_tuning.ipynb 
│   └── 05_seleccion.ipynb 
├── src/ 
│   ├── datos.py 
│   └── pipeline.py 
└── docs/ 
    └── corridas.csv 
    └── PSet3_memo_<apellido_1>_<apellido_2>.pdf 
El README.md debe explicar cómo levantar MLflow, cómo configurar la conexión a Snowflake 
y el orden de ejecución de los notebooks. 
Antes de entregar, ejecuta cada notebook primero con Restart y luego con Run All. Se 
calificará con la salida guardada. 
¡No subas contraseñas, tokens ni credenciales al repositorio! 
 
Entregables 
Entregable 
Requisito 
Repositorio 
Notebooks, src/ y README 
Documento técnico Máximo 6 páginas 
MLflow 
Servidor en Docker y experimento con todas las 
corridas 
Experimentación 
2 líneas base, 5 candidatos y tuning de los 3 mejores 
modelos 


## Página 8

Model Registry 
Ganador con alias champion, reproducible 
Evidencia 
docs/corridas.csv 
Nombre del documento: PSet3_memo_<apellido_1>_<apellido_2>.pdf 
 
Rúbrica 
Criterio 
Peso 
EDA y features 
15% 
Preparación sin fuga y esquema de 
validación 
15% 
Línea base y comparación de candidatos 
15% 
Ajuste de hiperparámetros 
15% 
Tracking y registro en MLflow 
20% 
Selección del modelo y métrica de negocio 
15% 
Reproducibilidad y documento técnico 
5% 
Total 
100%
