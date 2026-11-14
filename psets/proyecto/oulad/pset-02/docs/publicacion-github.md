# Publicación del paquete en el fork del curso

Destino autorizado por el autor el 14-nov-2026: [wilmerpuerta/data-science-end-to-end](https://github.com/wilmerpuerta/data-science-end-to-end), rama master. El repositorio ya contiene laboratorios, enunciados, rúbricas y configuración del curso; esos archivos se conservan.

El paquete revisado se ubica en [psets/proyecto/oulad/](https://github.com/wilmerpuerta/data-science-end-to-end/tree/master/psets/proyecto/oulad). Esa carpeta contiene el README del proyecto, datasets/ con metadatos, las entregas pset-01/ y pset-02/, y los marcadores de continuidad pset-03/ y pset-04/. Se añade una entrada desde el README de psets/proyecto/.

## Abrir y ejecutar desde otra copia

```bash
git clone https://github.com/wilmerpuerta/data-science-end-to-end.git
cd data-science-end-to-end/psets/proyecto/oulad
```

Desde esa carpeta, seguir [README.md del pipeline](../README.md). Los comandos documentados conservan su forma: por ejemplo, `python3 pset-02/scripts/infra.py prepare`. La raíz de ejecución del paquete es oulad/, no la raíz del fork que contiene los laboratorios. Las rutas se calculan desde los scripts y no dependen de una ubicación personal.

Solo se copian los archivos versionables revisados. CSV originales, entornos, archivos .env privados, claves, caches y logs permanecen fuera de la publicación. Para reproducir se obtienen los CSV identificados y se prepara la configuración privada de cada entorno según las guías.

## Alcance de la publicación

El enunciado aplicado a este paquete es [enunciado.md](../enunciado.md), entregado por el autor y basado en Snowflake, Kestra, dbt y Spark. El fork conserva además el material general del curso; sus plantillas no sustituyen ese enunciado específico ni implican que este pipeline use DuckDB.

Publicar los archivos no levanta la infraestructura en Codespaces, no carga datos en Snowflake y no demuestra que el pipeline se haya probado allí. El entorno de ejecución validado y la reproducción limpia siguen descritos en [revision-paquete.md](revision-paquete.md). El workflow heredado del curso comprueba psets/proyecto con pytest; su estado no equivale a las 168 pruebas dbt ni a una ejecución cloud de OULAD.

El conftest.py del paquete excluye de la colección pytest dos entradas de spark-submit: requieren argumentos CLI o CSV montados, y ejecutarlas al importar produciría un error ajeno a las pruebas unitarias. Los cuatro tests de invariantes Raw siguen disponibles sin datos originales ni Snowflake. Las siete pruebas sintéticas Spark se ejecutan con el comando test-features del pipeline, como antes.

No se modifica la configuración .devcontainer/ o .github/ del curso, ni se crean etiquetas de entrega académica como parte de esta publicación. El historial previo se mantiene mediante un commit descendiente de master, sin push forzado.
