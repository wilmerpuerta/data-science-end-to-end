# Validación de ejecutables de pset_3

Fecha local: 2026-11-18T22:26:27.386348-05:00.

Resultado: reproducción funcional comprobada desde `pset_3`, con las dependencias privadas originales disponibles. Se verificaron los 24 archivos de `scripts/`, distinguiendo los ejecutables de las dos bibliotecas auxiliares. Los modos científicos que volverían a entrenar y la autenticación real de OpenAI no se ejecutaron.

## Evidencia principal

| Comprobación | Resultado |
|---|---|
| Entorno propio | Python 3.11.16; dependencias fijadas; kernel `pset3-entrega` apunta a `pset_3/.venv` |
| Notebooks | 01-05 y anexo 06 ejecutados en kernels nuevos, sin errores |
| Pruebas | 48 aprobadas en el entorno propio |
| Fuentes | 52 archivos Python analizados; 20 módulos importados desde esta distribución |
| Auditoría | 21 comprobaciones aprobadas; 370 pipelines verificados |
| Champion | Predicciones exactamente iguales; diferencia máxima 0 |
| Docker | Compose válido, imagen construida, servidor temporal con HTTP 200; sin montar volúmenes históricos |
| Memo | Generación temporal de seis páginas; las seis coinciden píxel a píxel a 110 dpi con el PDF aprobado |
| MLflow y explicación | Captura real y contraste local ejecutados en copias temporales |
| Consumo | 382 corridas antes y después; cero llamadas nuevas; gasto histórico USD 1,1167655 de USD 10 |

## Cobertura por archivo

| Archivo | Prueba realizada |
|---|---|
| `scripts/auditar_entrega.py` | 21 comprobaciones y 370 pipelines verificados. |
| `scripts/capturar_mlflow.py` | Dependencias verificadas y captura real en copia temporal. |
| `scripts/cerrar_notebooks_cuando_listo.py` | Cierre real del estudio completo, sin espera indefinida. |
| `scripts/congelar_protocolo.py` | Protocolo y hashes comprobados. |
| `scripts/ejecutar_ablacion.py` | Modo predeterminado y --verificar: evidencia completa y protocolo válidos; sin entrenamiento nuevo. |
| `scripts/ejecutar_anticipacion.py` | Modo predeterminado y --verificar: evidencia completa y protocolo válidos; sin entrenamiento nuevo. |
| `scripts/ejecutar_comparacion.py` | Modo predeterminado y --verificar: evidencia completa y protocolo válidos; sin entrenamiento nuevo. |
| `scripts/ejecutar_estudio.py` | Verificación de estudio cerrado; no se usó --reanudar. |
| `scripts/ejecutar_negocio.py` | Modo predeterminado y --verificar: evidencia completa y protocolo válidos; sin entrenamiento nuevo. |
| `scripts/ejecutar_notebooks_entrega.py` | Seis notebooks completos en kernels nuevos del entorno propio. |
| `scripts/ejecutar_notebooks_finales.py` | Alias 03-06; validaciones vigentes reutilizadas. |
| `scripts/ejecutar_preparacion.py` | Alias 01-02; validaciones vigentes reutilizadas. |
| `scripts/ejecutar_seleccion.py` | Modo predeterminado y --verificar: evidencia completa y protocolo válidos; sin entrenamiento nuevo. |
| `scripts/ejecutar_tuning.py` | Modo predeterminado y --verificar: evidencia completa y protocolo válidos; sin entrenamiento nuevo. |
| `scripts/empaquetar_entrega.py` | ZIP real con CRC, manifiesto y estructura requeridos. |
| `scripts/explicar_local.py` | Contraste real del modelo nativo sobre desarrollo, en copia temporal. |
| `scripts/figura_tuning.py` | Biblioteca invocada por generador, notebook y auditoría. |
| `scripts/generar_memo.py` | Generación real en copia temporal; seis páginas visualmente idénticas. |
| `scripts/preflight_openai.py` | --verificar: configuración local; sin clave y sin inferencia. |
| `scripts/preparar_runtime_local.py` | Preparación real de bundles y kernel local. |
| `scripts/recuperar_respuestas_llm.py` | --verificar: inspección del libro y caché; sin recuperación nueva. |
| `scripts/reproducir.py` | Champion reproducido; predicciones exactamente iguales. |
| `scripts/verificar_avance_rubrica.py` | Evaluación real; salida redirigida a copia temporal. |
| `scripts/verificar_fase.py` | Biblioteca invocada por seis fases y coordinador. |

## Ajustes de portabilidad

Los auxiliares de preparación, ejecución final y cierre utilizan ahora el runner de esta entrega y su kernel propio. El coordinador reconoce el estado cerrado. El cierre informa un estado incompleto sin quedar esperando indefinidamente. Se añadieron modos explícitos para revisar evidencias existentes y para solicitar una nueva ejecución deliberada de las fases. Chrome puede configurarse mediante `CHROME_BIN`; el generador escribe directamente en `docs/`.

Los archivos científicos `src/datos.py` y `src/pipeline.py`, las particiones, las decisiones y el PDF aprobado conservan su contenido. La enmienda de portabilidad documenta los cambios limitados de raíz Git y ubicación de credenciales sin reescribir las fuentes de los entrenamientos. El nombre `v2` permanece en metadatos históricos y archivos de protocolo; no es un directorio necesario dentro de la entrega.

## Recursos y límites

La reproducción exacta requiere los bundles, predicciones, registro histórico de costos y el servidor MLflow con sus modelos originales. El ZIP público excluye estos insumos privados. La prueba utilizó esos recursos locales y un entorno Python propio de `pset_3`; no equivale a restaurar el proyecto en otra máquina.

No se volvieron a entrenar candidatos ni a ejecutar tuning. Los comandos de fase revisan los informes terminados; `--ejecutar` invoca la implementación original y `--reanudar` habilita la continuación deliberada del coordinador. El protocolo y sus condiciones siguen vigentes.

`preflight_openai.py --verificar` confirmó que no hay una clave configurada en la nueva carpeta. Se conserva el registro de la evaluación histórica del LLM, pero autenticación, acceso al modelo y nuevas respuestas de OpenAI no se probaron. Para repetir esa parte se necesita configurar credenciales privadas y respetar el presupuesto restante.

El generador y las capturas se probaron en copias temporales para preservar el PDF aprobado y su evidencia editorial. SHA-256 del PDF: `108a70a93e74b150121382b5cd266e64e61cf40435eb0d4c01c5b1089c4393c6`.

Detalle verificable: [validacion-ejecutables.json](validacion-ejecutables.json), [manifiestos de notebooks](01-verificacion.json), [auditoría](auditoria-rubrica.json) y [reproducción del champion](seleccion/reproduccion-champion.json).
