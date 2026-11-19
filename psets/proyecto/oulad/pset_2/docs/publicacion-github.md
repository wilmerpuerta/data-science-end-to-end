# Publicación del paquete en el fork del curso

Destino autorizado por el autor el 14-nov-2026: [wilmerpuerta/data-science-end-to-end](https://github.com/wilmerpuerta/data-science-end-to-end), rama master. El repositorio ya contiene laboratorios, enunciados, rúbricas y configuración del curso; esos archivos se conservan.

El paquete revisado se ubica en [psets/proyecto/oulad/](https://github.com/wilmerpuerta/data-science-end-to-end/tree/master/psets/proyecto/oulad). Esa carpeta contiene el README del proyecto, datasets/ con metadatos, las entregas pset-01/ y pset_2/, y los marcadores de continuidad pset-03/ y pset-04/. Se añade una entrada desde el README de psets/proyecto/.

## Abrir y ejecutar desde otra copia

```bash
git clone https://github.com/wilmerpuerta/data-science-end-to-end.git
cd data-science-end-to-end/psets/proyecto/oulad
```

Desde esa carpeta, seguir [README.md del pipeline](../README.md). Los comandos documentados conservan su forma: por ejemplo, `python3 pset_2/kestra/scripts/infra.py prepare`. La raíz de ejecución del paquete es oulad/, no la raíz del fork que contiene los laboratorios. Las rutas se calculan desde los scripts y no dependen de una ubicación personal.

Solo se copian los archivos versionables revisados. CSV originales, entornos, archivos .env privados, claves, caches y logs permanecen fuera de la publicación. Para reproducir se obtienen los CSV identificados y se prepara la configuración privada de cada entorno según las guías.

## Alcance de la publicación

El enunciado aplicado a este paquete es [enunciado.md](enunciado.md), entregado por el autor y basado en Snowflake, Kestra, dbt y Spark. El fork conserva además el material general del curso; sus plantillas no sustituyen ese enunciado específico ni implican que este pipeline use DuckDB.

Publicar los archivos no levanta la infraestructura en Codespaces, no carga datos en Snowflake y no demuestra que el pipeline se haya probado allí. El entorno de ejecución validado y la reproducción limpia siguen descritos en [revision-paquete.md](revision-paquete.md). El workflow heredado del curso comprueba psets/proyecto con pytest; su estado no equivale a las 168 pruebas dbt ni a una ejecución cloud de OULAD.

El conftest.py del paquete excluye de la colección pytest dos entradas de spark-submit: requieren argumentos CLI o CSV montados, y ejecutarlas al importar produciría un error ajeno a las pruebas unitarias. Los cuatro tests de invariantes Raw siguen disponibles sin datos originales ni Snowflake. Las siete pruebas sintéticas Spark se ejecutan con el comando test-features del pipeline, como antes.

No se modifica la configuración .devcontainer/ o .github/ del curso, ni se crean etiquetas de entrega académica como parte de esta publicación. El historial previo se mantiene mediante un commit descendiente de master, sin push forzado.

## Actualización autorizada del 15-nov-2026

El autor solicitó actualizar todos los archivos revisados de PSet 1 y PSet 2 en el mismo destino psets/proyecto/oulad/, rama master. La publicación incluye el memo PSet 1 ampliado a cinco páginas, Canvas, Markdown, notebook, PDF completo y pitch de seis diapositivas en PPTX/PPT, junto con generadores y verificaciones. El README y el contrato de datos de PSet 2 incorporan objetivo de cobertura/anticipación, tres políticas, presupuesto común, separación de futuras salidas de simulación y límites del MVP. El [diagnóstico de compatibilidad](impacto-revision-pset1.md) explica por qué no cambian el runtime ni las 35 columnas de la OBT.

El memo técnico PSet 2 conserva la instantánea de ejecución de los días 12-13 de noviembre y sus seis páginas. Las referencias a publicación pendiente dentro de ese memo o de informes previos corresponden a la fecha de esas verificaciones; no se reescribe evidencia histórica para aparentar una nueva ejecución. El estado de publicación se verifica en el historial de commits del destino y en GitHub Actions. Colab sigue pendiente de sincronización.

La copia de publicación se actualiza desde la lista de archivos candidatos revisados, se compara con el contenido local y se confirma que el diff se limita a psets/proyecto/oulad/. Se conserva el historial de master y se usa push normal. No se incluyen CSV, credenciales, entornos, respaldos ni archivos temporales; no se cambian materiales o configuración del curso.

## Actualización final de los memos PSet 1

El usuario autorizó publicar la síntesis del protocolo posterior de tutorías en ambas variantes: memo breve de dos páginas con nombre original y memo de cinco páginas con sufijo _version_extendida, ambos en pset-01/output/pdf/. La ejecución del piloto continúa fuera del MVP. Se incluyen las dos fuentes Markdown, notebook y documento completo sincronizados, README, trazabilidad, mapa de rúbrica, generadores e informes de verificación.

La actualización conserva el directorio psets/proyecto/oulad/ y el historial de master. No modifica código de ejecución del pipeline, las 35 columnas de la OBT ni recursos cloud; el memo técnico PSet 2 mantiene sus seis páginas. Los informes anteriores de revisión visual o compatibilidad conservan el estado de publicación en que fueron generados; el resultado del envío se verifica en GitHub.
