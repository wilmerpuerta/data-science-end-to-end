# Apoyo académico a tiempo con OULAD

Wilmer Puerta · Proyecto académico de ciencia de datos.

Evaluar si la actividad digital longitudinal permite detectar futuras reprobaciones con los mismos cupos de revisión preventiva. El contexto es una universidad hipotética; todavía no hay entrenamiento ni impacto educativo demostrado.

La implementación y los entregables revisados viven en [oulad/](oulad/README.md). Allí se conserva una estructura por etapas, con datos compartidos identificados y comandos reproducibles.

## Entregas disponibles

- [PSet 1: propuesta, Canvas, notebook y pitch](oulad/pset-01/README.md).
- [PSet 2: pipeline Kestra, Snowflake, dbt y Spark](oulad/pset-02/README.md).
- [Memo técnico PSet 2, seis páginas](oulad/pset-02/output/pdf/PSet2_memo_Puerta_Wilmer.pdf).
- [Revisión del paquete y límites de la evidencia](oulad/pset-02/docs/revision-paquete.md).

PSet 3 y PSet 4 permanecen pendientes de sus enunciados específicos. No se declaran modelos entrenados ni servicio de predicción.

## Datos y ejecución

Los cinco CSV originales OULAD se obtienen según [datasets/README.md](oulad/datasets/README.md) y se verifican contra su manifiesto. No se distribuyen datos originales ni credenciales en Git.

Desde la raíz del fork, entrar en el paquete antes de seguir sus comandos:

```bash
cd psets/proyecto/oulad
```

Seguir el [recorrido desde una copia nueva](oulad/pset-02/README.md#recorrido-desde-una-copia-nueva) para preparar autenticación privada, levantar Compose y ejecutar Kestra, dbt y Spark. El entorno probado y las limitaciones están documentados; esta publicación no afirma ejecución del pipeline en Codespaces.

El enunciado específico aplicado al PSet 2 es [el documento entregado por el autor](oulad/pset-02/enunciado.md), con Snowflake como destino. Se conserva además el material general del curso en las carpetas de enunciados, laboratorios y configuración.
