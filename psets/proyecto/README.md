# Proyecto OULAD: apoyo académico preventivo

Wilmer Puerta. El proyecto restaurado conserva la estructura por etapas en [oulad/](oulad/README.md).

- [PSet 1: propuesta, auditoría y entregables](oulad/pset-01/README.md).
- [PSet 2: entrega con estructura pset_2](oulad/pset_2/README.md); [versión histórica](oulad/pset-02/README.md).
- [PSet 3: entrega con estructura pset_3](oulad/pset_3/README.md); [versiones históricas](oulad/pset-03/README.md).
- [PSet 4: alcance y planificación](oulad/pset-04/README.md).
- [Proyecto final: implementación en curso](oulad/proyecto_final/README.md).
- [ZIP PSet 2](oulad/PSet2_entrega_Puerta_Wilmer.zip) y [ZIP PSet 3](oulad/PSet3_entrega_Puerta_Wilmer.zip).

PSet 3 conserva los modelos y métricas históricos. PSet 4 tiene el núcleo de priorización probado; sus servicios e integración siguen pendientes. La publicación excluye datos privados, credenciales, entornos, cachés y respaldos.

---

# [Nombre de tu proyecto]

> Este es el README de tu proyecto: reemplaza cada sección entre corchetes a medida que avanzas. Escríbelo para alguien que clona tu fork sin haber estado en clase y necesita entender qué hace el proyecto y correrlo, no como una nota para ti.

[Un párrafo: qué problema de negocio resuelve, para quién, y qué predice el modelo. Sale de tu propuesta del PSet 1, que está completa en `docs/`.]

**Métrica de éxito:** [la métrica de negocio y el umbral de decisión del PSet 1]

## Datos

| Fuente | Qué contiene | Cómo se obtiene | Dónde queda |
|---|---|---|---|
| [nombre de la fuente] | [qué filas y columnas trae, desde qué fecha] | [la URL, la API o el procedimiento exacto] | `data/raw/[archivo]` |

Los datos no están en el repositorio. Para regenerarlos desde cero: [los comandos, en orden]. Se completa con el PSet 1.

## Cómo correr el pipeline de datos

[Los comandos, en orden y desde qué carpeta, para ir de la fuente al warehouse: levantar la infraestructura, construir la imagen, subir el flow a Kestra, limpiar, cargar y correr dbt. Cada paso dice qué archivo deja y dónde. Se completa con el PSet 2.]

## Cómo entrenar y evaluar el modelo

[Qué notebook corre cada etapa del modelado, en qué orden, y qué necesita levantado (MLflow). Se completa con el PSet 3.]

## Modelo final

[El modelo elegido, su `run_id` en MLflow y la métrica que lo sostiene. El razonamiento completo está en `docs/decision_modelo.md`. Se completa con el PSet 3.]

## Cómo correr el servicio

[Cómo se construye y se levanta el contenedor de `servicio/`, qué versión del modelo carga desde el registro, y un ejemplo de petición con su respuesta. Se completa con el PSet 4.]
